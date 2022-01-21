from mpl_format.literals import H_ALIGN, V_ALIGN


def check_h_align(h_align: H_ALIGN):

    if h_align not in ('left', 'center', 'right'):
        raise ValueError("h_align not in ('left', 'center', 'right')")


def check_v_align(v_align: V_ALIGN):

    if v_align not in ('top', 'center', 'bottom'):
        raise ValueError("v_align not in ('top', 'center', 'bottom')")
