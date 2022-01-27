from scarv import scarv_diagnostics

def prep_data(indices, y, multiplier, seq_in, expand=False):
    import numpy as np

    seq = seq_in[indices]
    if expand:
        ix = np.repeat(range(len(indices)), multiplier)
        seq_out = seq[ix]
        y_out = y[ix]
        return seq_out, y_out 
    else:
        ix = np.where(multiplier > 0)
        weight_out = multiplier[ix]
        seq_out = seq[ix]
        y_out = y[ix]
        return seq_out, y_out, weight_out



def fit_cnn(X, y):
    import keras
    import numpy as np

    flank = X.shape[1]//2

    learning_rate = 0.0001
    mini_batch_size = 64
    n_epochs = 1000
    patience = 5
    interval = 1

    model = create_cnn(flank=flank)

    # 90-10 split into training and validation
    ix = np.random.choice(range(X.shape[0]), round(0.9*X.shape[0]), replace=False)

    X_val, y_val = np.delete(X, ix, axis=0), np.delete(y, ix, axis=0)
    X_train, y_train = X[ix], y[ix]

    optim = keras.optimizers.Adam(lr = learning_rate)
    model.compile(optimizer=optim,loss='categorical_crossentropy', metrics=['accuracy'])

    ival = scarv_diagnostics.IntervalEvaluation(validation_data=(X_val, y_val), flank=flank, patience=patience, interval=interval)
    model.fit(x = X_train, y = y_train, epochs=n_epochs, batch_size = mini_batch_size, callbacks = [ival])

    return model 


def create_cnn(flank):
    import keras
    import keras_genomics

    model = keras.models.Sequential()

    model.add(keras_genomics.layers.RevCompConv1D(filters=100, kernel_size=5, input_shape=(2*flank+1, 5), 
        padding="same", activation="relu", kernel_initializer="he_normal"))

    model.add(keras_genomics.layers.RevCompConv1D(filters=100, kernel_size=5, padding="same",
        activation="relu", kernel_initializer="he_normal"))

    model.add(keras_genomics.layers.RevCompConv1D(filters=100, kernel_size=model.layers[-1].output_shape[1],
        activation="relu", kernel_initializer="he_normal"))

    model.add(keras_genomics.layers.RevCompConv1D(filters=3, kernel_size=model.layers[-1].output_shape[1],
                activation="softmax", kernel_initializer="he_normal"))
    
    model.add(keras.layers.Flatten())

    model.add(keras.layers.Lambda(sum_middle_elements))

    return model



def sum_middle_elements(x):
    from keras import backend as K

    A_and_C = x[:, 0:2,]
    X = K.sum(x[:, 2:4], axis=1, keepdims=True)
    G_and_T = x[:, 4:]
    return K.concatenate([A_and_C, X, G_and_T], axis=1)



def fit_calibration(model, seq, y, weights):
    # isotonic regression
    from sklearn.isotonic import IsotonicRegression 
    import numpy as np

    Z = np.log(model.predict(seq))

    flank = seq.shape[1]//2
    Z_ref = np.nansum(Z * seq[:, flank, :], axis=1).astype(float)
    Z_ref[np.isinf(Z_ref)] = -100 # isotonic regression does not allow -inf

    y_bin = 1 * (np.argmax(y, axis=1) == np.argmax(seq[:, flank, :], axis=1))

    ir = IsotonicRegression(y_min=0, y_max=1, out_of_bounds='clip')
    ir.fit(Z_ref, y_bin, sample_weight=weights)

    return ir





