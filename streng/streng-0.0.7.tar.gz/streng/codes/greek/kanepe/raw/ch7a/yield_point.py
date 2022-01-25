import math
from tabulate import tabulate


def ξycalc(α, A, B, include_intermediates=False):
    """
        Το ύψος της θλιβόµενης ζώνης στη διαρροή, ξy, ανηγµένο στο στατικό ύψος d, είναι:

        .. math::
            ξ_y=(α^2A^2+2αB)^{0.5}-αA

    Args:
        α (float): Ο λόγος των μέτρων ελαστικότητας :math:`α = E_s/E_c`
        A (float): Ο συντελεστής A που υπολογίζονται για διαρροή λόγω χάλυβα ή μη-γραμμικότητα σκυροδέματος
        B (float): Ο συντελεστής B που υπολογίζονται για διαρροή λόγω χάλυβα ή μη-γραμμικότητα σκυροδέματος
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """

    value = (α ** 2 * A ** 2 + 2 * α * B) ** 0.5 - α * A

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r"ξ_y=(α^2A^2+2αB)^{0.5}-αA" \
            + fr'=({α:.3f}^2\cdot {A:.5f}^2+2\cdot {α:.3f}\cdot {B:.5f})^{{0.5}}-{α:.3f}\cdot {A:.5f}={value:.4f}'
        return _dict
    else:
        return value


def A_steel(ρ1, ρ2, ρv, N, b, d, fy, include_intermediates=False):
    """
        Συντελεστής A για διαρροή του οπλισμού. 
        Δίνεται από τη σχέση:

        .. math::
            A=ρ+ρ'+ρ_v+\dfrac{N}{bdf_y}     

    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        N (float): το αξονικό φορτίο (θετικό σε θλίψη) [kN]
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος  [m]
        fy (float): το όριο διαρροής του χάλυβα  [kPa]
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value
    """
    value = ρ1 + ρ2 + ρv + N / (b * d * fy)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r"A=ρ+ρ'+ρ_v+\dfrac{{N}}{{bdf_y}}=" \
            + f'{ρ1:.5f}+{ρ2:.5f}+{ρv:.5f}+' \
            + f'\dfrac{{{N:.2f}kN}}{{{b:.2f}m\cdot{d:.2f}m\cdot{fy:.1f}kPa}}={value:.5f}'
        return _dict
    else:
        return value


def B_steel(ρ1, ρ2, ρv, N, b, d, δtonos, fy, include_intermediates=False):
    """
        Συντελεστής B για διαρροή του οπλισμού. 
        Δίνεται από τη σχέση:

        .. math::
            B=ρ+ρ'δ'+0.5ρ_v(1+δ')+\dfrac{N}{bdf_y}

    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        N (float): το αξονικό φορτίο (θετικό σε θλίψη) [kN]
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος [m]
        δtonos (float): :math:`δ' = d'/d` όπου d' η απόσταση από το κέντρο του θλιβόµενου οπλισµού µέχρι την ακραία θλιβόµενη ίνα σκυροδέµατος
        fy (float): το όριο διαρροής του χάλυβα  [kPa]
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value
    """

    value = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos) + N / (b * d * fy)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r'\begin{aligned}' \
            + r"B &=ρ+ρ'δ'+0.5ρ_v(1+δ')+\dfrac{N}{bdf_y}=" + r'\\' \
            + f'&={ρ1:.5f}+{ρ2:.5f}\cdot{δtonos:.3f}+0.5\cdot{ρv:.5f}\cdot(1+{δtonos:.3f})+'  \
            + f'\dfrac{{{N:.2f}kN}}{{{b:.2f}m\cdot{d:.2f}m\cdot{fy:.1f}kPa}}={value:.5f}' \
            + r'\end{aligned}'
        return _dict
    else:
        return value


def φy_steel(fy, Es, ξy, d, include_intermediates=False):
    """
        Καμπυλότητα διαρροής για διαρροή του οπλισμού.
        Δίνεται από τη σχέση:

        .. math::        
            φ_y=\dfrac{f_y}{E_s(1-ξ_y)d}

    Args:
        fy (float): το όριο διαρροής του χάλυβα  [kPa]
        Es (float): το μέτρο ελαστικότητας του χάλυβα  [kPa]
        ξy (float): Το ύψος της θλιβόµενης ζώνης στη διαρροή, ανηγµένο στο στατικό ύψος d [m]
        d (float): το στατικό ύψος [m]
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value
    """

    value = fy / (Es * (1.0 - ξy) * d)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r"φ_y=\dfrac{f_y}{E_s(1-ξ_y)d}=" \
            + fr'\dfrac{{{fy:.1f}}}{{{Es:.1f}\cdot(1-{ξy:.4f})\cdot{d:.3f}}}={value:.5f}'
        return _dict
    else:
        return value


