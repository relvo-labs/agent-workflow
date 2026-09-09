"""Offline gates, including semantic mutations and cross-directory adoption."""
import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from jsonschema import Draft202012Validator
from tools.validate import ROOT, Invalid, load, validate
from tools.generate_diagram import render


class Fixtures(unittest.TestCase):
    def test_manifest(self):
        manifest = load(ROOT / 'examples/manifest.json')
        names = [row['file'] for row in manifest]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), {p.name for p in (ROOT / 'examples').glob('*.json')} - {'manifest.json'})
        self.assertGreaterEqual(sum(row['valid'] for row in manifest), 3)
        self.assertGreaterEqual(sum(not row['valid'] for row in manifest), 10)
        for row in manifest:
            with self.subTest(fixture=row['file']):
                bundle = load(ROOT / 'examples' / row['file'])
                if row['valid']:
                    self.assertTrue(validate(bundle))
                else:
                    with self.assertRaisesRegex(Invalid, '^' + row['error'] + '$'):
                        validate(bundle)

    def test_canonical_bundle_schemas(self):
        bundle = load(ROOT / 'schemas/0.1/bundle.schema.json')
        for key, name in [('task', 'task-packet'), ('checkpoint', 'checkpoint'), ('result', 'result'), ('receipts', 'control-receipt')]:
            standalone = load(ROOT / f'schemas/0.1/{name}.schema.json')
            for k in ('$schema', '$id', 'title'):
                standalone.pop(k, None)
            embedded = bundle['properties'][key]
            if key == 'receipts':
                embedded = embedded['items']
            self.assertEqual(standalone, embedded)
        for path in (ROOT / 'schemas/0.1').glob('*.json'):
            Draft202012Validator.check_schema(load(path))

    def test_semantic_mutations(self):
        cases = [
            ('candidate', lambda b: b['result'].update(candidate='c' * 40)),
            ('stage', lambda b: b['checkpoint'].update(state='running')),
            ('evidence', lambda b: b['result'].update(evidence=[])),
            ('evidence', lambda b: b['result']['evidence'][0].update(outcome='fail')),
            ('authorization', lambda b: b['task']['authorization'].update(actions=[])),
            ('write-authorization', lambda b: b['task']['authorization'].update(write_scopes=['docs'])),
            ('path', lambda b: b['task']['nodes'][0].update(writes=['src/../private'])),
            ('repair-budget', lambda b: (b['task'].update(repair_limit=0), b['result'].update(repair_attempts=1))),
            ('schema', lambda b: b['result'].update(repair_attempts=2)),
            ('schema', lambda b: b['task'].update(version='0.2')),
            ('schema', lambda b: b['task'].update(unexpected='value')),
            ('schema', lambda b: b['result']['evidence'][0].update(observed_at='not-a-date')),
            ('schema', lambda b: b['task'].update(candidate='B' * 40)),
            ('duplicate-evidence', lambda b: b['result']['evidence'].append(copy.deepcopy(b['result']['evidence'][0]))),
            ('durability', lambda b: b['checkpoint'].update(history_persisted=False)),
        ]
        for expected, mutate in cases:
            with self.subTest(expected=expected, mutate=mutate):
                b = load(ROOT / 'examples/happy-path.json')
                mutate(b)
                with self.assertRaisesRegex(Invalid, '^' + expected + '$'):
                    validate(b)

    def test_dependency_and_resource(self):
        b = load(ROOT / 'examples/happy-path.json')
        n = copy.deepcopy(b['task']['nodes'][0])
        n.update(id='child', depends_on=['implement'], writes=[], state='running')
        b['task']['nodes'][0]['state'] = 'waiting'
        b['task']['nodes'].append(n)
        with self.assertRaisesRegex(Invalid, '^dependency$'):
            validate(b)
        n['depends_on'] = []
        b['task']['nodes'][0]['state'] = 'running'
        for node in b['task']['nodes']:
            node['resources'] = ['deployment:example']
        with self.assertRaisesRegex(Invalid, '^overlap$'):
            validate(b)

    def test_same_pr_disjoint_writers_rejected(self):
        b = load(ROOT / 'examples/happy-path.json')
        n = copy.deepcopy(b['task']['nodes'][0])
        n.update(id='second', writes=['src/other.txt'])
        n['identity']['session'] = 'different-writer'
        b['task']['nodes'].append(n)
        with self.assertRaisesRegex(Invalid, '^writer-ownership$'):
            validate(b)

    def test_handoff_fail_closed(self):
        for field in ('prior_quiescent', 'acknowledged'):
            b = load(ROOT / 'examples/safe-handoff.json')
            b['checkpoint']['handoff'][field] = False
            with self.assertRaisesRegex(Invalid, '^handoff$'):
                validate(b)

    def test_authorized_high_risk(self):
        b = load(ROOT / 'examples/happy-path.json')
        b['task']['risk'] = 'high'
        self.assertTrue(validate(b))

    def test_external_reference_is_not_truth(self):
        b = load(ROOT / 'examples/happy-path.json')
        b['result']['evidence'][0].update(scope='external', readback='synthetic-reference-not-live')
        self.assertTrue(validate(b))  # This proves only the declared-reference rule.

    def test_parser_and_sanitized_cli(self):
        for payload, code in [(' {"task":1,"task":2}', 'duplicate-json-key'),
                              ('{"x": NaN}', 'json-number'),
                              ('{"untrusted-secret-example":', 'json-input'),
                              ('{"untrusted-secret-example":1}', 'schema')]:
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / 'input.json'
                p.write_text(payload)
                run = subprocess.run([sys.executable, str(ROOT / 'tools/validate.py'), str(p)],
                                     text=True, capture_output=True)
                self.assertEqual(run.returncode, 1)
                self.assertEqual(run.stderr.strip(), 'INVALID: ' + code)
                self.assertNotIn('untrusted-secret-example', run.stderr + run.stdout)


