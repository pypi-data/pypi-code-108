from lxml import objectify

class MicrovixUtils:

    def response_is_success(xml) -> bool:
        if not xml:
            return False

        root = objectify.fromstring(xml)
        return str(root.ResponseResult.ResponseSuccess) == 'True'

    def xml_to_dict_array(xml) -> list:
        result = list()

        root = objectify.fromstring(xml)

        headers = [ str(item) for item in root.ResponseData.C.D ]

        try:
            items = root.ResponseData.R
        except AttributeError as ex:
            return None

        for item in items:
            tmp = dict()

            for idx, header in enumerate(headers):
                tmp[header] = str(item.D[next(idx)])

            result.append(tmp)

        return result