#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import math as m
import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
import shutil
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
import pandas as pd


# In[ ]:


# Distribution Sampling functions

# negbin
def negbin_sample(mu, alpha, n_samples=1):
    tol = 1e-5
    r = 1.0 / alpha
    theta = alpha * mu
    r = tf.minimum(tf.maximum(tol, r), 1e10)
    theta = tf.minimum(tf.maximum(tol, theta), 1e10)
    beta = 1/theta
    x = tf.minimum(tf.random.gamma(shape=[n_samples], alpha=r, beta=beta), 1e6)
    x = tf.reduce_mean(x, axis=0)
    sample = tf.stop_gradient(tf.random.poisson(shape=[n_samples],lam=x))
    sample = tf.reduce_mean(sample, axis=0)
    return sample

def negbin_multi_sample(mu, alpha, n_samples=1):
    samples = []
    for i in range(n_samples):
        samples.append(negbin_sample(mu, alpha))
    sample_spread = tf.stack(samples, axis=1) #[batch,n_samples,1]
    return tf.reduce_mean(sample_spread, axis=1)

# normal
def normal_sample(mu, std, n_samples=1):
    dist = tfd.Normal(mu,std)
    dist.reparameterization_type == tfd.FULLY_REPARAMETERIZED
    return tf.reduce_mean(dist.sample(sample_shape=n_samples), axis=0)

# student's t sample
def student_sample(df, mu, std, n_samples=1):
    dist = tfd.StudentT(df,mu,std)
    dist.reparameterization_type == tfd.FULLY_REPARAMETERIZED
    return tf.reduce_mean(dist.sample(sample_shape=n_samples), axis=0)

# Poisson
def poisson_sample(mu, n_samples=1):
    dist = tfd.Poisson(rate=mu)
    dist.reparameterization_type == tfd.FULLY_REPARAMETERIZED
    return tf.reduce_mean(dist.sample(sample_shape=n_samples), axis=0)

# Gumbel
def GumbelSample(a, b, n_samples=1):
    dist = tfd.Gumbel(loc=a, scale=b)
    return tf.reduce_mean(tf.stop_gradient(dist.sample(sample_shape=n_samples)), axis=0)


# In[ ]:


# Model Class - Dense Transformer w/ Variable Selection

# Positional Encoding

def get_angles(pos, i, d_model):
    angle_rates = 1 / np.power(10000, (2 * (i//2)) / np.float32(d_model))
    return pos * angle_rates
  
@tf.function
def positional_encoding(position, d_model):
    angle_rads = get_angles(np.arange(position)[:, np.newaxis], np.arange(d_model)[np.newaxis, :], d_model)
    # apply sin to even indices in the array; 2i
    angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
    # apply cos to odd indices in the array; 2i+1
    angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])
    pos_encoding = angle_rads[np.newaxis, ...]
    return tf.cast(pos_encoding, dtype=tf.float32)

# Mask Creation

def create_padding_mask(seq):
    seq = tf.cast(tf.math.less(seq, 0), tf.float32)
    # add extra dimensions to add the padding to the attention logits.
    return seq[:, tf.newaxis, tf.newaxis, :]  # (batch_size, 1, 1, seq_len)

def create_look_ahead_mask(size):
    mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
    return mask  # (seq_len, seq_len)
  
# Self-Attention

def scaled_dot_product_attention(q, k, v, mask):
    matmul_qk = tf.matmul(q, k, transpose_b=True)  # (..., seq_len_q, seq_len_k)
    
    # scale matmul_qk
    dk = tf.cast(tf.shape(k)[-1], tf.float32)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

    # add the mask to the scaled tensor.
    if mask is not None:
        scaled_attention_logits += (mask * -1e9)  

    # softmax is normalized on the last axis (seq_len_k) so that the scores add up to 1.
    attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)  # (..., seq_len_q, seq_len_k)

    output = tf.matmul(attention_weights, v)  # (..., seq_len_q, depth_v)

    return output, attention_weights
  
# Multi-Head Self-Attention

class MultiHeadAttention(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model
    
        assert d_model % self.num_heads == 0
    
        self.depth = d_model // self.num_heads
    
        self.wq = tf.keras.layers.Dense(d_model)
        self.wk = tf.keras.layers.Dense(d_model)
        self.wv = tf.keras.layers.Dense(d_model)
    
        self.dense = tf.keras.layers.Dense(d_model)
        
    def split_heads(self, x, batch_size):
        """
        Split the last dimension into (num_heads, depth).
        Transpose the result such that the shape is (batch_size, num_heads, seq_len, depth)
        """
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    
    def call(self, v, k, q, mask, training):
        batch_size = tf.shape(q)[0]
    
        q = self.wq(q, training=training)  # (batch_size, seq_len, d_model)
        k = self.wk(k, training=training)  # (batch_size, seq_len, d_model)
        v = self.wv(v, training=training)  # (batch_size, seq_len, d_model)
    
        q = self.split_heads(q, batch_size)  # (batch_size, num_heads, seq_len_q, depth)
        k = self.split_heads(k, batch_size)  # (batch_size, num_heads, seq_len_k, depth)
        v = self.split_heads(v, batch_size)  # (batch_size, num_heads, seq_len_v, depth)
    
        # scaled_attention.shape == (batch_size, num_heads, seq_len_q, depth)
        # attention_weights.shape == (batch_size, num_heads, seq_len_q, seq_len_k)
        scaled_attention, attention_weights = scaled_dot_product_attention(q, k, v, mask)
    
        scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])  # (batch_size, seq_len_q, num_heads, depth)

        concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))  # (batch_size, seq_len_q, d_model)

        output = self.dense(concat_attention, training=training)  # (batch_size, seq_len_q, d_model)
        
        return output, attention_weights
      
# Point-wise FFN

def point_wise_feed_forward_network(d_model, dff):
    return tf.keras.Sequential([tf.keras.layers.Dense(dff, activation='relu'),  # (batch_size, seq_len, dff)
                                tf.keras.layers.Dense(d_model)  # (batch_size, seq_len, d_model)
                               ])

# Encoder Layer

class EncoderLayer(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads, dff, rate=0.1):
        super(EncoderLayer, self).__init__()

        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = point_wise_feed_forward_network(d_model, dff)

        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)
    
    def call(self, x, mask, training):

        attn_output, _ = self.mha(x, x, x, mask, training=training)  # (batch_size, input_seq_len, d_model)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)  # (batch_size, input_seq_len, d_model)
    
        ffn_output = self.ffn(out1, training=training)  # (batch_size, input_seq_len, d_model)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(out1 + ffn_output)  # (batch_size, input_seq_len, d_model)
    
        return out2

# Decoder Layer

class DecoderLayer(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads, dff, rate=0.1):
        super(DecoderLayer, self).__init__()

        self.mha1 = MultiHeadAttention(d_model, num_heads)
        self.mha2 = MultiHeadAttention(d_model, num_heads)

        self.ffn = point_wise_feed_forward_network(d_model, dff)
 
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm3 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)
        self.dropout3 = tf.keras.layers.Dropout(rate)
    
    def call(self, x, enc_output, look_ahead_mask, padding_mask, training):
        # enc_output.shape == (batch_size, input_seq_len, d_model)

        attn1, attn_weights_block1 = self.mha1(x, x, x, look_ahead_mask, training=training)  # (batch_size, target_seq_len, d_model)
        attn1 = self.dropout1(attn1, training=training)
        out1 = self.layernorm1(attn1 + x)
    
        attn2, attn_weights_block2 = self.mha2(enc_output, enc_output, out1, padding_mask, training=training)  # (batch_size, target_seq_len, d_model)
        attn2 = self.dropout2(attn2, training=training)
        out2 = self.layernorm2(attn2 + out1)  # (batch_size, target_seq_len, d_model)
    
        ffn_output = self.ffn(out2, training=training)  # (batch_size, target_seq_len, d_model)
        ffn_output = self.dropout3(ffn_output, training=training)
        out3 = self.layernorm3(ffn_output + out2)  # (batch_size, target_seq_len, d_model)
    
        return out3, attn_weights_block1, attn_weights_block2

# Encoder Module

class Encoder(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, maximum_position_encoding, rate=0.1):
        super(Encoder, self).__init__()

        self.d_model = d_model
        self.num_layers = num_layers
    
        self.pos_encoding = positional_encoding(maximum_position_encoding, self.d_model)
    
        self.enc_layers = [EncoderLayer(d_model, num_heads, dff, rate) for _ in range(num_layers)]
  
        self.dropout = tf.keras.layers.Dropout(rate)
        
    def call(self, x, mask, training):

        seq_len = tf.shape(x)[1]
    
        # adding position encoding.
        x += self.pos_encoding[:, :seq_len, :]

        x = self.dropout(x, training=training)
    
        for i in range(self.num_layers):
            x = self.enc_layers[i](x, mask, training=training)
    
        return x  # (batch_size, input_seq_len, d_model)
    
# Encoder QR

