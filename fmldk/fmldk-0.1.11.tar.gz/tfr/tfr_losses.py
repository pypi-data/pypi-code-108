#!/usr/bin/env python
# coding: utf-8


import numpy as np
import math as m
import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
import pprint

# Negbin Loss
@tf.function(experimental_relax_shapes=True)
def Negbin_loss(actual, mu, alpha):
    '''
    Negative Binomial Sample
    Args:
    actual: [batch, fh]
    mu: [batch, fh]
    alpha: [batch, fh]
    maximize log l_{nb} = log Gamma(z + 1/alpha) - log Gamma(z + 1) - log Gamma(1 / alpha)
                          - 1 / alpha * log (1 + alpha * mu) + z * log (alpha * mu / (1 + alpha * mu))
    minimize loss = - log l_{nb}
    Note: torch.lgamma: log Gamma function
    '''
    likelihood = tf.math.lgamma(actual + 1.0/alpha) - tf.math.lgamma(actual + 1) - tf.math.lgamma(1.0/alpha)                 - 1.0/alpha*tf.math.log(1 + alpha*mu) + actual*tf.math.log(alpha*mu/(1 + alpha * mu))
    nll = -1.0*likelihood
    return tf.reduce_mean(nll)
  
# Normal Loss
@tf.function(experimental_relax_shapes=True)
def Normal_loss(actual, mu, std):
    dist = tfd.Normal(mu,std)
    likelihood = dist.log_prob(actual)
    nll = -1.0*likelihood
    return tf.reduce_mean(nll)

# Student's t Loss
@tf.function(experimental_relax_shapes=True)
def Student_loss(actual, mu, std, df):
    dist = tfd.StudentT(df=df, loc=mu, scale=std)
    likelihood = dist.log_prob(actual)
    nll = -1.0*likelihood
    return tf.reduce_mean(nll)

# Poisson Loss
@tf.function(experimental_relax_shapes=True)
def Poisson_loss(mu, actual):
    dist = tfd.Poisson(rate=mu)
    likelihood = dist.log_prob(actual)
    nll = -1.0*likelihood
    return tf.reduce_mean(nll)

# Gumbel Loss
@tf.function(experimental_relax_shapes=True)
def Gumbel_loss(actual, a, b):
    '''
    k = (x-a)/b
    log_prob = -log(k) - k - exp(-k)
    '''
    eps = 1e-7
    b = b
    k = (actual - a)/b
    likelihood = -tf.math.log(b) - k - tf.math.exp(-k)
    nll = -1.0*likelihood
    return tf.reduce_mean(nll)


# Keras Custom Loss Subclasses -- Quantile Loss, RMSSE, RMSE, Negbin_NLL_Loss, Normal_NLL_Loss, Poisson_NLL_Loss, Gumbel_NLL_Loss

class QuantileLoss(tf.keras.losses.Loss):
    def __init__(self, quantiles = [0.50,0.60,0.65], ** kwargs): 
        self.quantiles = quantiles 
        super().__init__(** kwargs)
    
    def call(self, actuals, predictions):
        pred = tf.cast(predictions, tf.float32)
        true = tf.cast(tf.squeeze(actuals), tf.float32)
        losses = tf.cast(tf.zeros_like(true), tf.float32)
        for i,q in enumerate(self.quantiles):
            error = tf.subtract(true, pred[:,:,i])
            losses += tf.maximum(q*error, (q-1)*error) 
        return tf.reduce_mean(losses) 
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config, "quantiles": self.quantiles}
      
class QuantileLoss_Weighted(tf.keras.losses.Loss):
    def __init__(self, quantiles = [0.50,0.60,0.65], ** kwargs): 
        self.quantiles = quantiles 
        super().__init__(** kwargs)
    
    def call(self, actuals, output):
        predictions, wts = output[0], output[1]
        pred = tf.cast(predictions, tf.float32)
        true = tf.cast(tf.squeeze(actuals), tf.float32)
        losses = tf.cast(tf.zeros_like(true), tf.float32)
        for i,q in enumerate(self.quantiles):
            error = tf.subtract(true, pred[:,:,i])
            losses += tf.maximum(q*error, (q-1)*error)
        wts = tf.reshape(wts, [-1,1]) 
        return tf.reduce_mean(wts*losses)
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config, "quantiles": self.quantiles}
            
