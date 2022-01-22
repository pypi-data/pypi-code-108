# -*- coding: utf-8 -*-
# file: traj_plot.py
# time: 2021/12/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os

import matplotlib
import matplotlib.pyplot as plt
import tikzplotlib
from findfile import find_file, find_cwd_files, find_files

tex_template = r"""
      \documentclass{article}
      \usepackage{pgfplots}
      \usepackage{tikz}
      \usepackage{caption}
      \usetikzlibrary{intersections}
      \usepackage{helvet}
      \usepackage[eulergreek]{sansmath}
      \usepackage{amsfonts,amssymb,amsmath,amsthm,amsopn}% math related

      \begin{document}
          \pagestyle{empty}
              \pgfplotsset{ compat=1.12,every axis/.append style={
                  font = \normalsize,
                  grid = major,
                  thick,
                  xtick={0,1,2,3,4,5,6,7,8,9,10},
                  xticklabels={0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1},
                  ylabel = {Metric (Acc \& F1)},
                  xlabel = {$dataset$},
                  x tick label style={rotate=1,anchor=north},
                  xticklabel shift=2pt,
                  line width = 1pt,
                  tick style = {line width = 0.8pt}}}
          \pgfplotsset{every plot/.append style={thin}}


      \begin{figure}
      \centering

      $src_code$

      \end{figure}

      \end{document}

      """


def eta_plot(dataset, model, eta, data):
    acc = []
    f1 = []
    traj_acc = []
    traj_f1 = []
    for key in data:
        acc.append(sorted([data[key][i] for i in range(len(data[key])) if i % 2 == 0])[3:])
        f1.append(sorted([data[key][i] for i in range(len(data[key])) if i % 2 == 1])[3:])
        traj_acc.append(sum(sorted([data[key][i] for i in range(len(data[key])) if i % 2 == 0])[3:]) / 7)
        traj_f1.append(sum(sorted([data[key][i] for i in range(len(data[key])) if i % 2 == 1])[3:]) / 7)

    violin_parts = plt.violinplot(acc, positions=range(len(eta)), showmeans=True, showmedians=True, showextrema=True)

    for pc in violin_parts['bodies']:
        pc.set_edgecolor('black')
        pc.set_facecolor('black')
        pc.set_linewidth(2)

    boxs_parts = plt.boxplot(f1, positions=range(len(eta)), widths=0.3)
    for item in ['boxes', 'whiskers', 'fliers', 'medians', 'caps']:
        plt.setp(boxs_parts[item], color='black')
    plt.setp(boxs_parts["fliers"], markeredgecolor='black')
    # plt.show()
    # tikzplotlib.save('{}-{}-violin.tex'.format(waf, t))
    tikz_code = tikzplotlib.get_tikz_code()
    tex_src = tex_template.replace('$src_code$', tikz_code).replace('$model$', model).replace('$dataset$', dataset)
    # tex_src = tex_src.replace(r'\definecolor{color0}{rgb}{0.12156862745098,0.466666666666667,0.705882352941177}',
    #                           r'\definecolor{color0}{rgb}{0.28, 0.24, 0.2}')
    tex_name = '{}-{}-violin.tex'.format(model, dataset)
    open(tex_name, mode='w', encoding='utf8').write(tex_src)

    plt.close()