class EncoderQR(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, rate=0):
        super(EncoderQR, self).__init__()
        self.d_model = d_model
        self.num_layers = num_layers
        self.enc_layers = [EncoderLayer(d_model, num_heads, dff, rate) for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(rate)
        
    def call(self, x, causal_mask, training):
        seq_len = tf.shape(x)[1]
        x = self.dropout(x, training=training)
        for i in range(self.num_layers):
            x = self.enc_layers[i](x, causal_mask, training=training)
    
        return x  # (batch_size, input_seq_len, d_model)

# Decoder Module

class Decoder(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, maximum_position_encoding, rate=0.1):
        super(Decoder, self).__init__()

        self.d_model = d_model
        self.num_layers = num_layers
    
        self.pos_encoding = positional_encoding(maximum_position_encoding, d_model)
    
        self.dec_layers = [DecoderLayer(d_model, num_heads, dff, rate) for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(rate)
    
    def call(self, x, enc_output, look_ahead_mask, padding_mask, training):

        seq_len = tf.shape(x)[1]
        attention_weights = {}
    
        x += self.pos_encoding[:, :seq_len, :]
    
        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x, block1, block2 = self.dec_layers[i](x, enc_output, look_ahead_mask, padding_mask, training=training)
      
        attention_weights['decoder_layer{}_block1'.format(i+1)] = block1
        attention_weights['decoder_layer{}_block2'.format(i+1)] = block2
    
        # x.shape == (batch_size, target_seq_len, d_model)
        return x, attention_weights

# Decoder QR
class DecoderQR(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, rate=0):
        super(DecoderQR, self).__init__()
        self.d_model = d_model
        self.num_layers = num_layers
        self.dec_layers = [DecoderLayer(d_model, num_heads, dff, rate) for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(rate)
    
    def call(self, x, enc_output, look_ahead_mask, padding_mask, training):
        seq_len = tf.shape(x)[1]
        attention_weights = {}
        x = self.dropout(x, training=training)
        for i in range(self.num_layers):
            x, block1, block2 = self.dec_layers[i](x, enc_output, look_ahead_mask, padding_mask, training=training)
        attention_weights['decoder_layer{}_block1'.format(i+1)] = block1
        attention_weights['decoder_layer{}_block2'.format(i+1)] = block2
    
        # x.shape == (batch_size, target_seq_len, d_model)
        return x, attention_weights

# GRN & Gating

class linear_layer(tf.keras.layers.Layer):
    def __init__(self, size, activation=None, use_time_distributed=False, use_bias=True):
        super(linear_layer, self).__init__()
        self.linear = tf.keras.layers.Dense(size, activation=activation, use_bias=use_bias)
        if use_time_distributed:
            self.linear = tf.keras.layers.TimeDistributed(self.linear)
    
    def call(self,inputs, training):
        return self.linear(inputs, training=training)
    

class apply_gating_layer(tf.keras.layers.Layer):
    def __init__(self, hidden_layer_size, dropout_rate=None, use_time_distributed=True, activation=None):
        super(apply_gating_layer, self).__init__()
        self.dropout = tf.keras.layers.Dropout(dropout_rate)
        if use_time_distributed:
            self.activation_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(hidden_layer_size, activation=activation))
            self.gated_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(hidden_layer_size, activation='sigmoid'))
        else:
            self.activation_layer = tf.keras.layers.Dense(hidden_layer_size, activation=activation)
            self.gated_layer = tf.keras.layers.Dense(hidden_layer_size, activation='sigmoid')
    
    def call(self, inputs, training):
        x = self.dropout(inputs, training=training)
        a = self.activation_layer(x, training=training)
        g = self.gated_layer(x, training=training)
        return tf.keras.layers.Multiply()([a, g]), g
           
def add_and_norm(x_list):
    tmp = tf.keras.layers.Add()(x_list)
    tmp = tf.keras.layers.LayerNormalization()(tmp)
    return tmp

class add_norm_layer(tf.keras.layers.Layer):
    def __init__(self):
        super(add_norm_layer, self).__init__()
        self.add_layer = tf.keras.layers.Add()
        self.norm_layer = tf.keras.layers.LayerNormalization()
        
    def call(self, inputs, training):
        x = self.add_layer(inputs)
        x = self.norm_layer(x)
        return x
    
class gated_residual_network(tf.keras.layers.Layer):
    def __init__(self, hidden_layer_size, output_size=None, dropout_rate=None, use_time_distributed=True, 
                 additional_context=False, return_gate=False):
        super(gated_residual_network, self).__init__()
        
        self.hidden_layer_size = hidden_layer_size
        if output_size is None:
            self.output_size = hidden_layer_size
        else: 
            self.output_size = output_size
        if use_time_distributed:
            self.linear = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(self.output_size))
        else:
            self.linear = tf.keras.layers.Dense(self.output_size)
        self.additional_context = additional_context
        self.return_gate = return_gate
        self.hidden_1 = linear_layer(hidden_layer_size, activation=None, use_time_distributed=use_time_distributed)
        if additional_context:
            self.context = linear_layer(hidden_layer_size, activation=None, use_time_distributed=use_time_distributed, use_bias=False)
        self.hidden_2 = linear_layer(hidden_layer_size, activation=None, use_time_distributed=use_time_distributed)
        self.gate = apply_gating_layer(self.output_size, dropout_rate=dropout_rate, use_time_distributed=use_time_distributed, activation=None)
        self.add_norm = add_norm_layer()
    
    def call(self, inputs, training):
        
        if self.additional_context:
            x,c = inputs
            skip = self.linear(x, training=training)
            hidden = self.hidden_1(x, training=training)
            hidden = hidden + self.context(c, training=training)
            hidden = tf.keras.layers.Activation('elu')(hidden)
            hidden = self.hidden_2(hidden, training=training)
        else:
            x = inputs
            skip = self.linear(x, training=training)
            hidden = self.hidden_1(x, training=training)
            hidden = tf.keras.layers.Activation('elu')(hidden)
            hidden = self.hidden_2(hidden, training=training)
        
        gating_layer, gate = self.gate(hidden, training=training)
        if self.return_gate:
            grn_out, g = self.add_norm([skip, gating_layer], training), gate
            return grn_out, g
        else:
            grn_out = self.add_norm([skip, gating_layer], training)
            return grn_out
    
    
# Variable selection networks

class static_variable_selection_layer(tf.keras.layers.Layer):
    """
    Takes inputs as a list of embedded/linear transformed tensors
    """
    def __init__(self, hidden_layer_size, output_size, dropout_rate):
        super(static_variable_selection_layer, self).__init__()
        self.hidden_layer_size = hidden_layer_size
        self.output_size = output_size
        self.dropout_rate = dropout_rate
      
    def build(self, input_shape):
        self.num_static = len(input_shape) 
        self.grn_var = [gated_residual_network(self.hidden_layer_size, 
                                               self.output_size, 
                                               self.dropout_rate, 
                                               use_time_distributed=False, 
                                               additional_context=False, 
                                               return_gate=False) for _ in range(self.num_static)]
        
        self.grn_flat = gated_residual_network(self.hidden_layer_size, 
                                               self.num_static, 
                                               self.dropout_rate, 
                                               use_time_distributed=False, 
                                               additional_context=False, 
                                               return_gate=False)
        
    def call(self, inputs, training):
        flatten = tf.concat(inputs, axis=1) #[batch, sum_of_var_dims]
        mlp_outputs = self.grn_flat(flatten, training=training)
        
        static_weights = tf.keras.layers.Activation('softmax')(mlp_outputs) #[batch,num_static]
        weights = tf.expand_dims(static_weights, axis=-1) #[batch,num_static,1]
        
        trans_emb_list = []
        for i in range(self.num_static):
            e = self.grn_var[i](inputs[i], training=training)
            trans_emb_list.append(e)
        
        trans_embedding = tf.stack(trans_emb_list, axis=1) #[batch,num_static,hidden_layer_size]
        
        combined = tf.keras.layers.Multiply()([weights, trans_embedding])
        static_vec = tf.reduce_sum(combined, axis=1)
        
        return static_vec, static_weights

    
class static_contexts(tf.keras.layers.Layer):
    """
    Takes static_vec as input
    """
    def __init__(self, hidden_layer_size, output_size, dropout_rate):
        super(static_contexts, self).__init__()
        self.static_context_variable_selection = gated_residual_network(hidden_layer_size, 
                                                                        output_size, 
                                                                        dropout_rate, 
                                                                        use_time_distributed=False, 
                                                                        additional_context=False, 
                                                                        return_gate=False)
    def call(self, inputs, training):
        static_var_select_vec = self.static_context_variable_selection(inputs, training=training)
        return static_var_select_vec
      
class static_enrichment_layer(tf.keras.layers.Layer):
    def __init__(self, hidden_layer_size, dropout_rate):
        super(static_enrichment_layer, self).__init__()

        self.hidden_layer_size = hidden_layer_size
        self.dropout_rate = dropout_rate
        self.grn_enrich = gated_residual_network(hidden_layer_size=self.hidden_layer_size,
                                                 output_size=None,
                                                 dropout_rate=self.dropout_rate,
                                                 use_time_distributed=True,
                                                 additional_context=True,
                                                 return_gate=False)
    def call(self,inputs, training):
        # inputs: [temporal_features, static_enrichment_vec]
        x,c = inputs
        c = tf.expand_dims(c, axis=1)
        enriched = self.grn_enrich([x,c], training=training)
        return enriched
      
class lstm_init_states(tf.keras.layers.Layer):
    """
    Takes static_vec as input
    """
    def __init__(self, hidden_layer_size, output_size, dropout_rate):
        super(lstm_init_states, self).__init__()
        
        self.init_h = gated_residual_network(hidden_layer_size, 
                                             output_size, 
                                             dropout_rate, 
                                             use_time_distributed=False, 
                                             additional_context=False,                            
                                             return_gate=False)
        self.init_c = gated_residual_network(hidden_layer_size, 
                                             output_size, 
                                             dropout_rate, 
                                             use_time_distributed=False, 
                                             additional_context=False,                            
                                             return_gate=False)
    def call(self, inputs, training):
        init_h = self.init_h(inputs, training=training)
        init_c = self.init_c(inputs, training=training)
        return init_h, init_c
    

class temporal_variable_selection_layer(tf.keras.layers.Layer):
    """
    Takes inputs as a list of list of embedded/linear transformed tensors of shape [batch,time_steps,emb_dim] & context vec
    """
    def __init__(self, hidden_layer_size, output_size, context, dropout_rate):
        super(temporal_variable_selection_layer, self).__init__()
        
        self.hidden_layer_size = hidden_layer_size
        self.output_size = output_size
        self.context = context
        self.dropout_rate = dropout_rate
  
    def build(self, input_shape):
        if self.context:
            self.num_vars = len(input_shape[0]) 
        else:
            self.num_vars = len(input_shape)
          
        self.grn_var = [gated_residual_network(self.hidden_layer_size, 
                                               self.output_size, 
                                               self.dropout_rate, 
                                               use_time_distributed=True, 
                                               additional_context=False, 
                                               return_gate=False) for _ in range(self.num_vars)]
        
        self.grn_flat = gated_residual_network(self.hidden_layer_size, 
                                               self.num_vars, 
                                               self.dropout_rate, 
                                               use_time_distributed=True, 
                                               additional_context=self.context, 
                                               return_gate=False)
        
    def call(self, x, training):
        if self.context:
            inputs, context = x
            context = tf.expand_dims(context, axis=1)
            flatten = tf.concat(inputs, axis=-1) #[batch,time_steps,sum_of_var_dims]
            mlp_outputs = self.grn_flat([flatten,context], training=training) #[batch,time_steps,num_vars]
        else:
            inputs = x
            flatten = tf.concat(inputs, axis=-1) #[batch,time_steps,sum_of_var_dims]
            mlp_outputs = self.grn_flat(flatten, training=training) #[batch,time_steps,num_vars]
        
        dynamic_weights = tf.keras.layers.TimeDistributed(tf.keras.layers.Activation('softmax'))(mlp_outputs) #[batch,time_steps,num_vars]
        #weights = tf.expand_dims(dynamic_weights, axis=2) #[batch,time_steps,1,num_vars]
        weights = tf.expand_dims(dynamic_weights, axis=-1) #[batch,time_steps,num_vars,1]
        
        trans_emb_list = []
        for i in range(self.num_vars):
            e = self.grn_var[i](inputs[i], training=training)
            trans_emb_list.append(e)
        
        #trans_embedding = tf.stack(trans_emb_list, axis=-1) #[batch,time_steps,hidden_layer_size,num_vars]
        trans_embedding = tf.stack(trans_emb_list, axis=2) #[batch,time_steps,num_vars,hidden_layer_size]
        
        combined = tf.keras.layers.Multiply()([weights, trans_embedding])
        #tfr_input = tf.reduce_sum(combined, axis=-1) #[batch,time_steps,hidden_layers_size]
        tfr_input = tf.reduce_sum(combined, axis=2) #[batch,time_steps,hidden_layers_size]
        
        return tfr_input, dynamic_weights
      
