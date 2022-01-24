import base64
import requests
import json
import io
import sqlmorph_api
import sys
from contextlib import redirect_stdout, redirect_stderr
import unittest
import os
from pathlib import Path
import shutil

class TestClass(unittest.TestCase):

    def get_access_token(self):
        url = "https://account.phdata.io/oauth2/ausaxr6ifFEPr3KPY4x6/v1/token"
        client_id = "0oaqmyesrCGbkfnIA4x6"
        client_secret = os.environ['OKTA_CLIENT_SECRET']
        encoded = ("%s:%s" % (client_id, client_secret)).encode('utf-8')
        auth_header = "Basic " + base64.standard_b64encode(encoded).decode('utf-8')
        data = {'grant_type': 'client_credentials'}

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(url, data=data, headers=headers)
        return response.json().get('access_token')

    def test_shouldCreateDirectoryWithTranslationsWhenPassedFile(self):
        self.maxDiff = None
        shutil.rmtree('./cli/test/snowflake', ignore_errors=True)
        token = self.get_access_token()
        myArgs = [
            '--source', 'impala',
            '--target', 'snowflake',
            '--auth-token', token,
            '--input', './cli/test/known-good/statement.sql',
            '--output', './cli/test/',
            '--server-config', './cli/test/server-config-empty.properties',
            '--debug'
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            sqlmorph_api.runner(myArgs)
        self.assertTrue("No equivalent function for 'min_tinyint' exists in Snowflake" in output.getvalue())
        with open("cli/test/snowflake/cli/test/known-good/statement.sql") as fh:
            actual = fh.read()
        self.assertEqual("""SELECT
  PATINDEX(
    '%[^ 0-9A-z]%',
    'Please ensure the door is locked!'
  );
SELECT
  PATINDEX(
    '%[^ 0-9A-z]%',
    'Please ensure the door is locked again!!'
  );
SELECT
  -- ERROR: FunctionRewriter: line 3, character 7: No equivalent function for 'min_tinyint' exists in Snowflake.
  MIN_TINYINT(c1)
FROM
  t1;""", actual)

    def test_shouldPrintErrorToStdoutWhenFileFails(self):
        shutil.rmtree('./cli/test/snowflake', ignore_errors=True)
        token = self.get_access_token()
        myArgs = [
            '--source', 'impala',
            '--target', 'snowflake',
            '--auth-token', token,
            '--input', './cli/test/known-bad/statement.sql',
            '--output', './cli/test/'
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            sqlmorph_api.runner(myArgs)
        self.assertTrue("Error in file: ./cli/test/known-bad/statement.sql" in output.getvalue())

    def __shouldPrintErrorToStderrWhenInvalidOptions(self, args):
        shutil.rmtree('./cli/test/snowflake', ignore_errors=True)
        output = io.StringIO()
        with redirect_stderr(output):
            sqlmorph_api.runner(args)
        self.assertTrue("ERROR" in output.getvalue())

    def test_shouldPrintErrorToStderrWhenInvalidDBOptionsSourceImpala(self):
        myArgs = [
            '--source', 'impala',
            '--target', 'snowflake',
            '--auth-token', 'XXX',
            '--output', './cli/test/',
            '--db-url=HR/HR_USER@//oraclerds.caewceohkuoi.us-east-1.rds.amazonaws.com:1521/ORCL',
            '--db-schema=HR',
            '--db-table=%'
        ]
        self.__shouldPrintErrorToStderrWhenInvalidOptions(myArgs)

    def test_shouldPrintErrorToStderrWhenInvalidDBOptionsInputFile(self):
        myArgs = [
            '--source', 'oracle',
            '--target', 'snowflake',
            '--auth-token', 'XXX',
            '--input', './cli/test/known-bad/statement.sql',
            '--output', './cli/test/',
            '--db-url=HR/HR_USER@//oraclerds.caewceohkuoi.us-east-1.rds.amazonaws.com:1521/ORCL',
            '--db-schema=HR',
            '--db-table=%'
        ]
        self.__shouldPrintErrorToStderrWhenInvalidOptions(myArgs)

    def test_shouldPrintErrorToStderrWhenInvalidDBOptionsMissingSchema(self):
        myArgs = [
            '--source', 'oracle',
            '--target', 'snowflake',
            '--auth-token', 'XXX',
            '--output', './cli/test/',
            '--db-url=HR/HR_USER@//oraclerds.caewceohkuoi.us-east-1.rds.amazonaws.com:1521/ORCL',
            '--db-table=%'
        ]
        self.__shouldPrintErrorToStderrWhenInvalidOptions(myArgs)

    def test_shouldPrintErrorToStderrWhenInvalidDBOptionsMissingTable(self):
        myArgs = [
            '--source', 'oracle',
            '--target', 'snowflake',
            '--auth-token', 'XXX',
            '--output', './cli/test/',
            '--db-url=HR/HR_USER@//oraclerds.caewceohkuoi.us-east-1.rds.amazonaws.com:1521/ORCL',
            '--db-schema=HR'
        ]
        self.__shouldPrintErrorToStderrWhenInvalidOptions(myArgs)

    def test_shouldPrintErrorToStderrWhenInvalidDBOptionsMissingURL(self):
        myArgs = [
            '--source', 'oracle',
            '--target', 'snowflake',
            '--auth-token', 'XXX',
            '--output', './cli/test/',
            '--db-schema=HR',
            '--db-table=%'
        ]
        self.__shouldPrintErrorToStderrWhenInvalidOptions(myArgs)

    def test_shouldCreateDirectoryWithTranslationsWhenPassedDirectory(self):
        shutil.rmtree('./cli/test/snowflake', ignore_errors=True)
        token = self.get_access_token()
        target = 'snowflake'
        inputPath = './cli/test/known-good'
        outputPath = './cli/test/'
        myArgs = [
            '--source', 'oracle',
            '--target', target,
            '--auth-token', token,
            '--input', inputPath,
            '--output', outputPath,
            '--server-config', './cli/test/server-config.properties'
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            sqlmorph_api.runner(myArgs)
        self.assertTrue("support CHECK clause" in output.getvalue())

        dict = {
            "./cli/test/snowflake/cli/test/known-good/statement.sql": "MIN_TINYINT",
            "./cli/test/snowflake/cli/test/known-good/create-with-error-errors.txt": "doesn't support CHECK clause",
            "./cli/test/snowflake/cli/test/known-good/create-with-error.sql": "CREATE TABLE",
            "./cli/test/snowflake/cli/test/known-good/cfg-test.sql": "CREATE TABLE TEST",
            "./cli/test/snowflake/cli/test/known-good/statement-errors.txt": "mismatched input ';'",
            "./cli/test/snowflake/cli/test/known-good/myFolder/statement copy.sql": "",
            "./cli/test/snowflake/cli/test/known-good/myFolder/statement copy-errors.txt": "mismatched input ';'",
            "./cli/test/snowflake/cli/test/known-good/myFolder/anotherFolder/statement.sql":  "",
            "./cli/test/snowflake/cli/test/known-good/myFolder/anotherFolder/statement-errors.txt": "mismatched input ';'"
        }

        totalSourceFiles = 0
        for root, dirs, files in os.walk(inputPath):
            for f in files:
                totalSourceFiles += 1
        totalTargetFiles = 0
        for root, dirs, files in os.walk(os.path.join(outputPath, target)):
            for f in files:
                with open(os.path.join(root, f)) as fh:
                    fileContents = fh.read()
                self.assertIn(dict[os.path.join(root, f)] , fileContents)
                totalTargetFiles += 1
        self.assertEqual(totalSourceFiles + 4, totalTargetFiles) # extra 4 is for the .errors file

        # Test server side config options
        with open("cli/test/snowflake/cli/test/known-good/cfg-test.sql") as fh:
            actual = fh.read()
        self.assertNotIn("TEST_view", actual)
        self.assertIn('"TIMESTAMP" TIMESTAMP', actual)

    def test_calculate_output_file(self):
        self.maxDiff = None
        self.assertEqual(Path("/tmp/snowflake/sql").resolve(), sqlmorph_api._calculate_output_file("/tmp/sql/", "/tmp/snowflake"))
        self.assertEqual(Path("/tmp/snowflake/sql/a.sql").resolve(), sqlmorph_api._calculate_output_file("/tmp/sql/a.sql", "/tmp/snowflake"))
        self.assertEqual(Path("./snowflake/sql").resolve(), sqlmorph_api._calculate_output_file("./sql", "snowflake"))
        self.assertEqual(Path("/tmp/snowflake/sql").resolve(), sqlmorph_api._calculate_output_file("./sql", "/tmp/snowflake"))

if __name__ == '__main__':
    unittest.main()
