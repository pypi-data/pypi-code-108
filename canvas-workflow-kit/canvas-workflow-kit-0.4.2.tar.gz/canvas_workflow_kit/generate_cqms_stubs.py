#!/usr/bin/env python

import json
import textwrap
import re
import sys

from glob import iglob

import xmltodict

from colorama import Fore, init as colorama_init

from canvas_workflow_kit.internal.string import snakecase

from canvas_workflow_kit.value_set import v2021  # NOQA pylint: disable=unused-import
from canvas_workflow_kit.value_set.value_set import ValueSet

MAX_WIDTH = 99

colorama_init(autoreset=True)


def get_subclasses(cls):
    subclasses = []

    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(get_subclasses(subclass))

    return subclasses


value_sets = get_subclasses(ValueSet)


def value_set_by_oid(oid):
    for value_set in value_sets:
        if value_set.OID == oid:
            return value_set

    print(Fore.RED + f'No ValueSet found for OID: {oid}')


def wrap_and_indent(string, prefix=None, width=MAX_WIDTH, indent=4):
    if prefix:
        string = f'{prefix}: {string}'

    wrapped = []

    for line in string.splitlines():
        wrapped.append('\n'.join(
            textwrap.wrap(line, break_long_words=False, width=width - indent)))

    return textwrap.indent('\n'.join(wrapped), ' ' * indent)


def format_list(items, indent=4):
    return '\n'.join(
        "{}'{}',".format(' ' * indent, re.sub(r'\r|\n|\s+', ' ', item.replace("'", "\\'")))
        for item in items)


def v(element):
    if not element:
        return None

    if '@value' in element:
        return element['@value']

    if '@code' in element:
        return element['@code']

    if '@root' in element:
        return element['@root']

    if 'item' in element:
        return v(element['item'])

    if 'part' in element:
        return v(element['part'])

    return element


def d(element):
    return json.dumps(element, indent=2)


def ensure_list(element):
    if not isinstance(element, list):
        return [element]

    return element


