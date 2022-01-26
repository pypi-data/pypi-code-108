import pathlib
import os
from gitlab_ps_utils.json_utils import json_pretty
from gitlab_evaluate.ci_readiness.yaml_reader import get_readiness_config
from gitlab_evaluate.models.test_results import TestResults

class TestEngine():
    def __init__(self, root_path=None):
        self.rules = get_readiness_config()
        self.results = TestResults()
        self.tests = {}
        self.root_path = root_path
        self.cwd = ""
        self.inferred_results = []

    def register_test(self, test_name, test_function, ruleset, results_type, failure_message, fail_condition):
        '''
            Adds entry to self.tests for test execution
        '''
        self.tests[test_name] = {
            'func': test_function,
            'rules': ruleset,
            'results_type': results_type,
            'failure_message': failure_message,
            'fail_condition': fail_condition
        }

    def run_test_cases(self, files):
        '''
            Main function for running the test cases registered in self.tests
        '''
        for f in files:
            self.set_cwd(f)
            for test in self.tests.values():
                test['func'](f, test['rules'], test['results_type'])
    
    def infer_results(self):
        '''
            Infer the results from the tests executed
            and append the results to self.inferred_results
            and print the self.inferred_results to stdout
        '''
        for test_name, test_results in self.tests.items():
            msg = f"{test_name}"
            results = test_results['results_type']
            fail_condition = self.parse_fail_condition(test_results['fail_condition'])
            if eval(fail_condition):
                msg += f" FAILED: {test_results['failure_message']}: {results}"
                self.inferred_results.append({
                    'Test Name': test_name,
                    'Passed/Failed': 'FAILED',
                    'Error Message': test_results['failure_message'],
                    'Data': results
                })
            else:
                msg += f" PASSED"
                self.inferred_results.append({
                    'Test Name': test_name,
                    'Passed/Failed': 'PASSED',
                    'Error Message': '',
                    'Data': ''
                })
        print(json_pretty(self.inferred_results))

    def check_extension(self, file_name, extensions, test_category):
        '''
            Checks if a file with a specific extension exists
            in the folder structure
        '''
        file_ext = pathlib.Path(file_name).suffix
        if file_ext and file_ext in extensions:
            test_category[file_ext] = True
    
    def check_multiple_files(self, file_name, files, test_category):
        '''
            Checks if multiple occurences of a specific file name exists
            in the folder structure
        '''
        if pathlib.Path(file_name).name in files:
            self.incr_dict_val_count(test_category, file_name)
    
    def check_extra_build_commands(self, file_name, rules, test_category):
        '''
            Checks if any provided build files (ex: package.json, pom.xml, etc.)
            is executing any other build tools within them (ex: frontend-maven-plugin in pom.xml)
        '''
        if isinstance(rules, list):
            build_files = rules[0]
            commands = rules[1]
            if pathlib.Path(file_name).name in build_files:
                with open(file_name, 'r') as f:
                    data = f.read()
                    if found := [x for x in commands if x in data]:
                        test_category[file_name] = found
            

    def check_root_file_extension(self, file_name, file_type, test_category):
        '''
            Checks is provided file extensions are in a directory level below the root path

            If a file is found nested in a directory within the root path,
            that file will be flagged
        '''
        file_ext = pathlib.Path(file_name).suffix
        if file_ext and file_ext in file_type:
            if not self.in_root_path():
                self.incr_dict_val_count(test_category, self.strip_root_dir(file_name))
    
    def check_root_files(self, file_name, files, test_category):
        '''
            Checks is provided files are in a directory level below the root path

            If a file is found nested in a directory within the root path,
            that file will be flagged
        '''
        if pathlib.Path(file_name).name in files:
            if not self.in_root_path():
                self.incr_dict_val_count(test_category, self.strip_root_dir(file_name))
        
    def incr_dict_val_count(self, d, k):
        '''
            Helper function to increment a dictionary key value
            where the value is an int
        '''
        if count := d.get(k):
            d[k] = count + 1
        else:
            d[k] = 1

    def parse_fail_condition(self, fail_condition):
        '''
            Basic string comprehension to check for fail conditions
        '''
        if "loop count" in fail_condition:
            fail_condition = fail_condition.replace("loop count", "any(i")
            return f"{fail_condition} for i in results.values())"
        if "count" in fail_condition:
            return fail_condition.replace("count", "len(results)")
    
    def in_root_path(self):
        return self.cwd.split("/")[-1] == self.root_path
    
    def strip_root_dir(self, path):
        if self.root_path:
            return path.split(self.root_path)[-1]
        return path
    
    def set_cwd(self, file_path):
        self.cwd = str(pathlib.Path(file_path).parent)
