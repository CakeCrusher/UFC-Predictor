
# coding: utf-8

# In[21]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import random
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib 


# In[22]:


o_data = pd.read_csv('SD_dataset_for_RNN_v2_for_2side_clean.csv')


# In[25]:


cou = 0
new_is_UFC_col = []
for ind, col in o_data.iterrows():
    event = col['event']
    if 'UFC' in event:
        if 'WUFC' in event:
            new_is_UFC_col.append(0)
            cou = cou + 1
        elif 'UFCF' in event:
            new_is_UFC_col.append(0)
            cou = cou + 1
        else:
            new_is_UFC_col.append(1)
    else:
        new_is_UFC_col.append(0)


# In[27]:


o_data['Ais_UFC'] = new_is_UFC_col


# In[28]:


ufc_data = o_data[o_data['Ais_UFC'] == 1]


# In[29]:


ufc_fight_ids = []
for ind, col in ufc_data.iterrows():
    event = col['event']
    a_name = col['Aname']
    b_name = col['Bname']
    sorted_names = [a_name, b_name]
    sorted_names.sort()
    id_str = sorted_names[0] + '|SEPARATE|' + sorted_names[1] + '|SEPARATE|' + event
    ufc_fight_ids.append(id_str)


# In[30]:


ufc_fight_ids_pd = pd.DataFrame(data = ufc_fight_ids, columns = ['id'])
ufc_fight_ids_clean = list(ufc_fight_ids_pd.drop_duplicates(['id'])['id'])


# In[31]:


len(ufc_fight_ids_clean)


# In[33]:


final_combined_df = None
cou = 0
for ufc_fight_id_itr in ufc_fight_ids_clean:
    cou = cou + 1
    if cou % 10 == 0:
        print(cou)
    try:
        ufc_fight_id = ufc_fight_id_itr.split('|SEPARATE|')
        a_name = ufc_fight_id[0]
        b_name = ufc_fight_id[1]
        event = ufc_fight_id[2]
        a_name_df = o_data[o_data['Aname'] == a_name]
        b_name_df = o_data[o_data['Aname'] == b_name]
        a_name_fight_df = None
        b_name_fight_df = None
        for ind, col in a_name_df.iterrows():            
            ind_of_fight = None
            if col['event'] == event:
                ind_of_fight = ind
                ind_of_fighter = a_name_df.index
                untill_fight = ind_of_fight - ind_of_fighter[0] + 1
                a_name_fight_df = a_name_df.head(untill_fight)
        for ind, col in b_name_df.iterrows():            
            ind_of_fight = None
            if col['event'] == event:
                ind_of_fight = ind
                ind_of_fighter = b_name_df.index
                untill_fight = ind_of_fight - ind_of_fighter[0] + 1
                b_name_fight_df = b_name_df.head(untill_fight)
        rand = random.randint(0,1)
        if rand == 0:
            b_name_fight_df['fighterA'] = list(np.ones(len(b_name_fight_df), dtype = int))
            b_name_fight_df['fighterB'] = list(np.zeros(len(b_name_fight_df), dtype = int))
            a_name_fight_df['fighterA'] = list(np.zeros(len(a_name_fight_df), dtype = int))
            a_name_fight_df['fighterB'] = list(np.ones(len(a_name_fight_df), dtype = int))
            final_combined_df_ins = pd.concat([b_name_fight_df, a_name_fight_df])

        else:
            b_name_fight_df['fighterA'] = list(np.zeros(len(b_name_fight_df), dtype = int))
            b_name_fight_df['fighterB'] = list(np.ones(len(b_name_fight_df), dtype = int))
            a_name_fight_df['fighterA'] = list(np.ones(len(a_name_fight_df), dtype = int))
            a_name_fight_df['fighterB'] = list(np.zeros(len(a_name_fight_df), dtype = int))
            final_combined_df_ins = pd.concat([a_name_fight_df, b_name_fight_df])
        id_arr = []
        for i in range(len(final_combined_df_ins)): id_arr.append(ufc_fight_id_itr)
        final_combined_df_ins['id'] = id_arr
        final_combined_df = pd.concat([final_combined_df, final_combined_df_ins], ignore_index = True)
    except:
        cou = cou - 1
        print('FAILED!')


# In[34]:


final_combined_df.to_csv('SD_RNN_2side_dataset.csv', index = False)