class QuantileLoss_v2(tf.keras.losses.Loss):
    def __init__(self, quantiles=[0.1,0.5,0.9], is_equal_weights=True, quantile_weights=None, sample_weights=False, ** kwargs): 
        self.quantiles = quantiles
        self.is_equal_weights = is_equal_weights
        self.num_quantiles = len(quantiles)
        self.quantile_weights = (quantile_weights if quantile_weights else self.compute_quantile_weights())
        self.sample_weights = sample_weights
        super().__init__(** kwargs)
    
    def call(self, actuals, output):
        if self.sample_weights:
            predictions, wts = output[0], output[1]
            wts = tf.reshape(wts, [-1,1]) 
        else:
            wts = 1.0
            predictions = output
        y_pred = tf.cast(predictions, tf.float32)
        y_true = tf.cast(tf.squeeze(actuals), tf.float32)
        losses = tf.cast(tf.zeros_like(y_true), tf.float32)
        for i,q in enumerate(self.quantiles):
            losses += self.compute_quantile_loss(y_true, y_pred[:,:,i], q)*self.quantile_weights[i]
        return tf.reduce_mean(wts*losses)
    
    def compute_quantile_loss(self, y_true, y_pred, q):
        #under_bias = q * tf.maximum(y_true - y_pred, 0)
        #over_bias = (1.0 - q) * tf.maximum(y_pred - y_true, 0)
        #qt_loss = 2 * (under_bias + over_bias)
        error = tf.subtract(y_true, y_pred)
        qt_loss = tf.maximum(q*error, (q-1)*error)
        return qt_loss
    
    def compute_quantile_weights(self):
        if self.num_quantiles == 0:
            quantile_weights = []
        elif self.is_equal_weights or self.num_quantiles == 1:
            quantile_weights = [1.0 / self.num_quantiles] * self.num_quantiles
        else:
            quantile_weights = ([0.5 * (self.quantiles[1] - self.quantiles[0])] + 
                                [0.5 * (self.quantiles[i + 1] - self.quantiles[i - 1]) for i in range(1, self.num_quantiles - 1)] +
                                [0.5 * (self.quantiles[-1] - self.quantiles[-2])])
        return quantile_weights
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config, "quantiles":self.quantiles, "is_equal_weights":self.is_equal_weights, "quantile_weights": self.quantile_weights, "sample_weights":self.sample_weights}


class RMSSELoss(tf.keras.losses.Loss):
    def __init__(self, sl, fh, ** kwargs):
        self.sl = sl
        self.fh = fh  
        super().__init__(** kwargs)
    
    def call(self, actuals, predictions):
        pred = tf.cast(tf.squeeze(predictions), tf.float32)
        true = tf.cast(tf.squeeze(actuals), tf.float32)
        true_fh = true[:,-self.fh:]
        true_in = true[:,1:self.sl]
        true_in_lag = true[:,0:self.sl-1]
        error = tf.reduce_sum(tf.math.square(tf.abs(true_fh - pred)), axis=1, keepdims=True)/tf.cast(self.fh, tf.float32)
        scale = tf.reduce_sum(tf.math.square(tf.abs(true_in - true_in_lag)), axis=1, keepdims=True)/tf.cast((self.sl-1), tf.float32)
        #weights = tf.reduce_sum(true[:,:self.sl], axis=1, keepdims=True)/tf.reduce_sum(true[:,:self.sl])
        rmsse = tf.math.sqrt(error/scale)
        return tf.reduce_mean(rmsse)
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}


class RMSE(tf.keras.losses.Loss):
    def __init__(self,sample_weights=False, ** kwargs):
        self.sample_weights = sample_weights
        super().__init__(** kwargs)
    
    def call(self, actuals, pred):
        if self.sample_weights:
            output, wts = pred[0], pred[1]
            wts = tf.reshape(wts, [-1,1]) 
        else:
            wts = 1.0
            output = pred
        output = tf.cast(tf.squeeze(output), tf.float32)
        true = tf.cast(tf.squeeze(actuals), tf.float32)
        error = wts*tf.reduce_mean(tf.math.square(tf.abs(true - output)), axis=1, keepdims=True)
        rmse = tf.math.sqrt(error)
        return tf.reduce_mean(rmse)
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}
    

