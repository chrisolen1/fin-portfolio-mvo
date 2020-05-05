import pandas as pd
import numpy as np
import os
import math

from sklearn.preprocessing import StandardScaler

import tensorflow as tf
from keras.layers import LSTM,Dense
from keras.models import load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint

import tqdm

import julia

import time

import argparse
parser = argparse.ArgumentParser(description='train parser')

wkdir = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/finance/fin-portfolio-mvo/"
data_files = os.listdir(wkdir+'data')
data_files.remove('.DS_Store')
data = pd.read_csv(wkdir+'data/'+'data_cleaned.csv')

# Separating features into macroeconomic indictors and portfolio:

econ = ['CHNGDP','USGDP','EZGDP','US_UNEMP']

shock = ['CHNGDP_Shock','USGDP_Shock','EZGDP_Shock','US_UNEMP_Shock']

finstruments = ['UST_10YR','USFFR','USDRMB','CRUDOIL','CFE_VIX','USDEUR','UST_2YR',
             'SP500_GSCI','USDOIS','UIVE_SP500VALUEETF','USDJPY','USDGBP']

assets = ['VNQ_VANGREALEST','EMB_USDEMRGBOND','LQD_CORPBOND',
            'MUB_MUNIBOND','SHY_1-3USTR','VIG_VANGDIV','IVV_SP500','EEM_MSCIEMERGING',
            'XLE_ENERGYSPDR','EFA_MSCIEAFE','TIP_TIPSBOND']

asset_vols = data.columns[-11:]

# Create response variable matrix to be subsequently transformed into y

portfolio = data[assets]
log_returns = np.log(portfolio/portfolio.shift(1)).dropna()

# Create features matrix to be subsequently transformed into X

# Log returns of assets
asset_features = np.log(data[assets]/data[assets].shift(1))

# Scaled macroeconomic factors
scale = StandardScaler()
econ_features = pd.DataFrame(scale.fit_transform(data[econ]), columns = data[econ].columns)

# Log returns of financial instruments
finstruments_features = np.log(data[finstruments]/data[finstruments].shift(1))

features = pd.concat([asset_features, econ_features, finstruments_features, 
                     data[shock], data[asset_vols]], axis = 1).dropna()


"""
MODEL CONFIGURATIONS
"""

parser.add_argument('--batch_size', action='store', dest='batch_size', type=int)
parser.add_argument('--n_timesteps', action='store', dest='n_timesteps', type=int, help='length of series used for prediction (i.e. how many days were predict off of')
parser.add_argument('--n_epochs', action='store', dest='n_epochs', type=int)
parser.add_argument('--look_ahead_time', action='store',dest='look_ahead_time', type=int, \
help='number of days in advance we will predict')
parser.add_argument('--validation_split', action='store', dest='validation_split', type=float)
parser.add_argument('--burn_in_length', action='store', dest='burn_in_length', type=int, \
                    help='how many time steps to train on before updating portfolio weights')
parser.add_argument('--burn_in_epochs', action='store', dest='burn_in_epochs', type=int, \
                    help='how many epochs to use for just the burn-in period')
parser.add_argument('--delta', action='store', dest='delta', type=float, \
                    help='risk averness for rebalancing portfolio - the higher the number the more risk averse')
parser.add_argument('--min_weight', action='store', dest='min_weight', type=float, \
                    help='the minimum amount of a particular asset we can maintain as a percentage of the portfolio')
parser.add_argument('--vol_window', action='store', dest='vol_window', type=int, \
                    help='the number of time steps to use for calculating period volatility')

parse_results = parser.parse_args()

batch_size = parse_results.batch_size
print("batch_size: ", batch_size)
n_timesteps = parse_results.n_timesteps
print("n_timesteps: ", n_timesteps)
n_epochs = parse_results.n_epochs
print("n_epochs: ", n_epochs)
look_ahead_time = parse_results.look_ahead_time
print("look_ahead_time: ", look_ahead_time)
validation_split = parse_results.validation_split
print("validation_split: ", validation_split)
burn_in_length = parse_results.burn_in_length
print("burn_in_length: ", burn_in_length)
burn_in_epochs = parse_results.burn_in_epochs
print("burn_in_epochs: ", burn_in_epochs)
delta = np.array([parse_results.delta])
print("ndelta: ", delta)
min_weight = np.array([parse_results.min_weight])
print("min_weight: ", min_weight)
vol_window = parse_results.vol_window
print("vol_window: ", vol_window)

# number of batches in an epoch: depends on batch_size
n_batches = math.floor(features.shape[0] / batch_size) 
# number of features used for prediction
n_features = features.shape[1] 
# number of asset values being predicted
n_predicted_vars = log_returns.shape[1] 
# set checkpoint directory
checkpoint_dir = "model_checkpoints"
# empty list in which to storage weights
daily_portfolio_weights = []

# Sliding window:
            
def sliding_window(features, log_returns, end_index, n_timesteps, look_ahead_time):
    
    """
    Takes in features matrix and response var (i.e. log_returns) matrix
    RETURNS: X and y matrices for training
    
    end_index: the most recent time instance used for prediction
    n_timesteps: length of series used for prediction
    look_ahead_time: how many days ahead we are predicting
    """
    
    # start index is derived from end_index - n_timesteps
    # X slices up to but does not include end_index
    X = np.array(features.iloc[(end_index-n_timesteps):end_index, :])                              
    
    # y includes end_index and slices up to but does not include end_index + look_ahead_time
    # thus, if look_ahead_time = 1, y will only include one day for prediction
    y = np.array(log_returns.iloc[end_index+look_ahead_time-1, :]) # currently can only make predictions of a single time step
    
    # return (X:[n_timesteps,n_features], y:[look_ahead_time, n_assets])
    return X, y
    

