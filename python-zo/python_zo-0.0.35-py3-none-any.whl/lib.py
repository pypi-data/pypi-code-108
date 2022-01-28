import argparse
import configparser
import csv
import json
import os
import re
import sys

from itertools import permutations
from jinja2 import Environment, FileSystemLoader, BaseLoader
from .filters import apply_filters, first_lower, unknown_types
from .classes import Table


def load_schema(p):
	content = json.load(open(p))
	for v in content['data']:
		v['fieldMap'] = {y['key']: y for y in v['fields']}
		if 'kind' not in v:
			v['kind'] = content['kind']
	content['data'].sort(key=lambda x: x["key"])
	return content


def mix_all(args, mappings, tags):
	type_mappings = {a: b for a, b in mappings}
	for x, y in permutations(args, 2):
		y_map = {yy['key']: yy for yy in y['data']}
		for v in x['data']:
			k = v['key']
			if x['kind'] == 'gql' and k not in y_map and k.startswith('Input') and k[5:] in y_map:
				k = k[5:]
			if k not in y_map and k in type_mappings and type_mappings[k] in y_map:
				k = type_mappings[k]
			if 'tags' not in v:
				v['tags'] = {}
			if k in tags:
				for t in tags[k]:
					v['tags'][t] = 1
			if k not in y_map:
				continue
			vv = y_map.get(k, {})
			v[y['kind']], f_map = vv, vv['fieldMap']
			for f in v['fields']:
				f[y['kind']] = f_map.get(f['key'])
				if y['kind'] == 'gql' and not f[y['kind']]:
					f[y['kind']] = f_map.get(f.get('nameExact')) or f_map.get(f.get('tagGql')) or f_map.get(type_mappings.get(f['key']))


def load_file(name, args):
	init_path = os.path.join(args.template_path, name)
	if os.path.exists(init_path):
		target = {}
		exec(open(init_path).read(), target)
		return target
	return {}


def walk(path):
	return [os.path.join(root, f) for root, folders, files in os.walk(path) for f in files]


def apply_vars(tpl, my_vars):
	return re.sub(r'{{\s*([^}\s]+)\s*}}', lambda x: my_vars.get(x.group(1)) or 'None', tpl)


GO_FUNC_RE = re.compile(r'((?:\n//[^\n]*)?\nfunc \([^)]+\) (\w+)[\s\S]+?\n}(?=\n|$))')


def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