class Huber(tf.keras.losses.Loss):
    def __init__(self, delta=1.0, sample_weights=False, ** kwargs):
        self.sample_weights = sample_weights
        self.delta = delta
        self.loss_fn = tf.keras.losses.Huber(delta=self.delta)
        super().__init__(** kwargs)
    
    def call(self, actuals, pred):
        if self.sample_weights:
            output, wts = pred[0], pred[1]
            wts = tf.reshape(wts, [-1,1]) 
        else:
            wts = 1.0
            output = pred
        output = tf.cast(tf.squeeze(output), tf.float32)
        true = tf.cast(tf.squeeze(actuals), tf.float32)
        if self.sample_weights:
            loss = self.loss_fn.__call__(true, output, wts)
        else:
            loss = self.loss_fn(true, output)
        return loss
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}
      
        
class Negbin_NLL_Loss(tf.keras.losses.Loss):
    def __init__(self, sample_weights=False, ** kwargs):
        self.sample_weights = sample_weights
        super().__init__(** kwargs)
    
    def call(self, actuals, pred):
        if self.sample_weights:
            output, wts = pred[0], pred[1]
            wts = tf.reshape(wts, [-1,]) 
        else:
            wts = 1.0
            output = pred
        true = tf.cast(actuals, tf.float32) #[batch,fh]
        mu = tf.cast(output[:,:,0:1], tf.float32) #[batch,fh]
        alpha = tf.cast(output[:,:,1:2], tf.float32) #[batch,fh]
        nll = Negbin_loss(true, mu, alpha)
        return nll
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}

    
class Normal_NLL_Loss(tf.keras.losses.Loss):
    def __init__(self, sample_weights=False, ** kwargs):
        self.sample_weights = sample_weights
        super().__init__(** kwargs)
    
    def call(self, actuals, pred):
        if self.sample_weights:
            output, wts = pred[0], pred[1]
            wts = tf.reshape(wts, [-1,]) 
        else:
            wts = 1.0
            output = pred
        true = tf.cast(actuals, tf.float32) #[batch,fh,1]
        mu = tf.cast(output[:,:,0:1], tf.float32) #[batch,fh,1]
        alpha = tf.cast(output[:,:,1:2], tf.float32) #[batch,fh,1]
        nll = Normal_loss(true, mu, alpha)
        return nll
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}
      
        
class Poisson_NLL_Loss(tf.keras.losses.Loss):
    def __init__(self, sample_weights=False, ** kwargs):
        self.sample_weights = sample_weights
        super().__init__(** kwargs)
    
    def call(self, actuals, pred):
        if self.sample_weights:
            output, wts = pred[0], pred[1]
            wts = tf.reshape(wts, [-1,]) 
        else:
            wts = 1.0
            output = pred
        true = tf.cast(actuals, tf.float32) #[batch,fh,1]
        mu = tf.cast(output[:,:,0:1], tf.float32) #[batch,fh,1]
        nll = Poisson_loss(mu, true)
        return nll
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}

    
class Students_NLL_Loss(tf.keras.losses.Loss):
    def __init__(self, df=3, sample_weights=False, ** kwargs):
        self.df = df
        self.sample_weights = sample_weights
        super().__init__(** kwargs)
    
    def call(self, actuals, pred):
        if self.sample_weights:
            output, wts = pred[0], pred[1]
            wts = tf.reshape(wts, [-1,]) 
        else:
            wts = 1.0
            output = pred
        true = tf.cast(actuals, tf.float32) #[batch,fh,1]
        mu = tf.cast(output[:,:,0:1], tf.float32) #[batch,fh]
        alpha = tf.cast(output[:,:,1:2], tf.float32) #[batch,fh]
        nll = Student_loss(actual, mu, std, self.df)
        return nll
    
    def get_config( self): 
        base_config = super().get_config() 
        return {** base_config}      


supported_losses = {'RMSE': ['loss_type: Point', 'Usage: RMSE(sample_weights=False)'],
                    'Huber': ['loss_type: Point', 'Usage: Huber(delta=1.0, sample_weights=False)'],
                    'Quantile': ['loss_type: Quantile', 'Usage: QuantileLoss_v2(quantiles=[0.5], sample_weights=False)'], 
                    'Normal': ['loss_type: Normal', 'Usage: Normal_NLL_Loss(sample_weights=False)'], 
                    'Poisson': ['loss_type: Poisson', 'Usage: Poisson_NLL_Loss(sample_weights=False)'],
                    'Negbin': ['loss_type: Negbin', 'Usage: Negbin_NLL_Loss(sample_weights=False)']
                   }

#print("Supported Loss Functions & Typical Usage:")
#print("-----------------------------------------")
#pprint.pprint(supported_losses)