def A_conc(ρ1, ρ2, ρv, N, b, d, α, fc, include_intermediates=False):
    """
        Συντελεστής A για µή-γραµµικότητα των παραµορφώσεων του θλιβόµενου σκυροδέµατος
        Δίνεται από τη σχέση (χρησιμοποιείται η προσέγγιση):

        .. math::
            A=ρ+ρ'+ρ_v-\dfrac{N}{ε_c E_s bd}≈ρ+ρ'+ρ_v-\dfrac{N}{1.8αbdf_c}           

    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        N (float): το αξονικό φορτίο (θετικό σε θλίψη) [kN]
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος  [m]
        α (float): Ο λόγος των μέτρων ελαστικότητας :math:`α = E_s/E_c`
        fc (float): η θλιπτική αντοχή του σκυροδέματος  [kPa]
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value
    """
    value = ρ1 + ρ2 + ρv - N / (1.8 * α * b * d * fc)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r"A=ρ+ρ'+ρ_v-\dfrac{N}{1.8αbdf_c}=" \
            + f'{ρ1:.5f}+{ρ2:.5f}+{ρv:.5f}-' \
            + f'\dfrac{{{N:.2f}kN}}{{1.8\cdot{α:.3f}\cdot{b:.2f}m\cdot{d:.2f}m\cdot{fc:.1f}kPa}}={value:.5f}'
        return _dict
    else:
        return value


def B_conc(ρ1, ρ2, ρv, b, d, δtonos, include_intermediates=False):
    """
        Συντελεστής B για µή-γραµµικότητα των παραµορφώσεων του θλιβόµενου σκυροδέµατος
         Δίνεται από τη σχέση:

        .. math::
            B=ρ+ρ'δ'+0.5ρ_v(1+δ')

    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος  [m]
        δtonos (float): :math:`δ' = d'/d` όπου d' η απόσταση από το κέντρο του θλιβόµενου οπλισµού µέχρι την ακραία θλιβόµενη ίνα σκυροδέµατος
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value

    """
    value = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r"B=ρ+ρ'δ'+0.5ρ_v(1+δ')=" \
            + rf'{ρ1:.5f}+{ρ2:.5f}\cdot{{{δtonos:.3f}}}+0.5\cdot{ρv:.5f}\cdot(1+{{{δtonos:.3f}}})={value:.5f}'
        return _dict
    else:
        return value


def φy_conc(fc, Ec, ξy, d, include_intermediates=False):
    """
        Καμπυλότητα διαρροής για για µή-γραµµικότητα των παραµορφώσεων του θλιβόµενου σκυροδέµατος
        Δίνεται από τη σχέση (χρησιμοποιείται η προσέγγιση):

        .. math::
            φ_y=\dfrac{ε_c}{ξ_y d}≈\dfrac{1.8 f_y}{E_s ξ_y d}

    Args:
        fc (float): η θλιπτική αντοχή του σκυροδέματος  [kPa]
        Ec (float): το μέτρο ελαστικότητας του σκυροδέματος  [kPa]
        ξy (float): Το ύψος της θλιβόµενης ζώνης στη διαρροή, ανηγµένο στο στατικό ύψος d [m]
        d (float): το στατικό ύψος [m]
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value
    """

    value = 1.8 * fc / (Ec * ξy * d)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r"φ_y=\dfrac{1.8 f_y}{E_s ξ_y d}=" \
            + rf'\dfrac{{1.8\cdot{fc:.1f}}}{{{Ec:.1f}\cdot{ξy:.4f}\cdot{d:.3f}}}={value:.5f}'
        return _dict
    else:
        return value


def My(b, d, φy, Ec, ξy, δtonos, ρ1, ρ2, ρv, Es, include_intermediates=False):
    """
        Με δεδοµένη την καµπυλότητα στη διαρροή, η αντίστοιχη ροπή Μy προκύπτει ως:

        .. math::
            \dfrac{M_y}{bd^3}=φ_y\Bigg\{E_c\dfrac{ξ_y^2}{2}\Big(0.5(1+δ')-\dfrac{ξ_y}{3}\Big) + \Big[ (1-ξ_y)ρ+(ξ_y-δ')ρ'+\dfrac{ρ_v}{6}(1-δ') \Big]\cdot(1-δ')\dfrac{E_s}{2} \Bigg\}

    Args:
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος [m]
        φy (float): Καμπυλότητα διαρροής [m-1]
        Ec (float): το μέτρο ελαστικότητας του σκυροδέματος  [kPa]
        ξy (float): Το ύψος της θλιβόµενης ζώνης στη διαρροή ανηγµένο στο στατικό ύψος d
        δtonos (float): :math:`δ' = d'/d` όπου d' η απόσταση από το κέντρο του θλιβόµενου οπλισµού µέχρι την ακραία θλιβόµενη ίνα σκυροδέµατος
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        Es (float): το μέτρο ελαστικότητας του χάλυβα  [kPa]
        include_intermediates (bool): True για να δημιουργηθεί το latex string

    Returns:
        dict or float: A dict with all intermediate values or a float with final value

    """

    value = b * d ** 3 * φy * (0.5 * Ec * ξy ** 2 * (0.5 * (1 + δtonos) - ξy / 3) +
                               ((1 - ξy) * ρ1 + (ξy - δtonos) * ρ2 + ρv * (1 - δtonos) / 6) * (1 - δtonos) * Es / 2)

    if include_intermediates:
        _dict = {}
        _dict['value'] = value
        _dict['latex'] = r'\begin{aligned}' \
            r"M_y=φ_ybd^3\Bigg\{E_c\dfrac{ξ_y^2}{2}\Big(0.5(1+δ')-\dfrac{ξ_y}{3}\Big) + \Big[ (1-ξ_y)ρ+(ξ_y-δ')ρ'+\dfrac{ρ_v}{6}(1-δ') \Big]\cdot(1-δ')\dfrac{E_s}{2} \Bigg\}=" + r'\\' \
            + rf'&={φy:.4f}\cdot {b:.3f} \cdot {d:.3f}^3 \cdot \Bigg\{Ec:.1f}\cdot\dfrac{{{ξy:.4f}^2}}{{2}}\Big(0.5\cdot(1+{δtonos:.3f}) - \dfrac{{{ξy:.4f}}}{{3}}\Big) + ' + r'\\' \
            + rf'&+ \Big[ (1-{ξy:.4f})\cdot{ρ1:.5f}+({ξy:.4f}-{δtonos:.3f})\cdot{ρ2:.5f}+\dfrac{{{ρv:.5f}}}{6}(1-{δtonos:.3f}) \Big] \cdot(1-{δtonos:.3f})\dfrac{{{Es:.1f}}}{{2}} \Bigg\}}= ' + r'\\' \
            + rf'&={value:.3f}kNm' \
            + r'\end{aligned}'
        return _dict
    else:
        return value


