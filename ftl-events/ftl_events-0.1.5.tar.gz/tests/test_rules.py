

from durable.lang import *
import durable.lang

def test_m():
    assert m
    assert m.x
    assert m.x.define() == {'$m': 'x'}
    assert m.x > m.y
    assert (m.x > m.y).define() == {'$gt': {'x': {'$m': 'y'}}}
    assert m.x == m.y
    assert (m.x == m.y).define() ==  {'x': {'$m': 'y'}}
    assert m.x < m.y
    assert (m.x < m.y).define() ==  {'$lt': {'x': {'$m': 'y'}}}


def test_ruleset():

    some_rules = ruleset('test_rules')

    assert some_rules
    assert durable.lang._rulesets
    assert durable.lang._rulesets['test_rules'] == some_rules

    assert len(durable.lang._ruleset_stack) == 0

    with some_rules:
        assert durable.lang._ruleset_stack[-1] == some_rules

    assert len(durable.lang._ruleset_stack) == 0

    assert some_rules.define() == ('test_rules', {})


def test_rules():

    some_rules = ruleset('test_rules1')

    assert some_rules
    assert durable.lang._rulesets
    assert durable.lang._rulesets['test_rules1'] == some_rules

    assert len(durable.lang._ruleset_stack) == 0

    with some_rules:
        assert durable.lang._ruleset_stack[-1] == some_rules

        def x(c):
            print('c')

        #when_all(m.x == 5)(x)
        rule('all', True, m.x == 5)(x)

    assert len(durable.lang._ruleset_stack) == 0

    assert some_rules.define() == ('test_rules1', {'r_0': {'all': [{'m': {'x': 5}}],
                                                           'run': x}})
    post('test_rules1', {'x': '5'})



def test_assert_facts():

    some_rules = ruleset('test_assert_facts')

    with some_rules:
        @when_all(+m.subject.x)
        def output(c):
            print('Fact: {0} {1} {2}'.format(c.m.subject.x, c.m.predicate, c.m.object))

    assert_fact('test_assert_facts',  { 'subject': {'x': 'Kermit'}, 'predicate': 'eats', 'object': 'flies' })

