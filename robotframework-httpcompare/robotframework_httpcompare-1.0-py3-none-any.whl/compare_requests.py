from .data_manager import data_manager
import jsoncompare
from .libcommons import libcommons
from .compare_diff import compareDiff
import json, traceback
import re
from jsonpath_ng.ext import parser
from .json_merge import json_merge

ContractComparisonFailureError = "Contract comparison failed."
comparisonLib = "${INFRA}/compare_requests.py"
class compare_requests:

    def init_comparison(self, requestId_1, requestId_2, expectedDivergence=[], ignoreNodes=[], responseComparisonScheme=[], responseComparisonType='full', responseNames=['Response-1', 'Response-2'], responseDataType='JSON', compareByValueNodes=[], deferIgnoredNodeProcessing=False):
        self.requestId_1 = requestId_1
        self.requestId_2 = requestId_2
        self.expectedDivergence = expectedDivergence
        self.responseDiff, self.statusDiff, self.headersDiff = "[]", "[]", "[]"
        if isinstance(expectedDivergence, str) and libcommons.path_exists(expectedDivergence):
            with open(expectedDivergence) as inputFile:
                self.expectedDivergence = inputFile.read()
            self.expectedDivergence = data_manager.process_data(self.expectedDivergence)

        self.ignoreNodes = ignoreNodes
        self.responseComparisonScheme = responseComparisonScheme
        self.responseComparisonScheme = responseComparisonScheme if type(responseComparisonScheme) is list else json.load(open(responseComparisonScheme)) if libcommons.path_exists(responseComparisonScheme) else json.loads(responseComparisonScheme)
        self.responseComparisonType = responseComparisonType
        self.responseNames = responseNames
        self.responseDataType = responseDataType
        self.compareByValueNodes = compareByValueNodes
        self.deferIgnoredNodeProcessing = deferIgnoredNodeProcessing
        return self


    def Compare_Requests(self, compareInfo):
        import time
        # time.sleep(10)
        try:


            if compareInfo.requestId_1 in data_manager.responseStore and compareInfo.requestId_2 in data_manager.responseStore:

                jsoncompare.jsonNames = compareInfo.responseNames
                jsoncompare.diffNodeNames = ['actual_1', 'actual_2']
                compareInfo.response_1 = compareInfo.processedResponse_1 = json.dumps(data_manager.responseStore[compareInfo.requestId_1], indent=4)
                compareInfo.response_2 = compareInfo.processedResponse_2 = json.dumps(data_manager.responseStore[compareInfo.requestId_2], indent=4)

                compareInfo.processedResponse_1 = self.escapeRegex(compareInfo.processedResponse_1)
                compareInfo.processedResponse_2 = self.escapeRegex(compareInfo.processedResponse_2)

                if len(compareInfo.compareByValueNodes):
                    compareInfo.processedResponse_1 = self.updateCompareByValueNodes(compareInfo.compareByValueNodes, compareInfo.processedResponse_1, compareInfo.response_1)
                    compareInfo.processedResponse_2 = self.updateCompareByValueNodes(compareInfo.compareByValueNodes, compareInfo.processedResponse_2, compareInfo.response_2)

                compareInfo = libcommons.run_keyword('Compare Response Bodies', compareInfo, library=comparisonLib)
            elif compareInfo.requestId_1 in data_manager.responseStore or compareInfo.requestId_2 in data_manager.responseStore:
                actual_1 = data_manager.responseStore[compareInfo.requestId_1] if compareInfo.requestId_1 in data_manager.responseStore else '__EMPTY__'
                actual_2 = data_manager.responseStore[compareInfo.requestId_2] if compareInfo.requestId_2 in data_manager.responseStore else '__EMPTY__'
                if actual_1.__class__.__name__.lower() in ('dict', 'dotdict', 'list'):
                    actual_1 = json.loads(self.escapeRegex(json.dumps(actual_1)))
                if actual_2.__class__.__name__.lower() in ('dict', 'dotdict', 'list'):
                    actual_2 = json.loads(self.escapeRegex(json.dumps(actual_2)))
                compareInfo.responseDiff = json.dumps([{'type' : 'Response Body Missing', 'path' : '__responseBody__', 'actual_1' : actual_1, 'actual_2' : actual_2}], indent=4)
            else:
                print('No response body found for both the requests, skipping response body comparison.')

            if compareInfo.requestId_1 in data_manager.statusStore and compareInfo.requestId_2 in data_manager.statusStore:

                compareInfo.statusCode_1 = data_manager.statusStore[compareInfo.requestId_1]
                compareInfo.statusCode_2 = data_manager.statusStore[compareInfo.requestId_2]
                compareInfo = libcommons.run_keyword('Compare Status Codes', compareInfo, library=comparisonLib)
            else:
                print('No status code found for either both or one of the requests, skipping status code comparison.')

            compareInfo.actualDivergence = json.dumps(json.loads(compareInfo.responseDiff) + json.loads(compareInfo.statusDiff), indent=4)

            compareInfo = libcommons.run_keyword('Compare Divergences', compareInfo, library=comparisonLib)

        except Exception as e:

            if str(e) == ContractComparisonFailureError:
                print(str(e))
            else:
                print(traceback.format_exc())
            raise e
        # finally:
        #     if compareInfo.requestId_1 in data_manager.responseStore:
        #         data_manager.responseStore.pop(compareInfo.requestId_1)
        #     if compareInfo.requestId_2 in data_manager.responseStore:
        #         data_manager.responseStore.pop(compareInfo.requestId_2)
            # libcommons.run_keyword('log', "${compareInfo.formattedDiff}")

    def Compare_Response_Bodies(self, compareInfo):
        if compareInfo.responseDataType.upper() == 'TEXT' and compareInfo.processedResponse_1 != compareInfo.processedResponse_2:
            compareInfo.responseDiff = json.dumps([{'type' : 'Response Body Mismatch', 'path' : '__responseBody__', 'actual_1' : str(compareInfo.processedResponse_1), 'actual_2' : str(compareInfo.processedResponse_2)}], indent=4)
        else:

            compareInfo.responseDiff = json.dumps(jsoncompare.compare(compareInfo.processedResponse_1, compareInfo.processedResponse_2, ignoreNodes=compareInfo.ignoreNodes, verificationScheme=compareInfo.responseComparisonScheme, comparisionType=compareInfo.responseComparisonType, deferIgnoredNodeProcessing=compareInfo.deferIgnoredNodeProcessing), indent=4)
        libcommons.run_keyword('log', "${compareInfo.response_1}")
        libcommons.run_keyword('log', "${compareInfo.response_2}")
        libcommons.run_keyword('log', "${compareInfo.responseDiff}")
        return compareInfo

    def escapeRegex(self, data):
        escapeRegexList = {'___UUID___': '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                           '___DT-FORMAT-1___': '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.]?[0-9]{0,3}Z',
                           'XXXXXXXX.XXXXXXXX': '[0-9A-Z]{8}\.[0-9A-Z]{8}'}

        for name, regex in escapeRegexList.items():
            matches = re.findall(regex, data)
            for match in matches:
                if match in data:
                    data = data.replace(match, name)

        return data

    def Compare_Status_Codes(self, compareInfo):
        if compareInfo.statusCode_1 != compareInfo.statusCode_2:
            compareInfo.statusDiff = json.dumps([{'type' : 'Status Code Mismatch', 'path' : '__statusCode__', 'actual_1' : compareInfo.statusCode_1, 'actual_2' : compareInfo.statusCode_2}], indent=4)
            libcommons.run_keyword('log', "${compareInfo.statusDiff}")
        else:
            print('Status Codes Match!')
        return compareInfo
    
    def Compare_Divergences(self, compareInfo):
        
        if len(compareInfo.expectedDivergence):
            libcommons.run_keyword('log', "${compareInfo.expectedDivergence}")

        libcommons.run_keyword('log', "${compareInfo.actualDivergence}")
        compareInfo.divergenceDiff = compareDiff(compareInfo.expectedDivergence, compareInfo.actualDivergence, verificationScheme=[{"path": "$", "type": "NotSorted", "key": "path, type"}])
        compareInfo.divergenceDiff = [x for x in compareInfo.divergenceDiff if 'divergenceType' not in x or ('divergenceType' in x and x['divergenceType'].lower() != 'optional')]
        libcommons.run_keyword('Check If Contract Comparison Is Successful', compareInfo, library=comparisonLib)
        return compareInfo

    def Check_If_Contract_Comparison_Is_Successful(self, compareInfo):
            if len(compareInfo.divergenceDiff):
                print('Total ', len(compareInfo.divergenceDiff), ' difference(s) found between expected and actual divergence, below are the details:')
                print(json.dumps(compareInfo.divergenceDiff, indent=4))
                raise Exception(ContractComparisonFailureError)
            else:
                print('Contract comparison is successful, no unexpected divergence found.')

    def updateCompareByValueNodes(self, compareByValueNodes, processed_json, original_json):
        try:
            processed_json_obj = json.loads(processed_json)
            original_json_obj = json.loads(original_json)
            for path in compareByValueNodes:
                jsonPathExpression = parser.ExtentedJsonPathParser().parse(path.replace(' && ', ' & '))
                matches = jsonPathExpression.find(processed_json_obj)
                if len(matches):
                    for match in matches[::-1]:
                        jsonPath = '$.' + str(match.full_path)
                        localJsonPathExpression = parser.ExtentedJsonPathParser().parse(jsonPath.replace(' && ', ' & '))
                        matchesFromOriginal = localJsonPathExpression.find(original_json_obj)
                        if len(matchesFromOriginal):
                            originalValue = matchesFromOriginal[0].value
                            processed_json_obj = json_merge.addOrUpdateValueAtGivenJsonPath(processed_json_obj, jsonPath.replace(' && ', ' & '),
                                                                               originalValue)
            return json.dumps(processed_json_obj)
        except Exception as e:
            print(traceback.format_exc())

        return processed_json

if __name__ == '__main__':
    jsonStr = open(r'C:\API Automation\Robot\mkt-pune-comparison\src\test\testsuites\Plan\BU_ExpectedDiff.json').read()
    reg = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    matches = re.findall(reg, jsonStr)
    for match in matches:
        if match in jsonStr:
            jsonStr = jsonStr.replace(match, '___UUID___')



    print(json.dumps(json.loads(jsonStr), indent=4))


