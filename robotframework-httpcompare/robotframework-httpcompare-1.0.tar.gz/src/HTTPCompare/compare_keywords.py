from .libcommons import libcommons
from .compare_requests import compare_requests
class compare_keywords:

    def Compare_HTTP_Requests(self, requestId_1, requestId_2, expectedDivergence=[], ignoreNodes=[],
                              responseComparisonScheme=[], responseComparisonType='full',
                              responseNames=['Response-1', 'Response-2'], responseDataType='json', compareByValueNodes=[], deferIgnoredNodeProcessing=False):
        '''
        This keyword lets you compare two HTTP Requests, given that both the requests are made using 'Make HTTP Request' keyword

        This enables comparison of JSON response bodies and status codes as of now.

        It will log the difference between response bodies and status codes in robot report and pass/fail the testcase accordingly.

        Difference between both the responses is termed as Divergence.

        Actual Divergence (difference between the two responses)
        Expected Divergence (difference which is acknowledgeably expected by user, should be supplied by the user while invoking this keyword)

        This keyword will compare the actual divergence and expected divergence and will pass if they match, otherwise will highlight the differences and fail.

        Parameters:
        requestId_1 : request id of first request

        requestId_2 : request id of second request

        expectedDivergence : difference between the two responses, which is acknowledgeably expected by user, should be provided in the format of actual divergence which is logged in robot report. Only difference is that it has expected_<x> node rather than actual_<x> nodes.

        ignoreNodes : a list of json-paths of the nodes which we want to be ignored while response body comparison

        responseComparisonScheme : this parameter is useful to specify how we want our response bodies to get compared. In case of not sorted comparison, where we want to skip the sequence and verify the arrays with items in random order
                                example : [{"path":"$.items","type":"NotSorted","key":"name"},{"path":"$.items[*].links","type":"NotSorted","key":"rel"}]

        responseComparisonType :  type of baseline verification required, default is FULL, other supported values are PARTIAL.

        responseNames : using this parameter we can respectively attach nomenclature to the requests provided for comparison, ex responseNames=['elasticsearch response', 'lambda response']

        '''

        compareInfo = compare_requests().init_comparison(requestId_1, requestId_2,
                                                         expectedDivergence=expectedDivergence, ignoreNodes=ignoreNodes,
                                                         responseComparisonScheme=responseComparisonScheme,
                                                         responseComparisonType=responseComparisonType,
                                                         responseNames=responseNames, responseDataType=responseDataType, compareByValueNodes=compareByValueNodes, deferIgnoredNodeProcessing=deferIgnoredNodeProcessing)
        libcommons.robotBuiltIn.set_suite_variable("${compareInfo}", compareInfo)
        libcommons.run_keyword('Compare_Requests', "${compareInfo}")