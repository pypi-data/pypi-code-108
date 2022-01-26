
from durable.lang import ruleset, rule, m
import asyncio
import jinja2
from faster_than_light import run_module, load_inventory
from ftl_events.condition_parser import parse_condition
from ftl_events.condition_types import Identifier, String, OperatorExpression


def substitute_variables(value, context):
    return jinja2.Template(value, undefined=jinja2.StrictUndefined).render(context)


def call_module(module, module_args, variables, c):
    try:
        print(c)
        variables_copy = variables.copy()
        variables_copy['event'] = str(c.m._d)
        print('running')
        asyncio.run(run_module(load_inventory('inventory.yml'),
                               ['modules'],
                               module,
                               modules=[module],
                               module_args={k: substitute_variables(v, variables_copy) for k, v in module_args.items()}))
        print('ran')
    except Exception as e:
        print(e)


def visit_condition(parsed_condition, condition):
    if isinstance(parsed_condition, Identifier):
        return condition.__getattr__(parsed_condition.value)
    if isinstance(parsed_condition, String):
        return parsed_condition.value
    if isinstance(parsed_condition, OperatorExpression):
        if parsed_condition.operator == "!=":
            return visit_condition(parsed_condition.left, condition).__ne__(visit_condition(parsed_condition.right, condition))
    if isinstance(parsed_condition, OperatorExpression):
        if parsed_condition.operator == "==":
            return visit_condition(parsed_condition.left, condition).__eq__(visit_condition(parsed_condition.right, condition))


def generate_condition(ftl_condition):
    return visit_condition(parse_condition(ftl_condition.value), m)


def make_fn(ftl_rule, variables):
    def fn(c):
        print(f'calling {ftl_rule.name}')
        call_module(ftl_rule.action.module,
                    ftl_rule.action.module_args,
                    variables,
                    c)
    return fn

def generate_rulesets(ftl_rulesets, variables):

    rulesets = []

    for ftl_ruleset in ftl_rulesets:
        a_ruleset = ruleset(ftl_ruleset.name)
        with a_ruleset:

            for ftl_rule in ftl_ruleset.rules:
                fn = make_fn(ftl_rule, variables)
                r = rule('all', True, generate_condition(ftl_rule.condition))(fn)
                print(r.define())
        rulesets.append(a_ruleset)

    return rulesets
