# from urllib.request import urlopen
import io
# from colorthief import ColorThief

def get_data_type_for_given_feature(data_types, feature):
    for k in list(data_types.keys()):
        if feature in data_types[k]:
            if k == 'remove_cols' or k == 'binary':
                k = 'categorical'
            return k 
    return 'None'

def check_list_in_list(parent_list, sublist):
    for i in sublist:
        if i not in parent_list:
            return False
    return True

def add_labels_to_fig(fig, x, y, title):
    fig.update_layout(
        title=title,
        xaxis_title=x,
        yaxis_title=y
        )
        

# def get_color(logo_path_url, num_colors=2):  
#     if logo_path_url != '':
#         fd = urlopen(logo_path_url)
#         f = io.BytesIO(fd.read())
#         color_thief = ColorThief(f)
#         return color_thief.get_palette(color_count=num_colors)
#     else:
#         return ''

    