class all_variable_select_concat_layer(tf.keras.layers.Layer):
    def __init__(self, hidden_layer_size, output_size, dropout_rate):
        super(all_variable_select_concat_layer, self).__init__()
        
        self.hidden_layer_size = hidden_layer_size
        self.output_size = output_size
        self.dropout_rate = dropout_rate
  
    def build(self, input_shape):
        self.num_vars = len(input_shape)  
        self.grn_var = [gated_residual_network(self.hidden_layer_size, 
                                               self.output_size, 
                                               self.dropout_rate, 
                                               use_time_distributed=True, 
                                               additional_context=False, 
                                               return_gate=False) for _ in range(self.num_vars)]
        self.grn_flat = gated_residual_network(self.hidden_layer_size, 
                                               self.num_vars, 
                                               self.dropout_rate, 
                                               use_time_distributed=True, 
                                               additional_context=False, 
                                               return_gate=False)
    
        
    def call(self, inputs, training):
        flatten = tf.concat(inputs, axis=-1) #[batch,time_steps,sum_of_var_dims]
        mlp_outputs = self.grn_flat(flatten, training=training) #[batch,time_steps,num_vars]
        dynamic_weights = tf.keras.layers.TimeDistributed(tf.keras.layers.Activation('softmax'))(mlp_outputs) #[batch,time_steps,num_vars]
        weights = tf.expand_dims(dynamic_weights, axis=-1) #[batch,time_steps,num_vars,1]
        
        trans_emb_list = []
        for i in range(self.num_vars):
            e = self.grn_var[i](inputs[i], training=training)
            trans_emb_list.append(e)
        
        trans_embedding = tf.stack(trans_emb_list, axis=2) #[batch,time_steps,num_vars,hidden_layer_size]
        
        combined = tf.keras.layers.Multiply()([weights, trans_embedding]) #[batch,time_steps,num_vars,hidden_layer_size]
        batch_size, timesteps = tf.shape(combined)[0], tf.shape(combined)[1]
        tfr_input = tf.reshape(combined, [batch_size, timesteps, -1]) #[batch,time_steps,hidden_layers_size]
        
        return tfr_input, dynamic_weights   


# In[ ]:


# Variable Weighted Transformer Model

class VarTransformer(tf.keras.Model):
    def __init__(self,
                 static_variables,
                 num_layers,
                 d_model,
                 num_heads, 
                 dff,
                 hist_len, 
                 f_len,
                 loss_fn,
                 num_quantiles=1,
                 rate=0.1):
        super(VarTransformer, self).__init__()
        
        self.hist_len = hist_len
        self.f_len = f_len
        self.loss_fn = loss_fn
        self.stat_variables = static_variables
    
        self.encoder = Encoder(num_layers, d_model, num_heads, dff, hist_len, rate)
        self.decoder = Decoder(num_layers, d_model, num_heads, dff, f_len, rate)
        
        if self.stat_variables:
            self.static_input_layer = static_variable_selection_layer(hidden_layer_size=d_model, output_size=None, dropout_rate=rate)
            self.static_context_layer = static_contexts(hidden_layer_size=d_model, output_size=None, dropout_rate=rate)
            self.static_enrich_layer = static_contexts(hidden_layer_size=d_model, output_size=None, dropout_rate=rate)
            self.encoder_enrich = add_norm_layer()
            self.decoder_enrich = add_norm_layer()
        
        self.encoder_input_layer = temporal_variable_selection_layer(hidden_layer_size=d_model, output_size=None, context=self.stat_variables, dropout_rate=rate)
        self.decoder_input_layer = temporal_variable_selection_layer(hidden_layer_size=d_model, output_size=None, context=self.stat_variables, dropout_rate=rate)
        
        if self.loss_fn == 'Point':
            self.final_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1))
        elif self.loss_fn == 'Poisson':
            self.final_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
        elif self.loss_fn == 'Quantile':
            self.quantile_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=num_quantiles))
        elif self.loss_fn == 'Normal':
            self.m_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1))
            self.s_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
        elif self.loss_fn == 'Negbin':
            self.m_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
            self.a_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
        else:
            raise ValueError("Invalid Loss Function!")
        
    def call(self, inputs, training):
        '''
        shapes:
        static_vars_list: [TensorShape(batch,stat_var1_dim),TensorShape(batch,stat_var2_dim),...]
        encoder_vars_list: [TensorShape(batch, hist_timesteps, enc_var1_dim),...]
        decoder_vars_list: [TensorShape(batch, fh_timesteps, dec_var1_dim),...]
        mask: TensorShape(batch,hist+fh_timesteps,1)
        scale: TensorShape(batch,1,1)
        '''
        if self.stat_variables:
            static_vars_list, encoder_vars_list, decoder_vars_list, mask, scale = inputs
        else:
            encoder_vars_list, decoder_vars_list, mask, scale = inputs
        
        # scale
        scale = scale[:,-1:,:]
        
        # static var selection 
        if self.stat_variables:
            static_vec, static_weights = self.static_input_layer(static_vars_list, training=training)
            context = self.static_context_layer(static_vec, training=training)
            static_enrichment_vec = self.static_enrich_layer(static_vec, training=training)
            static_enrichment_vec = tf.expand_dims(static_enrichment_vec, axis=1)
            # enc input prep
            input_d, encoder_weights = self.encoder_input_layer([encoder_vars_list, context], training=training)
            input_d = self.encoder_enrich([input_d, static_enrichment_vec])
            # dec input prep
            target_d, decoder_weights = self.decoder_input_layer([decoder_vars_list, context], training=training)
            target_d = self.decoder_enrich([target_d, static_enrichment_vec])
        else:
            static_weights = None
            input_d, encoder_weights = self.encoder_input_layer(encoder_vars_list, training=training)
            target_d, decoder_weights = self.decoder_input_layer(decoder_vars_list, training=training)
          
        # Encoder
        padding_mask = create_padding_mask(mask[:,:self.hist_len,0])
        enc_output = self.encoder(input_d, padding_mask, training=training)  # (batch_size, inp_seq_len, d_model)
        
        # Decoder
        look_ahead_mask = create_look_ahead_mask(self.f_len)
        dec_output, _ = self.decoder(target_d, enc_output, look_ahead_mask, padding_mask, training=training)
        
        if self.loss_fn == 'Point':
            out = self.final_layer(dec_output, training=training)
        elif self.loss_fn == 'Poisson':
            mean = self.final_layer(dec_output, training=training)*scale
            parameters = mean
            out = poisson_sample(mu=mean)
        elif self.loss_fn == 'Quantile':
            out = self.quantile_layer(dec_output, training=training)
        elif self.loss_fn == 'Normal':
            mean = self.m_layer(dec_output, training=training)*scale       # (batch, f_len, 1)
            stddev = self.s_layer(dec_output, training=training)*scale      # (batch, f_len, 1)
            parameters = tf.concat([mean, stddev], axis=-1)
            out = normal_sample(mean, stddev)
        elif self.loss_fn == 'Negbin':
            mean = self.m_layer(dec_output, training=training)*scale       # (batch, f_len, 1)
            alpha = self.a_layer(dec_output, training=training)*tf.sqrt(scale)      # (batch, f_len, 1)
            parameters = tf.concat([mean, alpha], axis=-1)
            out = negbin_sample(mean, alpha)
        else:
            raise ValueError('Invalid Loss Function.')
        
        if self.loss_fn == 'Point' or self.loss_fn == 'Quantile':
            return out, scale, static_weights, encoder_weights, decoder_weights
        else:
            return out, parameters, static_weights, encoder_weights, decoder_weights


# In[ ]:


# Transformer Base Model

class Transformer(tf.keras.Model):
    def __init__(self,
                 num_layers,
                 d_model,
                 num_heads, 
                 dff, 
                 hist_len, 
                 f_len,
                 loss_fn,
                 num_quantiles=1,
                 rate=0.1):
        super(Transformer, self).__init__()
        
        self.hist_len = hist_len
        self.loss_fn = loss_fn
        
        self.encoder = Encoder(num_layers, d_model, num_heads, dff, hist_len, rate)

        self.decoder = Decoder(num_layers, d_model, num_heads, dff, f_len, rate)
        
        self.encoder_input_layer = tf.keras.layers.Conv1D(filters=d_model, kernel_size=1, strides=1, use_bias=False)
        
        self.decoder_input_layer = tf.keras.layers.Conv1D(filters=d_model, kernel_size=1, strides=1, use_bias=False)
        
        if self.loss_fn == 'Point':
            self.final_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=num_quantiles, activation=None))
        elif self.loss_fn == 'Binary':
            self.final_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='sigmoid'))
        elif self.loss_fn == 'Poisson':
            self.final_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
        elif self.loss_fn == 'Quantile':
            self.quantile_layers = [tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation=None)) 
                                    for _ in range(num_quantiles)]
        elif self.loss_fn == 'Normal':
            self.m_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1))
            self.s_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
        elif self.loss_fn == 'Negbin':
            self.m_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
            self.a_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=1, activation='softplus'))
        else:
            raise ValueError('Specifiy supported loss function.')
    
    def call(self, inputs, training): 
        encoder_vars, decoder_vars, enc_padding_mask, scale = inputs
        scale = scale[:,-1:,:]
        
        input_d = self.encoder_input_layer(encoder_vars, training=training)
        
        enc_output = self.encoder(input_d, enc_padding_mask, training=training)  # (batch_size, inp_seq_len, d_model)
        
        look_ahead_mask = create_look_ahead_mask(tf.shape(decoder_vars)[1])
        
        target_d = self.decoder_input_layer(decoder_vars, training=training)
        
        dec_output, _ = self.decoder(target_d, enc_output, look_ahead_mask, enc_padding_mask, training=training)
        
        if self.loss_fn == 'Point':
            out = self.final_layer(dec_output, training=training)
        elif self.loss_fn == 'Binary':
            out = self.final_layer(dec_output, training=training)
        elif self.loss_fn == 'Poisson':
            mean = self.final_layer(dec_output, training=training)*scale
            parameters = mean
            out = poisson_sample(mu=mean)
        elif self.loss_fn == 'Normal':
            mean = self.m_layer(dec_output, training=training)*scale       # (batch, f_len, 1)
            stddev = self.s_layer(dec_output, training=training)*scale      # (batch, f_len, 1)
            parameters = tf.concat([mean, stddev], axis=-1)
            out = normal_sample(mean, stddev)
        elif self.loss_fn == 'Negbin':
            mean = self.m_layer(dec_output, training=training)*scale       # (batch, f_len, 1)
            alpha = self.a_layer(dec_output, training=training)*tf.sqrt(scale)      # (batch, f_len, 1)
            parameters = tf.concat([mean, alpha], axis=-1)
            out = negbin_sample(mean, alpha)
        elif self.loss_fn == 'Quantile':
            output = []
            for i in range(len(self.quantile_layers)):
                out = self.quantile_layers[i](dec_output, training=training)
                output.append(out)
            out = tf.concat(output, axis=-1)
          
        if self.loss_fn == 'Point' or self.loss_fn == 'Binary' or self.loss_fn == 'Quantile':
            return out, scale
        else:
            return out, parameters


