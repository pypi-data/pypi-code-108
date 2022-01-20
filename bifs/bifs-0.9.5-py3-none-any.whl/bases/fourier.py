
###                 BIFS Fourier basis functions                ###
###                                                             ###
### Global variables:                                           ###
###                                                             ###
### param_func_choice - Current set of k-space                  ###
###                     function choices                        ###
###                                                             ###
### param_func_type - Current parameter funct type              ###
###                                                             ###
### bvec_ixsc - default offset and amplitude for                ###
###             power law decay function                        ###
###                                                             ###
### bvec_ixscbanded - default offset and amplitude for          ###
###                   banded power law decay function           ###
###                                                             ###
### bvec_linsc - default offset and amplitude for               ###
###              "linear" decay function                        ### 
###                                                             ###
### tx1 - bifs transform agnostic name for scipy.fftpack fft    ###
###                                                             ###
### itx1 - bifs transform agnostic name for scipy.fftpack ifft  ###
###                                                             ###
### tx2 - bifs transform agnostic name for scipy.fftpack fft2   ###
###                                                             ###
### itx2 - bifs transform agnostic name for scipy.fftpack ifft2 ###
###                                                             ###
### txn  - bifs transform agnostic name for scipy.fftpack fftn  ###
###                                                             ###
### itxn - bifs transform agnostic name for scipy.fftpack ifftn ###


import numpy as np
from scipy.fftpack import fft,ifft,fft2,ifft2,fftn,ifftn
from scipy import signal

# Choices for K-space parameter function
param_func_choices = ["Inverse Power Decay","Banded Inverse Power Decay","Linear Decay", "Empirical"]

# Default K-space parameter function choice
param_func_type = "Inverse Power Decay"

# Some defaults for parameter function parameters
bvec_ixsc = np.array([0.,500.])
bvec_ixscbanded = np.array([0.,500.])
bvec_linsc = np.array([0.1,500.])

# BIFS conformant transform names

tx1 = fft
itx1 = ifft
tx2 = fft2
itx2 = ifft2
txn = fftn
itxn = ifftn

# K-space distance calculations

