import os
import re
import json
import glob
import datetime
import difflib

from quickstats.utils.common_utils import timely_info

class NuisanceParameterHarmonizer(object):
    def __init__(self, ref_list=None):
        self.ref_list = ref_list

    @property
    def ref_list(self):
        return self._ref_list
    
    @ref_list.setter
    def ref_list(self, val):
        if val is None:
            self._ref_list = {}
        elif isinstance(val, list):
            self._ref_list = config
        elif isinstance(val, str):
            self._ref_list = json.load(open(val, 'r'))
        else:
            raise ValueError("invalid reference list format")
        
    @staticmethod
    def get_nuiance_parameter_names_collection(ws_paths):
        from quickstats.components import ExtendedModel
        nuis_names_collection = set()
        for ws_path in ws_paths:
            nuis_names = ExtendedModel.get_nuisance_parameter_names(ws_path)
            nuis_names_collection |= set(nuis_names)
        return sorted(list(nuis_names_collection))
    
    @staticmethod
    def filter_nuis(source, patterns=None, excludes=None, exact=False):
        if patterns is None:
            return []    
        if isinstance(patterns, str):
            patterns = [patterns]
        if exact:
            return list(set(source) & set(patterns))
        matches = []    
        for pattern in patterns:
            regex = re.compile(pattern)
            matches += [s for s in source if regex.search(s)]
        if excludes is not None:
            anti_matches = NuisanceParameterHarmonizer.filter_nuis(source, excludes)
            matches = list(set(matches) - set(anti_matches))
        return matches
    
    @staticmethod
    def get_suggested_names(source, possibilities, cutoff=0.6, replace={}):
        suggested_names = {}
        for name in source:
            _name = name
            for old, new in replace.items():
                _name = _name.replace(old, new)             
            matches = difflib.get_close_matches(_name, possibilities, n=1, cutoff=cutoff)
            if matches:
                suggested_names[name] = matches[0]
        return suggested_names
    
    @staticmethod
    def display_difference(old_name, new_name):
        sequence = difflib.SequenceMatcher(None, old_name, new_name)
        match = sequence.find_longest_match(0, len(old_name), 0, len(new_name))
        ahead = old_name[ : match.a]
        atail = old_name[match.a+match.size : ]
        bhead = new_name[ : match.b]
        btail = new_name[match.b+match.size : ]
        common1 = old_name[match.a : match.a+match.size]
        common2 = new_name[match.b : match.b+match.size]
        assert common1 == common2
        print(f'{ahead}\033[91m{common1}\033[0m{atail}'.rjust(80, ' '), '->', f'{bhead}\033[92m{common1}\033[0m{btail}')

    @staticmethod
    def display_mappings(mappings, reference, level=0):
        for k, v in mappings.items():
            description = reference[k].get('description', k)
            if reference[k].get('display', None) == False:
                continue
            print('{indent}{description}:'.format(indent='\t'*level, description=description))
            if 'source' in reference[k]:
                NuisanceParameterHarmonizer.display_mappings(v, reference[k]['source'], level=1)
            else:
                for old_name, new_name in v.items():
                    NuisanceParameterHarmonizer.display_difference(old_name, new_name)
                
    @staticmethod
    def reshape_mappings(mappings, roots=[], result=None):
        if result is None:
            result = {}
        for key, value in mappings.items():
            if isinstance(value, dict):
                NuisanceParameterHarmonizer.reshape_mappings(value, roots + [key], result)
            elif key not in result:
                result[key] = [(roots, value)]
            else:
                result[key].append((roots, value))
        return result

    @staticmethod
    def flatten_mappings(mappings):
        flattened_mappings = {}
        # check duplicates
        reshaped_mappings = NuisanceParameterHarmonizer.reshape_mappings(mappings)
        for old_name in reshaped_mappings:
            dest = reshaped_mappings[old_name]
            if len(reshaped_mappings[old_name]) > 1:
                raise RuntimeError('multiple mappings found for the NP: {} ({})'.format(old_name, 
                                   ','.join([':'.join(field[0]) for field in dest])))
            flattened_mappings[old_name] = dest[0][1]
        return flattened_mappings
    
    @staticmethod
    def remove_nuis(source, target):
        for t in target:
            source.remove(t)
        return source
        
    @staticmethod
    def match_source(suggested_names, source):
        mappings = {s:{} for s in source}
        for old_name, new_name in suggested_names.items():
            for key, value in source.items():
                if new_name in value['names']:
                    mappings[key][old_name] = new_name
        mappings = {k:v for k,v in mappings.items() if v != {}}
        return mappings
    
    @staticmethod
    def get_mappings(nuis_names, reference):
        mappings = {}
        for group in reference:
            # rename by custom mapping
            custom_map = reference[group].get('map', None)
            if custom_map is not None:
                temp = {}
                for old_name, new_name in custom_map.items():
                    if old_name in nuis_names:
                        temp[old_name] = new_name
                if temp:
                    mappings[group] = temp
                continue
                        
            selected = []
            # NPs that match a pattern with exclusion
            selected += NuisanceParameterHarmonizer.filter_nuis(nuis_names, reference[group].get('pattern', None), 
                        reference[group].get('exclude', None), exact=False)
            # NPs that match exactly
            selected += NuisanceParameterHarmonizer.filter_nuis(nuis_names, reference[group].get('match', None),
                        exact=True)
            if not selected:
                continue
            # rename by reformatting
            if ('source' not in reference[group]) and ('names' not in reference[group]):
                format_str = reference[group].get('format', '{NAME}')
                mappings[group] = {}
                for old_name in selected:
                    new_name = old_name
                    # replace strings in old NP
                    for old, new in reference[group].get('replace', {}).items():
                        new_name = new_name.replace(old, new)
                    # format new NP name
                    new_name = format_str.format(NAME=new_name)
                    mappings[group][old_name] = new_name
            # rename by matching suggestions
            else:
                cutoff = reference[group].get('cutoff', 0.6)
                if 'names' in reference[group]:
                    names = reference[group]['names']
                elif 'source' in reference[group]:
                    names = []
                    for key, value in reference[group]['source'].items():
                        names += value['names']
                replace = reference[group].get('replace', {})
                suggested_names = NuisanceParameterHarmonizer.get_suggested_names(selected, names, cutoff, replace)
                if suggested_names:
                    if 'names' in reference[group]:
                        mappings[group] = suggested_names
                    elif 'source' in reference[group]:
                        source = reference[group]['source']
                        mappings[group] = NuisanceParameterHarmonizer.match_source(suggested_names, source)
        return mappings


    def get_harmonize_map(self, nuis_names):
        mappings = self.get_mappings(nuis_names, self.ref_list)
        self.display_mappings(mappings, self.ref_list)
        flattened_mappings = self.flatten_mappings(mappings)
        unknown_nuis = list(set(nuis_names) - set(flattened_mappings))
        if len(unknown_nuis) > 0:
            print('Remained NPs:')
            for unknown in unknown_nuis:
                NuisanceParameterHarmonizer.display_difference(unknown, '?')
        flattened_mappings.update({np:None for np in unknown_nuis})
        return flattened_mappings
    
    def harmonize(self, ws_paths, outfile=None):
        if isinstance(ws_paths, str):
            ws_paths = [ws_paths]
        timely_info('Harmonizing collective workspace files', ','.join(ws_paths))
        nuis_names = NuisanceParameterHarmonizer.get_nuiance_parameter_names_collection(ws_paths)
        harmonize_map = self.get_harmonize_map(nuis_names)
        if outfile is not None:
            json.dump(harmonize_map, open(outfile, 'w'), indent=2, sort_keys=True)
        return harmonize_map
    
    def _harmonize_multi_input(self, input_paths):
        harmonize_map = {}
        if isinstance(input_paths, (str, list)):
            harmonize_map = self.harmonize(input_paths)
        elif isinstance(input_paths, dict):
            for k,v in input_paths.items():
                harmonize_map[k] = self._harmonize_multi_input(v)
        return harmonize_map
    
    @staticmethod
    def get_input_paths(input_expr, base_path='./'):
        if isinstance(input_expr, str):
            full_path = os.path.join(base_path, input_expr)
            ws_files = glob.glob(full_path)
            if not ws_files:
                print('WARNING: No matching input found in {}'.format(full_path))
            return ws_files
        elif isinstance(input_expr, list):
            input_paths = []
            for expr in input_expr:
                input_paths += NuisanceParameterHarmonizer.get_input_paths(expr, base_path)
            return input_paths
        elif isinstance(input_expr, dict):
            input_paths = {}
            for k,v in input_expr.items():
                input_paths[k] = NuisanceParameterHarmonizer.get_input_paths(v, base_path)
            return input_paths
        else:
            raise ValueError('invalid input expr')
        
    def harmonize_multi_input(self, input_config_path, base_path='./', outfile=None):
        config = json.load(open(input_config_path))
        input_paths = NuisanceParameterHarmonizer.get_input_paths(config, base_path)
        harmonize_map = self._harmonize_multi_input(input_paths)
        if outfile is not None:
            json.dump(harmonize_map, open(outfile, 'w'), indent=2, sort_keys=True)
            timely_info('Saved rename output as ', outfile)
        return harmonize_map
