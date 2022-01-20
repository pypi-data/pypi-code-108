import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import tensorflow as tf


def gensign(h1, h2, t1, t2, noise=0.005, size=1000, return_y_values=True):

    if [False for i in [h1, h2, t1, t2, noise, size] if i < 0].__contains__(False):
        raise ValueError('argument cannot be less than zero')

    x = np.arange(0, size, 1)
    place1 = t1
    place2 = t2
    y_f1 = scipy.stats.norm(place1, 100/2.355)
    y1 = y_f1.pdf(x)*100/2.355*(2*3.14)**(1/2)*h1
    y_f2 = scipy.stats.norm(place2, 100/2.355)
    y2 = y_f2.pdf(x)*100/2.355*(2*3.14)**(1/2)*h2
    y = y1+y2
    y = np.random.normal(loc=0, scale=noise, size=size)+y
    if return_y_values:
        return y, h1, h2, t1, t2
    else:
        return y


def ratio_of_uniforms(a, b, x, p=1.0):
    """
    Generate a probability density of the ratio of the variables generated in a normal distribution
     (normal distribution range from a to b).
     """

    out = 1./((b-a)**2)*((b*b)/(x*x)-a*a)
    out = tf.where(tf.less(x, 1.0), 0., out)
    out = tf.where(tf.greater(x, b/a), 0., out)
    p = tf.cast(p, tf.float32)
    out = tf.cast(out, tf.float32)
    return out/p


def sum_of_uniforms(a, b, x, p=1.0):
    """
    Generate a probability density of the sum of the variables generated in the normal distribution
     (normal distribution range from a to b).
     """

    out = 0
    out = tf.where(tf.greater(x, a), 4/(b-a)**2*(x-a), out)
    out = tf.where(tf.greater(x, (b-a)/2+a), -4/(b-a)**2*(x-b), out)
    out = tf.where(tf.greater(x, b), 0.0, out)
    p = tf.cast(p, tf.float32)
    out = tf.cast(out, tf.float32)
    return out/p


def standardize(y, t1_min, t1_max, t2_min, t2_max, h_min, h_max):
    """Standardize the dependent variables so that the values are between 0.1 and 0.9
    y - y data table (numpy array), columns: h1, h2, t1, t2

    t1_min - the minimum position of first signal
    t2_min - the minimum position of second signal

    t1_max - the maximum position of first signal
    t2_max - the maximum position of second signal

    h_min - the minimum height of signals
    h_max - the maximum height of signals

    returned: y data table with columns: h1, h2, t1, t2 (standardized to values between 0.1 and 0.9)
    """
    size = len(y)
    delta_t1 = t1_max - t1_min
    delta_t2 = t2_max - t2_min
    y_new = np.zeros((size, 4))
    y_new[:, :2] = (y[:, :2]-h_min)/(h_max-h_min)*0.8+0.1
    y_new[:, 2] = (((y[:, 2])-t1_min)/delta_t1)*0.8+0.1
    y_new[:, 3] = (((y[:, 3])-t2_min)/delta_t2)*0.8+0.1
    return y_new


def de_standardize(y, x1_min, x1_max, x2_min, x2_max, y_min, y_max):
    """Destandardize the dependent variables from 0.1 - 0.9 to those before standardization.
    y - y data table (numpy array), columns: h1, h2, t1, t2

    t1_min - target minimum position of first signal
    t2_min - target minimum position of second signal

    t1_max - target maximum position of first signal
    t2_max - target maximum position of second signal

    h_min - target minimum height of signals
    h_max - target maximum height of signals

    returned: y data table with columns: h1, h2, t1, t2 (standardized to target values)"""
    delta_x1 = x1_max - x1_min
    delta_x2 = x2_max - x2_min

    if len(y.shape) == 1:
        y = y.reshape(1, 4)

    size = len(y)
    y_old = np.zeros((size, 4))

    y_old[:, :2] = ((y[:, :2] - 0.1) / 0.8) * (y_max - y_min) + y_min
    y_old[:, 2] = ((y[:, 2] - 0.1) / 0.8) * delta_x1 + x1_min
    y_old[:, 3] = ((y[:, 3] - 0.1) / 0.8) * delta_x2 + x2_min
    return y_old


def gensign_random(h_min, h_max, t1_min, t1_max, t_delta, noise=0.005, size=1000, return_y_values=True):
    t1 = np.random.uniform(t1_min, t1_max)
    return gensign(h1=np.random.uniform(h_min, h_max),
                   h2=np.random.uniform(h_min, h_max),
                   t1=t1,
                   t2=t1 + np.random.uniform(0, t_delta),
                   noise=noise, size=size, return_y_values=return_y_values)


def destandardize_height(h, h_min, h_max): return ((h-0.1)/0.8)*(h_max-h_min)+h_min


def places_change(t, t_min, t_max): return ((t-0.1)/0.8)*(t_max-t_min)+t_min


def make_histogram(data, name, range=None):
    n, bins, patches = plt.hist(data, bins=50, range=range, density=True)
    plt.ylabel("The frequency / probability density")
    width = (bins[-1]-bins[0]) / 50
    width = round(width, 2)
    plt.xlabel(name+", (The width of the bar: "+str(width)+")")
    return n


def height_ratio(x, y, limit=20.0):
    """Calculate height ratio between two values.
    x > 0, y > 0
    h_ratio(x,y) = x/y if x>y
                 = y/x if y>x
                = limit if ( y/x>limit or x/y > limit )
    """
    output = tf.where(tf.greater(x/y, 1.0), x/y, y/x)
    output = tf.where(tf.greater(output, limit), limit, output)
    return output


def cost_function_nominator(function, a, b, alpha, epsilon):
    p1 = function(a, b, 1.)
    p2 = function(a, b, (a+b)/2)
    p = tf.where(tf.greater(p1, p2), p1, p2)
    p = tf.where(tf.less(p, epsilon), epsilon, p)
    p = tf.cast(p, tf.float32)

    def out(m, d=1.):
        return (1-alpha*function(a, b, m, p=p))/d
    return out


def cost_function_denominator(function, a, b, alpha, y, epsilon):

    out = cost_function_nominator(function, a, b, alpha=alpha, epsilon=epsilon)
    out = tf.math.reduce_mean(out(y), 0)
    return out


def cost_function(function, a, b, alpha, y, epsilon):
    out = cost_function_nominator(function, a, b, alpha, epsilon=epsilon)
    denominator = cost_function_denominator(function, a, b, alpha, y, epsilon=epsilon)
    denominator = tf.cast(denominator, tf.float32)

    def out_final(y_data):
        return out(y_data, d=denominator)
    return out_final


def uniform(a, b, x):
    out = 0
    out = tf.where(tf.greater(x, a), 1/(b-a), out)
    out = tf.where(tf.greater(x, b), 0, out)
    return out
