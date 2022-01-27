import boto3
import os
import pandas as pd
import numpy as np
import time
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import tensorflow.keras.backend as K
import itertools
from tensorflow.keras.models import Sequential, Model
import gc
from datupapi.configure.config import Config


class Forecast(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def create_forecast_deepar(self, forecast_name, predictor_arn):
        """
        Return a JSON response for AWS Forecast's create_forecast API calling

        :param forecast_name: Forecast's name to uniquely identify.
        :param predictor_arn: ARNs that identifies the predictor that produced backtesting.
        :return response: API's response

        >>> response = create_forecast(forecast_name='my_forecast', predictor_arn='arn:aws:forecast:us-east-1:account-id:predictor/my_predictor')
        >>> response = 'arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.create_forecast(
                ForecastName=forecast_name,
                PredictorArn=predictor_arn,
                ForecastTypes=[self.forecast_types[0],self.forecast_types[1],self.forecast_types[3],self.forecast_types[5],self.forecast_types[6]]
            )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The forecast already exists. Please forecast name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The forecast is not found. Please forecast name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Predictor creation in progress. Please wait some minutes: {err}')
            return False
        return response['ForecastArn']


    def create_forecast_export_deepar(self, export_job, forecast_arn, export_path):
        """
        Return a JSON response for AWS Forecast's create_forecast API calling

        :param export_job: Forecast export job's name to uniquely identify.
        :param forecast_arn: ARNs that identifies the forecast.
        :param export_path: S3 bucket's path to export the forecast. Do not include bucket's name.
        :return response: API's response

        >>> response = create_forecast_export_deepar(export_job='my_export', forecast_arn='arn:aws:forecast:us-east-1:account-id:forecast/my_forecast', export_path='path/to/export')
        >>> response = 'arn:aws:forecast:us-east-1:147018152776:forecast-export/my_forecast_export'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.create_forecast_export_job(
                ForecastExportJobName=export_job,
                ForecastArn=forecast_arn,
                Destination={
                    'S3Config': {
                        'Path': os.path.join('s3://', self.datalake, export_path),
                        'RoleArn': self.forecast_role
                    }
                }
            )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The forecast export already exists. Please forecast export name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The forecast export is not found. Please forecast export name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Forecast creation in progress. Please wait some minutes: {err}')
            return False
        return response['ForecastExportJobArn']


    def list_forecasts_deepar(self):
        """
        Return a JSON response for AWS Forecast's list_forecasts API calling

        :return response: API's response

        >>> response = list_forecasts_deepar()
        >>> response = {'ForecastArn': 'arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast'}
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.list_forecasts(
            MaxResults=100,
            Filters=[
                {
                    "Condition": "IS_NOT",
                    "Key": "Status",
                    "Value": "ACTIVE"
                }
            ]
        )
        return response['Forecasts']


    def list_forecast_export_deepar(self):
        """
        Return a JSON response for AWS Forecast's list_forecast_export_jobs API calling

        :return response: API's response

        >>> response = list_forecast_export_deepar()
        >>> response = {'ForecastExportJobArn': 'arn:aws:forecast:us-east-1:147018152776:forecast-export-job/my_export'}
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.list_forecast_export_jobs(
            MaxResults=100,
            Filters=[
                {
                    "Condition": "IS_NOT",
                    "Key": "Status",
                    "Value": "ACTIVE"
                }
            ]
        )
        return response['ForecastExportJobs']


    def delete_forecast_deepar(self, arn_forecast):
        """
        Delete the specified forecast resource

        :param arn_forecast: ARNs that identifies the forecast.
        :return None:

        >>> delete_forecast_deepar(arn_forecast='arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast')
        >>> None
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.delete_forecast(ForecastArn=arn_forecast)
        time.sleep(300)
        return None


    def check_status(self, arn_target, check_type):
        """
        Return a True or False flag to determine whether the status in progress

        :param arn_target: ARN to check with the API calling to resources in progress
        :param check_type: Type of status check, either import or predictor
        :return False: Determine the status check is done

        >>> check_status(arn_target='arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast', check_type='forecast')
        >>> False
        """
        in_progress = True
        if check_type == 'forecast':
            while in_progress:
               in_progress = any(arn['ForecastArn'] == arn_target for arn in self.list_forecasts_deepar())
               time.sleep(300)
        elif check_type == 'export':
            while in_progress:
               in_progress = any(arn['ForecastExportJobArn'] == arn_target for arn in self.list_forecast_export_deepar())
               time.sleep(300)
        else:
            self.logger.debug(f'Invalid check type option. Choose from import or predictor')
        return in_progress

        #ATTUP FUNCTIONS
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

    def predict_with_uncertainty(self, f, x, n_iter, n_steps_out, n_features):
        """
        Predicts with the trained model with dropout.
        
        :param f: Model with dropout during testing
        :param x: Input data used to make the predictions.
        :param n_iter: Number of iterations through the model.
        :param n_steps_out: Output size. Number of weeks to predict.
        :param n_features: Number of features to predict.

        :return predictions: Array with the predictions for each feature.

        """
        predictions = []
        for i in range(n_iter):
            predictions.append(f([x, 1]))
        predictions = np.array(predictions).reshape(n_iter, n_steps_out * n_features).T
        return predictions

    def prediction(self,data,models, data_train_list, scalers_list,n_features, n_train):
        """
        Takes the models trained and predicts the values for backtesting and forecasting.

        :param data (df): Dataframe with the historical data ordered by date, where each columns represents a feature.
        :param models: List of models trained for backtesting and forecasting.
        :param data_train_list: List of arrays used to train the models.
        :param scalers_list: List of scalers used for data normalization.

        :return predict (list(df)): Dataframe with the forecasted values of n_steps_out for each item in n_features.
        :return models (list(models)): List with the (n_backtests+1) models trained for backtesting and forecasting.
        :return intervals (list(arrays)): List with arrays of the predictions using dropout in order to find the confidence intervales.
                                Each array has a size of (n_iter, n_steps_out*n_features).
                                models,data_train_list, scalers_list, n_features
        """   
        tf.compat.v1.disable_eager_execution()
        intervals={}
        predict={}
        for i in range(self.backtests+1):
            lista=[]
            lista = list(data_train_list[i].columns)[0:n_features]
            listan= list(itertools.chain.from_iterable(itertools.repeat(x, self.forecast_horizon) for x in lista))
            size=len(data.index)
        
            #if params["trdata"]:
            predict_input =data_train_list[i].iloc[:,n_train:].tail(self.input_window)
            #......................................................................
            predict_input =predict_input.to_numpy()[0:self.input_window]
            model=tf.keras.models.load_model('../tmp/model'+str(i)+'.h5')
            #-------Add dropout to the model used during training to make the predictions---------------------------
            dropout = self.dropout_train
            conf = model.get_config()
            # Add the specified dropout to all layers      
     
            for layer in conf['layers']:
            # Dropout layers
                if layer["class_name"]=="Dropout":
                    layer["config"]["rate"] = dropout
            # Recurrent layers with dropout
                elif "dropout" in layer["config"].keys():
                    layer["config"]["dropout"] = dropout
            # Create a new model with specified dropout
            if type(model)==Sequential:
                # Sequential
                model_dropout = Sequential.from_config(conf)
            else:
                # Functional
                model_dropout = Model.from_config(conf)
            model_dropout.set_weights(model.get_weights())
               
            #Define the new model with dropout
            predict_with_dropout=K.function([model_dropout.layers[0].input, K.learning_phase()],[model_dropout.layers[-1].output])

            input_data=predict_input.copy()
            input_data=input_data[None,...]
            #num_samples = input_data.shape[0]
            #fill the intervals list with the n_iter outputs for each point.
            intervals[i]=self.predict_with_uncertainty(f=predict_with_dropout, x=input_data, n_iter=1, n_steps_out=self.forecast_horizon, n_features=n_features)          
            #-----------------------------------------------------------------------------------
            #Make predictions without dropout to compare the results
            #.......................................................................................
            #if params["trdata"]:
            predict_input =predict_input.reshape((1, self.input_window, len(data_train_list[i].iloc[:,n_train:].columns)))
            #else:
            #predict_input =predict_input.reshape((1, self.n_steps_in, len(data_train_list[i].columns)))

            predict_out = model.predict(predict_input, verbose=2)
            del model
            gc.collect()
            K.clear_session()

            #---------------------Invert normalization----------------------------
            if self.normalization:
                for index,k in enumerate(data_train_list[i].iloc[:,:n_features].columns):
                    scaler = scalers_list[i]['scaler_'+k]
                    predict_out[:,:,index]=scaler.inverse_transform(predict_out[:,:,index])
                    for j in range(self.forecast_horizon):            
                        intervals[i][j*n_features+index,:]=scaler.inverse_transform(intervals[i][j*n_features+index,:].reshape(-1,1))[:,0]
            #------------------------inverse transform-----------------------

            #Reshape predictions
            predict_out =np.reshape(predict_out,(n_features*self.forecast_horizon,1),order='F')
            predict[i]=pd.DataFrame(predict_out)

            idxa = np.arange(size-i*self.forecast_horizon,size-(i-1)*self.forecast_horizon)
            idx=idxa
            for k in range(n_features-1):
                idx =np.append(idx,idxa)
            predict[i].insert(0, "item_id",np.array(listan) , True)
            predict[i].insert(0, "time_idx",idx.T , True)
  
        return predict, models, intervals

    def intervals(self, data, predict, predictions, n_features,mult):

        """Define confidence intervals using the ['p50','p95','p5','p60','p40','p80','p20'] percentils with the predictions data 
            found using dropout and simulation path during the prediction.

        Args:
            data (df): Qprep data in matrix form.
            predict (df): Dataframe with the predicted values during prediction.
            predictions (df): predictions using dropout with size (n_iter, n_steps_out*n_features).
            n_features (int): Number of features or items to be predicted.
            n_backtests (int): Number of backtests to use during training.
            n_steps_in (int): Input window size. 8 weeks by default.
            n_steps_out (int): Number of weeks to be predicted. 4 by default

        Returns:
            predict (df): Dataframe with the confidence intervals for each product in each of the backtests and forecast.
        """   

        interv=['p50','p95','p5','p60','p40','p80','p20']
        columns=["time_idx","item_id","predict_orig"]
        size=len(data)
        #n_features_old=10
        for i in range(self.backtests+1):
            #predict[i]=predict[i].iloc[:,:2]
            p=np.zeros((self.forecast_horizon*n_features, len(interv)))
            predict[i].columns=columns
            for j in range(n_features):
                for k in range(self.forecast_horizon):
                    ci = 0
                    p50=np.quantile(predictions[i][n_features*k+j,:], 0.5)
                    p[j*self.forecast_horizon+k][0] = p50
                    ci = 0.95
                    p[j*self.forecast_horizon+k][1]=(np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)-p50)*mult[j][0]
                    p[j*self.forecast_horizon+k][2]=(np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)-p50)*mult[j][0]              
                    ci=0.6
                    p[j*self.forecast_horizon+k][3]=(np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)-p50)*mult[j][2]
                    p[j*self.forecast_horizon+k][4]=(np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)-p50)*mult[j][2]
                    ci=0.8
                    p[j*self.forecast_horizon+k][5]=(np.quantile(predictions[i][n_features*k+j,:], 0.5+ci/2)-p50)*mult[j][1]
                    p[j*self.forecast_horizon+k][6]=(np.quantile(predictions[i][n_features*k+j,:], 0.5-ci/2)-p50)*mult[j][1] 

            predict[i].insert(2, "p50a", p[:,0], allow_duplicates=False) 
            predict[i].insert(3, "p95a", p[:,1], allow_duplicates=False)  
            predict[i].insert(4, "p5a", p[:,2] , allow_duplicates=False) 
            predict[i].insert(5, "p60a", p[:,3], allow_duplicates=False)  
            predict[i].insert(6, "p40a", p[:,4] , allow_duplicates=False)
            predict[i].insert(7, "p80a", p[:,5], allow_duplicates=False)  
            predict[i].insert(8, "p20a", p[:,6] , allow_duplicates=False)

            predict[i]["p50"]= predict[i].apply(lambda row: row["predict_orig"],axis=1) 
            predict[i]["p95"]= predict[i].apply(lambda row: row["predict_orig"]+row["p95a"],axis=1) 
            predict[i]["p5"]= predict[i].apply(lambda row: row["predict_orig"]+row["p5a"],axis=1) 
            predict[i]["p60"]= predict[i].apply(lambda row: row["predict_orig"]+row["p60a"],axis=1) 
            predict[i]["p40"]= predict[i].apply(lambda row: row["predict_orig"]+row["p40a"],axis=1) 
            predict[i]["p80"]= predict[i].apply(lambda row: row["predict_orig"]+row["p80a"],axis=1) 
            predict[i]["p20"]= predict[i].apply(lambda row: row["predict_orig"]+row["p20a"],axis=1) 
        return predict  

    def gradient_importance(self, seq, model):
        """
        Finds the importance of each feature for a model.
        
        :param seq: Normalized input data used to find the importance of each feature.
        :param model: Model trained.

        :return grads: Importance of each varaible.

        """
        seq = tf.Variable(seq[np.newaxis,:,:], dtype=tf.float32)

        with tf.GradientTape() as tape:
            predictions = model(seq)

        grads = tape.gradient(predictions, seq)
        grads = tf.reduce_mean(grads, axis=1).numpy()[0]
    
        return grads

    def relative_importance(self, data, n_columns=0, list_columns=[]):
        """
        Finds the relative importance of each variable using the backtesting and forecasting models
        
        :param data: Normalized input data used to find the importance of each feature.
        :param n_columns: Number of features used in the input data.
        :param list_columns: List of features defined to find their relative importance.

        :return df_importancia_r: Importance of each varaible.

        """
        df_importancia={}
        df_importancia_mean={}
        df_importancia_r=pd.DataFrame()
  
        for i in range(self.backtests+1):

            scalers={}
            data_train=data.copy()
            size=len(data_train)
            data_train=data_train.head(size-(i)*self.forecast_horizon)

            if self.normalization:                                      
                scalers,data_train=self.min_max_scaler(data_train)
            # convert into input/output
            X, y = self.split_sequences(data_train.to_numpy(), self.input_window, self.forecast_horizon)
            #y=y[:,:,0:n_features]
            X=X[:,:,1:]

            att=tf.keras.models.load_model('../tmp/model'+str(i)+'.h5')
            grad_imp=[]
            columns=data_train.iloc[:,:].columns

            for k in range(X.shape[0]):
                grad_imp=np.append(grad_imp,self.gradient_importance(X[k], att))
  
            grad_imp=grad_imp.reshape(X.shape[0],X.shape[2])

            strings=["median","mean"]
            median_grad_imp=np.median(grad_imp, axis=0)
            if i==0:
                df_importancia[i] = pd.DataFrame(median_grad_imp, index=list(data_train.columns[1:])).applymap(lambda x: x*1e3)\
                                                                            .reset_index(drop=False)\
                                                                            .rename(columns={'index': 'SKU', 0: 'Importancia_median_0'})
            else:
                df_importancia[i] = pd.DataFrame(median_grad_imp, index=list(data_train.columns[1:])).applymap(lambda x: x*1e3)\
                                                                          .reset_index(drop=False)\
                                                                          .rename(columns={0: 'Importancia_median_'+str(i)})
  
            mean_grad_imp=np.mean(grad_imp, axis=0)
            if i==0:
                df_importancia_mean[i] = pd.DataFrame(mean_grad_imp, index=list(data_train.columns[1:])).applymap(lambda x: x*1e3)\
                                                                            .reset_index(drop=False)\
                                                                            .rename(columns={'index': 'SKU', 0: 'Importancia_median_0'})
            else:
                df_importancia_mean[i] = pd.DataFrame(mean_grad_imp, index=list(data_train.columns[1:])).applymap(lambda x: x*1e3)\
                                                                          .reset_index(drop=False)\
                                                                          .rename(columns={0: 'Importancia_median_'+str(i)})
 
        df_importancia_f=pd.concat(df_importancia, axis=1)
        df_importancia_f.columns=df_importancia_f.columns.droplevel()
        
        def sum_imp(row):
            sum=0
            idx_sum=0
            for k in range(self.backtests+1):
                idx_sum=idx_sum+6-k
                sum = sum+row["Importancia_median_"+str(k)]*(6-k)
            mean=sum/idx_sum
            return mean


        df_importancia_f["Total_importancia_median"]=df_importancia_f.apply(sum_imp,axis=1)
        
        #df_importancia_f["Total_importancia_median"]=df_importancia_f.apply(lambda row: 1*row["Importancia_median_5"]+2*row["Importancia_median_4"]+3*row["Importancia_median_3"]+4*row["Importancia_median_2"]+5*row["Importancia_median_1"]+6*row["Importancia_median_0"] ,axis=1)
        df_importancia_f=df_importancia_f[["SKU","Total_importancia_median"]].sort_values(by="Total_importancia_median", ascending=False)
        df_importancia_f=df_importancia_f.reset_index().iloc[:,1:]
        total_positive=df_importancia_f[df_importancia_f['Total_importancia_median']>=0]['Total_importancia_median'].sum()
        total_negative=df_importancia_f[df_importancia_f['Total_importancia_median']<0]['Total_importancia_median'].sum()

        df_importancia_r["SKU_"+str(strings[0])]=df_importancia_f["SKU"]
        df_importancia_r['Importancia_relativa_'+str(strings[0])]=df_importancia_f.apply(lambda row: (row['Total_importancia_median']*100/total_positive) if row['Total_importancia_median']>=0 else (-row['Total_importancia_median']*100/total_negative) , axis=1)  
    
        if n_columns == 0:
            if len(list_columns)==0:
                return df_importancia_r
            else:
                return df_importancia_r[(df_importancia_r["SKU_median"].isin(list_columns))]
        else:
            return df_importancia_r[(df_importancia_r["SKU_median"].isin(data_train.columns[0:n_columns]))]    

  
    def reorder_impct_columns(self, data):

        impct_columns=self.sku_impct
        #n_features=len(impct_columns)
        if all(item in data.columns  for item in impct_columns):
            reindex_col=impct_columns.copy()
            reindex_col.extend(data.columns[np.logical_not(data.columns.isin(impct_columns))])
            data = data.reindex(columns=reindex_col)
        return data

    def predict_with_simulation(self, data,scalers_list, mult=[0.9,1,1.1], item_sim="brentcrudeusd", n_features=1, n_train=1):
        new_values={}
        predict={}
        for j in range(len(mult)):
            data_test=data.copy()
            list_items=[]
            list_items = list(data_test.columns)[0:n_features]
            ids= list(itertools.chain.from_iterable(itertools.repeat(x, self.forecast_horizon) for x in list_items))

    
            old_values=data_test[item_sim].values[:-self.forecast_horizon]
            main_value=old_values[-1]

            new_values[j]=np.repeat(mult[j]*main_value,self.forecast_horizon)
            new_val=np.append(old_values, new_values[j])
            data_test[item_sim]=new_val
            
            if self.normalization:
                for item in data_test.columns:
                    s_s = scalers_list[0]['scaler_'+ item].transform(data_test[item].values.reshape(-1,1))
                    s_s=np.reshape(s_s,len(s_s))
                    data_test[item]=s_s

            predict_input =data_test.iloc[:,n_train:].tail(self.input_window)
    
            predict_input =predict_input.to_numpy()[0:self.input_window]
            model=tf.keras.models.load_model('../tmp/model'+str(0)+'.h5')
            predict_input =predict_input.reshape((1, self.input_window, len(data_test.iloc[:,n_train:].columns)))
            predict_out = model.predict(predict_input, verbose=2)

            if self.normalization:
                for index,k in enumerate(data_test.iloc[:,:n_features].columns):
                    scaler = scalers_list[0]['scaler_'+k]
                    predict_out[:,:,index]=scaler.inverse_transform(predict_out[:,:,index])

            predict_out =np.reshape(predict_out,(n_features*self.forecast_horizon,1),order='F')
            #print(predict_out)
            predict[j]=pd.DataFrame(predict_out)
        return predict, ids, new_values