def traj_plot(dataset, eta, lena_data, lena_s_data):
    lena_traj_acc = []
    lena_traj_f1 = []
    lenas_traj_acc = []
    lenas_traj_f1 = []

    for key in lena_data:
        lena_traj_acc.append(sum(sorted([lena_data[key][i] for i in range(len(lena_data[key])) if i % 2 == 0])[3:]) / 7)
        lena_traj_f1.append(sum(sorted([lena_data[key][i] for i in range(len(lena_data[key])) if i % 2 == 1])[3:]) / 7)

    for key in lena_s_data:
        lenas_traj_acc.append(sum(sorted([lena_s_data[key][i] for i in range(len(lena_s_data[key])) if i % 2 == 0])[3:]) / 7)
        lenas_traj_f1.append(sum(sorted([lena_s_data[key][i] for i in range(len(lena_s_data[key])) if i % 2 == 1])[3:]) / 7)

    l1 = plt.plot(eta, lena_traj_acc, 'm*-', label='Lena (Acc)', scalex=0.1)
    l2 = plt.plot(eta, lena_traj_f1, 'm--', label='Lena (F1)')
    l3 = plt.plot(eta, lenas_traj_acc, 'c^-', label='Lena-S (Acc)')
    l4 = plt.plot(eta, lenas_traj_f1, 'c--', label='Lena-S (F1)')

    # plt.plot(
    #     epoch, singletask_bypass_rnn, 'ro-',
    #     epoch, singletask_bypass_gru, 'g+-',
    #     epoch, singletask_bypass_lstm, 'b^-',
    #     epoch, singletask_bypass_lstm, 'y.-',
    #     epoch, singletask_bypass_lstm, 'mx-',
    #     epoch, singletask_bypass_lstm, 'c*-',
    # )
    # plt.title('Comparison of bypass cases of {} in {}'.format(label_map[task], waf))
    plt.xticks(fontsize=15)
    plt.xlabel(dataset, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Metric (Acc & F1)', fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.grid()
    plt.minorticks_on()
    plt.savefig('{}-eta-traj.pdf'.format(dataset))
    # plt.show()
    tikz_code = tikzplotlib.get_tikz_code()
    # tex_src = tex_template.replace('$src_code$', tikz_code).replace('$dataset$', dataset)

    tex_name = '{}-eta-traj.tex'.format(dataset)
    open(tex_name, mode='w', encoding='utf8').write(tex_template.replace('src_code', tikz_code))

    plt.close()


if __name__ == '__main__':
    eta_x = list(x / 10 for x in range(0, 11, 1))

    lena_s_15 = {
        0: [87.22, 72.78, 87.78, 75.61, 85, 71.28, 88.15, 75.12, 81.11, 63.48, 87.04, 77.84, 87.33, 76.2, 87.41, 77.11, 87.04, 72.8, 87.96, 75.17],
        0.1: [87.59, 74.37, 87.59, 75.11, 85.56, 69.12, 88.15, 74.62, 78.33, 52.39, 87.59, 74.94, 87.59, 75.11, 89.07, 77.18, 86.85, 74.25, 85.56, 75.2],
        0.2: [86.48, 73.05, 86.11, 75.94, 86.11, 70.65, 87.96, 74.23, 86.3, 73.6, 87.22, 71.17, 86.85, 73.26, 88.33, 79.17, 88.15, 75.15, 86.85, 72.2],
        0.3: [87.22, 72.45, 88.33, 75.01, 85.37, 71.59, 88.33, 73.92, 86.67, 73.43, 87.04, 73.49, 87.96, 75.74, 87.59, 75.89, 88.52, 74.67, 87.22, 73.39],
        0.4: [87.96, 75.98, 88.52, 75.23, 85.93, 68.1, 89.44, 77.06, 84.07, 65.95, 87.41, 76.68, 88.33, 75.31, 87.96, 76.1, 88.52, 75.77, 86.67, 71.35],
        0.5: [87.04, 73.49, 87.22, 75.33, 85.93, 74.02, 87.78, 73.34, 86.67, 74.77, 88.7, 74.1, 87.41, 75.2, 89.26, 76.93, 89.07, 75.17, 87.04, 70.08],
        0.6: [88.15, 74.76, 89.07, 78.83, 86.85, 72.86, 88.52, 76.17, 79.63, 60.35, 87.96, 74.91, 87.59, 72.11, 88.52, 76.1, 87.96, 76.09, 87.96, 76.44],
        0.7: [87.22, 74.04, 87.59, 74.54, 83.89, 68.29, 88.52, 76.04, 81.3, 55.12, 87.41, 75.2, 87.96, 76.12, 87.78, 77.28, 89.07, 78.16, 87.78, 75.42],
        0.8: [87.04, 73.45, 88.89, 77.77, 85.74, 70.2, 88.52, 74.05, 77.41, 51.71, 88.7, 75.97, 87.41, 75.11, 88.33, 77.23, 87.59, 73.88, 87.59, 74.95],
        0.9: [87.41, 74.75, 88.15, 75.04, 86.11, 70.19, 87.78, 75.66, 83.52, 64.45, 87.04, 74.2, 86.85, 72.95, 87.78, 76.9, 86.11, 76.92, 85.93, 71.91],
        1: [87.96, 73.95, 87.78, 75.72, 87.41, 73.31, 87.22, 73.42, 76.48, 55.96, 87.04, 74.37, 86.48, 73.46, 87.04, 77.62, 86.11, 75.15, 85.96, 75.65],
    }

    lena_s_16 = {
        0: [87.8, 64.87, 93.33, 84.63, 93.33, 80.71, 93.5, 77.69, 93.5, 81.46, 93.5, 79.57, 93.33, 80.22, 93.82, 81.49, 94.15, 77.92, 93.33, 81.03],
        0.1: [93.82, 81.71, 93.82, 81.83, 93.66, 79.26, 92.85, 77.76, 93.82, 80.26, 93.33, 79.06, 94.31, 81.82, 93.66, 81.31, 92.52, 78.91, 93.82, 82.21],
        0.2: [93.01, 77.62, 89.92, 74.78, 92.36, 75.23, 92.03, 78.7, 93.01, 78.55, 93.17, 78.95, 94.15, 80.91, 94.31, 82.67, 93.82, 81.34, 93.33, 77.35],
        0.3: [92.85, 78.95, 94.47, 82.75, 92.68, 76.84, 92.03, 75.82, 93.5, 78.84, 94.31, 81.24, 94.63, 83.66, 94.15, 84.23, 94.31, 80.21, 93.5, 79.78],
        0.4: [93.5, 80.39, 92.85, 78.29, 92.36, 78.45, 93.5, 80.95, 93.5, 77.29, 93.82, 82.02, 92.68, 79.81, 94.15, 82.84, 93.82, 78.85, 94.31, 83.42],
        0.5: [92.36, 77.36, 94.63, 82.95, 93.33, 81.23, 94.31, 81.42, 93.82, 81.33, 93.82, 80.47, 93.33, 79.68, 93.33, 79.69, 94.15, 80.68, 93.98, 79.69],
        0.6: [91.22, 74.36, 93.66, 81.12, 92.85, 78.34, 93.17, 81.34, 94.15, 79.79, 93.5, 79.7, 92.85, 77.95, 75.61, 28.7, 93.66, 81.08, 93.82, 81.3],
        0.7: [92.68, 77.46, 94.96, 83.03, 92.68, 76.96, 93.5, 79.25, 93.98, 79.75, 93.66, 78.92, 93.5, 80.85, 93.98, 83.22, 93.66, 80.57, 93.98, 82.25],
        0.8: [93.01, 77.1, 93.66, 82.1, 92.85, 77.72, 93.82, 83.75, 93.82, 80.17, 94.47, 82.72, 93.98, 81.21, 93.66, 80.11, 93.82, 79.09, 93.98, 80.38],
        0.9: [93.01, 77.87, 93.5, 80.35, 92.36, 74.67, 93.33, 79.53, 94.31, 80.58, 93.98, 78.07, 93.66, 79.77, 93.01, 81.03, 93.98, 77.8, 93.17, 78.86],
        1: [93.01, 76.65, 94.15, 79.35, 92.68, 76.65, 93.5, 77.35, 93.5, 78.64, 93.82, 78.55, 93.66, 79.26, 93.98, 81.6, 93.01, 79.45, 93.01, 78.86],
    }

    lena_t_15 = {
        0: [87.78, 75.39, 87.22, 75.32, 87.22, 75.86, 77.78, 58.66, 88.33, 74.93, 88.15, 74.83, 86.48, 72.35, 88.33, 76.15, 86.85, 70.95, 86.85, 76.45],
        0.1: [87.41, 74.5, 87.59, 72.48, 85.37, 70.84, 79.81, 53.92, 88.52, 73.62, 88.15, 76.3, 86.85, 74.04, 88.89, 75.72, 87.22, 73.83, 88.89, 76.39],
        0.2: [85.19, 71.47, 87.41, 72.17, 85.56, 72.5, 78.52, 60.36, 88.52, 75.92, 87.41, 72.13, 86.85, 74.68, 88.89, 77.64, 84.63, 67.65, 89.26, 79.33],
        0.3: [87.04, 73.88, 88.15, 77.97, 86.67, 73.47, 77.04, 51.29, 88.15, 72.24, 88.33, 75.61, 86.48, 75.06, 89.26, 78.14, 87.78, 73.74, 87.96, 76.82],
        0.4: [88.33, 77.34, 87.22, 74.72, 85.74, 70.04, 78.7, 60.38, 87.96, 72.9, 87.41, 75.31, 87.04, 75.32, 88.52, 74.49, 78.89, 62.63, 88.33, 74.72],
        0.5: [89.44, 75.74, 86.67, 72.75, 85.74, 70.69, 77.96, 55.67, 87.96, 74.88, 88.15, 75.06, 86.11, 73.61, 88.15, 77.15, 86.85, 69.03, 86.67, 75.14],
        0.6: [87.41, 74.61, 88.15, 74.79, 63.15, 33.1, 82.59, 63.14, 88.52, 76.22, 87.96, 74.33, 80.56, 59.83, 87.96, 75.95, 86.11, 68.92, 89.44, 78.76],
        0.7: [88.33, 76.27, 88.15, 72.63, 87.41, 74.68, 77.41, 57.38, 88.7, 74.77, 87.22, 75.56, 87.41, 75.92, 88.52, 74.76, 88.33, 77.02, 88.7, 76.78],
        0.8: [88.7, 78.17, 87.96, 74.92, 87.41, 74.28, 83.33, 66.12, 87.41, 74.82, 87.96, 74.74, 87.22, 75.72, 89.26, 76.23, 77.59, 51.78, 88.33, 75.04],
        0.9: [87.96, 75.07, 87.22, 73.8, 84.63, 67.66, 84.44, 70.41, 89.26, 76.52, 88.15, 72.94, 86.85, 73.25, 88.33, 77.17, 87.04, 71.72, 77.59, 77.6],
        1: [87.96, 78.87, 87.22, 72.92, 86.11, 69.16, 75.56, 52.9, 88.52, 76.34, 88.33, 76.33, 85.74, 73.54, 77.59, 75.04, 79.07, 59.86, 86.11, 75.04],
    }

    lena_t_16 = {
        0: [93.01, 76.2, 93.5, 79.4, 93.33, 76.9, 92.52, 76.47, 93.33, 76.92, 93.33, 78.95, 92.85, 74.94, 93.5, 78.39, 92.85, 79.14, 93.33, 78.99],
        0.1: [93.5, 77.61, 92.85, 76.63, 92.03, 76.48, 89.92, 71.4, 93.33, 84.51, 92.68, 74.7, 92.85, 76.46, 93.66, 81.23, 93.33, 78.28, 93.01, 76.8],
        0.2: [93.82, 80.45, 93.5, 80.15, 92.68, 79.21, 89.76, 64.99, 94.15, 84.04, 93.5, 79.58, 93.01, 82.03, 93.5, 77.82, 92.2, 80.55, 93.33, 81.88],
        0.3: [93.98, 76.55, 93.82, 81.17, 92.85, 79.86, 88.29, 68.08, 93.17, 79.23, 94.31, 81.34, 93.33, 79.82, 93.01, 77.82, 93.01, 80.93, 93.01, 78.92],
        0.4: [94.15, 82.27, 93.01, 76.51, 91.87, 76.03, 88.13, 62.75, 93.66, 80.32, 93.98, 80.05, 91.87, 76.24, 93.66, 79.66, 92.68, 77.39, 93.33, 76.8],
        0.5: [93.66, 81.29, 93.82, 82.5, 93.82, 78.46, 91.06, 73.05, 93.98, 80.71, 92.68, 78.57, 92.2, 75.86, 93.17, 79.93, 92.36, 76.11, 93.5, 79.23],
        0.6: [94.15, 81.23, 93.17, 78.69, 93.17, 78.5, 91.22, 74.53, 93.82, 80.87, 93.01, 77.41, 91.87, 76.08, 94.31, 83.24, 92.52, 79.08, 92.85, 75.85],
        0.7: [93.5, 81.61, 93.17, 78.16, 93.17, 81.5, 92.36, 78.22, 94.31, 82.71, 93.98, 77.84, 92.36, 76.06, 93.66, 81.43, 92.52, 78.99, 93.33, 80.31],
        0.8: [93.5, 80.36, 93.5, 79.48, 92.68, 79.21, 90.08, 68.79, 93.98, 82.53, 94.96, 83.11, 92.52, 77.12, 93.17, 79.64, 93.01, 80.8, 92.85, 78.52],
        0.9: [92.85, 75.24, 92.85, 78.05, 93.33, 79.97, 91.22, 72.37, 93.66, 80.53, 93.33, 80.64, 92.03, 75.24, 93.5, 80.66, 93.66, 80.33, 93.17, 76.14],
        1: [92.85, 75.75, 93.5, 78.67, 93.5, 78.04, 92.68, 76.54, 93.33, 80.64, 93.66, 78.28, 92.36, 76.26, 93.33, 79.16, 92.52, 75.49, 93.01, 76.13],
    }

    # eta_plot('restaurant15', 'Lena', eta_x, lena_t_15)
    # eta_plot('restaurant16', 'Lena', eta_x, lena_t_16)
    #
    # eta_plot('restaurant15', 'Lena-S', eta_x, lena_s_15)
    # eta_plot('restaurant16', 'Lena-S', eta_x, lena_s_16)

    traj_plot('restaurant15', eta_x, lena_t_15, lena_s_15)
    traj_plot('restaurant16', eta_x, lena_t_16, lena_s_16)

if __name__ == '__main__':

    # texs = find_cwd_files('.tex')
    # for pdf in texs:
    #     cmd = 'pdflatex "{}" "{}.crop.pdf"'.format(pdf, pdf).replace(os.path.sep, '/')
    #     os.system(cmd)

    pdfs = find_cwd_files('.pdf', exclude_key='crop')
    for pdf in pdfs:
        cmd = 'pdfcrop "{}" "{}.crop.pdf"'.format(pdf, pdf).replace(os.path.sep, '/')
        os.system(cmd)

    tmp_files = find_cwd_files(['.aux']) + find_cwd_files(['.log']) + find_cwd_files(['.tex']) + find_cwd_files(['pdf'], exclude_key='crop')
    for f in tmp_files:
        os.remove(f)
