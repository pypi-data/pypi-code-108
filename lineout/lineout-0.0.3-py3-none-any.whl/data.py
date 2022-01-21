__all__ = ['get_result_list']


def get_result_list(data):
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        results = data.get('results', None)
        if isinstance(results, list):
            return results

    raise ValueError("Data is not list api result: {}".format(data))


