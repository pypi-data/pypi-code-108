import json
import re, os, traceback
from jsonpath_ng.ext import parser
from .libcommons import libcommons
from .json_merge import json_merge
from .data_manager import data_manager

TypeMismatch = 'Type Mismatch'
NodeMissing = 'Node Missing'
CountMismatch = 'Item Count Mismatch'#need to remove this for diff
ValueMismatch = 'Value Mismatch'
jsonNames = ['Benchmark', 'Response']
diffNodeNames = ['expected', 'actual']


# we always assume benchmark is passed as first and response as second
class compare_diff(object):
    def __init__(self, first, second, with_values=False, swapped=False, partial=False):
        try:
            self.difference = []
            self.seen = []
            self.swapped = swapped
            self.partial = partial
            global NodeMissing
            NodeMissing = f'Node Missing From {jsonNames[int(not self.swapped)]}'
            self.check(first, second, with_values=with_values)

        except Exception as e:
            print(traceback.format_exc())
            raise e

    def check(self, first, second, path='', with_values=False):
        try:
            first_prefix = diffNodeNames[int(self.swapped)]
            second_prefix = diffNodeNames[int(not self.swapped)]
            first_nodes = ['type', 'path', first_prefix + '_1', first_prefix + '_2']
            second_nodes = ['type', 'path', second_prefix + '_1', second_prefix + '_2']
            if with_values and second != None:
                if not isinstance(first, type(second)):
                    self.save_diff(path, TypeMismatch, type(first).__name__, type(second).__name__)

            if first.__class__.__name__.lower() in ('dict', 'dotdict'):
                if path and len(first) == 0 and self.partial and isinstance(second, dict) and len(second) > 0:
                    self.save_diff(path, CountMismatch, str(len(first)), str(len(second)))

                for key in first:
                    # the first part of path must not have trailing dot.
                    if len(path) == 0:
                        new_path = key
                    else:
                        new_path = "%s.%s" % (path, key)

                    if isinstance(second, dict):
                        if key in second:
                            sec = second[key]
                        else:
                            #  there are key in the first, that is not presented in the second
                            self.save_diff(new_path, NodeMissing)

                            # prevent further values checking.
                            sec = None

                        # recursive call
                        if sec != None:
                            self.check(first[key], sec, path=new_path, with_values=with_values)
                    else:
                        # second is not dict. every key from first goes to the difference
                        self.save_diff(new_path, NodeMissing)
                        self.check(first[key], second, path=new_path, with_values=with_values)

            # if object is list, loop over it and check.
            elif isinstance(first, list):
                if path and len(first) == 0 and self.partial and isinstance(second, list) and len(second) > 0:
                    self.save_diff(path, CountMismatch, str(len(first)), str(len(second)))

                for (index, item) in enumerate(first):
                    new_path = "%s[%s]" % (path, index)
                    # try to get the same index from second
                    sec = None
                    if second != None:
                        try:
                            message = []
                            merged_obj = {}
                            sec = second[index]
                            if 'type' not in item or 'path' not in item:
                                self.difference.append(getExtendedDiffNode(item, {'message' : 'type or path missing from this ' + first_prefix + ' difference'}))
                                continue
                            if 'type' not in sec or 'path' not in sec:
                                self.difference.append(getExtendedDiffNode(sec, {'message' : 'type or path missing from this ' + second_prefix + ' difference'}))
                                continue
                            if item['type'] != sec['type'] or item['path'] != sec['path']:
                                self.difference.append(getExtendedDiffNode({first_prefix : item, second_prefix : sec}, {'message' : 'type or path do not match between expected and actual difference' }))
                                continue

                            merged_obj = {'type' : item['type'], 'path' : item['path']}
                            if 'divergenceType' in first:
                                merged_obj['divergenceType'] = first['divergenceType']

                            if first_prefix + '_1' in item:
                                merged_obj[first_prefix + '_1'] = item[first_prefix + '_1']
                                if second_prefix + '_1' in sec:
                                    merged_obj[second_prefix + '_1'] = sec[second_prefix + '_1']
                                    x = item[first_prefix + '_1']
                                    y = sec[second_prefix + '_1']
                                    if type(x) != type(y):
                                        message.append('type mismatch between expected_1 and actual_1')
                                    elif not self.compareValues(x, y):
                                        message.append('value mismatch between expected_1 and actual_1')
                                else:
                                    message.append(second_prefix + '_1 node missing from ' + second_prefix + ' difference')
                            elif second_prefix + '_1' in item:
                                message.append(first_prefix + '_1 node missing from ' + first_prefix + ' difference')


                            if first_prefix + '_2' in item:
                                merged_obj[first_prefix + '_2'] = item[first_prefix + '_2']
                                if second_prefix + '_2' in sec:
                                    merged_obj[second_prefix + '_2'] = sec[second_prefix + '_2']
                                    x = item[first_prefix + '_2']
                                    y = sec[second_prefix + '_2']
                                    if type(x) != type(y):
                                        message.append('type mismatch between expected_2 and actual_2')
                                    elif not self.compareValues(x, y):
                                        message.append('value mismatch between expected_2 and actual_2')
                                else:
                                    message.append(second_prefix + '_2 node missing from ' + second_prefix + ' difference')
                            elif second_prefix + '_2' in item:
                                message.append(first_prefix + '_2 node missing from ' + first_prefix + ' difference')

                            if len(message):
                                merged_obj['message'] = message
                                self.difference.append(merged_obj)




                        except (IndexError, KeyError):
                            # goes to difference
                            self.save_diff(new_path, NodeMissing)


                    # recursive call
                    # self.check(first[index], sec, path=new_path, with_values=with_values)


            # not list, not dict. check for equality (only if with_values is True) and return.
            else:
                if with_values and second != None:
                    if not self.compareValues(first, second):
                        self.save_diff(path, ValueMismatch, first, second)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return

    def save_diff(self, path, type_, first=None, second=None):
        try:
            if path not in self.difference:
                self.seen.append(path)
                diff = {}
                diff['type'] = type_
                diff['path'] = path
                if first != None and second != None:
                    diff[diffNodeNames[int(self.swapped)]] = first
                    diff[diffNodeNames[int(not self.swapped)]] = second
                self.difference.append(diff)
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def compareValues(self, first, second):
        if first.__class__.__name__.lower() in ('dict', 'dotdict', 'list') and second.__class__.__name__.lower() in ('dict', 'dotdict', 'list'):
            import jsoncompare
            diffs = jsoncompare.compare(first, second)
            return len(diffs) == 0
        result = first == second
        try:
            data = [first, second]
            benchIndex = int(self.swapped)
            respIndex = int(not self.swapped)
            try:
                if not result and type(first) is str:
                    secondRegex = re.compile('^' + data[benchIndex] + '$')
                    matches = secondRegex.findall(data[respIndex])
                    if len(matches) == 1:
                        result = True
            except:
                a = 1
        except Exception as e:
            print(traceback.format_exc())
            raise e
        return result

    def escapeSpecialCharsForRegex(self, data):
        result = data
        escapeChars = '\/^$|?*(){['
        if result:
            for char in escapeChars:
                result = result.replace(char, '\\' + char)
        return result
