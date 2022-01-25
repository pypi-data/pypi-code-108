#!/usr/bin/env python3.8
import argparse
import yaml
import os
from colorama import Fore
from datetime import datetime
import sys
import git
from jutge.judges.java_judge import JavaJudge
from jutge.judges.sql_judge import SQLJudge
from jutge.utils import run_or_exit, prettify_dict, load_file, copy_clipboard
import jutge.utils as utils

def loadYAML(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)
        except FileNotFoundError:
            print(f"{Fore.RED}Couldn't find testcase file: {filename}{Fore.RESET}")
            exit(1)

class Grade:
    def __init__(self, args):
        self.args = args
        self.result = {}

        self.tests = self.load_tests(args.test_cases)

        self.available_judges = {}
        self.available_judges["java"] = JavaJudge
        self.available_judges["sql"] = SQLJudge


    def find_and_load_yaml_files(self, tests, tests_dir):
        if isinstance(tests, list):
            for i, el in enumerate(tests):
                tests[i] = self.find_and_load_yaml_files(el, tests_dir)
        elif isinstance(tests, dict):
            for k, v in tests.items():
                if k == "file":
                    if v:
                        tests = load_file(f"{tests_dir}/{v}")
                        return tests
                else:
                    tests[k] = self.find_and_load_yaml_files(v, tests_dir)
        return tests


    def load_tests(self, tests_path):
        tests = loadYAML(tests_path)
        judge = tests.get("judge")
        if not judge:
            print(f"{Fore.RED}Error! No s'ha especificat la clau \"judge\" en els tests.{Fore.RESET}")
            exit(1)

        tests_dir = os.path.dirname(tests_path)
        tests = self.find_and_load_yaml_files(tests, tests_dir)
        # prettify_dict(tests)

        return tests


    def load_repo(self, repo_dir):
        repo = None
        try:
            repo = git.Repo(repo_dir)
        except git.exc.NoSuchPathError as e:
            print(f"Directory {repo_dir} does not exist.")
            raise e
        except git.exc.InvalidGitRepositoryError as e:
            print(f"Directory {repo_dir} is not a Git repository.")
            raise e
        return repo


    def prepare_repo(self, repo_dir, tag=None, limit_date=None):
        repo = run_or_exit(self.load_repo, repo_dir)
        origin = repo.remotes.origin
        self.result["repository"] = origin.url
        run_or_exit(repo.git.checkout, "master" , out=f"Checkout master branch...", err=f"Error checkout master")
        run_or_exit(origin.pull, tags=True, force=True, out=f"Pulling {repo_dir}...", err=f"Error pulling {repo_dir}")

        # Checkout specific tag
        if tag:
            self.result["tag"] = tag

            def on_tag_error():
                self.result.setdefault("errors", []).append(f"No s'ha trobat el tag: {tag}")
                self.copy_clipboard()
                exit(1)

            run_or_exit(repo.git.checkout, tag,
                    out=f"Checkout {tag} tag...",
                    err=f"Error checkout {tag} tag",
                    err_func=on_tag_error
            )

        # Get current commit date
        seconds_since_epoch = repo.head.commit.committed_date
        tag_date = datetime.fromtimestamp(seconds_since_epoch)
        print(f"Last change: {tag_date}")
        self.result["last_change"] = str(tag_date)
        if limit_date:
            self.result["deadline"] = limit_date
            limit_date = datetime.fromisoformat(limit_date)
            if tag_date > limit_date:
                print(Fore.RED + "COMPTE!! El tag ha segut modificat després de la data d'entrega" + Fore.RESET)
                result.setdefault("errors", []).append("El tag ha segut modificat després de la data d'entrega")

        return repo


    def copy_clipboard(self):
        if self.args.copy:
            utils.copy_clipboard(utils.json(self.result, sort_keys=False))


    def grade(self, repo_dir):
        interactive = self.args.interactive
        disable_git = self.args.disable_git

        self.result["name"] = self.tests.get("name")
        tag = self.tests.get("tag")
        if not disable_git:
            limit_date = self.tests.get("date")
            repo = self.prepare_repo(repo_dir, tag, limit_date)

        judge_type = self.tests.get("judge")
        Judge = self.available_judges.get(judge_type)
        if not Judge:
            print(f"Error! No s'ha trobat el judge: \"{judge_type}\"")
            exit(1)

        judge = Judge(repo_dir, self.tests, self.args)
        result_judge = judge.judge(interactive=interactive)
        self.result = {**self.result, **result_judge}

        self.copy_clipboard()

        # save JSON
        if self.args.save:
            pass

        # Checkout master on exit
        if not disable_git:
            run_or_exit(repo.git.checkout, "master" , out=f"Checkout master branch on exit...", err=f"Error checkout master")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("test_cases")
    parser.add_argument("dir", nargs="*")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--remove-color", action="store_true", default=False)
    parser.add_argument("-g", "--disable-git", action="store_true", default=False)
    parser.add_argument("-i", "--interactive", action="store_true", default=False)
    parser.add_argument("-v", "--volume", action="append", default=[])
    parser.add_argument("--copy", action="store_true", default=False)
    parser.add_argument("--save", nargs="?", default=False)
    parser.add_argument("--light", action="store_true", default=False)
    args = parser.parse_args()

    grade = Grade(args)
    for repo_dir in args.dir:
        grade.grade(repo_dir)

if __name__ == '__main__':
    main()
