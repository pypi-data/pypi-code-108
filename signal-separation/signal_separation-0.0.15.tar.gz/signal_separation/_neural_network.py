from tensorflow.keras import layers, Model, backend
import numpy as np
import tensorflow as tf
from signal_separation._signal_creator import destandardize_height, height_ratio, places_change, de_standardize


def multiply_cnn(n, kernel_size, added_filters, filter_beg, dense1, dense2, x, batch_n):
    for i in np.arange(n):
        x = layers.Conv1D(i * added_filters + filter_beg, kernel_size, 1)(x)

        if batch_n()[1]:
            x = layers.BatchNormalization()(x)
        x = layers.Activation('softplus')(x)
        if batch_n()[2]:
            x = layers.BatchNormalization()(x)
        x = layers.MaxPooling1D(2)(x)
    out = layers.Flatten()(x)
    out = layers.Dense(dense1, activation='softplus')(out)
    out = layers.Dense(dense2, activation='sigmoid')(out)
    return out


def multiply_cnn_denseless(n, kernel_size, added_filters, filter_beg, x, batch_n):
    for i in np.arange(n):
        x = layers.Conv1D(i * added_filters + filter_beg, kernel_size, 1)(x)
        if batch_n()[1]:
            x = layers.BatchNormalization()(x)
        x = layers.Activation('softplus')(x)
        if batch_n()[2]:
            x = layers.BatchNormalization()(x)
        x = layers.MaxPooling1D(2)(x)
    return x, (n - 1) * added_filters + filter_beg


def create_network(batch_n, f_p):
    inp = layers.Input(shape=(1000, 1))
    if batch_n()[0]:
        inp = layers.BatchNormalization()(inp)
    out, out_filters = multiply_cnn_denseless(f_p, 3, 2, 2, inp, batch_n)
    out2 = multiply_cnn(7 - f_p, 3, 2, out_filters + 2, 20, 2, out, batch_n)
    out4 = multiply_cnn(7 - f_p, 3, 2, out_filters + 2, 20, 2, out, batch_n)
    out = layers.Concatenate()([out2, out4])
    model = Model(inp, out, name="Network")
    return model


def no_batch(): return [False, False, False]


def only_before_act(): return [False, True, False]


def only_after_act(): return [False, False, True]


def after_input(): return [True, False, False]


def after_input_and_after_act(): return [True, False, True]


def after_input_and_before_act(): return [True, True, False]


def exclude_by_distance(l_top, l_bottom, y_destand, y_test_destand, y_pred_test_destand, y_pred_destand):
    y_destand_l = np.zeros((y_destand.shape[0], 4))
    y_test_destand_l = np.zeros((y_test_destand.shape[0], 4))
    y_pred_test_destand_l = np.zeros((y_pred_test_destand.shape[0], 4))
    y_pred_destand_l = np.zeros((y_pred_destand.shape[0], 4))

    for i in range(4):
        k = 0
        for j in range(y_destand.shape[0]):
            if l_top > (y_destand[j, 3] - y_destand[j, 2]) > l_bottom:
                y_destand_l[k, i] = y_destand[j, i]
                y_pred_destand_l[k, i] = y_pred_destand[j, i]
                k += 1
        y_destand_l = y_destand_l[:k, :]
        y_pred_destand_l = y_pred_destand_l[:k, :]

        k = 0
        for j in range(y_test_destand.shape[0]):
            if l_top > (y_test_destand[j, 3] - y_test_destand[j, 2]) > l_bottom:
                y_test_destand_l[k, i] = y_test_destand[j, i]
                y_pred_test_destand_l[k, i] = y_pred_test_destand[j, i]
                k += 1
        y_test_destand_l = y_test_destand_l[:k, :]
        y_pred_test_destand_l = y_pred_test_destand_l[:k, :]
    return y_destand_l, y_test_destand_l, y_pred_test_destand_l, y_pred_destand_l


def mean_squared_error_new_height(y_true, y_pred, y_true1, y_true2, weight_function):
    y_pred = tf.convert_to_tensor(y_pred)
    y_true = tf.cast(y_true, y_pred.dtype)

    # Destandaryzacja do 0.8 - 15:

    y_true1 = destandardize_height(y_true1, 0.8, 15)
    y_true2 = destandardize_height(y_true2, 0.8, 15)

    return backend.mean(
        tf.math.squared_difference(y_pred, y_true) * weight_function(height_ratio(y_true1, y_true2)),
        axis=-1)