# In[ ]:


# Transformer Wrapper

class Transformer_Model(tf.keras.Model):
    def __init__(self,
                 col_index_dict,
                 vocab_dict,
                 num_layers,
                 num_heads,
                 d_model,
                 forecast_horizon,
                 max_inp_len,
                 loss_type,
                 dropout_rate=0.1):
        """
        col_index_dict: A dictionary with struct {'colgroup_indices': [column names list, column indices list]}
        vocab_dict: A dictionary with struct {'colgroup_indices': [col names list, vocab list per col, list of indices]}
        num_layers: No.of Multiheaded Self-Attention Layers for Encoder & Decoder
        num_heads: No.of Heads used in Self-Attention layer. It should be a divisor of 'd_model'
        d_model: Model dimension. Should be a multiple of num_heads
        forecast_horizon: No. of periods ahead of the forecast cut-off period (Point at which forecast is generated)
        max_inp_len: Max. no. of periods before the forecast cut-off period
        loss_type: One of ['Point','Quantile','Normal','Poisson','Negbin']
        num_quantiles: Only required if 
        quantiles:
        dropout_rate:
        learning_rate:
        
        """
        super(Transformer_Model, self).__init__()

        self.hist_len = int(max_inp_len)
        self.f_len = int(forecast_horizon)
        self.loss_type = loss_type
        self.col_index_dict = col_index_dict
        self.decoder_lags = max(int(self.hist_len/4), 2)
        
        self.model = Transformer(num_layers=num_layers,
                                 d_model=d_model,
                                 num_heads=num_heads,
                                 dff=int(2*d_model),
                                 hist_len=max_inp_len,
                                 f_len=forecast_horizon,
                                 loss_fn=loss_type,
                                 num_quantiles=1,
                                 rate=dropout_rate)

        # Create static cat embedding layers
        self.stat_col_details = vocab_dict.get('static_cat_indices', None)
        if self.stat_col_details:
            self.stat_lookup_tables = {}
            self.stat_embed_layers = {}
            stat_col_names = self.stat_col_details[0]
            stat_col_vocab = self.stat_col_details[1]
            stat_col_emb_dim = self.stat_col_details[2]
            for i,(colname, values, emb) in enumerate(zip(stat_col_names, stat_col_vocab, stat_col_emb_dim)):
                values = tf.convert_to_tensor(values, dtype=tf.string)
                cat_indices = tf.range(len(values), dtype = tf.int64)
                cat_init = tf.lookup.KeyValueTensorInitializer(values, cat_indices)
                cat_lookup_table = tf.lookup.StaticVocabularyTable(cat_init, 1)
                self.stat_lookup_tables[colname] = cat_lookup_table
                self.stat_embed_layers[colname] = tf.keras.layers.Embedding(input_dim = len(values) + 1, 
                                                                            output_dim = emb,
                                                                            name = "embedding_layer_{}".format(colname))
        # Create temporal known cat embedding layers
        self.temporal_known_col_details = vocab_dict.get('temporal_known_cat_indices', None)
        if self.temporal_known_col_details:
            self.temporal_known_lookup_tables = {}
            self.temporal_known_embed_layers = {}
            temporal_known_col_names = self.temporal_known_col_details[0]
            temporal_known_col_vocab = self.temporal_known_col_details[1]
            temporal_known_col_emb_dim = self.temporal_known_col_details[2]
            for i,(colname, values, emb) in enumerate(zip(temporal_known_col_names, temporal_known_col_vocab, temporal_known_col_emb_dim)):
                values = tf.convert_to_tensor(values, dtype=tf.string)
                cat_indices = tf.range(len(values), dtype = tf.int64)
                cat_init = tf.lookup.KeyValueTensorInitializer(values, cat_indices)
                cat_lookup_table = tf.lookup.StaticVocabularyTable(cat_init, 1)
                self.temporal_known_lookup_tables[colname] = cat_lookup_table
                self.temporal_known_embed_layers[colname] = tf.keras.layers.Embedding(input_dim = len(values) + 1, 
                                                                                      output_dim = emb,
                                                                                      name = "embedding_layer_{}".format(colname))
        # Create temporal unknown cat embedding layers
        self.temporal_unknown_col_details = vocab_dict.get('temporal_unknown_cat_indices', None)
        if self.temporal_unknown_col_details:
            self.temporal_unknown_lookup_tables = {}
            self.temporal_unknown_embed_layers = {}
            temporal_unknown_col_names = self.temporal_unknown_col_details[0]
            temporal_unknown_col_vocab = self.temporal_unknown_col_details[1]
            temporal_unknown_col_emb_dim = self.temporal_unknown_col_details[2]
            for i,(colname, values, emb)in enumerate(zip(temporal_unknown_col_names, temporal_unknown_col_vocab, temporal_unknown_col_emb_dim)):
                values = tf.convert_to_tensor(values, dtype=tf.string)
                cat_indices = tf.range(len(values), dtype = tf.int64)
                cat_init = tf.lookup.KeyValueTensorInitializer(values, cat_indices)
                cat_lookup_table = tf.lookup.StaticVocabularyTable(cat_init, 1)
                self.temporal_unknown_lookup_tables[colname] = cat_lookup_table
                self.temporal_unknown_embed_layers[colname] = tf.keras.layers.Embedding(input_dim = len(values) + 1, 
                                                                                        output_dim = emb,
                                                                                        name = "embedding_layer_{}".format(colname))
         
        # Obtain col names & col positions in the input tensor
        self.target_col_name, self.target_index = self.col_index_dict.get('target_index')
        self.stat_num_col_names, self.stat_num_indices = self.col_index_dict.get('static_num_indices')
        self.stat_cat_col_names, self.stat_cat_indices = self.col_index_dict.get('static_cat_indices')
        self.known_num_col_names, self.known_num_indices = self.col_index_dict.get('temporal_known_num_indices')
        self.unknown_num_col_names, self.unknown_num_indices = self.col_index_dict.get('temporal_unknown_num_indices')
        self.known_cat_col_names, self.known_cat_indices = self.col_index_dict.get('temporal_known_cat_indices')
        self.unknown_cat_col_names, self.unknown_cat_indices = self.col_index_dict.get('temporal_unknown_cat_indices')
        
    def call(self, inputs, training):
        
        # target
        target = tf.strings.to_number(inputs[:,:,self.target_index:self.target_index+1], out_type=tf.dtypes.float32)
        
        # encoder, decoder tensors
        encoder_tensor = target[:,:self.hist_len,:]
        
        # decoder start token -- multiple lags
        decoder_tensor = target[:,self.hist_len-1:self.hist_len-1+self.f_len,:]
        for i in range(2, self.decoder_lags+1):
            decoder_tensor = tf.concat([decoder_tensor, target[:,self.hist_len-i:self.hist_len-i+self.f_len,:]], axis=-1)
        
        # static numeric
        if len(self.stat_num_indices)>0:
            for col, i in zip(self.stat_num_col_names, self.stat_num_indices):
                stat_var = tf.strings.to_number(inputs[:,:,i:i+1], out_type=tf.dtypes.float32)
                # encoder tensor
                encoder_tensor = tf.concat([encoder_tensor, stat_var[:,:self.hist_len,:]], axis=-1)
                # decoder tensor
                decoder_tensor = tf.concat([decoder_tensor, stat_var[:,-self.f_len:,:]], axis=-1)
                
        # known numeric 
        if len(self.known_num_indices)>0:
            for col, i in zip(self.known_num_col_names, self.known_num_indices):
                num_vars = tf.strings.to_number(inputs[:,:,i:i+1], out_type=tf.dtypes.float32)
                # encoder
                encoder_tensor = tf.concat([encoder_tensor, num_vars[:,:self.hist_len,:]], axis=-1)
                # decoder
                decoder_tensor = tf.concat([decoder_tensor, num_vars[:,-self.f_len:,:]], axis=-1)
        
        # unknown numeric
        if len(self.unknown_num_indices)>0:
            for col, i in zip(self.unknown_num_col_names, self.unknown_num_indices):
                num_vars = tf.strings.to_number(inputs[:,:,i:i+1], out_type=tf.dtypes.float32)
                # encoder
                encoder_tensor = tf.concat([encoder_tensor, num_vars[:,:self.hist_len,:]], axis=-1)
                     
        # static embeddings
        if len(self.stat_cat_indices)>0:
            for col, i in zip(self.stat_cat_col_names, self.stat_cat_indices):
                stat_var = inputs[:,:,i]
                stat_var_id = self.stat_lookup_tables.get(col).lookup(stat_var)
                stat_var_embeddings = self.stat_embed_layers.get(col)(stat_var_id)
                # encoder tensor
                encoder_tensor = tf.concat([encoder_tensor, stat_var_embeddings[:,:self.hist_len,:]], axis=-1)
                # decoder tensor
                decoder_tensor = tf.concat([decoder_tensor, stat_var_embeddings[:,-self.f_len:,:]], axis=-1)
        
        # known embeddings
        if len(self.known_cat_indices)>0:
            for col, i in zip(self.known_cat_col_names, self.known_cat_indices):
                cat_var = inputs[:,:,i]
                cat_var_id = self.temporal_known_lookup_tables.get(col).lookup(cat_var)
                cat_var_embeddings = self.temporal_known_embed_layers.get(col)(cat_var_id)
                # encoder tensor
                encoder_tensor = tf.concat([encoder_tensor, cat_var_embeddings[:,:self.hist_len,:]], axis=-1)
                # decoder tensor
                decoder_tensor = tf.concat([decoder_tensor, cat_var_embeddings[:,-self.f_len:,:]], axis=-1)
        
        # unknown embeddings
        if len(self.unknown_cat_indices)>0:
            for col, i in zip(self.unknown_cat_col_names, self.unknown_cat_indices):
                cat_var = inputs[:,:,i]
                cat_var_id = self.temporal_unknown_lookup_tables.get(col).lookup(cat_var)
                cat_var_embeddings = self.temporal_unknown_embed_layers.get(col)(cat_var_id)
                # encoder tensor
                encoder_tensor = tf.concat([encoder_tensor, cat_var_embeddings[:,:self.hist_len,:]], axis=-1)
                          
        # rel_age
        rel_age = tf.strings.to_number(inputs[:,:,-3:-2], out_type=tf.dtypes.float32)
        # encoder
        encoder_tensor = tf.concat([encoder_tensor, rel_age[:,:self.hist_len,:]], axis=-1)
        # decoder
        decoder_tensor = tf.concat([decoder_tensor, rel_age[:,-self.f_len:,:]], axis=-1)   
        
        # scale
        scale = tf.strings.to_number(inputs[:,:,-2:-1], out_type=tf.dtypes.float32)
        scale_log = tf.math.log(tf.math.sqrt(scale))
        # encoder
        encoder_tensor = tf.concat([encoder_tensor, scale_log[:,:self.hist_len,:]], axis=-1)
        # decoder
        decoder_tensor = tf.concat([decoder_tensor, scale_log[:,-self.f_len:,:]], axis=-1)   
        
        # mask
        mask = tf.strings.to_number(inputs[:,:,-1:], out_type=tf.dtypes.float32)
        padding_mask = create_padding_mask(mask[:,:self.hist_len,0])
        
        # model process
        o, s = self.model([encoder_tensor, decoder_tensor, padding_mask, scale], training=training)
         
        return o, s
    
    
