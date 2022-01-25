import numpy as np

A03 = (np.pi**4)/5
A10 = (8*np.pi**4)/15 -49
A11 = (8*np.pi**4)/5 - 219/2 - 12*A10
A12 = (16*np.pi**4)/5 - 117 - 36*A10 - 8*A11
A13 = (16*np.pi**4)/5 - 39 - 24*A10 - 12*A11 - 4*A12
A20 = (4*np.pi**4)/15 - 1 - A10 - A11 - 1/2*A12 - 1/6*A13
A21 = (2*np.pi**4)/5 - A11 - A12 - 1/2*A13
A22 = (2*np.pi**4)/5 - A12 - A13
A23 = (np.pi**4)/5 - A13

def lncomplex(z):
    """
    Complex natural logaritm.
    """
    x=np.real(z)
    _y=np.imag(z)
    _r=np.abs(z)
    return complex(np.log(_r),np.arctan2(_y, x))

def K_24(x):
    return A03*x**(-3) - (A10 + A11*x**(-1) + A12*x**(-2) + A13*x**(-3))*np.exp(-1*x) - (A20 + A21*x**(-1) + A22*x**(-2) + A23*x**(-3))*np.exp(-2*x)

def dK_24(x):
    return -3*A03/x**4-(-A11/x**2-2*A12/x**3-3*A13/x**4)*np.exp(-x)+(A10+A11/x+A12/x**2+A13/x**3)*np.exp(-x)-(-A21/x**2-2*A22/x**3-3*A23/x**4)*np.exp(-2*x)+(2*(A20+A21/x+A22/x**2+A23/x**3))*np.exp(-2*x)

def D_3(x):
    """
    Debye function with n=3.
    """
    if type(x)==np.ndarray:
        return np.array([D_3(xi) for xi in x])
    return K_24(x)
    # # if x<=1:
    if x >=499.99999999999966:
        return 1.5585456848144562e-07
    elif x>=1.579779e+01:
        return np.pi**4/(5*x**3)
    ex=np.exp(x)
    if x <=0.1111111111111111:
        return 0.958950526584995
    else:
        d1, d2, d3, d4, d5, d6 = -np.pi**4/(5*x**3), -3*x*(1/4), np.real(+3*lncomplex(-ex+1)),np.real(+9*mp.fp.polylog(2,ex)/x), np.real(-18*mp.fp.polylog(3,ex)/x**2), np.real(+18*mp.fp.polylog(4,ex)/x**3)
        return d1+d2+d3+d4+d5+d6
def dD_3dx(x, D3):
    if type(x)==np.ndarray:
        return np.array([dD_3dx(xi,D3i) for xi,D3i in zip(x,D3)])
    return dK_24(x)

    if x >= 709.782712893384:
        return -2.3027630998995085e-10
    return np.real(3./(np.exp(x)-1.)-3.*D3/x)

def d2D_3dx2(x, D3, dD3dx):
    if type(x)==np.ndarray:
        return np.array([d2D_3dx2(xi,D3i,dD3dxi) for xi,D3i,dD3dxi in zip(x,D3, dD3dx)])
    if x >=354.89135644669:
        exp_exp2=7.458340731215135e-155
    else:
        exp_exp2=(np.exp(x)/(np.exp(x)-1.)**2.)
    return np.real(-3.*exp_exp2+-3.*dD3dx/x+3.*D3/x**2)

def d3D_3dx3(x, _D3, _dD3dx,_d2D3dx2):
    if type(x)==np.ndarray:
        return np.array([d3D_3dx3(xi,D3i,dD3dxi,d2D3dx2i) for xi,D3i,dD3dxi,d2D3dx2i in zip(x,_D3, _dD3dx, _d2D3dx2)])
    if x>=709.782712893384:
        exp_x = 1.7976931348622732e+308
    else:
        exp_x=np.exp(x)
    if x>=354.89135644669:
        exp_exp2=7.458340731215135e-155
    else:
        exp_exp2 = exp_x/(exp_x-1.)**2.
    return (- 3*exp_exp2 + 6.*exp_exp2*exp_x/(exp_x-1.) - 3.*_d2D3dx2/x+6*_dD3dx/x**2 - 6.*_D3/x**3)
