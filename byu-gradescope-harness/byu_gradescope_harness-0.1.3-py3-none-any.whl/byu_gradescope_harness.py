import json
import traceback

class GradescopeHarness:
    def __init__(self):
        self._tests = []

    def test(self, score):
        """Returns test decorator
        Adds function to test suite
        """

        def decorator(func):
            def decorated():
                """If the function passes, you get the points"""
                try:
                    func()
                    return {
                        "score": score,
                        "name": func.__name__
                    }
                except Exception as ex:
                    tb = traceback.format_exc()
                    return {
                        "score": 0,
                        "name": func.__name__,
                        "output": f"Error: {ex}\n{tb}"
                    }

            self._tests.append(decorated)
            return decorated

        return decorator

    def run_tests(self):
        test_results = [test() for test in self._tests]
        return {
            # "visibility": "hidden", # use default "visible"
            "tests": test_results
        }

    def run_tests_and_save(self, filename="results.json"):
        results = self.run_tests()
        with open(filename, 'wt') as f:
            print(f"Saving test results to {filename}")
            json.dump(results, f)


harness = GradescopeHarness()
test = harness.test
save_test_results = harness.run_tests_and_save

