import joblib # Save model
import pandas as pd
import numpy as np

class PM25Forecaster:
    """
    LSTM model for forecasting 7-day PM2.5 values based on the previous 23 days.
    """
    def __init__(self, model_filepath:str, scaler_filepath:str):
        """Initialize PM25 Forecaster with filepaths to the LTSM model and 
        MinMaxScaler model.

        Args:
            model_filename (str): Filepath to model.
            scaler_filename (str): Filepath to data scaler.
        """
        self.model = joblib.load(model_filepath) 
        self.scaler = joblib.load(scaler_filepath)
        
        self.n_pred = 7
        self.n_dependent = 23
        self.features = ["pm25", "tmp", "rh", "ws", "wd"] 
        self.n_features = len(self.features)
        self.pollutant = "pm25"
        self.pollutant_idx = 0
        
    def _scale_data(self, data:np.ndarray)->np.ndarray:
        """ Scale data to [0, 1] range using pre-fitted scaler.

        Args:
            data (pd.DataFrame): Data to forecast.

        Returns:
            pd.DataFrame: Scaled data.
        """
        # Scale the information in each column
        return self.scaler.transform(data)
    
    def _series_to_supervised(self, data:np.ndarray)->pd.DataFrame:
        """Convert time series data into supervised learning format.
        The final dataset will have shape (`n_pred`, `n_dependent`*`n_features`).

        Args:
            data (np.ndarray): Data to forecast.

        Returns:
            pd.DataFrame: Formatted data for supervised learning.
        """
        # Obtain number of variables in data
        n_vars = 1 if type(data) is list else data.shape[1]
        
        # Create a dataframe of the data
        df = pd.DataFrame(data)
        
        # Save shifted columns and their names
        cols, names = list(), list()
        
        # Create the input sequence (t-n, ... t-1) number of past instances
        for i in range(self.n_dependent, 0, -1):
            # Shift all data in features i positions downwards
            cols.append(df.shift(i))
            # Save the name of the column and how many positions it was shifted
            names += [(f"{self.features[j]}(t-{i})") for j in range(n_vars)]
        
        # Join the resulting columns and give them column names
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        agg.dropna(inplace=True)
        return agg
    
    def _create_X_set(self, data:pd.DataFrame)->np.ndarray:
        """Reshape data to LSTM input format: (samples, time_steps, features).

        Args:
            data (pd.DataFrame): Dataframe with series-to-supervised format.

        Returns:
            np.ndarray: Reshaped data.
        """
        # Obtain the values for the set of data
        values = data.values
        # Reshape each set
        return values.reshape(data.shape[0], self.n_dependent, self.n_features)
    
    def _inverse_scale(self, yhat:np.ndarray)->np.ndarray:
        """ Inverse-transform the scaled PM2.5 predictions.

        Args:
            yhat (np.ndarray): Predicted values by LTSM.

        Returns:
            np.ndarray: Real predicted values.
        """
        n_samples = yhat.shape[1]
        
        # Placeholder for full features needed by scaler
        dummy = np.zeros((n_samples * self.n_pred, self.n_features))

        # Flatten yhat to 1D, and place it into dummy
        dummy[:, self.pollutant_idx] = yhat.reshape(-1)

        # Inverse transform
        inv_feat = self.scaler.inverse_transform(dummy)

        # Extract only the feature from the result
        inv_feat = inv_feat[:, self.pollutant_idx]
        return inv_feat
    
    def _predict(self, X:np.ndarray)->np.ndarray:
        """Predict PM2.5 using the LSTM model.

        Args:
            X (np.ndarray): Reshaped data for LTSM.

        Returns:
            np.ndarray: Predicted values.
        """
        # Use the loaded model to make predictions 
        yhat = self.model.predict(X, verbose=0)
        return yhat
    
    def forecast(self, data:np.ndarray)->np.ndarray:
        """Forecast PM2.5 values 7 days ahead using the last 30 days of data.
        This data must include daily readings for PM25, temperature, relative 
        humidity, wind speed and wind direction.

        Args:
            data (np.ndarray): Data for prediction.

        Returns:
            np.ndarray: 7 day prediction for PM25.
        """
        # Scale data between 0 and 1
        scaled_data = self._scale_data(data)
        
        # Supervised learning format
        supervised = self._series_to_supervised(scaled_data)
        
        # Reshape data for LTSM
        X = self._create_X_set(supervised)
        
        # Get predictions
        yhat = self._predict(X)
        
        # Inverse the scale to get real predictions
        inv_yhat = self._inverse_scale(yhat)
        
        return inv_yhat
        