def Transformer_Train(model, 
                      train_dataset, 
                      test_dataset, 
                      loss_type,
                      loss_function, 
                      metric, 
                      learning_rate,
                      max_epochs, 
                      min_epochs,
                      train_steps_per_epoch,
                      test_steps_per_epoch,
                      patience,
                      weighted_training,
                      model_prefix,
                      logdir):
    """
     train_dataset, test_dataset: tf.data.Dataset iterator for train & test datasets 
     loss_type: One of ['Point','Quantile','Normal','Poisson','Negbin']
     loss_function: One of the supported loss functions in loss library
     metric: 'MAE' or 'MSE' 
     max_epochs: Max. training epochs
     min_epochs: Min. Training epochs
     *_steps_per_epoch: batches per epoch 
     weighted_training: True/False
     model_prefix: relative or absolute model path with a prefix for a model name
     logdir: tensorflow training logs for tensorboard
        
    """
    
    def trainstep(model, optimizer, x_train, y_train, scale, wts, training):
        with tf.GradientTape() as tape:
            o, s = model(x_train, training=training)
            out_len = tf.shape(s)[1]
            if loss_type in ['Normal','Poisson','Negbin']:
                if weighted_training:
                    loss = loss_function(y_train*scale[:,-out_len:,:], [s, wts])
                else:
                    loss = loss_function(y_train*scale[:,-out_len:,:], s)                           
            elif loss_type in ['Point']:
                if weighted_training:                               
                    loss = loss_function(y_train, [o, wts])
                else:
                    loss = loss_function(y_train, o)
            elif loss_type in ['Quantile']:
                if weighted_training:                               
                    loss = loss_function(y_train, [o, wts])
                else:
                    loss = loss_function(y_train, o)                                   
            else:
                raise ValueError("Invalid loss_type specified!")
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients((grad, var) for (grad, var) in zip(grads, model.trainable_variables) if grad is not None)
        return loss, o
    
    def teststep(model, x_test, y_test, scale, wts, training):
        o, s = model(x_test, training=training)
        out_len = tf.shape(s)[1]
        if loss_type in ['Normal','Poisson','Negbin']:
            if weighted_training:
                loss = loss_function(y_test*scale[:,-out_len:,:], [s, wts])
            else:
                loss = loss_function(y_test*scale[:,-out_len:,:], s)                           
        elif loss_type in ['Point']:
            if weighted_training:                               
                loss = loss_function(y_test, [o, wts])
            else:
                loss = loss_function(y_test, o)
        elif loss_type in ['Quantile']:
            if weighted_training:                               
                loss = loss_function(y_test, [o, wts])
            else:
                loss = loss_function(y_test, o)                                   
        else:
            raise ValueError("Invalid loss_type specified!")        
        return loss, o
       
    # training specific vars
    optimizer = tf.keras.optimizers.Nadam(learning_rate=learning_rate)
        
    # model loss & metric
    train_loss_avg = tf.keras.metrics.Mean('train_loss', dtype=tf.float32)
    test_loss_avg = tf.keras.metrics.Mean('test_loss', dtype=tf.float32)

    if metric == 'MAE':  
        train_metric = tf.keras.metrics.MeanAbsoluteError('train_mae')
        test_metric = tf.keras.metrics.MeanAbsoluteError('test_mae')
    elif metric == 'MSE':
        train_metric = tf.keras.metrics.MeanSquaredError('train_mse')
        test_metric = tf.keras.metrics.MeanSquaredError('test_mse')
    else:
        raise ValueError("{}: Not a Supported Metric".format(metric))
            
    #logging
    train_log_dir = str(logdir).rstrip('/') +'/train'
    test_log_dir = str(logdir).rstrip('/')+'/test'
    train_summary_writer = tf.summary.create_file_writer(train_log_dir)
    test_summary_writer = tf.summary.create_file_writer(test_log_dir)
        
    # hold results
    train_loss_results = []
    train_metric_results = []
    test_loss_results = []
    test_metric_results = []
        
    # initialize model tracking vars
    model_list = []
    best_model = None
    time_since_improvement = 0
        
    # train loop
    for epoch in range(max_epochs):
        print("Epoch {}/{}". format(epoch, max_epochs)) 
        for step, (x_batch, y_batch, scale, wts) in enumerate(train_dataset):
            if step > train_steps_per_epoch:
                break
            else:
                train_loss, train_out = trainstep(model, optimizer, x_batch, y_batch, scale, wts, training=True)
                out_len = tf.shape(train_out)[1]
                train_loss_avg.update_state(train_loss)
                if loss_type in ['Normal','Poisson','Negbin']:
                    train_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], train_out)
                elif loss_type in ['Point','Quantile']:
                    train_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], train_out*scale[:,-out_len:,:])
                with train_summary_writer.as_default():
                    tf.summary.scalar('loss', train_loss_avg.result(), step=epoch)
                    tf.summary.scalar('accuracy', train_metric.result(), step=epoch)
          
        for step, (x_batch, y_batch, scale, wts) in enumerate(test_dataset):
            if step > train_steps_per_epoch:
                break
            else:
                test_loss, test_out = teststep(model, x_batch, y_batch, scale, wts, training=False)
                out_len = tf.shape(test_out)[1]
                test_loss_avg.update_state(test_loss)
                if loss_type in ['Normal','Poisson','Negbin']:
                    test_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], test_out)
                elif loss_type in ['Point','Quantile']:
                    test_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], test_out*scale[:,-out_len:,:])
                with test_summary_writer.as_default():
                    tf.summary.scalar('loss', test_loss_avg.result(), step=epoch)
                    tf.summary.scalar('accuracy', test_metric.result(), step=epoch)
              
        print("Epoch: {}, train_loss: {}, test_loss: {}, train_metric: {}, test_metric: {}".format(epoch, 
                                                                                                    train_loss_avg.result().numpy(),
                                                                                                    test_loss_avg.result().numpy(),
                                                                                                    train_metric.result().numpy(),
                                                                                                    test_metric.result().numpy()))
    
        # record losses & metric in lists
        train_loss_results.append(train_loss_avg.result().numpy())
        train_metric_results.append(train_metric.result().numpy())
        test_loss_results.append(test_loss_avg.result().numpy())
        test_metric_results.append(test_metric.result().numpy())
            
        # reset states
        train_loss_avg.reset_states()
        train_metric.reset_states()
        test_loss_avg.reset_states()
        test_metric.reset_states()
        
        # Save Model
        model_path = model_prefix + '_' + str(epoch) 
        tf.keras.models.save_model(model, model_path)
        model_list.append(model_path)
            
        # track best model
        if test_loss_results[epoch]==np.min(test_loss_results):
            best_model = model_path
            # reset time_since_improvement
            time_since_improvement = 0
        else:
            time_since_improvement += 1
            
        # remove older models
        if len(model_list)>patience:
            for m in model_list[:-patience]:
                if m != best_model:
                    try:
                        shutil.rmtree(m)
                    except:
                        pass
                
        print("Best Model: ", best_model)
        if (time_since_improvement > patience) and (epoch > min_epochs):
            print("Terminating Training. Best Model path: {}".format(best_model))
            break
    
    return best_model
    
    
def Transformer_Infer(model, inputs, loss_type, hist_len, f_len, target_index):
    infer_tensor, scale, id_arr, date_arr = inputs
    scale = scale[:,-1:,-1]
    window_len = int(hist_len + f_len)
    output = []
        
    for i in range(f_len):
        print("Forecasting Period: ", i+1)
        out, dist = model(infer_tensor, training=False)
            
        # update target
        if loss_type in ['Normal','Poisson','Negbin']:
            dist = dist.numpy()
            output.append(dist[:,i:i+1,0])
            infer_arr = infer_tensor.numpy()
            infer_arr[:,hist_len:hist_len+i+1,target_index] = out[:,0:i+1,0]/scale
        elif loss_type in ['Point','Quantile']:
            out = out.numpy()
            output.append(out[:,i:i+1,0])
            infer_arr = infer_tensor.numpy()
            infer_arr[:,hist_len:hist_len+i+1,target_index] = out[:,0:i+1,0]
            
        # feedback updated hist + fh tensor
        infer_tensor = tf.convert_to_tensor(infer_arr.astype(str), dtype=tf.string)
            
    output_arr = np.concatenate(output, axis=1) 
        
    # rescale if necessary
    if loss_type in ['Normal','Poisson','Negbin']:
        output_df = pd.DataFrame(np.concatenate((id_arr.reshape(-1,1),output_arr), axis=1))
    elif loss_type in ['Point','Quantile']:
        output_df = pd.DataFrame(np.concatenate((id_arr.reshape(-1,1),output_arr*scale.reshape(-1,1)), axis=1))
    output_df = output_df.melt(id_vars=0).sort_values(0).drop(columns=['variable']).rename(columns={0:'id','value':'forecast'})
    output_df = output_df.rename_axis('index').sort_values(by=['id','index']).reset_index(drop=True)
        
    # merge date_columns
    date_df = pd.DataFrame(date_arr.reshape(-1,)).rename(columns={0:'period'})
    forecast_df = pd.concat([date_df, output_df], axis=1)
    forecast_df['forecast'] = forecast_df['forecast'].astype(np.float32)
        
    return forecast_df