class RepositoryGates(unittest.TestCase):
    def test_skills_metadata_ownership_relationships(self):
        skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
        self.assertGreaterEqual(len(skills), 4)
        self.assertLessEqual(len(skills), 6)
        names, relations, ownership = set(), {}, set()
        for path in skills:
            text = path.read_text()
            front = json.loads(text.split('---', 2)[1])
            self.assertEqual(front['name'], path.parent.name)
            self.assertEqual(front['license'], 'Apache-2.0')
            self.assertEqual(front['metadata']['version'], '0.1.0')
            self.assertEqual(set(front), {'name', 'description', 'license', 'compatibility', 'metadata'})
            self.assertTrue(all(isinstance(k, str) and isinstance(v, str) for k, v in front['metadata'].items()))
            self.assertLessEqual(len(front['compatibility']), 500)
            self.assertRegex(front['name'], r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
            self.assertLessEqual(len(front['name']), 64)
            self.assertTrue(front['description'].startswith('Use when '))
            self.assertLessEqual(len(front['description']), 1024)
            self.assertNotIn(front['name'], names)
            names.add(front['name'])
            relations[front['name']] = front['metadata']['related-skills'].split(',')
            for title in ('When to Use', 'Owns', 'Does not own', 'Inputs', 'Outputs', 'Procedure', 'Relationships', 'Verification', 'Pitfalls'):
                self.assertIn('## ' + title + '\n', text)
            self.assertIn('Counter-trigger:', text)
            self.assertIn('tools/validate.py', text)
            own = text.split('## Owns\n', 1)[1].split('\n\n', 1)[0]
            self.assertNotIn(own, ownership)
            ownership.add(own)
        for name, related in relations.items():
            self.assertTrue(set(related) <= names - {name})
            self.assertEqual(len(related), len(set(related)))

    def test_all_local_markdown_links(self):
        for path in ROOT.rglob('*.md'):
            if '.venv' in path.parts or '.git' in path.parts:
                continue
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(), (path, target))

    def test_diagram_source_and_traceability(self):
        data = load(ROOT / 'diagrams/core.json')
        output = (ROOT / 'diagrams/core.svg').read_text()
        self.assertEqual(output, render(data))
        root = ElementTree.fromstring(output)
        ids = {el.attrib.get('id') for el in root.iter()}
        for node in data['nodes']:
            self.assertIn(node['id'], ids)
        for source, target in data['edges']:
            self.assertIn(f'data-edge="{source}:{target}"', output)
        self.assertIn(['repair', 'evidence'], data['edges'])

    def test_no_automatic_workflows(self):
        self.assertEqual(list((ROOT / '.github/workflows').glob('*')), [])

    def test_full_checkout_adoption_from_other_directory(self):
        with tempfile.TemporaryDirectory(prefix='workflow-consumer-') as tmp:
            target = Path(tmp) / 'project with spaces'
            target.mkdir()
            args = [sys.executable, str(ROOT / 'tools/adopt.py'), '--target', str(target)]
            run = subprocess.run(args + ['--probe'], cwd=target, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('VALID: offline contract', run.stdout)
            text = (target / '.agent-workflow/ADOPTION.md').read_text()
            self.assertIn(str(ROOT / 'tools/validate.py'), text)
            self.assertIn(str(ROOT / 'skills/task-intake/SKILL.md'), text)
            self.assertEqual(subprocess.run(args + ['--check', '--probe'], cwd=target,
                                           capture_output=True).returncode, 0)
            self.assertNotEqual(subprocess.run(args, cwd=target, capture_output=True).returncode, 0)
            self.assertEqual({p.name for p in target.iterdir()}, {'.agent-workflow'})

    def test_adoption_refuses_symlink_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target, other = Path(tmp) / 'target', Path(tmp) / 'other'
            target.mkdir(); other.mkdir()
            (target / '.agent-workflow').symlink_to(other, target_is_directory=True)
            run = subprocess.run([sys.executable, str(ROOT / 'tools/adopt.py'), '--target', str(target)],
                                 capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(list(other.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
