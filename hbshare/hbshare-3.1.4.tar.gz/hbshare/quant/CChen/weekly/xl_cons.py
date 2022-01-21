import numpy as np

# xlsx params
row_num = 3
module_1_cols = 11
module_2_cols = 12


# xlwings format
cell_format = {
    'type': '3_color_scale',
    'min_color': '#2EDFA3',
    'mid_color': '#F3F8F1',
    'max_color': '#f47983'
}

cell_format_r = {
    'type': '3_color_scale',
    'min_color': '#f47983',
    'mid_color': '#F3F8F1',
    'max_color': '#2EDFA3'
}

cell_format2 = {
    'type': 'data_bar',
    'bar_color': 'red',
    'bar_only': False,
    'bar_solid': False,
    'bar_negative_color': 'green',
    'bar_direction': 'left',
    'bar_axis_position': 'middle'
}


# 10进制转26进制
sequence = list(map(lambda x: chr(x), range(ord('A'), ord('Z') + 1)))


def ten2twentysix(num):
    lll = []
    if num > 25:
        while 1:
            d = int(num / 26)
            remainder = num % 26
            if d <= 25:
                lll.insert(0, sequence[remainder])
                lll.insert(0, sequence[d - 1])
                break
            else:
                lll.insert(0, sequence[remainder])
                num = d - 1
    else:
        lll.append(sequence[num])

    return ''.join(lll)


# 基金表现统计
def pool_board(data_df, fund_list):
    ret_this_week = data_df[
        data_df['index'] == '本周'
        ].drop(
        columns={'index'}
    ).reset_index(drop=True).T.rename(
        columns={0: 'return'}
    )
    ret_this_week = ret_this_week[
        np.isnan(ret_this_week['return'].tolist()) == False
        ].sort_values(by='return', ascending=False).reset_index()

    result = {
        'all': data_df.drop(columns={'index'}).shape[1],
        'onTime': len(ret_this_week),
        'win': len(ret_this_week[ret_this_week['return'] > 0]),
        'bestName': ret_this_week['index'][0],
        'bestRet': ret_this_week['return'][0],
        'bestType': fund_list[fund_list['name'] == ret_this_week['index'][0]]['type'].tolist()[0],
        'bestName1': ret_this_week['index'][1],
        'bestRet1': ret_this_week['return'][1],
        'bestType1': fund_list[fund_list['name'] == ret_this_week['index'][1]]['type'].tolist()[0],
        'bestName2': ret_this_week['index'][2],
        'bestRet2': ret_this_week['return'][2],
        'bestType2': fund_list[fund_list['name'] == ret_this_week['index'][2]]['type'].tolist()[0],
        'worstName': ret_this_week['index'][len(ret_this_week) - 1],
        'worstRet': ret_this_week['return'][len(ret_this_week) - 1],
        'worstType': fund_list[
            fund_list['name'] == ret_this_week['index'][len(ret_this_week) - 1]
            ]['type'].tolist()[0],
        'worstName1': ret_this_week['index'][len(ret_this_week) - 2],
        'worstRet1': ret_this_week['return'][len(ret_this_week) - 2],
        'worstType1': fund_list[
            fund_list['name'] == ret_this_week['index'][len(ret_this_week) - 2]
            ]['type'].tolist()[0],
        'worstName2': ret_this_week['index'][len(ret_this_week) - 3],
        'worstRet2': ret_this_week['return'][len(ret_this_week) - 3],
        'worstType2': fund_list[
            fund_list['name'] == ret_this_week['index'][len(ret_this_week) - 3]
            ]['type'].tolist()[0],
        'average': ret_this_week['return'].mean()
    }
    return result


if __name__ == '__main__':
    print(ten2twentysix(0))