# In[ ]:


class Simple_Transformer:
    def __init__(self, 
                 col_index_dict,
                 vocab_dict,
                 num_layers,
                 num_heads,
                 d_model,
                 forecast_horizon,
                 max_inp_len,
                 loss_type,
                 dropout_rate):
        
        self.col_index_dict = col_index_dict
        self.vocab_dict = vocab_dict
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.d_model = d_model
        self.forecast_horizon = forecast_horizon
        self.max_inp_len = max_inp_len
        self.loss_type = loss_type
        self.dropout_rate = dropout_rate
        self.target_col_name, self.target_index = self.col_index_dict.get('target_index')
    
    def build(self):
        tf.keras.backend.clear_session()
        self.model = Transformer_Model(self.col_index_dict,
                                  self.vocab_dict,
                                  self.num_layers,
                                  self.num_heads,
                                  self.d_model,
                                  self.forecast_horizon,
                                  self.max_inp_len,
                                  self.loss_type,
                                  self.dropout_rate)
        
    def train(self, 
              train_dataset, 
              test_dataset,
              loss_function, 
              metric, 
              learning_rate,
              max_epochs, 
              min_epochs,
              train_steps_per_epoch,
              test_steps_per_epoch,
              patience,
              weighted_training,
              model_prefix,
              logdir):
        
        # Initialize Weights
        for x,y,s,w in train_dataset.take(1):
            self.model(x, training=False)
        
        best_model = Transformer_Train(self.model, 
                                       train_dataset, 
                                       test_dataset, 
                                       self.loss_type,
                                       loss_function, 
                                       metric, 
                                       learning_rate,
                                       max_epochs, 
                                       min_epochs,
                                       train_steps_per_epoch,
                                       test_steps_per_epoch,
                                       patience,
                                       weighted_training,
                                       model_prefix,
                                       logdir)
        return best_model
    
    def load(self, model_path):
        tf.keras.backend.clear_session()
        self.model = tf.keras.models.load_model(model_path)
        
    def infer(self, inputs):
        forecast = Transformer_Infer(self.model, inputs, self.loss_type, self.max_inp_len, self.forecast_horizon, self.target_index)
        
        return forecast
    
    def evaluate(self, forecasts, actuals, aggregate_on=[]):
        
        results_df = actuals.merge(forecasts, on=['id','period'], how='inner')
        
        assert results_df.shape[0] == forecasts.shape[0], "forecasts & actuals dataframes dissimilar!"
        
        results_df['abs_error'] = np.abs(results_df['forecast'] - results_df['actual'])
        results_df = results_df.groupby(['period']+aggregate_on).agg({'forecast':'sum', 'actual':'sum', 'abs_error':'sum'}).reset_index(drop=True)
        
        # FA & FB
        results_df['Forecast_Accuracy'] = (1 - results_df['abs_error']/np.maximum(results_df['actual'], 1.0))*100
        results_df['Forecast_Bias'] = (results_df['forecast']/np.maximum(results_df['actual'],1.0) - 1)*100
        
        return results_df
        
                


# In[ ]:


# VarTransformer Wrapper

