import time

from spell.cli.integration_tests.testing_utils import verify_exit_code


class TestModel:
    def test_create_model(self, run, tmpdir):
        with tmpdir.as_cwd():
            # Create a file
            model_name = "my_model"
            contents = "a sweet model"
            with open(model_name, "w") as f:
                f.write(contents)

            # Upload the file to Spell
            result = run(["upload", "--name", model_name, model_name])
            verify_exit_code(result, 0)
            resource_name = f"uploads/{model_name}"

            # Wait until server has processed upload
            retries = 0
            while run(["ls", resource_name]).exit_code and retries < 10:
                time.sleep(1)
                retries += 1

            # Create model
            result = run(["model", "create", model_name, resource_name])
            verify_exit_code(result, 0)

            # Create model with custom version
            result = run(["model", "create", f"{model_name}:custom_version", resource_name])
            verify_exit_code(result, 0)

            # Create model with a description and specific files
            result = run(
                [
                    "model",
                    "create",
                    model_name,
                    resource_name,
                    "-f",
                    f"{model_name}:destination",
                    "-d",
                    "description",
                ]
            )
            verify_exit_code(result, 0)

            # List models
            result = run(["model", "list"])
            verify_exit_code(result, 0)

            # List model versions
            result = run(["model", "describe", model_name])
            verify_exit_code(result, 0)

            # Edit model description
            result = run(["model", "update-description", f"{model_name}:v1", "new description"])
            verify_exit_code(result, 0)

            # Delete model version
            result = run(["model", "rm", f"{model_name}:v1"])
            verify_exit_code(result, 0)

            # Delete whole model
            result = run(["model", "rm", model_name])
            verify_exit_code(result, 0)
