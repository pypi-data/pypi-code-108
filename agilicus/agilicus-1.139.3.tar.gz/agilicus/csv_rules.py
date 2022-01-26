import csv
import sys

import agilicus

from . import context


def parse_rules(rule_file, hostname):
    if rule_file == "-":
        input_file = sys.stdin
    else:
        input_file = open(rule_file, "r")

    rules = list()
    with input_file:
        csv_input = csv.DictReader(input_file, delimiter=",", quotechar='"')

        for rule_in in csv_input:
            rule = parse_rule(rule_in, hostname)
            if rule:
                rules.append(rule)

    return rules


def parse_rule(rule, hostname):
    name = rule.get("Name", None)
    path = rule.get("Path", None)
    method = rule.get("Method", None)
    if not name or not path or not method:
        return None

    return agilicus.Rule(
        name=name, path=path, method=method, query_parameters=[], host=hostname
    )


def add_or_replace_rule(role, rule):
    for index in range(len(role.rules)):
        if role.rules[index].name == rule.name:
            role.rules[index] = rule
            return

    role.rules.append(rule)


def add_rules(role, rules):
    if not role.rules:
        role.rules = []

    for rule in rules:
        add_or_replace_rule(role, rule)


def find_role(application, role_name):
    if not application.roles:
        application.roles = []

    if application.roles:
        for role in application.roles:
            if role["name"] == role_name:
                return role

    role = agilicus.Role(name=role_name)
    application.roles.append(role)
    return role


def add_rules_to_app(
    ctx, application_id, role_name, rule_file, org_id=None, hostname=None
):

    token = context.get_token(ctx)
    if not org_id:
        org_id = context.get_org_id(ctx, token)
    apiclient = context.get_apiclient(ctx, token)

    application = apiclient.application_api.get_application(
        app_id=application_id, org_id=org_id
    )

    role = find_role(application, role_name)
    rules = parse_rules(rule_file, hostname)
    add_rules(role, rules)

    application.id = None
    application.created = None
    application.updated = None

    return apiclient.application_api.replace_application(
        application_id, application=application
    )
