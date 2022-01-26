import boto3
import datetime
import numpy as np
import openpyxl
import os
import pandas as pd
import tensorflow as tf
import tensorflow.keras.backend as K
import time
from matplotlib import pyplot as plt
from datetime import date, timedelta, datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import plot_model
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input, BatchNormalization
from tensorflow.keras.layers import multiply, concatenate, Flatten, Activation, dot, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.activations import softmax
from dateutil.relativedelta import relativedelta
#from tensorflow.python.framework import indexed_slices
import gc
import featurewiz as FW
from datupapi.configure.config import Config

class Attup(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def transform_with_loc_to_matrix(self, df):
        """
        Returns a dataframe in matrix form in order to be trained by the attention model

        :param df: Dataframe with columns: timestamp, item_id, demand and location
        :return df_out: Output dataframe with each item as a column
        >>> df =
                Date        item_id  Demand  Location
                2021-16-05     sku1      23     1
                2021-16-05     sku2     543     2
                2021-16-05     sku3     123     3
        >>> df = transform_to_matrix(df)
        >>> df =
                      Date           sku1    sku2     sku3 ......... skuN
                idx1  2021-16-05      23      543      123 ......... 234
        """
        n_features_list = []
        frames = []
        locations = df.location.unique()
        for i in range(len(locations)):
            data_aux = df[df['location'] == locations[i]].iloc[:, :3].sort_values(by='timestamp')
            n_features_list.append(len(data_aux.item_id.unique()))
            data_aux = data_aux.pivot(index='timestamp', columns='item_id', values='demand')
            frames.append(data_aux)
        df_out = pd.concat(frames, axis=1).fillna(0).reset_index()
        df_out = df_out.rename(columns={'index': 'Date'})

        for_loc = []
        for i in range(len(locations)):
            aux_for = np.repeat(locations[i], n_features_list[i] * self.forecast_horizon)
            for_loc.append(aux_for)
        for_loc = np.concatenate(for_loc)

        return df_out, for_loc


    def transform_to_matrix(self, df, value=None, method=None):
        """
        Returns a dataframe in matrix form in order to be trained by the attention model

        :param df: Dataframe with columns: timestamp, item_id and demand
        :return df_out: Output dataframe with each item as a column
        >>> df =
                Date        item_id  Demand
                2021-16-05     sku1      23
                2021-16-05     sku2     543
                2021-16-05     sku3     123
        >>> df = transform_to_matrix(df)
        >>> df =
                      Date           sku1    sku2     sku3 ......... skuN
                idx1  2021-16-05      23      543      123 ......... 234
        """
        df_out = df.sort_values(by='timestamp')
        df_out = df_out.reset_index()
        df_out = df_out.iloc[:, 1:]
        df_out = df_out.pivot(index='timestamp', columns='item_id', values='demand').reset_index()
        df_out = df_out.fillna(value=value, method=method)
        df_out = df_out.rename(columns={'timestamp': 'Date'})
        df_out=df_out.set_index("Date")
        df_out =df_out.reindex(sorted(df_out.columns), axis=1)
        df_out=df_out.reset_index()
        for_loc = []
        return df_out, for_loc


    def fill_dates(self, df, freq='W', value=None, method=None):
        """
        Returns a dataframe in matrix form with a row for each week between the start and end date
        defined in the df input dataframe. The NaN values are filled by the value.

        :param df: Dataframe in matrix form with the data as first column and each SKU as the next columns.
        :param freq: Aggregation type for time dimension. Default W.
        :param value: Value to fill incomplete records.
        :param method: Filling method for incomplete intermediate records.
        :return df: Output dataframe with each week between the start and end date as a row.
        >>> df =
                        Date           sku1    sku2 ......... skuN
                idx1    2021-16-05     543      123 ......... 234
                idx2    2021-30-05     250      140 ......... 200
        >>> df =fill_dates(df)
        >>> df =
                        Date           sku1    sku2 ......... skuN
                idx1    2021-16-05     543      123 ......... 234
                idx2    2021-23-05      0        0  ......... 0
                idx3    2021-30-05     250      140 ......... 200
        """
        df = df.sort_values(by='Date', ascending=True)
        sdate = datetime.strptime(df['Date'].iloc[0], '%Y-%m-%d').date()
        # start date
        edate = datetime.strptime(df['Date'].iloc[len(df) - 1], '%Y-%m-%d').date()

        dates = pd.date_range(sdate, edate, freq='d')
        if freq == 'W':
            dates = dates[::7]
        dates = dates.strftime("%Y-%m-%d")
        dates_df = df.sort_values(by='Date').Date.values

        n_dates = []
        for j in range(len(dates)):
            if np.isin(dates[j], dates_df) == False:
                n_dates.append(dates[j])

        if n_dates:
            df2 = pd.DataFrame(n_dates)
            df2.columns = ['Date']
            df = df.append(df2, ignore_index=True)
            df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')

            df = df.sort_values(by='Date', ascending=True)
            df = df.reset_index().iloc[:, 1:]
            df = df.fillna(value=value, method=method)
            return df
        else:
            df['Date'] = pd.to_datetime(df.Date, format='%Y-%m-%d')
            return df


    def add_dates(self, data_date, data, predict, n_features, for_loc):
        """
        Add the timestamp, backtesting intervals and target to the predictions dataframe based on each rows index and Qprep.

        :param data_date (df): Original Qprep dataframe.
        :param data (df): training data without dates.
        :param predict (df): Dataframe with the neural network output.
        :param n_features (int): Number of features or items that were predicted.
        :param n_backtests (int): Number of backtests. 5 by default.
        :param n_steps_out (int): Number of weeks predicted. 4 by default

        :return predict (df): Prediction dataframe with the target values, timestamp and backtesting intervals.
        """

        edate=data_date['Date'].iloc[len(data_date)-1]
        edate=datetime.strptime(edate, '%Y-%m-%d').date()
        if self.dataset_frequency=="W":
            dates = [edate + relativedelta(weeks=+i) for i in range(1,self.forecast_horizon+1)]
        elif self.dataset_frequency=="M":
            dates = [edate + relativedelta(months=+i) for i in range(1,self.forecast_horizon+1)]
        elif self.dataset_frequency=="D":
            dates = [edate + relativedelta(days=+i) for i in range(1,self.forecast_horizon+1)]

        size=len(data)
        print(size)
        target={}
    
        predict[0].insert(2,column='date',value=np.tile(dates,(n_features)))
        #Take the target column from the data dataframe and add it to the Predict dataframe.
        for i in range(1,self.backtests+1):
            target[i]=data.iloc[size-i*self.forecast_horizon:size-(i-1)*self.forecast_horizon].to_numpy()
            print(len(target[i]))
            target[i]=np.reshape(target[i],(n_features*self.forecast_horizon,1),order='F')
            predict[i].insert(3,"target_value",target[i], allow_duplicates=False)
        
        #Add the dates column to the forecast dataframe based on the respective time_idx of each row and drop the time_idx column.
    
        predict[0]=predict[0].drop(columns='time_idx')

        #Reorder the forecast columns according to the order defined in datupapi.
        column_names=["item_id","date","p5","p20","p40","p50","p60","p80","p95"]
        predict[0] = predict[0].reindex(columns=column_names)

        ##Add the dates, backtest start time and backtest end time column to each backtest dataframe based on the respective time_idx of each row
        timestamp={}
        for j in range(1,self.backtests+1):
            aux_d=data_date["Date"].iloc[size-j*self.forecast_horizon:size-(j-1)*self.forecast_horizon].to_numpy()
            timestamp[j]=np.tile(aux_d,(n_features))
            timestamp[j]=np.reshape(timestamp[j],(n_features*self.forecast_horizon,1),order='F')
            predict[j].insert(2,"timestamp",timestamp[j], allow_duplicates=False)

        
            startdate=[]
            enddate=[]
            for i in range(len(predict[j].index)):
                startdate.append(timestamp[j][0][0])
                enddate.append(timestamp[j][self.forecast_horizon-1][0])

            predict[j].insert(3,column='backtestwindow_start_time',value=startdate)
            predict[j].insert(4,column='backtestwindow_end_time',value=enddate)
            predict[j]=predict[j].drop(columns='time_idx')

            #Reorder the backtest columns according to the order defined in datupapi.
            column_names=["item_id","timestamp","target_value","backtestwindow_start_time","backtestwindow_end_time","p5",                          "p20", "p40","p50","p60","p80","p95"]
            predict[j] = predict[j].reindex(columns=column_names)

        return predict


    def clean_negatives(self, df):
        """
        Replace negative values with zeros.

        :param noneg (df): Dataframe with the negative values to be replaces.
        :param n_backtests (int): Number of backtests. 5 by default.

        :return noneg (df): Dataframe without negative values.
        """
        inter = ["p95", "p5", "p60", "p40", "p80", "p20", "p50"]
        for i in range(1, self.backtests + 1):
            df[i]['target_value'] = df[i]['target_value'].map(lambda x: 0 if x < 0 else x)

        for i in inter:
            for j in range(self.backtests + 1):
                df[j][i] = df[j][i].map(lambda x: 0 if x < 0 else x)

        return df


    def split_sequences(self, sequences, n_steps_in, n_steps_out):
        """
        Split a multivariate sequence into samples to use the sequences as a supervised learning model.

        :param sequences(df): Dataframe use to train the model in matrix form.
        :param n_steps_out (int): Number of weeks  to be predicted. 4 by default.
        :param n_steps_in (int): Input window size. Number of weeks used to make the prediction.

        :return X (numpy_array): Input values for training the model.
        :return y (numpy_array): Output values for training the model.
        """
        X, y = list(), list()
        for i in range(len(sequences)):
            # find the end of this pattern
            end_ix = i + n_steps_in
            out_end_ix = end_ix + n_steps_out
            # check if we are beyond the dataset
            if out_end_ix > len(sequences):
                break
            # gather input and output parts of the pattern
            seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix:out_end_ix, :]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)

    def min_max_scaler(self, data):
        """
        Scales the data with a Min Max scaler.
        
        :param data: Input dataframe used to train the models predictions.
 
        :return scalers: Array with the scalers for each feature.
        :return data_train: Normalized input dataframe.

        """
        scalers={}
        #data_train=data.iloc[:,n_features:].copy()
        data_train=data.copy()
        for j in data_train.columns:
                scaler = MinMaxScaler(feature_range=(-1,1))
                s_s = scaler.fit_transform(data_train[j].values.reshape(-1,1))
                s_s=np.reshape(s_s,len(s_s))
                scalers['scaler_'+ j] = scaler
                data_train[j]=s_s
        return scalers, data_train

    def get_model(self, X, y, units, dropout_train, momentum, lr, epochs, verbose):
          #------------------------------Define the model---------------------------------------------------
          n_hidden =units
          input_train = Input(shape=(X.shape[1], X.shape[2]))
          output_train = Input(shape=(y.shape[1], y.shape[2]))
          encoder_stack_h, encoder_last_h, encoder_last_c = LSTM(n_hidden, activation='relu', dropout=dropout_train, recurrent_dropout=dropout_train,return_state=True, return_sequences=True)(input_train)
          encoder_last_h =BatchNormalization(momentum=momentum)(encoder_last_h)
          encoder_last_c = BatchNormalization(momentum=momentum)(encoder_last_c)
          decoder_input = RepeatVector(y.shape[1])(encoder_last_h)            
          decoder_stack_h = LSTM(n_hidden, activation='relu',return_state=False, return_sequences=True)(decoder_input, initial_state=[encoder_last_h, encoder_last_c])
          attention = dot([decoder_stack_h, encoder_stack_h], axes=[2, 2])
          attention = Activation('softmax')(attention)
          context = dot([attention, encoder_stack_h], axes=[2,1])
          context = BatchNormalization(momentum=momentum)(context)
          decoder_combined_context = concatenate([context, decoder_stack_h])
          out = TimeDistributed(Dense(y.shape[2]))(decoder_combined_context)
          model = Model(inputs=input_train, outputs=out)

          #model.summary()
          lr = lr
          adam = Adam(lr)     
          #Compile model   
          model.compile(optimizer=adam, loss='mean_squared_error', metrics=['mae'])

            # fit model
          def scheduler(epoch, lr):
                if epoch < epochs/2:
                    return lr
                elif epoch < int(epochs*2/3) :
                    return lr/2
                elif epoch < int(epochs*3/4) :  
                    return lr/4
                else:
                    return lr/8

          LearningScheduler= tf.keras.callbacks.LearningRateScheduler(scheduler, verbose=verbose)
          checkpoint_best_path='../tmp/model.h5'
          checkpoint_best=ModelCheckpoint(filepath=checkpoint_best_path, save_weights_only=False, save_freq="epoch", monitor="mae", save_best_only=True, verbose=verbose)
          earlyStopping=tf.keras.callbacks.EarlyStopping( monitor='mae', min_delta=0.01, patience=90, verbose=verbose,    mode='auto')
            

          return model, checkpoint_best,LearningScheduler, earlyStopping


    def hyp_tuning(self, data, n_features, units_list=[50,150, 250],   dropout_train_list=[0,0.5,0.9],  momentum_list=[0.99, 0.6],  lr_list=[0.01, 0.05, 0.005],   batch_size_list=[16, 32]):
        n_train=0
        data_train=pd.DataFrame()
        data_train=data.copy()  
        size=len(data.index)
        #-------------------------------scaler----------------------------------
        scalers,data_train=self.min_max_scaler(data_train)   
        #-----------------------------------------------------------       
        # convert into input/output
        X, y = self.split_sequences(data_train.to_numpy(), self.input_window, self.forecast_horizon)
        #....................................................................
        #if params["trdata"]:
        X=X[:,:,n_train:]
        ###########
        y=y[:,:,0:n_features]
        n_features = y.shape[2]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0, shuffle=True)

        print("X_train shape: ",X_train.shape)
        print("y_test shape: ",y_test.shape)

        #Validation loop
        epochs=100
        loss_df={}
        count=0
        for batch_size in batch_size_list:
            for lr in lr_list:
                for momentum in momentum_list:
                    for dropout_train in dropout_train_list:
                        for units in units_list:
                            model, checkpoint_best,LearningScheduler, earlyStopping=self.get_model(X=X, y=y,units=units, dropout_train=dropout_train, momentum=momentum, lr=lr, epochs=epochs, verbose=0 )
                            history= model.fit(X_train, y_train, epochs=epochs, validation_data=(X_test, y_test),shuffle=True, verbose=0, batch_size=batch_size,   callbacks=[LearningScheduler, earlyStopping])
                            print("units: "+str(units)+"  "+"dropout_train: "+str(dropout_train)+"  "+"momentum: "+str(momentum)+"  "+"lr: "+str(lr)+"  "+"batch_size: "+str(batch_size))
           
                            loss=pd.DataFrame(data=history.history['loss'], columns=["loss"])
                            loss["val_loss"]=history.history['val_loss']
                            loss["dif"]=loss["val_loss"]-loss["loss"]
                            loss=loss.reset_index()
                            loss.columns=["epoch","loss","val_loss","dif"]
                            loss=loss.tail(1)
                            print("Loss: ",loss.loss.values," Diferencia: ",loss.dif.values)
                            loss=loss.assign(units=units)
                            loss=loss.assign(dropout_train=dropout_train)
                            loss=loss.assign(momentum=momentum)
                            loss=loss.assign(lr=lr)
                            loss=loss.assign(batch_size=batch_size)       
                            loss_df[count]=loss
                            count=count+1
                            print("train: "+ str(count))
                            gc.collect()
                            K.clear_session()

        validation=pd.concat(loss_df, axis=0)
        validation.dif=abs(validation.dif)
        validation=validation.sort_values(by="dif")
        return validation

    def training(self, data_m,n_features, n_train, verbose=0):
        """
        Train models for backtesting and forecasting.

        :param data_m (df): Dataframe with the historical data ordered by date, where each columns represents a feature.
        :param n_features: Number of features to predict.
        
        :return data (df): Dataframe with the historical data ordered by date, where each columns represents a feature.
        :return models: List of models trained for backtesting and forecasting.
        :return data_train_list: List of arrays used to train the models.
        :return scalers_list: List of scalers used for data normalization.
        """   

        models = [None] * (self.backtests+1)
        data_train_list={}
        scalers_list={}

        #Train and predict forecast and backtests models
        for i in range(self.backtests+1):
            scalers={}
            data_train=pd.DataFrame()
            data_train=data_m.copy()  
            size=len(data_m.index)
            data_train =data_train.head(size-(i)*self.forecast_horizon)
            if self.normalization:
            #-------------------------------scaler----------------------------------
                scalers,data_train=self.min_max_scaler(data_train)   
            #-----------------------------------------------------------       
            # convert into input/output
            X, y = self.split_sequences(data_train.to_numpy(), self.input_window, self.forecast_horizon)
            #....................................................................
            #if params["trdata"]:
            X=X[:,:,n_train:]
            ###########

            y=y[:,:,0:n_features]
            n_features = y.shape[2]
            print("Backtest: ",i)
            print("Input shape ", X.shape)
            print("Output shape " ,y.shape)

            #------------------------------Define the model---------------------------------------------------
            model, checkpoint_best,LearningScheduler, earlyStopping=self.get_model(X=X, y=y,units=self.units, dropout_train=self.dropout_train, momentum=self.momentum, lr=self.lr, epochs=self.epochs_attup, verbose=0 )

            # Custom Callback To Include in Callbacks List At Training Time
          

            if self.lrS:
                if self.save_last_epoch==False:
                    history= model.fit(X, y, epochs=self.epochs_attup, verbose=verbose, batch_size=self.batch_size,   callbacks=[checkpoint_best,LearningScheduler, earlyStopping])
                else:
                    history= model.fit(X, y, epochs=self.epochs_attup, verbose=verbose, batch_size=self.batch_size, callbacks=[LearningScheduler,earlyStopping])
            else:
                if self.save_last_epoch==False:
                    history= model.fit(X, y, epochs=self.epochs_attup, verbose=verbose, batch_size=self.batch_size,  callbacks=[checkpoint_best, earlyStopping])
                else:
                    history= model.fit(X, y, epochs=self.epochs_attup, verbose=verbose, batch_size=self.batch_size,  callbacks=[earlyStopping])
            #print(history.history.keys())

            plt.plot(history.history['loss'],  label='Training loss')
            plt.title('model loss')
            plt.ylabel('loss')
            plt.xlabel('epoch')
            plt.figure()
            plt.show() 
            scalers_list[i]=scalers
            data_train_list[i]=data_train
            
            models[i]=model
            if self.save_last_epoch:
                model.save('../tmp/model'+str(i)+'.h5')
            
            del model
            gc.collect()
            K.clear_session()
        #--------------------------------------------------------
        return models, data_train_list, scalers_list, n_features
  
    def add_date_features(self, data_date):
        data=data_date.copy()
        ts_column = 'Date'
        data["Mes"]=pd.to_datetime(data.Date).dt.month
        data, ts_adds_in = FW.FE_create_time_series_features(data, ts_column, ts_adds_in=[])
        data=data.drop(columns=["Date_month_typeofday_cross","Date_typeofday","Date_age_in_years","Date_month_dayofweek_cross","Date_is_warm","Date_is_cold","Date_is_festive","Date_month","Date_dayofweek_hour_cross","Date_dayofweek"])
        data["Date"]=data_date["Date"]
        data=data.set_index("Date")
        data.index=pd.to_datetime(data.index)
        return data


    def string_normalization(self, texto):
        tupla = (("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),(",", ""),(".", ""),(":", ""),(";", "")
                ,("-", ""),("¡", ""),("!", ""),("¿", ""),("?", "")
                ,("'", ""),("#", ""),("$", ""),("%", ""),("&", ""),("/", "_"),('<', ""),('>', ""),('[', "")
                ,(']', ""),('*', ""),('-', ""),('+', ""),('°', ""),('¬', ""),('{', ""),('}', ""),('\n', ""),('\t', "")
                ,('"',""),('«',""),('»',""),("@",""),(" ","_"))
        for a, b in tupla:
            texto = texto.replace(a, b)
        return texto 


    def join_related_dataset(self, Qfwd, data_date, data):
        if ("location" in Qfwd.columns) or ("Location" in Qfwd.columns):
            Qfwd["item_id"]=Qfwd.apply(lambda row: (str(row["item_id"])+"-"+str(row["location"])),axis=1)
            Qfwd=Qfwd.drop(columns=["location"])
        data_date_fwd=[]
        for item in Qfwd.columns[2:]:
            Qfwd_temp=Qfwd[["timestamp","item_id",item]]
            Qfwd_temp.columns=["timestamp", "item_id", "demand"]
            Qfwd_temp,_=self.transform_to_matrix(df=Qfwd_temp, value=0)
            Qfwd_temp=Qfwd_temp.set_index("Date")
            Qfwd_temp =Qfwd_temp.reindex(sorted(Qfwd_temp.columns), axis=1)
            Qfwd_temp=Qfwd_temp.add_suffix('-'+str(item))
            Qfwd_temp.index=pd.to_datetime(Qfwd_temp.index)
            data_date_fwd.append(Qfwd_temp)
        data_date_fwd=pd.concat(data_date_fwd, axis=1)
        data_date_fwd=data_date_fwd.reset_index()
        if self.dataset_frequency=='W':
            date_diff=int((data_date_fwd.Date.max()-pd.to_datetime(data_date.Date).max()) / np.timedelta64(1, 'W'))
        elif self.dataset_frequency=='M':
            date_diff=int((data_date_fwd.Date.max()-pd.to_datetime(data_date.Date).max()) / np.timedelta64(1, 'M'))

        if date_diff ==0:
            data_date_fwd=data_date_fwd.set_index("Date")
            data=pd.concat([data, data_date_fwd], axis=1, join='inner')
        elif date_diff > 0:
            data_date_fwd=data_date_fwd.set_index("Date")
            data_date_fwd=data_date_fwd.shift(periods=-date_diff).iloc[:-date_diff]
            data=pd.concat([data, data_date_fwd], axis=1, join='inner')
        return data