# Not needed anymore
def Mycalc(b, d, φy, Ec, ξy, δ2, ρ1, ρ2, ρv, Es):
    return b * d ** 3 * φy * (0.5 * Ec * ξy ** 2 * (0.5 * (1 + δ2) - ξy / 3) + (
        (1 - ξy) * ρ1 + (ξy - δ2) * ρ2 + ρv * (1 - δ2) / 6) * (1 - δ2) * Es / 2)

# Not needed anymore
def ABξφ_steel(ρ, ρ2, ρv, N, b, d, δ2, fy, α, Es):
    A = ρ + ρ2 + ρv + N / (b * d * fy)
    B = ρ + ρ2 * δ2 + 0.5 * ρv * (1 + δ2) + N / (b * d * fy)
    ξy = ξycalc(α, A, B)
    φy = fy / (Es * (1 - ξy) * d)
    return A, B, ξy, φy

# Not needed anymore
def ABξφ_conc(ρ, ρ2, ρv, N, b, d, δ2, α, Ec, fc):
    A = ρ + ρ2 + ρv - N / (1.8 * α * b * d * fc)
    B = ρ + ρ2 * δ2 + 0.5 * ρv * (1 + δ2)
    ξy = ξycalc(α, A, B)
    φy = 1.8 * fc / (Ec * ξy * d)
    return A, B, ξy, φy


def yield_props(ρ1, ρ2, ρv, N, b, d, δtonos, fc, Ec, fy, Es, include_intermediates=False):
    logtext = ''
    latext = ''

    _dict = {}

    α = Es/Ec
    Asteel = ρ1 + ρ2 + ρv + N / (b * d * fy)
    Bsteel = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos) + N / (b * d * fy)
    ξysteel = ξycalc(α, Asteel, Bsteel, False)
    φysteel = fy / (Es * (1.0 - ξysteel) * d)
    Aconc = ρ1 + ρ2 + ρv - N / (1.8 * α * b * d * fc)
    Bconc = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos)
    ξyconc = ξycalc(α, Aconc, Bconc, False)
    φyconc = 1.8 * fc / (Ec * ξyconc * d)

    if φysteel < φyconc:
        φy = φysteel
        ξy = ξysteel
    else:
        φy = φyconc
        ξy = ξyconc

    if include_intermediates:
        headers = ['', 'value', 'units']
        table = [['α', α],
                 ['Asteel', Asteel],
                 ['Bsteel', Bsteel],
                 ['ξysteel', ξysteel, 'm'],
                 ['φysteel', φysteel, 'm-1'],
                 ['Aconc', Aconc],
                 ['Bconc', Bconc],
                 ['ξyconc', ξyconc],
                 ['φyconc', φyconc, 'm-1'],
                 ['φy', φy, 'm-1'],
                 ['ξy', ξy, 'm']]
        logtext = tabulate(table, headers, tablefmt="pipe", floatfmt=".3E")

        _dict['α'] = α
        _dict['Asteel'] = Asteel
        _dict['Bsteelα'] = Bsteel
        _dict['ξysteel'] = ξysteel
        _dict['φysteel'] = φysteel
        _dict['Aconc'] = Aconc
        _dict['Bconc'] = Bconc
        _dict['ξyconc'] = ξyconc
        _dict['φyconc'] = φyconc
        _dict['φy'] = φy
        _dict['ξy'] = ξy

    # return α, Asteel, Bsteel, ξysteel[0], φysteel, Aconc, Bconc, ξyconc[0], φyconc, φy, ξy, logtext, latext
    return _dict