class VarTransformer_Model(tf.keras.Model):
    def __init__(self,
                 col_index_dict,
                 vocab_dict,
                 num_layers,
                 num_heads,
                 d_model,
                 forecast_horizon,
                 max_inp_len,
                 loss_type,
                 dropout_rate):

        super(VarTransformer_Model, self).__init__()

        self.hist_len = int(max_inp_len)
        self.f_len = int(forecast_horizon)
        self.loss_type = loss_type
        self.col_index_dict = col_index_dict
        self.decoder_lags = max(int(self.hist_len/4), 2)
        
        if (len(self.col_index_dict.get('static_num_indices')[0])==0) and (len(self.col_index_dict.get('static_cat_indices')[0])==0):
            self.static_variables = False
        else:
            self.static_variables = True
        
        self.model = VarTransformer(static_variables = self.static_variables,
                                    num_layers = num_layers,
                                    d_model = d_model,
                                    num_heads = num_heads, 
                                    dff = int(2*d_model),
                                    hist_len = self.hist_len, 
                                    f_len = self.f_len,
                                    loss_fn = self.loss_type,
                                    num_quantiles = 1,
                                    rate = dropout_rate)
        
        # Create static cat embedding layers
        self.stat_col_details = vocab_dict.get('static_cat_indices', None)
        if self.stat_col_details:
            self.stat_lookup_tables = {}
            self.stat_embed_layers = {}
            stat_col_names = self.stat_col_details[0]
            stat_col_vocab = self.stat_col_details[1]
            stat_col_emb_dim = self.stat_col_details[2]
            for i,(colname, values, emb) in enumerate(zip(stat_col_names, stat_col_vocab, stat_col_emb_dim)):
                values = tf.convert_to_tensor(values, dtype=tf.string)
                cat_indices = tf.range(len(values), dtype = tf.int64)
                cat_init = tf.lookup.KeyValueTensorInitializer(values, cat_indices)
                cat_lookup_table = tf.lookup.StaticVocabularyTable(cat_init, 1)
                self.stat_lookup_tables[colname] = cat_lookup_table
                self.stat_embed_layers[colname] = tf.keras.layers.Embedding(input_dim = len(values) + 1, 
                                                                            output_dim = emb,
                                                                            name = "embedding_layer_{}".format(colname))
        # Create temporal known cat embedding layers
        self.temporal_known_col_details = vocab_dict.get('temporal_known_cat_indices', None)
        if self.temporal_known_col_details:
            self.temporal_known_lookup_tables = {}
            self.temporal_known_embed_layers = {}
            temporal_known_col_names = self.temporal_known_col_details[0]
            temporal_known_col_vocab = self.temporal_known_col_details[1]
            temporal_known_col_emb_dim = self.temporal_known_col_details[2]
            for i,(colname, values, emb) in enumerate(zip(temporal_known_col_names, temporal_known_col_vocab, temporal_known_col_emb_dim)):
                values = tf.convert_to_tensor(values, dtype=tf.string)
                cat_indices = tf.range(len(values), dtype = tf.int64)
                cat_init = tf.lookup.KeyValueTensorInitializer(values, cat_indices)
                cat_lookup_table = tf.lookup.StaticVocabularyTable(cat_init, 1)
                self.temporal_known_lookup_tables[colname] = cat_lookup_table
                self.temporal_known_embed_layers[colname] = tf.keras.layers.Embedding(input_dim = len(values) + 1, 
                                                                                      output_dim = emb,
                                                                                      name = "embedding_layer_{}".format(colname))
        # Create temporal unknown cat embedding layers
        self.temporal_unknown_col_details = vocab_dict.get('temporal_unknown_cat_indices', None)
        if self.temporal_unknown_col_details:
            self.temporal_unknown_lookup_tables = {}
            self.temporal_unknown_embed_layers = {}
            temporal_unknown_col_names = self.temporal_unknown_col_details[0]
            temporal_unknown_col_vocab = self.temporal_unknown_col_details[1]
            temporal_unknown_col_emb_dim = self.temporal_unknown_col_details[2]
            for i,(colname, values, emb) in enumerate(zip(temporal_unknown_col_names, temporal_unknown_col_vocab, temporal_unknown_col_emb_dim)):
                values = tf.convert_to_tensor(values, dtype=tf.string)
                cat_indices = tf.range(len(values), dtype = tf.int64)
                cat_init = tf.lookup.KeyValueTensorInitializer(values, cat_indices)
                cat_lookup_table = tf.lookup.StaticVocabularyTable(cat_init, 1)
                self.temporal_unknown_lookup_tables[colname] = cat_lookup_table
                self.temporal_unknown_embed_layers[colname] = tf.keras.layers.Embedding(input_dim = len(values) + 1, 
                                                                                        output_dim = emb,
                                                                                        name = "embedding_layer_{}".format(colname))
        
        # columns names & indices
        self.target_col_name, self.target_index = self.col_index_dict.get('target_index')
        self.stat_num_col_names, self.stat_num_indices = self.col_index_dict.get('static_num_indices')
        self.stat_cat_col_names, self.stat_cat_indices = self.col_index_dict.get('static_cat_indices')
        self.known_num_col_names, self.known_num_indices = self.col_index_dict.get('temporal_known_num_indices')
        self.unknown_num_col_names, self.unknown_num_indices = self.col_index_dict.get('temporal_unknown_num_indices')
        self.known_cat_col_names, self.known_cat_indices = self.col_index_dict.get('temporal_known_cat_indices')
        self.unknown_cat_col_names, self.unknown_cat_indices = self.col_index_dict.get('temporal_unknown_cat_indices')
        
        # Create Numerical Embedding (Linear Transform) Layers
        
        self.target_linear_transform_layer = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=d_model, use_bias=False)) 
        self.scale_linear_transform_layer = tf.keras.layers.Dense(units=d_model, use_bias=False)
        
        self.decoderlag_linear_transform_layers = {}
        for i in range(2, self.decoder_lags+1):
            colname = "{}_lag_{}".format(self.target_col_name,i)
            self.decoderlag_linear_transform_layers[colname] = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=d_model, use_bias=False)) 
            
        if len(self.stat_num_col_names)>0:
            self.stat_linear_transform_layers = {}
            for colname in self.stat_num_col_names:
                self.stat_linear_transform_layers[colname] = tf.keras.layers.Dense(units=d_model, use_bias=False)
        
        if len(self.known_num_col_names)>0:
            self.known_linear_transform_layers = {}
            for colname in self.known_num_col_names + ['rel_age']:
                self.known_linear_transform_layers[colname] = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=d_model, use_bias=False))
        
        if len(self.unknown_num_col_names)>0:
            self.unknown_linear_transform_layers = {}
            for colname in self.unknown_num_col_names + ['rel_age']:
                self.unknown_linear_transform_layers[colname] = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(units=d_model, use_bias=False))
                
    def call(self, inputs, training):
        
        # target
        target = tf.strings.to_number(inputs[:,:,self.target_index:self.target_index+1], out_type=tf.dtypes.float32)
        target = self.target_linear_transform_layer(target)
        
        # ordered col names list
        stat_cols_ordered_list = []
        past_cols_ordered_list = []
        future_cols_ordered_list = []
        
        # stat, encoder, decoder tensor lists
        static_vars_list = []
        encoder_vars_list = [target[:,:self.hist_len,:]]
        decoder_vars_list = [target[:,self.hist_len-1:self.hist_len-1+self.f_len,:]]
        
        past_cols_ordered_list = past_cols_ordered_list + [self.target_col_name]
        future_cols_ordered_list = future_cols_ordered_list + [self.target_col_name]
        
        # decoder start token
        for i in range(2, self.decoder_lags+1):
            dec_lag_var = target[:,self.hist_len-i:self.hist_len-i+self.f_len,:]
            dec_lag_var = self.decoderlag_linear_transform_layers["{}_lag_{}".format(self.target_col_name,i)](dec_lag_var)
            decoder_vars_list.append(dec_lag_var)
            future_cols_ordered_list = future_cols_ordered_list + ["{}_lag_{}".format(self.target_col_name,i)]
        
        # static numeric
        if len(self.stat_num_indices)>0:
            stat_cols_ordered_list = stat_cols_ordered_list + self.stat_num_col_names
            for col, i in zip(self.stat_num_col_names, self.stat_num_indices):
                stat_var = tf.strings.to_number(inputs[:,-1,i:i+1], out_type=tf.dtypes.float32)
                stat_var = self.stat_linear_transform_layers[col](stat_var)
                # append
                static_vars_list.append(stat_var)
        
        # static embeddings
        if len(self.stat_cat_indices)>0:
            stat_cols_ordered_list = stat_cols_ordered_list + self.stat_cat_col_names
            for col, i in zip(self.stat_cat_col_names, self.stat_cat_indices):
                stat_var = inputs[:,:,i]
                stat_var_id = self.stat_lookup_tables.get(col).lookup(stat_var)
                stat_var_embeddings = self.stat_embed_layers.get(col)(stat_var_id)
                # append
                static_vars_list.append(stat_var_embeddings[:,-1,:])
                
        # known numeric 
        if len(self.known_num_indices)>0:
            past_cols_ordered_list = past_cols_ordered_list + self.known_num_col_names
            future_cols_ordered_list = future_cols_ordered_list + self.known_num_col_names
            for col, i in zip(self.known_num_col_names, self.known_num_indices):
                num_vars = tf.strings.to_number(inputs[:,:,i:i+1], out_type=tf.dtypes.float32)
                num_vars = self.known_linear_transform_layers[col](num_vars)
                # append
                encoder_vars_list.append(num_vars[:,:self.hist_len,:])
                decoder_vars_list.append(num_vars[:,-self.f_len:,:])
        
        # unknown numeric
        if len(self.unknown_num_indices)>0:
            past_cols_ordered_list = past_cols_ordered_list + self.unknown_num_col_names
            for col, i in zip(self.unknown_num_col_names, self.unknown_num_indices):
                num_vars = tf.strings.to_number(inputs[:,:,i:i+1], out_type=tf.dtypes.float32)
                num_vars = self.unknown_linear_transform_layers[col](num_vars)
                # append
                encoder_vars_list.append(num_vars[:,:self.hist_len,:])
                     
        # known embeddings
        if len(self.known_cat_indices)>0:
            past_cols_ordered_list = past_cols_ordered_list + self.known_cat_col_names
            future_cols_ordered_list = future_cols_ordered_list + self.known_cat_col_names
            for col, i in zip(self.known_cat_col_names, self.known_cat_indices):
                cat_var = inputs[:,:,i]
                cat_var_id = self.temporal_known_lookup_tables.get(col).lookup(cat_var)
                cat_var_embeddings = self.temporal_known_embed_layers.get(col)(cat_var_id)
                # append
                encoder_vars_list.append(cat_var_embeddings[:,:self.hist_len,:])
                decoder_vars_list.append(cat_var_embeddings[:,-self.f_len:,:])
        
        # unknown embeddings
        if len(self.unknown_cat_indices)>0:
            past_cols_ordered_list = past_cols_ordered_list + self.unknown_cat_col_names
            for col, i in zip(self.unknown_cat_col_names, self.unknown_cat_indices):
                cat_var = inputs[:,:,i]
                cat_var_id = self.temporal_unknown_lookup_tables.get(col).lookup(cat_var)
                cat_var_embeddings = self.temporal_unknown_embed_layers.get(col)(cat_var_id)
                # append
                encoder_vars_list.append(cat_var_embeddings[:,:self.hist_len,:])
                          
        # rel_age
        rel_age = tf.strings.to_number(inputs[:,:,-3:-2], out_type=tf.dtypes.float32)
        rel_age_enc = self.known_linear_transform_layers['rel_age'](rel_age[:,:self.hist_len,:])
        rel_age_dec = self.unknown_linear_transform_layers['rel_age'](rel_age[:,-self.f_len:,:])
        # append
        encoder_vars_list.append(rel_age_enc)
        decoder_vars_list.append(rel_age_dec)
        
        # scale
        scale = tf.strings.to_number(inputs[:,:,-2:-1], out_type=tf.dtypes.float32)
        scale_log = tf.math.log(tf.math.sqrt(scale))
        scale_log = self.scale_linear_transform_layer(scale_log[:,-1,:])
        # append
        static_vars_list.append(scale_log)
        
        # Append additional columns
        stat_cols_ordered_list = stat_cols_ordered_list + ['scale']
        past_cols_ordered_list = past_cols_ordered_list + ['rel_age']
        future_cols_ordered_list = future_cols_ordered_list + ['rel_age']
        
        # mask
        mask = tf.strings.to_number(inputs[:,:,-1:], out_type=tf.dtypes.float32)
        
        # model process
        if self.static_variables:
            o, s, s_wts, p_wts, f_wts = self.model([static_vars_list, encoder_vars_list, decoder_vars_list, mask, scale], training=training)
        else:
            o, s, s_wts, p_wts, f_wts = self.model([encoder_vars_list, decoder_vars_list, mask, scale], training=training)
        
        # Average feature weights across time dim
        p_wts = tf.reduce_mean(p_wts, axis=1)
        f_wts = tf.reduce_mean(f_wts, axis=1)
              
        return o, s, ([stat_cols_ordered_list,past_cols_ordered_list,future_cols_ordered_list], [s_wts, p_wts, f_wts])
    
    
def VarTransformer_Train(model, 
                      train_dataset, 
                      test_dataset, 
                      loss_type,
                      loss_function, 
                      metric, 
                      learning_rate,
                      max_epochs, 
                      min_epochs,
                      train_steps_per_epoch,
                      test_steps_per_epoch,
                      patience,
                      weighted_training,
                      model_prefix,
                      logdir):
    """
     train_dataset, test_dataset: tf.data.Dataset iterator for train & test datasets 
     loss_type: One of ['Point','Quantile','Normal','Poisson','Negbin']
     loss_function: One of the supported loss functions in loss library
     metric: 'MAE' or 'MSE' 
     max_epochs: Max. training epochs
     min_epochs: Min. Training epochs
     *_steps_per_epoch: batches per epoch 
     weighted_training: True/False
     model_prefix: relative or absolute model path with a prefix for a model name
     logdir: tensorflow training logs for tensorboard
        
    """
    
    def trainstep(model, optimizer, x_train, y_train, scale, wts, training):
        with tf.GradientTape() as tape:
            o, s, f = model(x_train, training=training)
            out_len = tf.shape(s)[1]
            if loss_type in ['Normal','Poisson','Negbin']:
                if weighted_training:
                    loss = loss_function(y_train*scale[:,-out_len:,:], [s, wts])
                else:
                    loss = loss_function(y_train*scale[:,-out_len:,:], s)                           
            elif loss_type in ['Point']:
                if weighted_training:                               
                    loss = loss_function(y_train, [o, wts])
                else:
                    loss = loss_function(y_train, o)
            elif loss_type in ['Quantile']:
                if weighted_training:                               
                    loss = loss_function(y_train, [o, wts])
                else:
                    loss = loss_function(y_train, o)                                   
            else:
                raise ValueError("Invalid loss_type specified!")
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients((grad, var) for (grad, var) in zip(grads, model.trainable_variables) if grad is not None)
        return loss, o
    
    def teststep(model, x_test, y_test, scale, wts, training):
        o, s, f = model(x_test, training=training)
        out_len = tf.shape(s)[1]
        if loss_type in ['Normal','Poisson','Negbin']:
            if weighted_training:
                loss = loss_function(y_test*scale[:,-out_len:,:], [s, wts])
            else:
                loss = loss_function(y_test*scale[:,-out_len:,:], s)                           
        elif loss_type in ['Point']:
            if weighted_training:                               
                loss = loss_function(y_test, [o, wts])
            else:
                loss = loss_function(y_test, o)
        elif loss_type in ['Quantile']:
            if weighted_training:                               
                loss = loss_function(y_test, [o, wts])
            else:
                loss = loss_function(y_test, o)                                   
        else:
            raise ValueError("Invalid loss_type specified!")        
        return loss, o
       
    # training specific vars
    optimizer = tf.keras.optimizers.Nadam(learning_rate=learning_rate)
        
    # model loss & metric
    train_loss_avg = tf.keras.metrics.Mean('train_loss', dtype=tf.float32)
    test_loss_avg = tf.keras.metrics.Mean('test_loss', dtype=tf.float32)

    if metric == 'MAE':  
        train_metric = tf.keras.metrics.MeanAbsoluteError('train_mae')
        test_metric = tf.keras.metrics.MeanAbsoluteError('test_mae')
    elif metric == 'MSE':
        train_metric = tf.keras.metrics.MeanSquaredError('train_mse')
        test_metric = tf.keras.metrics.MeanSquaredError('test_mse')
    else:
        raise ValueError("{}: Not a Supported Metric".format(metric))
            
    #logging
    train_log_dir = str(logdir).rstrip('/') +'/train'
    test_log_dir = str(logdir).rstrip('/')+'/test'
    train_summary_writer = tf.summary.create_file_writer(train_log_dir)
    test_summary_writer = tf.summary.create_file_writer(test_log_dir)
        
    # hold results
    train_loss_results = []
    train_metric_results = []
    test_loss_results = []
    test_metric_results = []
        
    # initialize model tracking vars
    model_list = []
    best_model = None
    time_since_improvement = 0
        
    # train loop
    for epoch in range(max_epochs):
        print("Epoch {}/{}". format(epoch, max_epochs)) 
        for step, (x_batch, y_batch, scale, wts) in enumerate(train_dataset):
            if step > train_steps_per_epoch:
                break
            else:
                train_loss, train_out = trainstep(model, optimizer, x_batch, y_batch, scale, wts, training=True)
                out_len = tf.shape(train_out)[1]
                train_loss_avg.update_state(train_loss)
                if loss_type in ['Normal','Poisson','Negbin']:
                    train_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], train_out)
                elif loss_type in ['Point','Quantile']:
                    train_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], train_out*scale[:,-out_len:,:])
                with train_summary_writer.as_default():
                    tf.summary.scalar('loss', train_loss_avg.result(), step=epoch)
                    tf.summary.scalar('accuracy', train_metric.result(), step=epoch)
          
        for step, (x_batch, y_batch, scale, wts) in enumerate(test_dataset):
            if step > train_steps_per_epoch:
                break
            else:
                test_loss, test_out = teststep(model, x_batch, y_batch, scale, wts, training=False)
                out_len = tf.shape(test_out)[1]
                test_loss_avg.update_state(test_loss)
                if loss_type in ['Normal','Poisson','Negbin']:
                    test_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], test_out)
                elif loss_type in ['Point','Quantile']:
                    test_metric.update_state(y_batch[:,-out_len:,:]*scale[:,-out_len:,:], test_out*scale[:,-out_len:,:])
                with test_summary_writer.as_default():
                    tf.summary.scalar('loss', test_loss_avg.result(), step=epoch)
                    tf.summary.scalar('accuracy', test_metric.result(), step=epoch)
              
        print("Epoch: {}, train_loss: {}, test_loss: {}, train_metric: {}, test_metric: {}".format(epoch, 
                                                                                                    train_loss_avg.result().numpy(),
                                                                                                    test_loss_avg.result().numpy(),
                                                                                                    train_metric.result().numpy(),
                                                                                                    test_metric.result().numpy()))
    
        # record losses & metric in lists
        train_loss_results.append(train_loss_avg.result().numpy())
        train_metric_results.append(train_metric.result().numpy())
        test_loss_results.append(test_loss_avg.result().numpy())
        test_metric_results.append(test_metric.result().numpy())
            
        # reset states
        train_loss_avg.reset_states()
        train_metric.reset_states()
        test_loss_avg.reset_states()
        test_metric.reset_states()
        
        # Save Model
        model_path = model_prefix + '_' + str(epoch) 
        tf.keras.models.save_model(model, model_path)
        model_list.append(model_path)
            
        # track best model
        if test_loss_results[epoch]==np.min(test_loss_results):
            best_model = model_path
            # reset time_since_improvement
            time_since_improvement = 0
        else:
            time_since_improvement += 1
            
        # remove older models
        if len(model_list)>patience:
            for m in model_list[:-patience]:
                if m != best_model:
                    try:
                        shutil.rmtree(m)
                    except:
                        pass
                
        print("Best Model: ", best_model)
        if (time_since_improvement > patience) and (epoch > min_epochs):
            print("Terminating Training. Best Model path: {}".format(best_model))
            break
    
    return best_model
        
