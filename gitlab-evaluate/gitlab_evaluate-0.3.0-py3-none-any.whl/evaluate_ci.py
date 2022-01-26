import os
import sys
sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

import csv
import argparse
from gitlab_evaluate.lib import git
from gitlab_evaluate.lib.filetree import traverse
from gitlab_evaluate.lib.utils import write_to_csv
from gitlab_evaluate.ci_readiness.test_engine import TestEngine
from gitlab_evaluate.ci_readiness.yaml_reader import get_readiness_report_headers


# Main Loop
# TODO:
# 1. Clone Repository
# 2. Move into Repository
# 3. Iterate over registeredTests and execute each test inside it.
# 4. Conduct tests against repository
# 5. Form Tests into JSON.

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--repo", help="Git Repository To Clone (ex: https://username:password@repo.com")
	args = parser.parse_args()
	repo_url = args.repo
	repo_folder = git.get_repo_folder(repo_url)

	if not os.path.exists(repo_folder):
		git.clone(repo_url)
	
	te = TestEngine(root_path=repo_folder)
	te.register_test("Programming languages", te.check_extension, te.rules.languages, te.results.programming_languages, "More than 2 programming languages found", "count > 2")
	te.register_test("No database files", te.check_extension, te.rules.database_filetypes, te.results.no_stored_database_files, "Database files found", "count > 0")
	te.register_test("No more than one Dockerfile, docker-compose, or Vagrantfile", te.check_multiple_files, te.rules.container_filetypes, te.results.multiple_container_files, "Multiple container files found", "loop count > 1")
	te.register_test("No multiple build files", te.check_multiple_files, te.rules.build_dependencies, te.results.multiple_build_files, "Multiple build files found", "loop count > 1")
	te.register_test("Config files only at root level", te.check_root_file_extension, te.rules.config_filetypes, te.results.sprawling_config_files, "Config files found outside of root directory", "count > 0")
	te.register_test("Build config files only at root level", te.check_root_files, te.rules.build_dependencies, te.results.sprawling_build_files, "Build config files found outside of root directory", "count > 0")
	te.register_test("No build systems building other build systems", te.check_extra_build_commands, [te.rules.build_dependencies, te.rules.build_command_snippets], te.results.nested_build_tools, "Some build tools are triggering other build tools", "count > 0")
	traverse(os.path.abspath(repo_folder), te.run_test_cases)
	te.infer_results()
	csv_file = f"{repo_folder}.csv"
	write_to_csv(csv_file, get_readiness_report_headers()['headers'], te.inferred_results)

	

if __name__ == "__main__":
    main()
