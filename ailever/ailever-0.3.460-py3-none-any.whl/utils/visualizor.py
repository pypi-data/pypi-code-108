import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

def korean(font_name='NanumBarunGothic'):
    font_names = list()
    for font in fm.fontManager.ttflist:
        font_names.append(font.name)

    if font_name in font_names:
        plt.rcParams["font.family"] = font_name
