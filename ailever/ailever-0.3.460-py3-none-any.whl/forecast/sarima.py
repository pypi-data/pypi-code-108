from ..logging_system import logger

import numpy as np
import sympy
import matplotlib.pyplot as plt
import statsmodels.tsa.api as smt

dummies = type('dummies', (dict,), {})
def Process(trendparams:tuple=(0,0,0), seasonalparams:tuple=(0,0,0,1), trendAR=None, trendMA=None, seasonAR=None, seasonMA=None, n_samples=300, verbose=True):
    r"""
    Examples:
        >>> from ailever.forecast import sarima
        >>> ...
        >>> trendAR=[]; trendMA=[]
        >>> seasonAR=[]; seasonMA=[]
        >>> process = sarima.Process((1,1,2), (2,0,1,4), trendAR=trendAR, trendMA=trendMA, seasonAR=seasonAR, seasonMA=seasonMA, n_samples=300)
        >>> process.final_coeffs
        >>> process.TS_Yt
        >>> process.samples
    """

    results = dummies()

    p, d, q = trendparams
    P, D, Q, m = seasonalparams

    assert type(p) is int, 'Input parameter "p" is not an integer type.'
    assert type(d) is int, 'Input parameter "d" is not an integer type.'
    assert type(q) is int, 'Input parameter "q" is not an integer type.'
    assert type(P) is int, 'Input parameter "P" is not an integer type.'
    assert type(D) is int, 'Input parameter "D" is not an integer type.'
    assert type(Q) is int, 'Input parameter "Q" is not an integer type.'
    assert type(m) is int, 'Input parameter "m" is not an integer type.'

    if trendAR : assert len(trendAR) == p, f'The len(trendAR) must be {p}. Reset the parameters.'
    else : trendAR = [0.01]*p
    if trendMA : assert len(trendMA) == q, f'The len(trendMA) must be {q}. Reset the parameters.'
    else : trendMA = [0.01]*q
    if seasonAR : assert len(seasonAR) == P, f'The len(seasonAR) must be {P}. Reset the parameters.'
    else : seasonAR = [0.01]*P
    if seasonMA : assert len(seasonMA) == Q, f'The len(seasonMA) must be {Q}. Reset the parameters.'
    else : seasonMA = [0.01]*Q


    Y_order = p + P*m + d + D*m
    e_order = q + Q*m

    # define Y, e
    Y, e = sympy.symbols('Y_t, e_t')
    I, J = sympy.symbols('i, j')
    Y_ = {}; e_ = {}
    Y_['t'] = Y; Y__ = [ [Y_['t']] ]
    e_['t'] = e; e__ = [ [e_['t']] ]
    for i in range(1, Y_order+1):
        Y_[f't-{i}'] = sympy.symbols(f'Y_t-{i}')
        Y__.append( [Y_[f't-{i}']*(I**i)] )    # Y__ = [ [Y_['t']], [Y_['t-1']], ..., [Y_['t-(p+P*m+q+Q*m)']] ]
    for i in range(1, e_order+1):   
        e_[f't-{i}'] = sympy.symbols(f'e_t-{i}')
        e__.append( [e_[f't-{i}']*(J**i)] )    # e__ = [ [e_['t']], [e_['t-1']], ..., [e_['t-(q+Q*m)']] ]

    # define L
    L = sympy.symbols('L')
    S_Lag = L**m
    T_Lag = L
    S_Lag_Diff = (1-L**m)**D
    T_Lag_Diff = (1-L)**d

    # define coefficients : phis(T), Phis(S), thetas(T), Thetas(S)
    T_phi = {}; T_phis = []; L_byT_phi = []
    S_phi = {}; S_phis = []; L_byS_phi = []
    T_theta = {}; T_thetas = []; L_byT_theta = []
    S_theta = {}; S_thetas = []; L_byS_theta = []

    for p_ in range(0, p+1):
        T_phi[p_] = sympy.symbols(f'phi_{p_}')
        T_phis.append(-T_phi[p_])       # T_phis      = [T_phi[0], T_phi[1], ..., T_phi[p]]
        L_byT_phi.append([T_Lag**p_])   # L_byT_phi   = [[L**0], [L**1], ..., [L**p]]
    for P_ in range(0, P+1):
        S_phi[P_] = sympy.symbols(f'Phi_{P_}')
        S_phis.append(-S_phi[P_])       # S_phis      = [S_phi[0], S_phi[1], ..., S_phi[P]]
        L_byS_phi.append([S_Lag**P_])   # L_byS_phi   = [[(L**m)**0], [(L**m)**1], ..., [(L**m)**P]]
    for q_ in range(0, q+1):
        T_theta[q_] = sympy.symbols(f'theta_{q_}')
        T_thetas.append(T_theta[q_])    # T_thetas    = [T_theta[0], T_theta[1], ..., T_theta[q]]
        L_byT_theta.append([T_Lag**q_]) # L_byT_theta = [[L**0], [L**1], ..., [L**q]]
    for Q_ in range(0, Q+1):
        S_theta[Q_] = sympy.symbols(f'Theta_{Q_}')
        S_thetas.append(S_theta[Q_])    # S_thetas    = [T_theta[0], T_theta[1], ..., T_theta[Q]]
        L_byS_theta.append([S_Lag**Q_]) # L_byS_theta = [[(L**m)**0], [(L**m)**1], ..., [(L**m)**Q]]

    T_phi_Lag = sympy.Matrix([T_phis]) * sympy.Matrix(L_byT_phi)
    S_phi_Lag = sympy.Matrix([S_phis]) * sympy.Matrix(L_byS_phi)
    T_theta_Lag = sympy.Matrix([T_thetas]) * sympy.Matrix(L_byT_theta)
    S_theta_Lag = sympy.Matrix([S_thetas]) * sympy.Matrix(L_byS_theta)

    Y_operator = (T_phi_Lag * S_phi_Lag * T_Lag_Diff * S_Lag_Diff).subs(T_phi[0], -1).subs(S_phi[0], -1)[0]
    e_operator = (T_theta_Lag * S_theta_Lag).subs(T_theta[0], 1).subs(S_theta[0], 1)[0]

    Y_operation = sympy.collect(Y_operator.expand(), L)
    e_operation = sympy.collect(e_operator.expand(), L)

    Y_coeff = sympy.Poly(Y_operation, L).all_coeffs()[::-1]
    e_coeff = sympy.Poly(e_operation, L).all_coeffs()[::-1]

    Y_term = sympy.Matrix([Y_coeff]) * sympy.Matrix(Y__) # left-side
    e_term = sympy.Matrix([e_coeff]) * sympy.Matrix(e__) # right-side
    
    Time_Series = {}
    Time_Series['Y_t(i,j)'] = sympy.Poly(Y - Y_term[0] + e_term[0], (I,J))
    Time_Series['Y_t'] = Time_Series['Y_t(i,j)'].subs(I, 1).subs(J, 1)
    for i in range(1, int(p+P*m+d+D*m)+1):
        Time_Series['Y_t'] = sympy.collect(Time_Series['Y_t'], Y_[f't-{i}']).simplify()
    for i in range(1, int(q+Q*m)+1):
        Time_Series['Y_t'] = sympy.collect(Time_Series['Y_t'], e_[f't-{i}']).simplify()
    sympy.pprint(Time_Series['Y_t'])

    Time_Series['Analytic_Coeff_of_Y'] = Time_Series['Y_t(i,j)'].subs(J, 0).all_coeffs()[::-1]
    Time_Series['Analytic_Coeff_of_e'] = Time_Series['Y_t(i,j)'].subs(I, 0).all_coeffs()[::-1]

    Time_Series['Numeric_Coeff_of_Y'] = Time_Series['Y_t(i,j)'].subs(J, 0) - e_['t']
    Time_Series['Numeric_Coeff_of_e'] = Time_Series['Y_t(i,j)'].subs(I, 0)
    for i, (phi, Np) in enumerate(zip(list(T_phi.values())[1:], trendAR)):
        Time_Series['Numeric_Coeff_of_Y'] = Time_Series['Numeric_Coeff_of_Y'].subs(phi, Np)
    for i, (Phi, NP) in enumerate(zip(list(S_phi.values())[1:], seasonAR)):
        Time_Series['Numeric_Coeff_of_Y'] = Time_Series['Numeric_Coeff_of_Y'].subs(Phi, NP)
    for i, (theta, Nt) in enumerate(zip(list(T_theta.values())[1:], trendMA)):
        Time_Series['Numeric_Coeff_of_e'] = Time_Series['Numeric_Coeff_of_e'].subs(theta, Nt)
    for i, (Theta, NT) in enumerate(zip(list(S_theta.values())[1:], seasonMA)):
        Time_Series['Numeric_Coeff_of_e'] = Time_Series['Numeric_Coeff_of_e'].subs(Theta, NT)
    Time_Series['Numeric_Coeff_of_Y'] = sympy.Poly(Time_Series['Numeric_Coeff_of_Y'], I).all_coeffs()[::-1]
    Time_Series['Numeric_Coeff_of_e'] = sympy.Poly(Time_Series['Numeric_Coeff_of_e'], J).all_coeffs()[::-1]

    final_coeffs = [[], []]
    if verbose:
        logger['forecast'].info(f'  - TAR({trendparams[0]}) {"phi":5} : {trendAR}')
        logger['forecast'].info(f'  - TMA({trendparams[2]}) {"theta":5} : {trendMA}')
        logger['forecast'].info(f'  - SAR({seasonalparams[0]}) {"Phi":5} : {seasonAR}')
        logger['forecast'].info(f'  - SMA({seasonalparams[2]}) {"Theta":5} : {seasonMA}')

        logger['forecast'].info('\n* [Y params]')
    for i, (A_coeff_Y, N_coeff_Y) in enumerate(zip(Time_Series['Analytic_Coeff_of_Y'], Time_Series['Numeric_Coeff_of_Y'])):
        if i == 0:
            pass
        elif i != 0:                
            A_coeff_Y = A_coeff_Y.subs(Y_[f"t-{i}"], 1)
            N_coeff_Y = N_coeff_Y.subs(Y_[f"t-{i}"], 1)
            if verbose:
                logger['forecast'].info(f'  - t-{i:2} : {A_coeff_Y} > {round(N_coeff_Y, 5)}')
            final_coeffs[0].append(N_coeff_Y)
    
    if verbose:
        logger['forecast'].info('\n* [e params]')
    for i, (A_coeff_e, N_coeff_e) in enumerate(zip(Time_Series['Analytic_Coeff_of_e'], Time_Series['Numeric_Coeff_of_e'])):
        if i == 0:
            A_coeff_e = A_coeff_e.subs(e_[f"t"], 1)
            N_coeff_e = N_coeff_e.subs(e_[f"t"], 1)
            if verbose:
                logger['forecast'].info(f'  - t-{i:2} : {A_coeff_e} > {1}')

        elif i != 0:                
            A_coeff_e = A_coeff_e.subs(e_[f"t-{i}"], 1)
            N_coeff_e = N_coeff_e.subs(e_[f"t-{i}"], 1)
            if verbose:
                logger['forecast'].info(f'  - t-{i:2} : {A_coeff_e} > {round(N_coeff_e, 5)}')
            final_coeffs[1].append(N_coeff_e)
    
    # Correlation
    plt.style.use('ggplot')
    if d == 0 and D == 0 :
        _, axes = plt.subplots(5,1, figsize=(25, 15))
        ar_params = np.array(final_coeffs[0])
        ma_params = np.array(final_coeffs[1])
        ar, ma = np.r_[1, -ar_params], np.r_[1, ma_params]
        y = smt.ArmaProcess(ar, ma).generate_sample(n_samples, burnin=50)

        axes[0].plot(y, 'o-')
        axes[0].set_title(f"SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[0].grid(True)

        axes[1].stem(smt.ArmaProcess(ar, ma).acf(lags=40))
        axes[1].set_xlim(-1, 41)
        axes[1].set_ylim(-1.1, 1.1)
        axes[1].set_title(f"Theoretical autocorrelation function of an SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[1].grid(True)

        axes[2].stem(smt.ArmaProcess(ar, ma).pacf(lags=40))
        axes[2].set_xlim(-1, 41)
        axes[2].set_ylim(-1.1, 1.1)
        axes[2].set_title(f"Theoretical partial autocorrelation function of an SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[2].grid(True)

        smt.graphics.plot_acf(y, lags=40, ax=axes[3])
        axes[3].set_xlim(-1, 41)
        axes[3].set_ylim(-1.1, 1.1)
        axes[3].set_title(f"Experimental autocorrelation function of an SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[3].grid(True)

        smt.graphics.plot_pacf(y, lags=40, ax=axes[4])
        axes[4].set_xlim(-1, 41)
        axes[4].set_ylim(-1.1, 1.1)
        axes[4].set_title(f"Experimental partial autocorrelation function of an SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[4].grid(True)

        plt.tight_layout()
        #plt.show()

        results.samples = y
    else:
        _, axes = plt.subplots(3,1,figsize=(25,10))

        window_ar = len(final_coeffs[0])     # Y_['t-1'] ~ 
        window_ma = len(final_coeffs[1]) - 1 # e_['t-1'] ~

        white_noise = np.random.normal(size=int(2*n_samples))
        time_series = np.zeros_like(white_noise)
        for t, noise in enumerate(white_noise):
            if t>=window_ar and t>=window_ma:
                time_series[t] = time_series[t-window_ar:t][::-1]@final_coeffs[0] + noise + white_noise[t-window_ma:t][::-1]@final_coeffs[1][1:]
        y = time_series[-n_samples:]

        axes[0].plot(y, marker='o')
        axes[0].set_title(f"SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[0].grid(True)

        smt.graphics.plot_acf(y, lags=40, ax=axes[1])
        axes[1].set_title(f"Experimental autocorrelation function of an SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[1].grid(True)

        smt.graphics.plot_pacf(y, lags=40, ax=axes[2])     
        axes[2].set_title(f"Experimental partial autocorrelation function of an SARIMA(({p},{d},{q}),({P},{D},{Q},{m})) process")
        axes[2].grid(True)

        plt.tight_layout()
        #plt.show()

        results.samples = y
        
    results.final_coeffs = final_coeffs
    results.TS_Yt = Time_Series['Y_t']
    results.experimental_acf = smt.stattools.acf(y, nlags=40)
    results.experimental_pacf = smt.stattools.pacf(y, nlags=40)
    results['Args_0'] = 'final_coeffs'
    results['Args_1'] = 'TS_Yt'
    results['Args_2'] = 'samples'
    return results