def height_dif(y_true, y_pred, weight_function):
    return mean_squared_error_new_height(height_ratio(y_true[:, 1], y_true[:, 0]),
                                         height_ratio(y_pred[:, 1], y_pred[:, 0]), y_true[:, 0], y_true[:, 1],
                                         weight_function=weight_function) * 0.00255


def mean_squared_error_new_position2(y_true, y_pred, weight_function):
    y_pred = tf.convert_to_tensor(y_pred)
    y_true = tf.cast(y_true, y_pred.dtype)

    # Destandaryzacja do 0.8 - 15:

    return backend.mean(tf.math.squared_difference(y_pred, y_true) * weight_function(y_true), axis=-1)


def freq_dif(y_true, y_pred):
    true = places_change(y_true[:, 3], 0.1, 1.7) - y_true[:, 2]
    pred = places_change(y_pred[:, 3], 0.1, 1.7) - y_pred[:, 2]

    return tf.keras.losses.mean_squared_error(true, pred) * 0.224


def h1loss(y_true, y_pred): return tf.keras.losses.mean_squared_error(y_true[:, 0], y_pred[:, 0])


def h2loss(y_true, y_pred): return tf.keras.losses.mean_squared_error(y_true[:, 1], y_pred[:, 1])


def p1loss(y_true, y_pred): return tf.keras.losses.mean_squared_error(y_true[:, 2], y_pred[:, 2])


def p2loss(y_true, y_pred, weight_function): return mean_squared_error_new_position2(y_true[:, 3], y_pred[:, 3],
                                                                                     weight_function=weight_function)


def custom_loss_function_creator(weight_function_h_ratio, weight_function_t2):
    def custom_loss_function(y_true, y_pred):
        loss = height_dif(y_true, y_pred, weight_function=weight_function_h_ratio) \
               + h1loss(y_true, y_pred) + h2loss(y_true, y_pred) \
               + p1loss(y_true, y_pred) \
               + p2loss(y_true, y_pred, weight_function=weight_function_t2) \
               + freq_dif(y_true, y_pred)
        return loss

    return custom_loss_function


def train_network_maker(x_t, y_new_test, x, y_new, weight_function_h_ratio, weight_function_t2):
    custom_loss_function = custom_loss_function_creator(weight_function_h_ratio=weight_function_h_ratio,
                                                        weight_function_t2=weight_function_t2)

    def train_network(seed, fork_point, optim, basic_lr, batch_normalization):
        tf.random.set_seed(seed)
        model = create_network(batch_normalization,
                               fork_point)  # Ustal czy w architekturze sieci będzie normalizacja Batch na początku czy nie
        opt = optim(learning_rate=basic_lr)
        model.compile(loss=custom_loss_function,
                      optimizer=opt,
                      run_eagerly=False)

        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=5, verbose=1, mode='min')
        reduce_lr_loss = tf.keras.callbacks.ReduceLROnPlateau(monitor='loss', factor=0.1, patience=4, verbose=1,
                                                              min_lr=0.00001, min_delta=1e-4, mode='min')

        mymodel = model.fit(
            x,
            y_new,
            batch_size=100,
            epochs=300,
            verbose=1,
            callbacks=[reduce_lr_loss, early_stopping],
            validation_data=(x_t, y_new_test)
        )

        print('Koniec uczenia')
        return mymodel

    return train_network


def vectors_from_cnn(model):
    hvector = Model(inputs=model.input,
                    outputs=model.layers[-5].output)
    tvector = Model(inputs=model.input,
                    outputs=model.layers[-4].output)
    return hvector, tvector


def predicting(model, svrh, svrt, signal):
    '''
    Enter None as the svrh and svrt variables if you don't have the SVR algorithm trained
    '''
    inp = np.zeros((1, len(signal)))
    inp[0, :] = signal
    if svrh is None:
        out = model.predict(inp)
    else:
        hvector, tvector = vectors_from_cnn(model)
        xp = tvector.predict(inp)
        xh = hvector.predict(inp)
        out1 = svrh.predict(xh)
        out2 = svrt.predict(xp)
        out = np.hstack((out1, out2))
    out = de_standardize(out, 400, 500, 400, 600, 0.8, 15)
    return out
