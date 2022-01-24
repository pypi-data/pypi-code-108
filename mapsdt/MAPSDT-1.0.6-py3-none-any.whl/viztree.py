from graphviz import Digraph


def viztree(leaf_list, root, config):
    leaf_id = list(map(lambda x: [x.id, x.branchAttribute, x.parent, x.classes, x.decision], leaf_list))
    dot = Digraph(comment='Visualization', format='svg')
    color = ['slategray1', 'mistyrose', 'papayawhip', 'antiquewhite4', 'lightgoldenrodyellow', 'sandybrown']
    if len(leaf_id[0][4]) == 2:
        for i in leaf_id:
            if sum(i[4]) > 0:
                bar = color[0] + ';' + str(i[4][0] / sum(i[4])) + ':' + color[1] + ';' + str(i[4][1] / sum(i[4]))
            else:
                bar = color[0] + ';0.5:' + color[1] + ';0.5'
            if i[1] is None:
                if i[4][0] == i[4][1] == 0:
                    label = config['target_names'][0]+':' + str(i[4][0]) + ' / ' + config['target_names'][1]+':' + str(i[4][1]) + '\n'
                    dot.node(i[0], label, style='filled', fillcolor=color[2], fontname='Arial', fontcolor=color[3],
                             color=color[2])
                elif i[4][0] < i[4][1]:
                    decision = config['target_names'][1]
                    label = config['target_names'][0]+':' + str(i[4][0]) + ' / ' + config['target_names'][1]+':' + str(i[4][1]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='red'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
                else:
                    decision = config['target_names'][0]
                    label = config['target_names'][0]+':' + str(i[4][0]) + ' / ' + config['target_names'][1]+':' + str(i[4][1]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='blue'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
            else:
                if 'obj.' in i[1]:
                    dot.node(i[0],
                             i[1].replace('obj.', '') + '\n['+config['target_names'][0]+':' + str(i[4][0]) + ' / '+config['target_names'][1]+':' + str(i[4][1]) + ']',
                             color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=bar,
                             fontcolor=color[3])
                else:
                    dot.node(i[0], i[1] + '\n['+config['target_names'][0]+':' + str(i[4][0]) + ' / '+config['target_names'][1]+':' + str(i[4][1]) + ']',
                             color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=bar,
                             fontcolor=color[3])
            if i[2] is '1':
                dot.edge(i[2], i[0], i[3], fontname='Arial', arrowhead='normal', color=color[3])
            else:
                dot.edge(i[2].id, i[0], i[3], fontname='Arial', arrowhead='normal', color=color[3])

        # ===========================================================

        root_bar = color[0] + ';' + str(root.decision[0] / sum(root.decision)) + ':' + color[1] + ';' + str(
            root.decision[1] / sum(root.decision))
        if 'obj.' in root.branchAttribute:
            dot.node('1',
                     root.branchAttribute.replace('obj.', '') + '\n['+config['target_names'][0]+':' + str(root.decision[0]) + ' / '+config['target_names'][1]+':' + str(
                         root.decision[1]) + ']',
                     color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=root_bar,
                     fontcolor=color[3])
        else:
            dot.node('1', root.branchAttribute + '\n['+config['target_names'][0]+':' + str(root.decision[0]) + ' / '+config['target_names'][1]+':' + str(
                root.decision[1]) + ']', color=color[3], shape='box', fontname='Arial', style='striped',
                     fillcolor=root_bar, fontcolor=color[3])

    elif len(leaf_id[0][4]) == 3:
        for i in leaf_id:
            if sum(i[4]) > 0:
                bar = color[0] + ';' + str(i[4][0] / sum(i[4])) + ':' + color[1] + ';' + str(
                    i[4][1] / sum(i[4])) + ':' + color[4] + ';' + str(i[4][2] / sum(i[4]))
            else:
                bar = color[0] + ';1/3:' + color[1] + ';1/3' + color[4] + ';1/3'
            if i[1] is None:
                if i[4][0] == i[4][1] == i[4][2] == 0:
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + '\n'
                    dot.node(i[0], label, style='filled', fillcolor=color[2], fontname='Arial', fontcolor=color[3],
                             color=color[2])
                elif i[4][1] < i[4][0] and i[4][2] < i[4][0]:
                    decision = config['target_names'][0]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='blue'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
                elif i[4][0] < i[4][1] and i[4][2] < i[4][1]:
                    decision = config['target_names'][1]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='red'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
                else:
                    decision = config['target_names'][2]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='gold'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
            else:
                if 'obj.' in i[1]:
                    dot.node(i[0],
                         i[1].replace('obj.', '') + '\n['+config['target_names'][0]+': ' + str(i[4][0]) + ' / '+config['target_names'][1]+': ' + str(i[4][1]) + ' / '+config['target_names'][2]+': ' + str(
                             i[4][2]) + ']',
                         color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=bar,
                         fontcolor=color[3])
                else:
                    dot.node(i[0],
                             i[1] + '\n['+config['target_names'][0]+': ' + str(i[4][0]) + ' / '+config['target_names'][1]+': ' + str(
                                 i[4][1]) + ' / '+config['target_names'][2]+': ' + str(
                                 i[4][2]) + ']',
                             color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=bar,
                             fontcolor=color[3])
            if i[2] is '1':
                dot.edge(i[2], i[0], i[3], fontname='Arial', arrowhead='normal', color=color[3])
            else:
                dot.edge(i[2].id, i[0], i[3], fontname='Arial', arrowhead='normal', color=color[3])

        # ===========================================================

        root_bar = color[0] + ';' + str(root.decision[0] / sum(root.decision)) + ':' + color[1] + ';' + str(
            root.decision[1] / sum(root.decision)) + ':' + color[4] + ';' + str(root.decision[2] / sum(root.decision))
        if 'obj.' in root.branchAttribute:
            dot.node('1',
                     root.branchAttribute.replace('obj.', '') + '\n['+config['target_names'][0]+': ' + str(root.decision[0]) + ' / '+config['target_names'][1]+': ' + str(
                         root.decision[1]) + ' / '+config['target_names'][2]+': ' + str(root.decision[2]) + ']',
                     color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=root_bar,
                     fontcolor=color[3])
        else:
            dot.node('1',
                     root.branchAttribute + '\n['+config['target_names'][0]+': ' + str(
                         root.decision[0]) + ' / '+config['target_names'][1]+': ' + str(
                         root.decision[1]) + ' / '+config['target_names'][2]+': ' + str(root.decision[2]) + ']',
                     color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=root_bar,
                     fontcolor=color[3])

    elif len(leaf_id[0][4]) == 4:
        for i in leaf_id:
            if sum(i[4]) > 0:
                bar = color[0] + ';' + str(i[4][0] / sum(i[4])) + ':' + color[1] + ';' + str(
                    i[4][1] / sum(i[4])) + ':' + color[4] + ';' + str(i[4][2] / sum(i[4])) + ':' + color[5] + ';' + str(i[4][3] / sum(i[4]))
            else:
                bar = color[0] + ';1/4:' + color[1] + ';1/4' + color[4] + ';1/4' + color[5] + ';1/4'
            if i[1] is None:
                if i[4][0] == i[4][1] == i[4][2] == i[4][3] == 0:
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + ' / ' + config['target_names'][3]+': ' + str(i[4][3]) + '\n'
                    dot.node(i[0], label, style='filled', fillcolor=color[2], fontname='Arial', fontcolor=color[3],
                             color=color[2])
                elif i[4][1] < i[4][0] and i[4][2] < i[4][0] and i[4][3] < i[4][0]:
                    decision = config['target_names'][0]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + ' / ' + config['target_names'][3]+': ' + str(i[4][3]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='blue'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
                elif i[4][0] < i[4][1] and i[4][2] < i[4][1] and i[4][3] < i[4][1]:
                    decision = config['target_names'][1]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + ' / ' + config['target_names'][3]+': ' + str(i[4][3]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='red'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
                elif i[4][0] < i[4][2] and i[4][1] < i[4][2] and i[4][3] < i[4][2]:
                    decision = config['target_names'][2]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + ' / ' + config['target_names'][3]+': ' + str(i[4][3]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='green'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
                else:
                    decision = config['target_names'][3]
                    label = config['target_names'][0]+': ' + str(i[4][0]) + ' / ' + config['target_names'][1]+': ' + str(i[4][1]) + ' / ' + config['target_names'][2]+': ' + str(
                        i[4][2]) + ' / ' + config['target_names'][3]+': ' + str(i[4][3]) + '\n'
                    dot.node(i[0], "<" + label + "<font color='gold'><br/>" + decision + "<br/></font>>",
                             fontcolor=color[3], color=color[3], fontname='Arial')
            else:
                if 'obj.' in i[1]:
                    dot.node(i[0],
                         i[1].replace('obj.', '') + '\n['+config['target_names'][0]+': ' + str(i[4][0]) + ' / ' +config['target_names'][1]+': ' + str(i[4][1]) + ' / '+config['target_names'][2]+': ' + str(
                             i[4][2]) + ' / '+config['target_names'][3]+': ' + str(i[4][3]) + ']',
                         color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=bar,
                         fontcolor=color[3])
                else:
                    dot.node(i[0],
                             i[1] + '\n['+config['target_names'][0]+': ' + str(i[4][0]) + ' / ' +config['target_names'][1]+': ' + str(
                                 i[4][1]) + ' / '+config['target_names'][2]+': ' + str(
                                 i[4][2]) + ' / '+config['target_names'][3]+': ' + str(i[4][3]) + ']',
                             color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=bar,
                             fontcolor=color[3])
            if i[2] is '1':
                dot.edge(i[2], i[0], i[3], fontname='Arial', arrowhead='normal', color=color[3])
            else:
                dot.edge(i[2].id, i[0], i[3], fontname='Arial', arrowhead='normal', color=color[3])

        # ===========================================================

        root_bar = color[0] + ';' + str(root.decision[0] / sum(root.decision)) + ':' + color[1] + ';' + str(
            root.decision[1] / sum(root.decision)) + ':' + color[4] + ';' + str(root.decision[2] / sum(root.decision)) + ':' + color[5] + ';' + str(root.decision[3] / sum(root.decision))
        if 'obj.' in root.branchAttribute:
            dot.node('1',
                     root.branchAttribute.replace('obj.', '') + '\n['+config['target_names'][0]+': ' + str(root.decision[0]) + ' / '+config['target_names'][1]+': ' + str(
                         root.decision[1]) + ' / '+config['target_names'][2]+': ' + str(root.decision[2]) + ' / '+config['target_names'][3]+': ' + str(root.decision[3]) + ']',
                     color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=root_bar,
                     fontcolor=color[3])
        else:
            dot.node('1',
                     root.branchAttribute + '\n['+config['target_names'][0]+': ' + str(
                         root.decision[0]) + ' / '+config['target_names'][1]+': ' + str(
                         root.decision[1]) + ' / '+config['target_names'][2]+': ' + str(root.decision[2]) + ' / '+config['target_names'][3]+': ' + str(root.decision[3]) + ']',
                     color=color[3], shape='box', fontname='Arial', style='striped', fillcolor=root_bar,
                     fontcolor=color[3])
    print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
    dot.render('test-output/Visualization.gv', view=True)