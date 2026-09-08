"""Offline contract checks only; never execute commands or fetch evidence URLs."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=ValueError)
def strict_datetime(value):
    if not isinstance(value, str):
        return True  # Schema type check owns non-string values.
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
        return False
    return datetime.fromisoformat(value).tzinfo is not None


class Invalid(ValueError):
    """A stable diagnostic code, not a copy of untrusted input."""


def require(condition, code):
    if not condition:
        raise Invalid(code)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate-json-key')
        result[key] = value
    return result


def load(path):
    try:
        text = Path(path).read_text(encoding='utf-8')
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(Invalid('json-number')))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        raise Invalid('json-input') from None


def schema(name, value):
    definition = load(ROOT / 'schemas' / '0.1' / (name + '.schema.json'))
    Draft202012Validator.check_schema(definition)
    validator = Draft202012Validator(definition, format_checker=FORMATS)
    require(next(validator.iter_errors(value), None) is None, 'schema')


def path_parts(value):
    # Canonical portable relative paths; no normalization of malformed tokens.
    require('\\' not in value and not value.startswith('/') and ':' not in value,
            'path')
    parts = value.split('/')
    require(all(p not in ('', '.', '..') for p in parts), 'path')
    return PurePosixPath(value).parts


def within(path, parent):
    p, q = path_parts(path), path_parts(parent)
    return p[:len(q)] == q


def overlap(a, b):
    return within(a, b) or within(b, a)


def writer(identity):
    return identity['provider'], identity['session']


def validate(bundle):
    schema('bundle', bundle)
    task, check, result = (bundle[k] for k in ('task', 'checkpoint', 'result'))
    for name, value in [('task-packet', task), ('checkpoint', check), ('result', result)]:
        schema(name, value)
    for rec in bundle['receipts']:
        schema('control-receipt', rec)
    for item in [check, result, *bundle['receipts']]:
        require(all(item[k] == task[k] for k in ('task_id', 'run_id', 'identity')), 'correlation')
    require(result['candidate'] == task['candidate'], 'candidate')
    require(task['identity']['pr'].strip() == task['identity']['pr'], 'identity')
    require(task['acceptance'] and len(set(task['acceptance'])) == len(task['acceptance']), 'acceptance')
    auth = task['authorization']
    require(auth['granted'] and auth['by'].strip() and task['required_actions']
            and set(task['required_actions']) <= set(auth['actions']), 'authorization')
    require(len(set(auth['actions'])) == len(auth['actions']), 'authorization')
    for scope in auth['write_scopes']:
        path_parts(scope)
    nodes = task['nodes']
    require(nodes and len({n['id'] for n in nodes}) == len(nodes), 'dag')
    by_id = {n['id']: n for n in nodes}
    visited, visiting = set(), set()

    def visit(key):
        require(key in by_id and key not in visiting, 'dag')
        if key in visited:
            return
        visiting.add(key)
        n = by_id[key]
        require(len(set(n['depends_on'])) == len(n['depends_on']), 'dag')
        for dep in n['depends_on']:
            visit(dep)
            if n['state'] in ('running', 'completed'):
                require(by_id[dep]['state'] == 'completed', 'dependency')
        visiting.remove(key)
        visited.add(key)

    identities, pr_writers = {}, {}
    for n in nodes:
        visit(n['id'])
        ident = n['identity']
        require(all(str(v).strip() == str(v) and str(v).strip() for v in ident.values()), 'identity')
        key = writer(ident)
        if key in identities:
            require(identities[key]['pr'] == ident['pr'], 'cross-pr-writer')
            require(identities[key] == ident, 'writer-identity')
        identities[key] = ident
        if n['writes']:
            binding = ident['repository'], ident['pr']
            require(binding not in pr_writers or pr_writers[binding] == ident, 'writer-ownership')
            pr_writers[binding] = ident
        for path in n['writes']:
            path_parts(path)
            require(any(within(path, scope) for scope in auth['write_scopes']), 'write-authorization')
        require(len(set(n['resources'])) == len(n['resources']), 'resource')
    require(task['identity'] in [n['identity'] for n in nodes], 'identity')
    active = [n for n in nodes if n['state'] == 'running']
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            require(not (set(a['resources']) & set(b['resources'])) and not any(
                overlap(x, y) for x in a['writes'] for y in b['writes']), 'overlap')
    require(result['repair_attempts'] <= task['repair_limit'], 'repair-budget')
    if task['resume_requested'] and not task['resume_supported']:
        require(result['outcome'] == 'blocked' and check['state'] == 'blocked', 'resume-unsupported')
    if check['durable']:
        require(check['history_persisted'] and check['process_state'] == 'quiescent', 'durability')
    handoff = check['handoff']
    if handoff:
        require(handoff['to'] == task['identity'] and handoff['from'] != handoff['to']
                and writer(handoff['from']) != writer(handoff['to'])
                and handoff['prior_quiescent'] and handoff['acknowledged'], 'handoff')
        require(all(handoff['from'][k] == handoff['to'][k]
                    for k in ('repository', 'branch', 'base', 'issue', 'pr')), 'handoff')
    seen_receipts, seen_controls, last_sequence = set(), set(), -1
    for receipt in bundle['receipts']:
        require(receipt['receipt_id'] not in seen_receipts
                and receipt['control_id'] not in seen_controls, 'duplicate-receipt')
        seen_receipts.add(receipt['receipt_id'])
        seen_controls.add(receipt['control_id'])
        require(last_sequence < receipt['sequence'] <= check['sequence'], 'receipt-sequence')
        last_sequence = receipt['sequence']
        require(not receipt['observed'] or receipt['persisted'], 'receipt-state')
        require(not receipt['applied'] or receipt['observed'], 'receipt-state')
        if receipt['action'] == 'resume' and receipt['applied']:
            require(task['resume_supported'], 'resume-unsupported')
    seen_evidence, passed = set(), set()
    for evidence in result['evidence']:
        require(evidence['id'] not in seen_evidence, 'duplicate-evidence')
        seen_evidence.add(evidence['id'])
        require(evidence['candidate'] == task['candidate'], 'stale-evidence')
        require(evidence['acceptance_id'] in task['acceptance'], 'acceptance')
        if evidence['scope'] == 'external':
            require(evidence['readback'].strip(), 'readback')
        if evidence['outcome'] == 'pass':
            passed.add(evidence['acceptance_id'])
    outcome = result['outcome']
    if outcome == 'delivered':
        require(check['state'] == 'completed' and check['process_state'] == 'quiescent'
                and all(n['state'] == 'completed' for n in nodes), 'stage')
        require(passed == set(task['acceptance'])
                and all(e['outcome'] == 'pass' for e in result['evidence']), 'evidence')
    elif outcome == 'blocked':
        require(check['state'] == 'blocked' and result['reason'].strip(), 'stage')
    else:
        require(check['state'] == 'cancelled' and check['process_state'] == 'quiescent'
                and not active, 'cancellation')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    try:
        validate(load(args.bundle))
    except (Invalid, RecursionError) as exc:
        print('INVALID: ' + (str(exc) if isinstance(exc, Invalid) else 'depth'), file=sys.stderr)
        return 1
    print('VALID: offline contract checks passed; external state not verified')
    return 0


if __name__ == '__main__':
    sys.exit(main())