def render_template(env, schemas, args):
	schema = schemas[0]
	tpls = set(env.list_templates())
	classes = load_file('classes.py', args)
	table = classes.get('Table', lambda x: x)

	if args.cmd == 'scaffold':
		db_model = api_field = None
		if args.graphql.count("/") != 1:
			return eprint('--graphql pattern should be like "Query/MySettings"')
		gql_type, gql_model = args.graphql.split("/")
		for schema in schemas:
			if schema['kind'] == 'spanner':
				for m in schema['data']:
					if m['key'] == args.model:
						db_model = m
						break
			if schema['kind'] == 'gql':
				for m in schema['data']:
					if m['key'] == gql_type:
						for f in m['fields']:
							if f['key'] == gql_model:
								api_field = f
		if not db_model:
			return eprint('model not specified or not found')
		if not api_field:
			return eprint(gql_model, 'not found')

		if args.verb.count('/') != 1:
			return eprint('verb must be in pattern Get/Getter')
		verb, verb_er = args.verb.split('/', maxsplit=2)

		skel_path = os.path.join(args.template_path, 'skel')
		skels = walk(skel_path)
		if not skels:
			return eprint('skel folder not found in template')

		paths_csv = os.path.join(args.template_path, 'paths.csv')
		path_tags = {x[1]: x[0] for x in os.path.exists(paths_csv) and csv.reader(open(paths_csv).read().strip().splitlines()[1:]) or []
					 if len(x) == 2 and x[0].strip() and x[0].strip()[0] != "#"}

		for skel in skels:
			content = open(skel).read()
			env = Environment(loader=BaseLoader())
			apply_filters(env, {}, {})
			var_filters = load_file('filters.py', args)
			custom_filters = var_filters.get('apply_filters', lambda *_: None)
			custom_filters(env, {})
			my_args = dict(
				usecase=args.usecase,
				service=first_lower(verb_er), Service=verb_er,
				apiType=first_lower(verb), ApiType=verb,
				nameType=db_model['name'] + verb, NameType=db_model['Name'] + verb,
				api=api_field, modelType=gql_type,
				args=args,
			)
			my_vars = table(Table(db_model, **my_args))
			skel_rel_path = os.path.relpath(skel, skel_path)
			rel_path = apply_vars(skel_rel_path, my_vars)
			if 'None' in rel_path: continue
			out_path = os.path.join(args.out_path, rel_path).replace('.jinja2', '').replace('.j2', '')
			patch = not args.force and os.path.exists(out_path) and any(1 for x in path_tags if x in skel_rel_path and path_tags[x] == 'patch')
			template = env.from_string(content)
			output = template.render(my_vars, patch=patch)
			if not os.path.exists(out_path) or (args.force and not patch):
				eprint('[DONE] file written', out_path)
				dirname = os.path.dirname(out_path)
				if not os.path.exists(dirname):
					os.makedirs(dirname, exist_ok=True)
				with open(out_path, 'w', encoding="utf8") as dst:
					dst.write(output)
			elif patch:
				existing = open(out_path, 'r').read()
				func_names = {b: a for a, b in GO_FUNC_RE.findall(output)}
				if GO_FUNC_RE.search(existing):  # and args.force
					existing = GO_FUNC_RE.sub(lambda x: func_names.get(x.group(2), x.group(0)), existing)
				with open(out_path, 'w') as dst:
					dst.write(existing)
				eprint('[PATCHED] existing file patched', out_path)
			else:
				eprint('[SKIPPED] output file exists', out_path)
				if args.verbose:
					print(output)

	elif args.cmd == 'generate':
		targets = {args.out_path: schema['data']} if args.one_file else {os.path.join(args.out_path, x[args.name_key] + args.suffix): [x] for x in schema['data']}
		schema_map = {s['kind']: {x['key']: x for x in s['data']} for s in schemas}

		for f, tbls in targets.items():
			type_contents = []
			type_tpls = [x for x in tpls if x.startswith("type.")]
			if type_tpls:
				template = env.get_template(type_tpls[0])
				for x in tbls:
					out = template.render(table(Table(x, this=x, schema=schema_map, args=args)))
					if out.strip():
						type_contents.append(out)

			headers = []
			header_tpls = [x for x in tpls if x.startswith("header.")]
			if header_tpls:
				template1 = env.get_template(header_tpls[0])
				headers.append(
					template1.render(tables=schema['data'], schema=schema_map, args=args, unknown_types=[y for x in tbls for y in unknown_types(x['fields'])]))

			footers = []
			footer_tpls = [x for x in tpls if x.startswith("footer.")]
			if footer_tpls:
				template3 = env.get_template(footer_tpls[0])
				footers.append(template3.render(tables=schema['data'], schema=schema_map, args=args))

			if not type_contents and len(headers) == 0:
				eprint(f'[{os.path.basename(f)}] no template found\n')
				continue

			output = headers + type_contents + footers

			with open(f, 'w', encoding="utf8") as dst:
				dst.write('\n'.join(output))


def merge_schemas(schemas, kinds):
	m = {}
	ret = []
	for x in schemas:
		kind = kinds[0] if x['kind'] in kinds else x['kind']
		if kind in m:
			m[kind]['data'] += x['data']
		else:
			m[kind] = x
			ret.append(x)
	for x in ret:
		m = {}
		for y in x['data']:
			m[y['key']] = y
		for y in x['data']:
			fields = y['fields']
			new_fields, updated = [], False
			y['embeds'] = []
			for z in fields:
				if not z['Name']:
					if z['Type'] in m:
						new_fields += [
							{kk: (first_lower(y['key'] + 'Id') if kk == 'key' and vv == first_lower(z['key']) + 'Id' else vv) for kk, vv in yy.items()}
							for yy in m[z['Type']]['fields']]
						updated = True
						y['embeds'].append(z['Type'])
				else:
					new_fields.append(z)
			if updated:
				y['fields'] = new_fields
				y['fieldMap'] = {yy['key']: yy for yy in y['fields']}
	return ret