def generate_epoch(features, log_returns, n_timesteps, look_ahead_time):
    
    # begin with empty arrays to which we will append 
    X = np.array([]) 
    y = np.array([])
    
    window_count = 0
    
    for i in range(len(features)-n_timesteps):
        
        end_index = i + n_timesteps
        
        # pull out one window
        X_one, y_one = sliding_window(features, log_returns, end_index, n_timesteps, look_ahead_time)
        
        ### append sliding windows ###
        # append X_one:[n_timesteps,n_features] to batch ndarray X
        X = np.append(X, X_one)
        # append y_one:[look_ahead_time, n_assets] to batch ndarray y
        y = np.append(y, y_one)
        
        # count the number of windows (i.e. training instances)
        window_count += 1
     
    
    # reshape training vectors given window_count
    X = X.reshape(window_count, n_timesteps, features.shape[1])    
    y = y.reshape(window_count, log_returns.shape[1])
        
    return X, y


# build model:

sliding_window_input = tf.keras.layers.Input(shape=(n_timesteps, n_features,), 
                                             name = "input_layer")
lstm_out = tf.keras.layers.LSTM(n_predicted_vars, 
                                activation='tanh', recurrent_activation='sigmoid',
                                dropout=0.2, stateful=False,
                                name = "lstm")(sliding_window_input)
dense_out = tf.keras.layers.Dense(n_predicted_vars, 
                                  activation='relu', name = "dense_layer")(lstm_out)

model = tf.keras.models.Model(inputs=sliding_window_input, outputs=dense_out)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5), 
              loss='mse')    
model.summary()

checkpoints = tf.keras.callbacks.ModelCheckpoint("./model_checkpoints/saved_weights.hdf5", 
    verbose=5, 
    save_weights_only=True, 
    save_best_only=True, 
    mode='auto', 
    save_freq='epoch')

# burn in period

training_features = features.iloc[0:burn_in_length,:]
training_response = log_returns.iloc[0:burn_in_length,:]

X, y = generate_epoch(training_features, training_response, n_timesteps, look_ahead_time)

model.fit(X, y,
          validation_split = validation_split,
          epochs = burn_in_epochs,
          batch_size = batch_size,
          callbacks = [checkpoints])
    

# day-to-day training and prediction

# initialize julia instances
j = julia.Julia(compiled_modules=False)

# iterate through the remaining time steps
for i in tqdm.tqdm(range(len(features)-burn_in_length)):

    # extract training features for the current time-step (includes all instances up to the current time-step)
    training_features = features.iloc[0:burn_in_length+i,:]
  
    # extract response variables (log returns) for the current time-step
    training_response = log_returns.iloc[0:burn_in_length+i,:]
    
    # generate training epoch of sliding windows for current time-step
    X, y = generate_epoch(training_features, training_response, n_timesteps, look_ahead_time)
    
    print("X shape: ", X.shape)
    print("y shape: ", y.shape)
    
    # load latest model weights
    print("loading model....")
    start_loading = time.time()
    model.load_weights("./model_checkpoints/saved_weights.hdf5")
    end_loading = time.time()
    loading_time = end_loading - start_loading
    print("loading time: ", loading_time)    
    
    print("training...")
    # fit to features for current time-step
    model.fit(X, y,
          validation_split = validation_split,
          epochs = n_epochs,
          batch_size = batch_size,
          callbacks = [checkpoints])
    
    # extract most recent window of features for current time-step prediction
    pred_window = np.array(features.iloc[-n_timesteps:,:]).reshape(1,n_timesteps,features.shape[1])
    
    # extract log returns for the last 'vol_window' time-steps for current 'vol_window'-day volatility
    returns_vol_window = np.array(log_returns.iloc[-vol_window:,:])
    
    # predict mu for tomorrow
    mu = model.predict(pred_window)
    
    # find current sigma 
    sigma = np.dot(np.transpose(returns_vol_window),returns_vol_window)
    
    # save optimization params to tmp
    np.savetxt("tmp/mu.txt",mu)
    np.savetxt("tmp/sigma.txt",sigma)
    np.savetxt("tmp/delta.txt",delta)
    np.savetxt("tmp/min_weight.txt",min_weight)
    
    try:
        # run mvo julia optimizer
        j.include("mvo.jl")
    except:
        print("skipped julia!")
        pass
    
    # pull in optimal weights from optimizer for rebalancing
    with open("tmp/weights.txt", 'r') as f:
        w = f.readlines()
        weights = [float(e.replace('\n',"")) for e in w]
    
    # append rebalanced weights to daily_portfolio_weights object
    daily_portfolio_weights.append(weights)

    # clear in-mem TF graph
    tf.keras.backend.clear_session()

    print("finished iteration", i, " of ", len(features)-burn_in_length)
    
print("training completed")

# move daily portfolio weights to df

daily_portfolio_weights_df = pd.DataFrame(daily_portfolio_weights, columns = log_returns.columns)

# write to csv
daily_portfolio_weights_df.to_csv("daily_portfolio_weights.csv")






