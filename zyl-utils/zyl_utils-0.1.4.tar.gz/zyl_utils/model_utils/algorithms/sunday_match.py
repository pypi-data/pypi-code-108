def sunday_match(target, pattern) -> list:
    """
    find all pattern's starts,在一个序列中找到要的所有的子序列
    Args:
        target: str or list ，原始序列
        pattern: str or list，要匹配的序列

    Returns:
        starts: 匹配到子序列在原始序列中的起始位置
    """
    len_target = len(target)
    len_pattern = len(pattern)

    if len_pattern > len_target:
        return list()

    index = 0
    starts = []
    while index < len_target:
        if pattern == target[index:index + len_pattern]:
            starts.append(index)
            index += 1
        else:
            if (index + len(pattern)) >= len_target:
                return starts
            else:
                if target[index + len(pattern)] not in pattern:
                    index += (len_pattern + 1)
                else:
                    index += 1
    return starts


if __name__ == '__main__':
    t = "this is an apple , apple app app is app not app"
    # t = t.split()
    p = "app"
    # p = p.split()
    print(t)
    print(p)
    print(sunday_match(target=t, pattern=p))

    import pandas as pd
    dict = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
                       'train')

    print('1')