def add_arg(parser, conf, key, *args, help=None, fn=lambda x: x, **kwargs):
	parser.add_argument(*args, help=argparse.SUPPRESS if key in conf else help, required=key not in conf, default=fn(conf.get(key)), **kwargs)


def parse_args():
	conf = {}
	if os.path.exists('.zo'):
		cp = configparser.ConfigParser()
		cp.read('.zo')
		conf = {s: dict(cp.items(s)) for s in cp}

	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers(dest="cmd")
	subparsers.required = True

	parser_g = subparsers.add_parser('generate', help='generate')
	parser_g.add_argument('--one-file', action='store_true', default=False)
	parser_g.add_argument('--merge-schemas', nargs='+', help="merge schemas")
	parser_g.add_argument('--suffix', nargs='?', default="")
	parser_g.add_argument('--name-key', nargs='?', default="nameDb")

	parser_g.add_argument('--enum-type', default="string", type=str, choices=["string", "int"], help="enum type", dest="enumType")
	parser_g.add_argument('--enum-start', default=1, type=int, help="enum start", dest="enumStart")

	parser_g.add_argument('--src-json-paths', nargs='+', help="source json paths", required=True)
	parser_g.add_argument('--template-path', help="template path", required=True)
	parser_g.add_argument('-o', '--out-path', help="output file path", required=True)
	parser_g.add_argument('-v', '--verbose', help="verbose output", action="store_true")

	parser_s = subparsers.add_parser('scaffold', help='scaffold')
	parser_s.add_argument('--model', help="spanner model (eg. User)", required=True)
	parser_s.add_argument('--graphql', help="graphql pattern (Query/MySettings or Mutation/SetSetting)", required=True)
	parser_s.add_argument('--verb', default="Get/Getter", help="verb (eg. Get/Getter or Find/Finder)", required=True)
	parser_s.add_argument('--usecase', default="usecase", help="usecase rel path (eg. usecase or usecase/user)")
	parser_s.add_argument('-f', '--force', help="force overwrite", action="store_true")
	parser_s.add_argument('-v', '--verbose', help="verbose output", action="store_true")

	conf_scaffold = conf.get('scaffold', {})
	add_arg(parser_s, conf_scaffold, 'src_json_paths', '--src-json-paths', nargs='+', help="source json paths", fn=lambda x: x and x.split('\n'))
	add_arg(parser_s, conf_scaffold, 'template_path', '--template_path', help="template path")
	add_arg(parser_s, conf_scaffold, 'out_path', '-o', '--out-path', help="output file path")

	args = parser.parse_args()
	return args


def main():
	args = parse_args()
	env = Environment(loader=FileSystemLoader(args.template_path))
	mappings_path = os.path.join(args.template_path, 'mappings.csv')
	mappings, aliases = {}, {}
	if os.path.exists(mappings_path):
		lines = [x for x in csv.reader(open(mappings_path).read().strip().splitlines()[1:]) or [] if len(x) >= 2 and x[0].strip() and x[0].strip()[0] != "#"]
		mappings.update({(x[0], x[1]): x[2] for x in lines if len(x) == 3})
		for x in lines:
			if len(x) != 2: continue
			if x[0] not in aliases:
				aliases[x[0]] = []
			aliases[x[0]].append(x[1])
	tags_path = os.path.join(args.template_path, 'tags.csv')
	tags = {}
	for x in os.path.exists(tags_path) and csv.reader(open(tags_path).read().strip().splitlines()[1:]) or []:
		if len(x) == 2 and x[0].strip() and x[0].strip()[0] != "#":
			if x[1] not in tags:
				tags[x[1]] = []
			tags[x[1]].append(x[0])
	apply_filters(env, mappings, aliases)
	var_filters = load_file('filters.py', args)
	custom_filters = var_filters.get('apply_filters', lambda *_: None)
	custom_filters(env, mappings, aliases)

	schemas = [load_schema(x) for x in args.src_json_paths]
	if args.cmd == 'generate' and args.merge_schemas:
		schemas = merge_schemas(schemas, args.merge_schemas)
	mix_all(schemas, mappings, tags)
	render_template(env, schemas, args)
