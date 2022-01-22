__env__ = '''Envs]
    Python 3.9.7 64-bit(conda 4.11.0)
    macOS 12.1
'''
__version__ = '''Version]
    version 0.01(beta)
'''
__doc__ = '''\
This module contains various Deep Learning models.
''' + __env__+__version__

from ..layers.layers import CPatches, CPatchEncoder, CRandomSampling, TransformerBlock, CMaskToken, CPosEncoder, CDownsample, CUpsample
from tensorflow.keras.layers import Input, Dense, Add, LayerNormalization, Reshape, Permute, GlobalAveragePooling1D
from tensorflow.keras.models import Model
import tensorflow as tf
from ..losses.gan_loss import generator_loss, discriminator_loss

# Masked Auto Encoder(MAE) model
def mae_model(input_shape, img_h, img_w, patch_size=40, mask_ratio=0.75, d_model=32, d_decoder=32, dff=128, dff_decoder=128, num_heads=4, drop=0.1, N_e=3, N_d=1):
    # --------------- Embeddnig -------------------
    input = Input(shape=input_shape)
    x = CPatches(patch_size) (input)
    num_patches = int(img_h*img_w//(patch_size*patch_size))
    x = CPatchEncoder(num_patches, d_model) (x)
    
    random_sampler = CRandomSampling(num_patches, mask_ratio=mask_ratio)
    x, mask_indices, un_masked_indices = random_sampler (x)

    # ----------------- Encoder -------------------
    for _ in range(N_e):
        x = TransformerBlock(num_heads=num_heads, mlp_dim=dff, dropout=drop) (x) 
    mst = CMaskToken()
    x = mst (x, mask_indices, un_masked_indices )

    # -------------- Positional Embedding -------------------
    x = CPosEncoder(x.shape[1], d_model) (x)  
    x = Dense(units=d_decoder) (x)
    # ----------------- Decoder -------------------
    for _ in range(N_d):
        x = TransformerBlock(num_heads=num_heads, mlp_dim=dff_decoder, dropout=drop) (x)
    x = Dense(units=patch_size*patch_size*3) (x)
    model = Model(inputs=input, outputs=x)
    return model


# MLP-Mixer model
def mlp_mixer_model(sequence_len=14, C=6, d_model = 1024, N=13, Ds=1042, Dc=12):
    input = Input(shape=(sequence_len, ))
    
    # Embedding Layes -----------------------------------
    x = Dense(units=d_model*C, activation='gelu') (input)
    x = Reshape((C, -1))(x)
    x = Dense(units=d_model) (x)
    x = Permute((2, 1)) (x)
    #----------------------------------------------------
    for i in range(N):
        x_in = x
        x = LayerNormalization() (x_in)
        x = Permute((2, 1)) (x)
        # -------------Token Mixing------
        MLP1 = Dense(units=Ds, activation='gelu')
        lin1 = Dense(units=d_model)
    
        x = MLP1 (x)
        x = lin1 (x)
    
        x = Permute((2, 1)) (x)
        x = Add() ([x, x_in])
        # ---------Channel Mixing--------
        x_in = x
        x = LayerNormalization() (x)

        MLP2 = Dense(units=Dc, activation='gelu')
        lin2 = Dense(units=C)
    
        x = MLP2 (x)
        x = lin2 (x)
    
        x = Add() ([x, x_in])
  
    x = Permute((2, 1)) (x)
  
    x = GlobalAveragePooling1D() (x)
    x = Dense(units=45*60*2) (x)
    out = Reshape((45, 60, 2)) (x)

    model = Model(inputs=input, outputs=out)
    return model

# pix2pix generator model
class P2PGenerator(Model):
    def __init__(self, *args, **kwargs):
        super(P2PGenerator, self).__init__(self, *args, **kwargs)
        self.initializer = tf.random_normal_initializer(0., 0.02)
        self.down_stacks = [
            CDownsample(64, 4, stride=2, batch_norm=False), # (bs, 128, 128, 64)
            CDownsample(128, 4, stride=2), # (bs, 64, 64, 128)
            CDownsample(256, 4, stride=2), # (bs, 32, 32, 256)
            CDownsample(512, 4, stride=2), # (bs, 16, 16, 512)
            CDownsample(512, 4, stride=2), # (bs, 8, 8, 512)
            CDownsample(512, 4, stride=2), # (bs, 4, 4, 512)
            CDownsample(512, 4, stride=2), # (bs, 2, 2, 512)
            CDownsample(512, 4, stride=2), # (bs, 1, 1, 512)
        ]
        self.up_stack = [
            CUpsample(512, 4, stride=2, dropout=True), # (bs, 2, 2, 1024)
            CUpsample(512, 4, stride=2, dropout=True), # (bs, 4, 4, 1024)
            CUpsample(512, 4, stride=2, dropout=True), # (bs, 8, 8, 1024)
            CUpsample(512, 4, stride=2), # (bs, 16, 16, 1024)
            CUpsample(256, 4, stride=2), # (bs, 32, 32, 512)
            CUpsample(128, 4, stride=2), # (bs, 64, 64, 256)
            CUpsample(64, 4, stride=2), # (bs, 128, 128, 128)
        ]
        self.last = tf.keras.layers.Conv2DTranspose(3, 4,
                                         strides=2,
                                         padding='same',
                                         kernel_initializer=self.initializer,
                                         activation='tanh') # (bs, 256, 256, 3)

    def call(self, input):
        x = input
        # Downsampling through the model
        skips = []
        for down in self.down_stacks:
            x = down(x)
            skips.append(x)

        skips = reversed(skips[:-1])
        # Upsampling and establishing the skip connections
        for up, skip in zip(self.up_stack, skips):
            x = up(x)
            x = tf.keras.layers.Concatenate()([x, skip])

        x = self.last(x)
        return x


# pix2pix discriminator model
class P2PDiscriminator(Model):
    def __init__(self, *args, **kwargs):
        super(P2PDiscriminator, self).__init__(self, *args, **kwargs)
        self.initializer = tf.random_normal_initializer(0., 0.02)
        
        self.down1 = CDownsample(64, 4, stride=2, batch_norm=False) # (bs, 128, 128, 64)
        self.down2 = CDownsample(128, 4, stride=2) # (bs, 64, 64, 128)
        self.down3 = CDownsample(256, 4, stride=2) # (bs, 32, 32, 256)

        self.zero_pad1 = tf.keras.layers.ZeroPadding2D() # (bs, 34, 34, 256)
        self.conv = tf.keras.layers.Conv2D(512, 4, strides=1,
                                        kernel_initializer=self.initializer,
                                        use_bias=False) # (bs, 31, 31, 512)

        self.batchnorm1 = tf.keras.layers.BatchNormalization()
        self.leaky_relu = tf.keras.layers.LeakyReLU()
        self.zero_pad2 = tf.keras.layers.ZeroPadding2D() # (bs, 33, 33, 512)
        self.last = tf.keras.layers.Conv2D(1, 4, strides=1,
                                        kernel_initializer=self.initializer) # (bs, 30, 30, 1)
        
    def call(self, concat_input):
        x = concat_input
        x = self.down1(x)
        x = self.down2(x)
        x = self.down3(x)

        x = self.zero_pad1(x)
        x = self.conv(x)
        x = self.batchnorm1(x)
        x = self.leaky_relu(x)
        x = self.zero_pad2(x)
        x = self.last(x)
        return x
