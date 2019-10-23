
# coding: utf-8

# In[276]:


import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


# In[277]:


# a = pd.read_csv('fightsData.csv')
data = pd.read_csv('fightsDataSD.csv')


# In[278]:


data.columns


# In[279]:


data.drop(['Unnamed: 0', 'ID', 'Event', 'Aname', 'ResultBy', 'ResultIn',
        'Awins', 'Alosses', 'AwinOtr', 'AlossOtr', 'Al3Wins', 'Al3Losses', 'Al3WinStk', 
        'Al3WinGra', 'Al3WinDec', 'Al3WinOtr', 'Al3LossStk', 'Al3LossGra', 'Al3LossDec', 'Al3LossOtr',
        'Bname', 'Bwins', 'Blosses', 'BwinOtr', 'BlossOtr', 'Bl3Wins', 'Bl3Losses', 'Bl3WinStk', 
        'Bl3WinGra', 'Bl3WinDec', 'Bl3WinOtr', 'Bl3LossStk', 'Bl3LossGra', 'Bl3LossDec', 'Bl3LossOtr'],
        axis = 1, inplace = True)


# In[280]:


data.dropna(inplace = True)


# In[281]:


data[['Aheight', 'Bheight', 'Result']] = data[['Aheight', 'Bheight', 'Result']].astype('int64', errors='raise')


# In[282]:


spec_data = data[(data['AisMale'] == 1) & (data['Aweight'] == 170)]


# In[283]:


spec_data.drop(['AisMale', 'Aweight', 'BisMale', 'Bweight'], axis = 1, inplace = True)


# In[284]:


spec_data = spec_data.sample(frac=1)


# In[285]:


X = spec_data.drop('Result', axis = 1)
y = spec_data['Result']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.12)


# In[286]:


scaler = MinMaxScaler()


# In[287]:


scaler.fit(X_train)


# In[288]:


X_train = scaler.transform(X_train)


# In[289]:


X_test = scaler.transform(X_test)


# In[290]:


X_train = pd.DataFrame(data = X_train, columns = spec_data.columns[:-1])


# In[291]:


X_test = pd.DataFrame(data = X_test, columns = spec_data.columns[:-1])


# In[292]:


y_train = pd.DataFrame(data = np.array(y_train), columns = ['Result'])
y_test = pd.DataFrame(data = np.array(y_test), columns = ['Result'])


# In[293]:


feat_cols = []
for col in spec_data.columns[:-1]:
    feat_cols.append(tf.feature_column.numeric_column(col))


# In[294]:


input_func = tf.estimator.inputs.pandas_input_fn(X_train, y_train, batch_size = 100, num_epochs = 100, shuffle = False)


# In[295]:


model = tf.estimator.LinearClassifier(feat_cols)


# In[296]:


model.train(input_func, steps = 10000)


# In[297]:


pred_func = tf.estimator.inputs.pandas_input_fn(X_test, batch_size = len(X_test), shuffle = False)


# In[298]:


pred_gen = model.predict(pred_func)


# In[299]:


preds = list(pred_gen)


# In[300]:


preds_list = []
for pred in preds:
    preds_list.append(pred['class_ids'][0])


# In[301]:


print(classification_report(y_test, preds_list))