def VarTransformer_Infer(model, inputs, loss_type, hist_len, f_len, target_index):
    infer_tensor, scale, id_arr, date_arr = inputs
    scale = scale[:,-1:,-1]
    window_len = hist_len + f_len
    output = []
    stat_wts_df = None 
    encoder_wts_df = None 
    decoder_wts_df = None
        
    for i in range(f_len):
        print("Forecasting Period: ", i+1)
        out, dist, feature_wts = model(infer_tensor, training=False)
            
        # update target
        if loss_type in ['Normal','Poisson','Negbin']:
            dist = dist.numpy()
            output.append(dist[:,i:i+1,0])
            infer_arr = infer_tensor.numpy()
            infer_arr[:,hist_len:hist_len+i+1,target_index] = out[:,0:i+1,0]/scale
        elif loss_type in ['Point','Quantile']:
            out = out.numpy()
            output.append(out[:,i:i+1,0])
            infer_arr = infer_tensor.numpy()
            infer_arr[:,hist_len:hist_len+i+1,target_index] = out[:,0:i+1,0]
            
        # feedback updated hist + fh tensor
        infer_tensor = tf.convert_to_tensor(infer_arr.astype(str), dtype=tf.string)
            
        if i == (f_len - 1):
            column_names_list, wts_list = feature_wts
            stat_columns, encoder_columns, decoder_columns = column_names_list
            stat_columns_string = []
            encoder_columns_string = []
            decoder_columns_string = []
            for col in stat_columns:
                stat_columns_string.append(col.numpy().decode("utf-8")) 
            for col in encoder_columns:
                encoder_columns_string.append(col.numpy().decode("utf-8"))
            for col in decoder_columns:
                decoder_columns_string.append(col.numpy().decode("utf-8"))
                
            stat_wts, encoder_wts, decoder_wts = wts_list
            # Average feature weights across time dim
            encoder_wts = encoder_wts.numpy()
            decoder_wts = decoder_wts.numpy()
            # convert wts to df    
            encoder_wts_df = pd.DataFrame(encoder_wts, columns=encoder_columns_string)   
            decoder_wts_df = pd.DataFrame(decoder_wts, columns=decoder_columns_string)    
            if stat_wts is not None:
                stat_wts = stat_wts.numpy()
                stat_wts_df = pd.DataFrame(stat_wts, columns=stat_columns_string)   
            
    output_arr = np.concatenate(output, axis=1) 
        
    # rescale if necessary
    if loss_type in ['Normal','Poisson','Negbin']:
        output_df = pd.DataFrame(np.concatenate((id_arr.reshape(-1,1),output_arr), axis=1))
    elif loss_type in ['Point','Quantile']:
        output_df = pd.DataFrame(np.concatenate((id_arr.reshape(-1,1),output_arr*scale.reshape(-1,1)), axis=1))
    output_df = output_df.melt(id_vars=0).sort_values(0).drop(columns=['variable']).rename(columns={0:'id','value':'forecast'})
    output_df = output_df.rename_axis('index').sort_values(by=['id','index']).reset_index(drop=True)
        
    # merge date_columns
    date_df = pd.DataFrame(date_arr.reshape(-1,)).rename(columns={0:'period'})
    forecast_df = pd.concat([date_df, output_df], axis=1)
    forecast_df['forecast'] = forecast_df['forecast'].astype(np.float32)
        
    # weights df merge with id
    stat_wts_df = pd.concat([pd.DataFrame(id_arr.reshape(-1,1)), stat_wts_df], axis=1)
    encoder_wts_df = pd.concat([pd.DataFrame(id_arr.reshape(-1,1)), encoder_wts_df], axis=1)
    decoder_wts_df = pd.concat([pd.DataFrame(id_arr.reshape(-1,1)), decoder_wts_df], axis=1)
    print(stat_wts_df.shape, encoder_wts_df.shape, decoder_wts_df.shape)
        
    return forecast_df, stat_wts_df, encoder_wts_df, decoder_wts_df


# In[ ]:


class Feature_Weighted_Transformer:
    def __init__(self, 
                 col_index_dict,
                 vocab_dict,
                 num_layers,
                 num_heads,
                 d_model,
                 forecast_horizon,
                 max_inp_len,
                 loss_type,
                 dropout_rate):
        
        self.col_index_dict = col_index_dict
        self.vocab_dict = vocab_dict
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.d_model = d_model
        self.forecast_horizon = forecast_horizon
        self.max_inp_len = max_inp_len
        self.loss_type = loss_type
        self.dropout_rate = dropout_rate
        self.target_col_name, self.target_index = self.col_index_dict.get('target_index')
    
    def build(self):
        tf.keras.backend.clear_session()
        self.model = VarTransformer_Model(self.col_index_dict,
                                  self.vocab_dict,
                                  self.num_layers,
                                  self.num_heads,
                                  self.d_model,
                                  self.forecast_horizon,
                                  self.max_inp_len,
                                  self.loss_type,
                                  self.dropout_rate)
        
    def train(self, 
              train_dataset, 
              test_dataset,
              loss_function, 
              metric, 
              learning_rate,
              max_epochs, 
              min_epochs,
              train_steps_per_epoch,
              test_steps_per_epoch,
              patience,
              weighted_training,
              model_prefix,
              logdir):
        
        # Initialize Weights
        for x,y,s,w in train_dataset.take(1):
            self.model(x, training=False)
        
        best_model = VarTransformer_Train(self.model, 
                                          train_dataset, 
                                          test_dataset, 
                                          self.loss_type,
                                          loss_function, 
                                          metric, 
                                          learning_rate,
                                          max_epochs, 
                                          min_epochs,
                                          train_steps_per_epoch,
                                          test_steps_per_epoch,
                                          patience,
                                          weighted_training,
                                          model_prefix,
                                          logdir)
        return best_model
    
    def load(self, model_path):
        tf.keras.backend.clear_session()
        self.model = tf.keras.models.load_model(model_path)
        
    def infer(self, inputs):
        forecast, stat_wts_df, encoder_wts_df, decoder_wts_df = VarTransformer_Infer(self.model, inputs, self.loss_type, self.max_inp_len, self.forecast_horizon, self.target_index)
        
        return forecast, [stat_wts_df, encoder_wts_df, decoder_wts_df]
        
    def evaluate(self, forecasts, actuals, aggregate_on=[]):
        
        results_df = actuals.merge(forecasts, on=['id','period'], how='inner')
        
        assert results_df.shape[0] == forecasts.shape[0], "forecasts & actuals dataframes dissimilar!"
        
        results_df['abs_error'] = np.abs(results_df['forecast'] - results_df['actual'])
        results_df = results_df.groupby(['period']+aggregate_on).agg({'forecast':'sum', 'actual':'sum', 'abs_error':'sum'}).reset_index()
        
        # FA & FB
        results_df['Forecast_Accuracy'] = (1 - results_df['abs_error']/np.maximum(results_df['actual'], 1.0))*100
        results_df['Forecast_Bias'] = (results_df['forecast']/np.maximum(results_df['actual'],1.0) - 1)*100
        
        return results_df
    