def getContentFromFile(filePath):
    try:
        if type(filePath) is str and libcommons.path_exists(filePath):
            filePath = open(filePath, 'r').read()
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return filePath


def getContent(location):
    try:
        if location.__class__.__name__.lower() in ('dict', 'dotdict', 'list'):
            return location

        content = getContentFromFile(location)
        if content is None:
            raise Exception("Could not load content for " + location)
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return json.loads(content)

def getExtendedDiffNode(node, extensionObj):
    res = node.copy()
    for key, val in extensionObj.items():
        res[key] = val

    return res


def processVerificationSchemes(json1, json2, verificationScheme, swapped=False):
    try:
        if len(verificationScheme):
            NotSortedInstances = [x for x in verificationScheme if 'type' in x and x['type'].upper() == 'NOTSORTED']
            diffs = []
            for scheme in NotSortedInstances:
                path = scheme['path']
                keys = scheme['key'].split(',')
                keys = [key.strip() for key in keys]

                jsonPathExpression = parser.ExtentedJsonPathParser().parse(path.replace(' && ', ' & '))
                matches = jsonPathExpression.find(json1)
                for index, match in enumerate(matches):
                    if type(match.value) is list and len(match.value):
                        localJsonPathExpression = parser.ExtentedJsonPathParser().parse(
                            '$.' + str(match.full_path).replace(' && ', ' & '))
                        benchmarkList = match.value
                        responseList = localJsonPathExpression.find(json2)

                        if len(responseList):
                            responseList = responseList[0].value
                            responseListUpdated = False
                            MissingNodeList = []
                            for benchIndex, benchItem in enumerate(benchmarkList[::-1]):
                                respIndex = [index for index, item in enumerate(responseList) if allKeysSameInBothItems(keys, item, benchItem)]
                                if len(respIndex):
                                    respIndex = respIndex[0]
                                    responseList.insert(0, responseList.pop(respIndex))
                                    responseListUpdated = True
                                else:
                                    MissingNodeList.append(len(benchmarkList) - benchIndex - 1)
                                    # print('item with ' + ' and '.join([key + ' = ' + benchItem[key] for key in keys]) + ' not found in response body for json path ', path)
                                    diffs.append(getExtendedDiffNode(benchItem, {'message': 'item with ' + ' and '.join([key + ' = \'' + benchItem[key] + '\'' for key in keys]) + ' not found in ' + diffNodeNames[int(not swapped)] + ' differences'}))


                            if len(MissingNodeList):
                                for idx, index in enumerate(MissingNodeList[::-1]):
                                    json1 = json_merge.addOrUpdateValueAtGivenJsonPath(json1, path.replace(' && ', ' & ') + '[' + str(index - idx) + ']', '@@DELETE@@')

                            if responseListUpdated:
                                localJsonPathExpression.update(json2, responseList)
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return json1, json2, diffs

def allKeysSameInBothItems(keys, item1, item2):
    same = True
    for key in keys:
        same = same and key in item1 and item1[key] == item2[key]
    return same


def compareDiff(location1, location2, comparisionType='full', verificationScheme=[]):
    diffs = []
    try:
        json1 = getContent(location1)  # benchmark
        json2 = getContent(location2)  # response



        diff1, diff2 = [], []

        json3, json4, diff1 = processVerificationSchemes(json1, json2, verificationScheme, swapped=False)

        diff1 = diff1 + compare_diff(json3, json4, True, False, comparisionType.lower() == 'partial').difference
        # print('diff1')
        # print(json.dumps(diff1, indent=4))

        json5, json6, diff2 = processVerificationSchemes(json2, json1, verificationScheme, swapped=True)

        # diff2 = diff2 + compare_diff(json5, json6, True, False, comparisionType.lower() == 'partial').difference
        # print('diff2')
        # print(json.dumps(diff2, indent=4))

        # if not comparisionType.lower() == 'partial':
        #     diff2 = compare_diff(json2, json1, False, True).difference
        #     print('diff2')
        #     print(json.dumps(diff2, indent=4))

        diffs = diff1 + diff2
    except Exception as e:
        print(traceback.format_exc())
        raise e
    return diffs