def generate(directory, year):
    with open('./builtin_cqms/stub_template.py.txt') as stub:
        stub_template = stub.read()

    oids = None
    qmd = None

    for xml_file in iglob(f'./data/cqms/{directory}/**/CMS*.xml'):
        if 'SimpleXML' in xml_file:
            continue

        print(Fore.GREEN + f'Processing "{xml_file}"')

        with open(xml_file) as file:
            contents = file.read()

        qmd = xmltodict.parse(contents)['QualityMeasureDocument']

        authors = []
        cqm_number = None
        cqm_version = v(qmd['versionNumber']).split('.')[0]
        data_criteria = None
        oids = []
        qmd_value_sets = set()
        references = []
        short_description = v(qmd['text'])
        title = v(qmd['title'])

        for author in ensure_list(qmd['author']):
            authors.append(
                v(author['responsibleParty']['representedResponsibleOrganization']['name']))

        for subject_of in qmd['subjectOf']:
            code = subject_of['measureAttribute']['code']
            value = subject_of['measureAttribute']['value']

            if v(code.get('originalText')) == 'eCQM Identifier (Measure Authoring Tool)':
                cqm_number = v(value)

            if v(code) == 'RAT':
                rationale = v(value)

            if v(code) == 'CRS':
                recommendation = v(value)

            if v(code) == 'DEF':
                definition = v(value)

            if v(code) == 'REF':
                references.append(v(value))

            if v(code) == 'GUIDE':
                guidance = v(value)

            if v(code) == 'IPOP':
                initial_population = v(value)

            if v(code) == 'DENOM':
                denominator = v(value)

            if v(code) == 'DENEX':
                denominator_exclusions = v(value)

            if v(code) == 'DENEXCEP':
                denominator_exceptions = v(value)

            if v(code) == 'NUMER':
                numerator = v(value)

            if v(code) == 'NUMEX':
                numerator_exclusions = v(value)

        cms_id = f'{cqm_number}v{cqm_version}'

        # Heart Failure (HF): Angiotensin-Converting Enzyme (ACE) Inhibitor or Angiotensin Receptor
        # Blocker (ARB) Therapy for Left Ventricular Systolic Dysfunction (LVSD)

        snake_title = re.sub(r'\([^()]*?\)', ' ', title)
        snake_title = (snake_title
                       .lower()
                       .replace(' - ', ' ')
                       .replace(':', '')
                       .replace('%', ' percent')
                       .replace('>', 'gt')
                       .replace('<', 'lt')
                       .replace('.', '_')
                       .replace('/', '_')
                       .strip())  # yapf: disable
        snake_title = re.sub(r'\s+', ' ', snake_title)
        snake_title = snakecase(snake_title)

        denominator_body = 'pass'

        if denominator == 'Equals Initial Population':
            denominator_body = 'return self.in_initial_population()'

        for component in ensure_list(qmd['component']):
            if 'dataCriteriaSection' in component:
                data_criteria = component['dataCriteriaSection']

        if not data_criteria:
            print(Fore.RED + 'dataCriteriaSection not found')
            sys.exit(1)

        def add_oid(oid):
            if oid:
                oids.append(oid)

                return True

            return False

        def handle_observation_criteria(observation):
            value = observation.get('value')
            code = observation.get('code')
            participation = observation.get('participation')

            if not value and not code:
                print(Fore.RED + 'Unknown observationCriteria type:', d(observation))
                return

            value_set_added = False

            if value:
                try:
                    add_oid(value['@valueSet'])
                    value_set_added = True
                except KeyError:
                    # BAG: nothing useful if there's no valueSet
                    pass

            if participation:
                try:
                    add_oid(participation['role']['playingEntity']['code']['@valueSet'])
                    value_set_added = True
                except KeyError:
                    if not value_set_added:
                        print(Fore.RED + 'Unable to get observationCriteria participation code', d(observation))

            if code:
                try:
                    add_oid(code['@valueSet'])
                except KeyError:
                    if (
                            not value_set_added and
                            'Patient Characteristic' not in v(observation['title'])
                    ):
                        print(Fore.RED + 'Unable to get observationCriteria code', d(observation))

            handle_participants(observation.get('participation', []))

        def handle_participants(participants):
            if not participants:
                return

            participants = ensure_list(participants)

            found_participant = False

            for participant in participants:
                role = participant['role']

                if 'playingDevice' in role:
                    if add_oid(role['playingDevice']['code'].get('@valueSet')):
                        found_participant = True

                if 'playingEntity' in role:
                    if add_oid(role['playingEntity']['code'].get('@valueSet')):
                        found_participant = True

                if 'playingMaterial' in role:
                    if add_oid(role['playingMaterial']['code'].get('@valueSet')):
                        found_participant = True

                if 'playingManufacturedMaterial' in role:
                    if add_oid(role['playingManufacturedMaterial']['code'].get('@valueSet')):
                        found_participant = True

            if not found_participant:
                print(Fore.YELLOW + 'participant not found', d(participants))

        for entry in ensure_list(data_criteria['entry']):
            if 'actCriteria' in entry:
                handle_participants(entry['actCriteria'].get('participation', []))

                if 'code' in entry['actCriteria']:
                    try:
                        add_oid(entry['actCriteria']['code']['@valueSet'])
                    except KeyError:
                        print(Fore.RED + 'Unable to get actCriteria code', d(entry['actCriteria']))
                elif 'outboundRelationship' in entry['actCriteria']:
                    try:
                        add_oid(entry['actCriteria']['outboundRelationship']['observationCriteria']['value']['@valueSet'])
                    except KeyError:
                        print(Fore.RED + 'Unable to get actCriteria code', d(entry['actCriteria']))
                else:
                    print(Fore.YELLOW + 'actCriteria', d(entry['actCriteria']))
            elif 'encounterCriteria' in entry:
                try:
                    add_oid(entry['encounterCriteria']['code']['@valueSet'])
                except KeyError:
                    print(Fore.RED + 'Unable to get encounterCriteria code', d(entry['encounterCriteria']))

                if 'dischargeDispositionCode' in entry['encounterCriteria']:
                    add_oid(entry['encounterCriteria']['dischargeDispositionCode']['valueSet'])
            elif 'grouperCriteria' in entry:
                continue
            elif 'observationCriteria' in entry:
                handle_observation_criteria(entry['observationCriteria'])
            elif 'procedureCriteria' in entry:
                if entry['procedureCriteria']['code']:
                    try:
                        add_oid(entry['procedureCriteria']['code'].get('valueSet'))
                    except KeyError:
                        print(Fore.RED + 'Unable to get procedureCriteria code', d(entry['procedureCriteria']))
                else:
                    print(Fore.YELLOW + 'procedureCriteria', entry['procedureCriteria'])
            elif 'substanceAdministrationCriteria' in entry:
                handle_participants(entry['substanceAdministrationCriteria']['participation'])
            elif 'supplyCriteria' in entry:
                handle_participants(entry['supplyCriteria']['participation'])
            else:
                print(Fore.RED + 'Unknown criterion type:', entry)

            for oid in oids:
                value_set = value_set_by_oid(oid)

                qmd_value_sets.add(value_set.__name__)

        with open(f'./builtin_cqms/stubs/cms{cms_id}_{snake_title}.py', 'w') as stub:
            stub.write(
                stub_template.format(
                    authors=format_list(authors, indent=8),
                    class_name=cms_id,
                    cms_url=f'https://ecqi.healthit.gov/ecqm/measures/cms{cms_id}',
                    definition=wrap_and_indent(definition, 'Definition'),
                    denominator=wrap_and_indent(denominator, 'Denominator', indent=8),
                    denominator_body=denominator_body,
                    denominator_exceptions=wrap_and_indent(
                        denominator_exceptions, 'Exceptions', indent=8),
                    denominator_exclusions=wrap_and_indent(
                        denominator_exclusions, 'Exclusions', indent=8),
                    funding_source='',
                    guidance=wrap_and_indent(guidance, 'Guidance'),
                    initial_population=wrap_and_indent(
                        initial_population, 'Initial population', indent=8),
                    numerator=wrap_and_indent(numerator, 'Numerator', indent=8),
                    numerator_exclusions=wrap_and_indent(
                        numerator_exclusions, 'Exclusions', indent=8),
                    rationale=wrap_and_indent(rationale, 'Rationale'),
                    recommendation=wrap_and_indent(
                        recommendation, 'Clinical recommendation', indent=8),
                    references=format_list(references, indent=8),
                    short_description=wrap_and_indent(short_description, 'Description'),
                    title=wrap_and_indent(title),
                    plain_title=title,
                    types=['CQM'],
                    value_sets='\n' + wrap_and_indent(', '.join(sorted(qmd_value_sets))),
                    year=year))


if __name__ == '__main__':
    generate('2021', '2021')
