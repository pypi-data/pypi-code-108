# Test fit functions
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
from bfit.fitting.functions import *
import numpy as np

def test_lorentzian():
    
    # test values
    amp = 1
    fwhm = 0.25
    peak = 0.5
    
    gety = lambda x : -lorentzian(x, peak, fwhm, amp) # flip y for less confusion on my part
    dx = 1e-9   # window to check values in
        
    # check amplitude
    x = np.linspace(peak-dx/2, peak+dx/2, 10000)
    y = gety(x)
    assert_almost_equal(max(y), 1, err_msg = "lorentzian amplitude")
    
    # check peak location
    xmax = x[y == max(y)][0]
    assert_almost_equal(xmax, peak, err_msg = "lorentzian peak")
    
    # check FWHM
    xleft = np.linspace(peak-fwhm/2-dx, peak-fwhm/2+dx, 10000)
    xright = np.linspace(peak+fwhm/2-dx, peak+fwhm/2+dx, 10000)
    
    yleft = gety(xleft) - amp/2
    yright = gety(xright) - amp/2
    
    x1 = max(xleft[yleft < 0])
    x2 = min(xright[yright < 0])
    
    width = x2 - x1
    assert_almost_equal(width, fwhm, err_msg = "lorentzian fwhm")
    
def test_bilorentzian():
    
    x = np.linspace(0, 1, 10000)
    
    # test values for lor2 = 0
    amp = 1
    fwhm = 0.25
    peak = 0.5
    
    lor = lorentzian(x, peak, fwhm, amp)
    bi1 = bilorentzian(x, peak, fwhm, amp, 0, 0)
    bi2 = bilorentzian(x, peak, 0, 0, fwhm, amp)
    
    assert_array_almost_equal(lor, bi1, err_msg = "bilorenzian component 1")
    assert_array_almost_equal(lor, bi2, err_msg = "bilorenzian component 2")
    
def test_gaussian():
    
    # test values
    amp = 1
    sigma = 0.25
    mean = 0.5
    
    x = np.linspace(0, 1, 100000)
    y = -gaussian(x, mean, sigma, amp)
    
    # test amp
    assert_almost_equal(max(y), amp, err_msg = "gaussian amp")
    
    # test mean 
    avg = np.average(x, weights=y)
    assert_almost_equal(avg, mean, err_msg = "gaussian mean")
    
    # test stdev
    mean = 5
    x = np.linspace(0, 10, 100000)
    y = -gaussian(x, mean, sigma, amp)
    
    wsum = np.sum(np.square(mean - x) * y)
    sig = np.sqrt( wsum / np.sum(y) )
    assert_almost_equal(sig, sigma, err_msg = "gaussian sigma")
    
def test_quadlorentzian():
    
    # ~ nu_0 = 1e6
    nu_q = 1e3
    eta = 0
    theta = 0
    phi = 0
    
    # test first order peak locations for I = 2
    I = 2
    peaks = np.array([qp_1st_order(nu_q, eta, theta, phi, m) for m in np.arange(-(I-1), I+1, 1)])
    
    assert_almost_equal(len(peaks), 4, err_msg = "quadlorentzian number of first order peaks for I=2")
    assert_array_almost_equal(peaks, np.array([nu_q*3, nu_q, -nu_q, -3*nu_q]), 
                            err_msg = "quadlorentzian first order shifts for I=2")
    
    # test first order peak locations for I = 3/2
    I = 3/2
    peaks = np.array([qp_1st_order(nu_q, eta, theta, phi, m) for m in np.arange(-(I-1), I+1, 1)])
    assert_almost_equal(len(peaks), 3, err_msg = "quadlorentzian number of first order peaks for I=3/2")
    assert_array_almost_equal(peaks, np.array([nu_q*2, 0, -2*nu_q]), 
                                err_msg = "quadlorentzian first order shifts for I=3/2")
    
def test_pulsed_exp():
    
    # settings
    amp = 1
    tau = 1
    pulse_len = 4
    
    x = np.linspace(1e-9, 10, 10000)
    pexp = pulsed_exp(lifetime = tau, pulse_len = pulse_len)
    
    # test amp
    y = pexp(x, 1, amp)
    assert_almost_equal(amp, y[0], err_msg = "pulsed exp amp")
    
    # test non-relaxing
    y = pexp(x, 0, amp)
    assert_almost_equal(y[-1], amp, err_msg = "pulsed exp non-relaxing behaviour")
    
    # test inf relaxing
    y = pexp(x, np.inf, amp)
    assert_almost_equal(y[0], 0, err_msg = "pulsed exp infinitly fast relaxing behaviour")
    
    # test beam off position
    x = np.linspace(pulse_len-1e-6, pulse_len+1e-6, 10000)
    y = pexp(x, 1, amp)
    
    ddy = np.diff(np.diff(y))
    idx = ddy == min(ddy)
    
    assert_almost_equal((x[:-2])[idx], pulse_len, err_msg = "pulsed exp beam off position")
    
def test_pulsed_strexp():
    
    # settings
    amp = 1
    tau = 1
    pulse_len = 4
    
    x = np.linspace(1e-9, 10, 10000)
    psexp = pulsed_strexp(lifetime = tau, pulse_len = pulse_len)
    pexp = pulsed_exp(lifetime = tau, pulse_len = pulse_len)
    
    # test equivalence with pexp
    y1 = pexp(x, 1, amp)
    y2 = psexp(x, 1, 1, amp)
    # 1e-6 is the error in the integration
    assert_array_almost_equal(y1, y2, decimal=6, err_msg = 'pulsed str exp comparison to pulsed single exp when beta = 1')
    
    # test amp
    x = np.linspace(1e-15, 1, 10)
    y = psexp(x, 1, 0.5, amp)
    assert_almost_equal(amp, y[0], decimal=3, err_msg = 'pulsed str exp amp')
    
    # test non-relaxing
    y = psexp(x, 0, 0.5, amp)
    assert_almost_equal(y[0], y[-1], decimal=3, err_msg = 'pulsed str exp non-relaxing behaviour')
    
    # test inf relaxing
    y = psexp(x, np.inf, 0.5, amp)
    assert_almost_equal(y[0], 0, err_msg = 'pulsed str exp infinitly fast relaxing behaviour')
    
    # test beam off position
    x = np.linspace(pulse_len-1e-6, pulse_len+1e-6, 10000)
    y = psexp(x, 1, 0.5, amp)
    
    ddy = np.diff(np.diff(y))
    idx = ddy == min(ddy)
    
    assert_almost_equal((x[:-2])[idx], pulse_len, err_msg = 'pulsed str exp beam off position')
