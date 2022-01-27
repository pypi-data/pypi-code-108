from AutoFeedback.varchecks import check_value
import matplotlib.pyplot as plt


def _grab_figure(modname='main'):
    fighand = None
    try:
        plt.ion()  # make any show commands non-blocking
        if modname == 'main':
            __import__(modname)
        fighand = plt.gca()
        # plt.close() # close any open figures
    except ModuleNotFoundError:
        import sys
        sys.exit()
    return fighand


def _extract_plot_elements(fighand, lines=True, patches=False,
                           axislabels=False, axes=False, legend=False):
    line_data, patch_data, axes_data, labels, legend_data =\
        None, None, None, None, [None]

    if lines:
        line_data = fighand.get_lines()

    if patches:
        patch_data = fighand.patches

    if axes:
        axes_data = [*fighand.get_xlim(), *fighand.get_ylim()]

    if axislabels:
        labels = [fighand.get_xlabel(), fighand.get_ylabel(),
                  fighand.get_title()]

    if legend:
        try:
            legend_data = [x.get_text()
                           for x in fighand.get_legend().get_texts()]
        except AttributeError:
            legend_data = []

    return line_data, patch_data, axes_data, labels, legend_data


def _check_linestyle(line, expected):
    style = line.get_linestyle()
    return (style in expected)


def _check_marker(line, expected):
    style = line.get_marker()
    return (style in expected)


def _check_colour(line, expected):
    color = line.get_color()
    return (color in expected)


def _check_linedata(line, expline, no_diagnose=False):
    x, y = zip(*line.get_xydata())
    return expline.check_linedata(x, y, no_diagnose)


def _check_patchdata(patch, exppatch):
    x, y = [], []
    for p in patch:
        xd, yd = p.get_xy()
        yd = p.get_height()
        x.append(xd + 0.5*p.get_width())
        y.append(yd)
    return exppatch.check_linedata(x, y)


def _check_legend(legend_data, expected):
    return(legend_data and check_value(legend_data, expected))


def _check_axes(l1, l2):
    return(check_value(l1, l2))


def _reorder(a, b):
    from itertools import permutations
    for perm in permutations(b):
        if (all([_check_linedata(x, y, no_diagnose=True)
                 for x, y in zip(perm, a)])):
            return (perm)
    return b


def _e_string(error, label):
    if label:
        return error+'("'+label+'")'
    else:
        return error+"('')"


def check_plot(explines, exppatch=None, explabels=None, expaxes=None,
               explegend=False, output=False, check_partial=False,
               modname='main'):
    from AutoFeedback.plot_error_messages import print_error_message
    from itertools import zip_longest
    try:
        fighand = _grab_figure(modname)
        lines, patch, axes, labels, legends =\
            _extract_plot_elements(fighand, lines=(len(explines) > 0),
                                   patches=exppatch, axes=bool(expaxes),
                                   axislabels=bool(explabels),
                                   legend=explegend)
        explegends = [line.label for line in explines
                      if line.label is not None]
        expline = ""
        if not check_partial:
            if explines:
                assert (len(lines) == len(explines)), "_datasets"
            if explegend:
                assert (len(legends) == len(explegends)), "_legend"

        if (explines and not lines):
            assert (False), "_datasets"

        if (explines):
            lines = _reorder(explines, lines)

            for line, expline, legend in zip_longest(lines, explines, legends):
                if expline:
                    assert (_check_linedata(line, expline)), _e_string(
                        "_data", expline.label)
                    if expline.linestyle:
                        assert(_check_linestyle(line, expline.linestyle)
                               ), _e_string("_linestyle", expline.label)
                    if expline.marker:
                        assert(_check_marker(line, expline.marker)
                               ), _e_string("_marker", expline.label)
                    if expline.colour:
                        assert(_check_colour(line, expline.colour)
                               ), _e_string("_colour", expline.label)
                    if expline.label and explegend:
                        if line.get_label()[0] != "_":
                            assert(_check_legend(line.get_label(),
                                                 expline.label)), "_legend"
                        else:
                            assert(_check_legend(legend, expline.label)),\
                                "_legend"
                    if output:
                        print_error_message(
                            _e_string("_partial", expline.label), expline)
        if (exppatch):
            expline = exppatch
            assert(_check_patchdata(patch, exppatch)), _e_string("_data", "")
            if output:
                print_error_message(_e_string("_partial", ""), exppatch)
        if not explines and not exppatch:
            assert(False), "_data"
        if explabels:
            if len(explabels) == 2:
                explabels.append("")
            assert(_check_axes(labels, explabels)), "_labels"
        if expaxes:
            assert(_check_axes(axes, expaxes)), "_axes"
        if output:
            print_error_message("_success", expline)
        return(True)
    except AssertionError as error:
        if output:
            print_error_message(error, expline)
        return(False)
