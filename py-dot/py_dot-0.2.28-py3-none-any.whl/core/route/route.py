from typing import List


def divide_path(path: str, separator='/', divider='|') -> List[str]:
    """ Dividing Single Path to Multiple Path

    ['a/b/c', 'a/b/d']
    >>> divide_path('a/b/c|d')

    ['a/1/b','a/2/b']
    >>> divide_path('a/1|2/b')
    """
    segments = path.split(separator)
    result = []
    for segment in segments:
        divided_segments = segment.split(divider)

        if len(result) > 0:
            divided_paths = []
            for divided_segment in divided_segments:
                for divided_path in result:
                    divided_paths.append(
                        divided_path + separator + divided_segment
                    )
            result = divided_paths
        else:
            for divided_segment in divided_segments:
                result.append(divided_segment)

    return result
