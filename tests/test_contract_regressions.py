"""Generic completion and submitted handoff consistency regressions."""
import copy
import unittest

from tools.validate import ROOT, Invalid, load, schema, validate


DEVELOPMENT = ('repository', 'worktree', 'branch', 'base', 'issue', 'pr')


def generic_bundle():
    return load(ROOT / 'examples/nonrepo-delivered.json')


def live_prior_bundle():
    b = load(ROOT / 'examples/safe-handoff.json')
    n = copy.deepcopy(b['task']['nodes'][0])
    n.update(id='prior-session', identity=copy.deepcopy(b['checkpoint']['handoff']['from']),
             state='running', writes=[], resources=[], depends_on=[])
    b['task']['nodes'].append(n)
    b['task']['nodes'][0]['state'] = 'running'
    b['checkpoint'].update(state='blocked', process_state='inflight', durable=False,
                           next_action='Establish prior session quiescence')
    b['result'].update(outcome='blocked', reason='Prior session is still running')
    return b


class ContractRegressions(unittest.TestCase):
    def test_generic_delivered_without_development_fields(self):
        b = generic_bundle()
        self.assertTrue(validate(b))
        self.assertEqual(len(b['task']['nodes']), 1)
        self.assertEqual(b['task']['classification'], 'S')
        self.assertEqual(b['task']['nodes'][0]['mode'], 'coordinator')
        self.assertEqual(b['task']['nodes'][0]['writes'], [])
        self.assertEqual(b['result']['outcome'], 'delivered')
        for obj in [b['task'], b['checkpoint'], b['result'],
                    *b['task']['nodes'], *b['receipts']]:
            self.assertEqual(set(obj['identity']), {'provider', 'session'})
        for obj in [b['task'], b['result'], *b['result']['evidence']]:
            self.assertNotIn('candidate', obj)
        for key, name in [('task', 'task-packet'), ('checkpoint', 'checkpoint'),
                          ('result', 'result')]:
            schema(name, b[key])
        schema('control-receipt', b['receipts'][0])

    def test_generic_record_correlations(self):
        for record in ('checkpoint', 'result', 'receipt'):
            for field in ('task_id', 'run_id', 'provider', 'session'):
                with self.subTest(record=record, field=field):
                    b = generic_bundle()
                    obj = b['receipts'][0] if record == 'receipt' else b[record]
                    target = obj['identity'] if field in ('provider', 'session') else obj
                    target[field] = 'unrelated'
                    with self.assertRaisesRegex(Invalid, '^correlation$'):
                        validate(b)

    def test_generic_node_identity_is_required(self):
        for field in ('provider', 'session'):
            b = generic_bundle()
            b['task']['nodes'][0]['identity'][field] = 'unrelated'
            with self.assertRaisesRegex(Invalid, '^identity$'):
                validate(b)
            b = generic_bundle()
            del b['task']['nodes'][0]['identity'][field]
            with self.assertRaisesRegex(Invalid, '^schema$'):
                validate(b)

    def test_development_extension_cannot_be_partial(self):
        for field in DEVELOPMENT:
            with self.subTest(field=field):
                b = load(ROOT / 'examples/happy-path.json')
                del b['task']['identity'][field]
                with self.assertRaisesRegex(Invalid, '^schema$'):
                    validate(b)
                b = generic_bundle()
                b['task']['identity'][field] = 'a' * 40 if field == 'base' else 'example'
                with self.assertRaisesRegex(Invalid, '^schema$'):
                    validate(b)

    def test_standalone_development_extensions_remain_strict(self):
        development = load(ROOT / 'examples/safe-handoff.json')
        receipt = copy.deepcopy(generic_bundle()['receipts'][0])
        receipt['identity'] = development['task']['identity']
        for name, original in [('task-packet', development['task']),
                               ('checkpoint', development['checkpoint']),
                               ('result', development['result']),
                               ('control-receipt', receipt)]:
            schema(name, original)
            for field in DEVELOPMENT:
                with self.subTest(schema=name, field=field):
                    obj = copy.deepcopy(original)
                    del obj['identity'][field]
                    with self.assertRaisesRegex(Invalid, '^schema$'):
                        schema(name, obj)
        for record in ('task', 'result', 'evidence'):
            obj = copy.deepcopy(development['task' if record == 'task' else 'result'])
            target = obj['evidence'][0] if record == 'evidence' else obj
            del target['candidate']
            with self.assertRaisesRegex(Invalid, '^schema$'):
                schema('task-packet' if record == 'task' else 'result', obj)

    def test_development_candidates_remain_required(self):
        for record in ('task', 'result', 'evidence'):
            for value in (None, 'not-a-sha'):
                b = load(ROOT / 'examples/happy-path.json')
                obj = b['result']['evidence'][0] if record == 'evidence' else b[record]
                if value is None:
                    del obj['candidate']
                else:
                    obj['candidate'] = value
                with self.subTest(record=record, value=value):
                    with self.assertRaisesRegex(Invalid, '^schema$'):
                        validate(b)

    def test_generic_optional_candidate_correlations(self):
        b = generic_bundle()
        b['result']['candidate'] = 'a' * 40
        with self.assertRaisesRegex(Invalid, '^candidate$'):
            validate(b)
        b['task']['candidate'] = 'a' * 40
        with self.assertRaisesRegex(Invalid, '^stale-evidence$'):
            validate(b)
        b['result']['evidence'][0]['candidate'] = 'a' * 40
        self.assertTrue(validate(b))

    def test_development_node_cannot_drop_binding(self):
        b = load(ROOT / 'examples/happy-path.json')
        n = copy.deepcopy(b['task']['nodes'][0])
        n.update(id='unbound-writer', writes=['src/other.txt'])
        n['identity'] = {'provider': 'example', 'session': 'unbound'}
        b['task']['nodes'].append(n)
        with self.assertRaisesRegex(Invalid, '^writer-identity$'):
            validate(b)

    def test_live_prior_rejected_even_when_blocked_without_writes(self):
        b = live_prior_bundle()
        self.assertEqual(b['task']['nodes'][-1]['writes'], [])
        with self.assertRaisesRegex(Invalid, '^handoff$'):
            validate(b)
        b['task']['nodes'][-1]['state'] = 'completed'
        self.assertTrue(validate(b))
        self.assertTrue(validate(load(ROOT / 'examples/safe-handoff.json')))

    def test_handoff_matches_exact_provider_and_session(self):
        for field in ('provider', 'session'):
            b = live_prior_bundle()
            b['task']['nodes'][-1]['identity'][field] = 'different'
            self.assertTrue(validate(b))
        b = live_prior_bundle()
        b['checkpoint']['handoff'] = None
        self.assertTrue(validate(b))  # Blocked/inflight alone remains honest.

    def test_generic_handoff_uses_same_live_prior_check(self):
        b = generic_bundle()
        prior = dict(b['task']['identity'], session='prior')
        b['checkpoint']['handoff'] = dict(
            to=copy.deepcopy(b['task']['identity']), **{'from': prior},
            prior_quiescent=True, acknowledged=True)
        self.assertTrue(validate(b))
        n = copy.deepcopy(b['task']['nodes'][0])
        n.update(id='prior', identity=prior, state='running')
        b['task']['nodes'].append(n)
        b['checkpoint'].update(state='blocked', process_state='inflight', durable=False)
        b['result'].update(outcome='blocked')
        with self.assertRaisesRegex(Invalid, '^handoff$'):
            validate(b)


if __name__ == '__main__':
    unittest.main()
