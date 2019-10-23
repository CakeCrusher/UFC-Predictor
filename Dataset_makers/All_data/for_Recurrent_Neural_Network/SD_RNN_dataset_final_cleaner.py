
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import random
import datetime
from dateutil.parser import parse
from scipy import stats


# In[2]:


data = pd.read_csv('SD_new_dataset_for_RNN_v2_na_clean.csv')


# In[3]:


data_names = data.groupby('Aname').count().index


# In[4]:


true_names = []
false_names = []
for name in data_names:
    name_df = data[data['Aname'] == name]
    len_of_false = len(name_df[name_df['event'].str.contains('UFCF')])
    len_of_true = (len(name_df[name_df['event'].str.contains('UFC')]) - len_of_false)
    if len_of_true > 0:
        true_names.append(name)
    else:
        false_names.append(name)


# In[5]:


new_data = pd.DataFrame(columns = data.columns)
for name in true_names:
    name_df = data[data['Aname'] == name]
    new_data = pd.concat([new_data, name_df], ignore_index = False)
data = new_data


# In[6]:


data_names = data.groupby('Aname').count().index


# In[7]:


names_weight = {}
for name in data_names:
    name_df = data[data['Aname'] == name]
    name_weights = name_df['Aweight']
    estimated_weight = stats.mode(name_weights)
    if estimated_weight[1][0] == 1:
        estimated_weight = name_weights.mean()
    else:
        estimated_weight = estimated_weight[0][0]
#     new_weights = np.full(len(name_df), int(estimated_weight))
#     data[data['Aname'] == name]['Aweight'] = new_weights
    names_weight[name] = estimated_weight


# In[8]:


new_weights = []
for row, col in data.iterrows():
    name = col['Aname']
    new_weights.append(names_weight[name])


# In[9]:


data['Aweight'] = new_weights


# In[10]:


Aages = []
Bages = []
for row, col in data.iterrows():
    AdateB = parse(col['Adate_born'])
    AdateF = parse(col['Adate_of_fight'])
    Aage = AdateF - AdateB
    Aage = Aage.days
    Aages.append(Aage)
    BdateB = parse(col['Bdate_born'])
    BdateF = parse(col['Bdate_of_fight'])
    Bage = BdateF - BdateB
    Bage = Bage.days
    Bages.append(Bage)
data['Aage'] = Aages
data['Bage'] = Bages


# In[11]:


data.drop(['Adate_born','Adate_of_fight', 'Bdate_born','Bdate_of_fight','Atotal_fights', 'Btotal_fights', 'Bis_male', 'Bis_UFC',], axis = 1, inplace = True)


# In[12]:


new_is_UFC = []
for row, col in data.iterrows():
    event = col['event']
    is_UFC = col['Ais_UFC']
    if is_UFC == 1:
        if 'UFC' in event:
            if 'UFCF' in event:
                new_is_UFC.append(0)
            else:
                new_is_UFC.append(1)
    else:
        new_is_UFC.append(0)


# In[13]:


data['Ais_UFC'] = new_is_UFC


# In[14]:


data.to_csv('SD_dataset_for_RNN_v2_for_2side_clean.csv', index = False)


# In[64]:


names = list(data.groupby('Aname').count().index)


# In[65]:


random.shuffle(names)


# In[66]:


names_percent = (len(names) / 100)


# In[67]:


names_train = names[:int(names_percent * 75)]
names_test = names[int(names_percent * 75):]


# In[68]:


train_df = data[data['Aname'] == names_train[0]]
for name in names_train[1:]:
    train_df =  pd.concat([train_df, data[data['Aname'] == name]])
test_df = data[data['Aname'] == names_test[0]]
for name in names_test[1:]:
    test_df =  pd.concat([test_df, data[data['Aname'] == name]])


# In[69]:


from sklearn.preprocessing import MinMaxScaler


# In[70]:


scaler = MinMaxScaler()


# In[71]:


train_scaled = scaler.fit_transform(train_df.drop(['Aname','event', 'result', 'resultIn'], axis = 1))
test_scaled = scaler.transform(test_df.drop(['Aname','event', 'result', 'resultIn'], axis = 1))


# In[72]:


train_df[['Ais_male', 'Aheight', 'Aweight', 'Ais_UFC', 'Aprev_fight_length',
       'Awin_stk', 'Awin_gra', 'Awin_dec', 'Aloss_stk', 'Aloss_gra',
       'Aloss_dec', 'Bis_male', 'Bheight', 'Bweight', 'Bis_UFC',
       'Bprev_fight_length', 'Bwin_stk', 'Bwin_gra', 'Bwin_dec', 'Bloss_stk',
       'Bloss_gra', 'Bloss_dec','Aage',
       'Bage']] = train_scaled
test_df[['Ais_male', 'Aheight', 'Aweight', 'Ais_UFC', 'Aprev_fight_length',
       'Awin_stk', 'Awin_gra', 'Awin_dec', 'Aloss_stk', 'Aloss_gra',
       'Aloss_dec', 'Bis_male', 'Bheight', 'Bweight', 'Bis_UFC',
       'Bprev_fight_length', 'Bwin_stk', 'Bwin_gra', 'Bwin_dec', 'Bloss_stk',
       'Bloss_gra', 'Bloss_dec','Aage',
       'Bage']] = test_scaled


# In[73]:


train_df


# In[52]:


train_df.to_csv('train_df_for_RNN.csv', index = False)
test_df.to_csv('test_df_for_RNN.csv', index = False)