def kdist_calc(N):
    """
    kdist(N)

    kdist outputs centered k-space indicex array

    Inpute:
    
    N - Length of desired k-space index array

    Outputs:

    centered, length N k-space index array

    """
    kval = np.zeros((1,N))
    kval[0,0:N//2] = range(1,N//2+1)
    kval[0,0:N//2] = kval[0,0:N//2] - 1 # try this so you get an origin 
    kval[0,N//2:N] = range(-N//2,0)
        
    return kval
        

def kdist1D(N1):
    """
    kdist1D() generates array with distance from
    center of Fourier space but shifted so origin is at index 0 

    Inpute:
    
    N1 - Size of desired array

    Outputs:

    shifted, length N1 k-space distance array

    """
    xvec = kdist_calc(N1)
    kdmat = np.zeros((N1))
    for i in range(N1):
        kdmat[i] = np.sqrt(xvec[0,i]**2)
    return kdmat
    
def kdist2D(N1,N2):
    """
    kdist2D() generates array with distance from
    center of Fourier space but shifted so origin is at index (0,0) 

    Inpute:
    
    N1 - Size of desired array in kx
    N2 - Size of desired array in ky

    Outputs:

    shifted, size (N1,N2) k-space distance array

    """
    xvec = kdist_calc(N1)
    yvec = kdist_calc(N2)
    kdmat = np.zeros((N1,N2))
    for i in range(N1):
        for j in range(N2):
            kdmat[i,j] = np.sqrt(xvec[0,i]**2 + yvec[0,j]**2)
    return kdmat
    
def kdist3D(*ns):
    """
    kdist3D() generates array with distance from
    center of Fourier space but shifted so origin is at index (0,0,0) 

    Input:

    ns should be 3 arguments:
    N1 - Size of desired array in kx
    N2 - Size of desired array in ky
    N3 - Size of desired array in kz 

    Outputs:

    shifted, size (N1,N2,N3) k-space distance array

    Comment: This code could almost work for the 1 and 2D cases,
    but doing so would require a way to generalize the
    a+b+c expression. It is rougly 400x faster than a naive loop-based implmentation.
    """
    dist = [kdist_calc(n)[0, ]**2 for n in ns]
    a, b, c = np.ix_(*dist)
    kdmat = np.sqrt(a+b+c)
    return kdmat


# K-space functional forms for parameter function 

def ixsc(bvec,x,y):
    """
    ixsc() generates a k-space parameter function for the modulus of 
    the prior mean of the form: 
                 amplitude/distance^y + offset
    where the offset is from center of k-space. 

    Inputs:

    bvec - 2 element array where bvec[0] is offset, bvec[1] is amplitude

    x - function argument

    y - power law decay index

    Outputs:

    function value

    """
    zero_offset = 0.01
    try:
        if np.abs(x) > 0.0:
            return bvec[0] + bvec[1]*x**(-y)
    except:
        return bvec[0] + bvec[1]*(x+zero_offset)**(-y)

      
def ixscbanded(bvec,x,y,z):
    """
    ixscbanded() generates a k-space parameter function for the modulus of 
    the prior mean of the form: 
                 amplitude/distance^y + offset
    where the offset is from center of k-space and in addition has a 
    cutoff at a distance z from the center of k-space.

    Inputs:

    bvec - 2 element array where bvec[0] is offset, bvec[1] is amplitude

    x - function argument

    y - power law decay index

    z - cutoff value, distance from center of k-space

    Outputs:

    function value

    """
    idx1 = x < z
    zero_offset = 0.01
    zero_floor = 0.0001
    try:
        if np.abs(x) > 0.0:
            idx2 = bvec[0] + bvec[1]*x**(-y)
    except:
        idx2 = bvec[0] + bvec[1]*(x+zero_offset)**(-y)
    return idx1*idx2 + zero_floor
    # return np.where(x<z,bvec[0] + bvec[1]*x**(-y),0.)

def linsc(bvec,x):
    """
    linsc() generates a k-space parameter function for the modulus of 
    the prior mean of the form: 
                 offset - amplitude*x^2
    where the offset is from center of k-space. 

    Inputs:

    bvec - 2 element array where bvec[0] is offset, bvec[1] is amplitude

    x - function argument

    Outputs:

    function value
    
    """
    zero_floor = 0.0001
    if not (bvec[0] > 0.0): # Assume there was a mistake like
                            # resetting param_func_type and
                            # forgetting to reset bvec - should
                            # probably fix this by using getter's
        bvec[0] = 0.1  # default bvec[0]
        bvec[1] = 500. # might as well set bvec[1] to default in this case
    y = bvec[1] - bvec[0]*x**2
    return np.where(y>0,y,zero_floor)

def add_bumps_to_pf(bvec,x,bumps,kmax):
    """ 
    add_bumps_to_pf() adds filter "bumps" to the k-space paramter
    function to enhance or supress certain frequency ranges in 
    generating the prior mean. Since the k-space paramter functions 
    currently used are rotationally symmetric this adds a ring or 
    spherical shell in 2D or 3D. This function uses the window shapes 
    from scipy.singal to generate the "bumps" so all filter shapes that 
    only require the filter type and size are available. The documentation
    for scipy.signal can be be consulted for a current list of available
    filter shapes.

    Inputs:
    
    bvec - 2 element array where bvec[0] is offset, bvec[1] is amplitude
           for current k-space paramter function; bvec[1] is used to
           generate the amplitude of the bump re. relative fraction of 
           bvec[1].

    x - argument for the bump function(s)

    bumps - a python dictionary with elements of the form:

            bump_name:[bump_location,bump_amplitude,bump_width]

            where:
            bump_name(key) - a text string containing one of the 
                             available scipy.signal filter forms
            bump_location -  location of the bump as fraction of the
                             maximum k-space value
            bump_amplitude - amplitude of the bump as fraction of the
                             maximum of the k-space paramter function,
                             i.e. bvec[1]
            bump_width -     width of the bump as fraction of the
                             maximum k-space value

    kmax - maximum k-space value

    Outputs:

    Function with all bumps in the bumps dictionary added (to be
    added to the paramter function)

    """

    # Make cumlative bump function to add
    
    bump_func = np.zeros(np.int(kmax))
    if bumps: # just to be sure
        bump_count = 0
        #
        # print(bumps)
        #
        for k,v in bumps.items():
            bump_center = np.int(v[0]*kmax)
            bump_amp = float(v[1]*bvec[1])
            bump_width = np.int(v[2]*kmax)
            start = bump_center - np.int(np.floor(bump_width/2))
            stop = bump_center + np.int(np.ceil(bump_width/2))
            #
            # print(x,kmax,k,v,bump_center,bump_amp,bump_width,start,stop)
            #
            # Split k in case multiple cases of same filter type
            # in which case the convention is to append ".something"
            bump_func[start:stop] = bump_amp*signal.get_window(k.split('.')[0],bump_width)
            if bump_count == 0:
                y = bump_func[np.asarray(x, dtype=int)-1]
            else:
                y += bump_func[np.asarray(x, dtype=int)-1]
            #
            # print("nonzero y in add_bumps",np.sum(np.where(y !=0,1,0)))
            #
        return np.where(y > 0.0,y,0.0)
#    except:
#        print("Couldn't implement bump function additions")
#        return
    
