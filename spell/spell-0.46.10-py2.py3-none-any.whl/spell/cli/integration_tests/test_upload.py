import os
import time

from spell.cli.integration_tests.testing_utils import verify_exit_code


class TestUpload:
    def test_upload_file(self, run, tmpdir):
        with tmpdir.as_cwd():
            # Create a file
            file = "my_dataset"
            contents = "a bunch of data"
            with open(file, "w") as f:
                f.write(contents)

            # Upload the file to Spell
            result = run(["upload", "--name", "test", file])
            verify_exit_code(result, 0)

            # Wait until server has processed upload
            retries = 0
            while run(["ls", "uploads/test"]).exit_code and retries < 10:
                time.sleep(1)
                retries += 1

            # List the uploaded file
            result = run(["ls", "uploads/test"])
            verify_exit_code(result, 0)
            assert file in result.output

            # Remove the local copy
            os.remove(file)

            # Download a copy from Spell
            result = run(["cp", "uploads/test"])
            verify_exit_code(result, 0)

            # Verify the contents
            with open(file, "r") as f:
                assert f.read() == contents
