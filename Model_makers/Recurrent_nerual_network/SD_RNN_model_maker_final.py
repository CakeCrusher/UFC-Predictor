
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import random
import datetime
from dateutil.parser import parse
import tensorflow as tf
import time


# In[12]:




startTime = datetime.datetime.now()
def timer():
    global startTime
    secondsPassed = (datetime.datetime.now() - startTime).seconds
    def addzero(x):
        if len(x) == 1:
            x = '0' + x
        return x
    sec = addzero(str(int(secondsPassed % 60)))
    minu = addzero(str(int((secondsPassed/60) % 60)))
    hr = addzero(str(int(secondsPassed/60/60)))
    return '[' + str(hr) + ':' + str(minu) + ':' + str(sec) + '] '

weights_str = ['115','125','135','145','155','170','185','205','265']
# weights_str = ['115','205','265']
reports = {}
top_reports_per_weight = {}

for weight_str in weights_str:
    print(timer())
    train_data = pd.read_csv('Datasets_per_weight/SD_new_2_' + weight_str + '_train')
    test_data = pd.read_csv('Datasets_per_weight/SD_new_2_' + weight_str + '_test')

    # TRAIN
    results = []
    resultIns = []
    for col, row in train_data.iterrows():
        result = row['result']
        resultIn = row['resultIn']
        if result == 'Awins':
            results.append(1)
        else:
            results.append(0)
        if resultIn == 'Inside':
            resultIns.append(1)
        else:
            resultIns.append(0)
    train_data['result'] = results
    train_data['resultIn'] = resultIns
    new_name_df = None
    per_fighter_array = {}
    names = list(train_data.groupby('Aname').count().index)
    for name in names:
        name_df = train_data[train_data['Aname'] == name]
        name_df.drop(['Aname','event'], axis = 1, inplace = True)
        start_index = name_df.head(1).index[0]
        len_df = len(name_df)
        df_results = list(name_df['result'])
    #     df_results.insert(0, 'Bwins')
        df_results.insert(0, 0)
        df_resultIns = list(name_df['resultIn'])
    #     df_resultIns.insert(0, 'Distance')
        df_resultIns.insert(0, 0)
        none_filler = []
        for i in range(22): none_filler.append(None)
        false_df = pd.DataFrame(data = [none_filler], columns = name_df.columns)
        new_name_df = pd.concat([name_df, false_df])
        new_name_df['result'] = df_results
        new_name_df['resultIn'] = df_resultIns
        new_name_df.reset_index(drop = True, inplace = True)
        per_fighter_array[name] = new_name_df

    # TEST
    results = []
    resultIns = []
    for col, row in test_data.iterrows():
        result = row['result']
        resultIn = row['resultIn']
        if result == 'Awins':
            results.append(1)
        else:
            results.append(0)
        if resultIn == 'Inside':
            resultIns.append(1)
        else:
            resultIns.append(0)
    test_data['result'] = results
    test_data['resultIn'] = resultIns
    new_name_df = None
    per_fighter_train_array = {}
    names_train = list(train_data.groupby('Aname').count().index)
    for name in names_train:
        name_df = train_data[train_data['Aname'] == name]
        name_df.drop(['Aname','event'], axis = 1, inplace = True)
        start_index = name_df.head(1).index[0]
        len_df = len(name_df)
        df_results = list(name_df['result'])
    #     df_results.insert(0, 'Bwins')
        df_results.insert(0, 0)
        df_resultIns = list(name_df['resultIn'])
    #     df_resultIns.insert(0, 'Distance')
        df_resultIns.insert(0, 0)
        none_filler = []
        for i in range(22): none_filler.append(None)
        false_df = pd.DataFrame(data = [none_filler], columns = name_df.columns)
        new_name_df = pd.concat([name_df, false_df])
        new_name_df['result'] = df_results
        new_name_df['resultIn'] = df_resultIns
        new_name_df.reset_index(drop = True, inplace = True)
        per_fighter_train_array[name] = new_name_df
    new_name_df = None
    per_fighter_test_array = {}
    names_test = list(test_data.groupby('Aname').count().index)
    for name in names_test:
        name_df = test_data[test_data['Aname'] == name]
        name_df.drop(['Aname','event'], axis = 1, inplace = True)
        start_index = name_df.head(1).index[0]
        len_df = len(name_df)
        df_results = list(name_df['result'])
    #     df_results.insert(0, 'Bwins')
        df_results.insert(0, 0)
        df_resultIns = list(name_df['resultIn'])
    #     df_resultIns.insert(0, 'Distance')
        df_resultIns.insert(0, 0)
        none_filler = []
        for i in range(22): none_filler.append(None)
        false_df = pd.DataFrame(data = [none_filler], columns = name_df.columns)
        new_name_df = pd.concat([name_df, false_df])
        new_name_df['result'] = df_results
        new_name_df['resultIn'] = df_resultIns
        new_name_df.reset_index(drop = True, inplace = True)
        per_fighter_test_array[name] = new_name_df

    def next_batch(training_keys, what_set, step_for_test = None, get_fights_UFC = False):
        fighter_df = [0]
        if len(training_keys) > 1:
            rand_key = random.randint(0, (len(training_keys) - 1))
        else:
            name = training_keys[0]
        if what_set == 'train':
            if len(training_keys) > 1:
                fighter_df = per_fighter_train_array[training_keys[rand_key]]
            else:
                fighter_df = per_fighter_train_array[name]
        elif what_set == 'test':
            fighter_df = per_fighter_test_array[name]
        fights_UFC = []
        for row, col in fighter_df.iterrows():
            if col['Ais_UFC'] == 1:
                fights_UFC.append(row + 2)
        if step_for_test == None:
            steps = fights_UFC[random.randint(0,(len(fights_UFC) - 1))]
        else:
            steps = step_for_test
        batch = fighter_df[:steps]
        X_batch = np.array(batch[:-1]).reshape(22, (steps - 1)).reshape((steps - 1), 22).reshape(-1, (steps - 1), 22)
        y_batch = np.array(batch[1:][['result', 'resultIn']]).reshape(2, (steps - 1)).reshape((steps - 1), 2).reshape(-1, (steps - 1), 2)
    #     y_batch = np.array(batch.tail(1)[['result', 'resultIn']]).reshape(2, 1).reshape(1, 2).reshape(1, 1, 2)
        if get_fights_UFC:
            return[X_batch, y_batch, fights_UFC]
        return [X_batch, y_batch]

    def result_hit(true, pred, accepted_diff):
        if pred - accepted_diff < 0 or pred + accepted_diff > 1:
            diff = abs(true - pred)
            if diff <= accepted_diff:
                return True
            return False
        return None
    def results_report(results, diff_fighter = 0.5, diff_way = 0.5, weight_rr = weight_str):
        fighter_hit = [0,0]
        way_hit = [0,0]
        both_hit = [0,0]
        fighter_change = False
        way_change = False
        qualifying_results = []
        for result in results:
            preds = result[0]
            trues = result[1]
            fighter_change = False
            way_change = False

            fighter_result = result_hit(trues[0], preds[0], diff_fighter)
            way_result = result_hit(trues[1], preds[1], diff_way)
            both_result = None
            if fighter_result:
                fighter_hit[0] = fighter_hit[0] + 1
                fighter_change = True
            elif fighter_result == False:
                fighter_hit[1] = fighter_hit[1] + 1
                fighter_change = True
            if way_result:
                way_hit[0] = way_hit[0] + 1
                way_change = True
            elif way_result == False:
                way_hit[1] = way_hit[1] + 1
                way_change = True
            if fighter_change and way_change:
                qualifying_results.append(result)
                if fighter_result and way_result:
                    both_hit[0] = both_hit[0] + 1
                else:
                    both_hit[1] = both_hit[1] + 1

        try: final_fighter = fighter_hit[0] / (fighter_hit[0] + fighter_hit[1])
        except: final_fighter = [fighter_hit[0], fighter_hit[0] + fighter_hit[1]]        
        try: final_way = way_hit[0] / (way_hit[0] + way_hit[1])
        except: final_way = [way_hit[0], way_hit[0] + way_hit[1]]        
        try: final_both = both_hit[0] / (both_hit[0] + both_hit[1])
        except: final_both = [both_hit[0], both_hit[0] + both_hit[1]]

    #     print('Accurate predictions chance of hitting BOTH: ' + str(final_both))
    #     print('Amount of BOTH predictions with ' + str(diff_fighter) + ' fighter certainty and ' + str(diff_way) + ' way certainty: ' + str(both_hit[0] + both_hit[1]) + '\n\n')
    #     print('Accurate predictions chance of hitting FIGHTER: ' + str(final_fighter))
    #     print('Amount of FIGHTER predictions with ' + str(diff_fighter) + ' certainty: ' + str(fighter_hit[0] + fighter_hit[1]) + '\n\n')
    #     print('Accurate predictions chance of hitting WAY: ' + str(final_way))
    #     print('Amount of WAY predictions with ' + str(diff_way) + ' certainty: ' + str(way_hit[0] + way_hit[1]) + '\n\n')
        both_report = [qualifying_results, (int(final_both * 100), len(qualifying_results)), weight_rr, weight_rr + ' | Accurate predictions chance of hitting BOTH: ' + str(int(final_both * 100)) + '\nAmount of BOTH predictions with ' + str(diff_fighter) + ' fighter certainty and ' + str(diff_way) + ' way certainty: ' + str(both_hit[0] + both_hit[1]) + '\n\n']
        return both_report

    num_inputs = 22
    num_time_steps = None
    num_neurons = 100
    num_outputs = 2
    learning_rate = 0.001
    num_train_iterations = (len(per_fighter_train_array) * 5)
    batch_size = 1
    tf.reset_default_graph()

    # Random itr
    reports_for_weight = []
     
#     while len(top_report) == 2:
    for i in range(200):
        X = tf.placeholder(tf.float32, [None, None, num_inputs])
        y = tf.placeholder(tf.float32, [None, None, num_outputs])
        cell = tf.contrib.rnn.OutputProjectionWrapper(tf.contrib.rnn.GRUCell(num_units=num_neurons, activation=tf.nn.relu),output_size=num_outputs) 
        outputs, states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)
        loss = tf.reduce_mean(tf.square(outputs - y)) # MSE
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train = optimizer.minimize(loss)
        init = tf.global_variables_initializer()
        saver = tf.train.Saver()
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
        with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
            sess.run(init)
            for iteration in range(num_train_iterations):
                X_batch, y_batch = next_batch(names_train, 'train')
                sess.run(train, feed_dict={X: X_batch, y: y_batch})
                if iteration % 200 == 0:
                    mse = loss.eval(feed_dict={X: X_batch, y: y_batch})
                    print(weight_str + ' | ' + str(i) + ' | Train | ' + str(int((iteration / num_train_iterations) * 100)) + "\tMSE:" + str(mse))
#             saver.save(sess, "Models_per_weight/SD_RNN_155_model")
            results = []
            cou = 0
            for name in names_test:
                fights_UFC = next_batch([name], 'test', get_fights_UFC = True)[2]
                for fight in fights_UFC:
                    batch = next_batch([name], 'test', fight)
                    X_batch = batch[0]
                    y_batch = batch[1]
                    y_true = y_batch[0, -1, :]
                    y_pred = sess.run(outputs, feed_dict={X: X_batch})[0, -1, :]
        #           pred_eval = test_eval(y_pred, y_true)
                    results.append([y_pred, y_true])
                if (cou % 20) == 0:
                    print(weight_str + ' | ' + str(i) + ' | Test | ' + str(int((cou / len(names_test)) * 100)))
                cou = cou + 1
            result_report = results_report(results,0.5,0.5)
            best_model(result_report)
        tf.reset_default_graph()
        reports_for_weight.append(result_report)
    top_reports_per_weight[weight_str] = top_report
    reports[weight_str] = reports_for_weight


# In[52]:


def results_report(results, diff_fighter = 0.5, diff_way = 0.5, weight_rr = 'None'):
    fighter_hit = [0,0]
    way_hit = [0,0]
    both_hit = [0,0]
    fighter_change = False
    way_change = False
    qualifying_results = []
    for result in results:
        preds = result[0]
        trues = result[1]
        fighter_change = False
        way_change = False

        fighter_result = result_hit(trues[0], preds[0], diff_fighter)
        way_result = result_hit(trues[1], preds[1], diff_way)
        both_result = None
        if fighter_result:
            qualifying_results.append(result)
            fighter_hit[0] = fighter_hit[0] + 1
            fighter_change = True
        elif fighter_result == False:
            qualifying_results.append(result)
            fighter_hit[1] = fighter_hit[1] + 1
            fighter_change = True
        if way_result:
            way_hit[0] = way_hit[0] + 1
            way_change = True
        elif way_result == False:
            way_hit[1] = way_hit[1] + 1
            way_change = True
        if fighter_change and way_change:
            if fighter_result and way_result:
                both_hit[0] = both_hit[0] + 1
            else:
                both_hit[1] = both_hit[1] + 1

    try: final_fighter = fighter_hit[0] / (fighter_hit[0] + fighter_hit[1])
    except: final_fighter = [fighter_hit[0], fighter_hit[0] + fighter_hit[1]]        
    try: final_way = way_hit[0] / (way_hit[0] + way_hit[1])
    except: final_way = [way_hit[0], way_hit[0] + way_hit[1]]        
    try: final_both = both_hit[0] / (both_hit[0] + both_hit[1])
    except: final_both = [both_hit[0], both_hit[0] + both_hit[1]]
    both_report = [qualifying_results, (int(final_fighter * 100), len(qualifying_results)), weight_rr, weight_rr + ' | Accurate predictions chance of hitting BOTH: ' + str(int(final_both * 100)) + '\nAmount of BOTH predictions with ' + str(diff_fighter) + ' fighter certainty and ' + str(diff_way) + ' way certainty: ' + str(both_hit[0] + both_hit[1]) + '\n\n']
    return both_report


# In[61]:


weights_str = ['115','125','135','145','155','170','185','205','265']
num_inputs = 22
num_time_steps = None
num_neurons = 100
num_outputs = 2
learning_rate = 0.001
num_train_iterations = (len([0]) * 5)
batch_size = 1
tf.reset_default_graph()
def result_hit(true, pred, accepted_diff):
    diff = abs(true - pred)
    if abs(pred - 0.5) > abs(accepted_diff - 0.5): 
        if diff <= accepted_diff:
            return True
        return False
    return None
def results_report(results, diff_fighter = 0.5, diff_way = 0.5, weight_rr = 'None'):
    fighter_hit = [0,0]
    way_hit = [0,0]
    both_hit = [0,0]
    fighter_change = False
    way_change = False
    qualifying_results = []
    for result in results:
        preds = result[0]
        trues = result[1]
        fighter_change = False
        way_change = False

        fighter_result = result_hit(trues[0], preds[0], diff_fighter)
        way_result = result_hit(trues[1], preds[1], diff_way)
        both_result = None
        if fighter_result:
            qualifying_results.append(result)
            fighter_hit[0] = fighter_hit[0] + 1
            fighter_change = True
        elif fighter_result == False:
            qualifying_results.append(result)
            fighter_hit[1] = fighter_hit[1] + 1
            fighter_change = True
        if way_result:
            way_hit[0] = way_hit[0] + 1
            way_change = True
        elif way_result == False:
            way_hit[1] = way_hit[1] + 1
            way_change = True
        if fighter_change and way_change:
            if fighter_result and way_result:
                both_hit[0] = both_hit[0] + 1
            else:
                both_hit[1] = both_hit[1] + 1

    try: final_fighter = fighter_hit[0] / (fighter_hit[0] + fighter_hit[1])
    except: final_fighter = [fighter_hit[0], fighter_hit[0] + fighter_hit[1]]        
    try: final_way = way_hit[0] / (way_hit[0] + way_hit[1])
    except: final_way = [way_hit[0], way_hit[0] + way_hit[1]]        
    try: final_both = both_hit[0] / (both_hit[0] + both_hit[1])
    except: final_both = [both_hit[0], both_hit[0] + both_hit[1]]
    both_report = [qualifying_results, (int(final_fighter * 100), len(qualifying_results)), weight_rr, weight_rr + ' | Accurate predictions chance of hitting BOTH: ' + str(int(final_both * 100)) + '\nAmount of BOTH predictions with ' + str(diff_fighter) + ' fighter certainty and ' + str(diff_way) + ' way certainty: ' + str(both_hit[0] + both_hit[1]) + '\n\n']
    return both_report
#     for result in results:
#         preds = result[0]
#         trues = result[1]
#         fighter_change = False
#         way_change = False

#         fighter_result = result_hit(trues[0], preds[0], diff_fighter)
#         way_result = result_hit(trues[1], preds[1], diff_way)
#         both_result = None
#         if fighter_result:
#             fighter_hit[0] = fighter_hit[0] + 1
#             fighter_change = True
#         elif fighter_result == False:
#             fighter_hit[1] = fighter_hit[1] + 1
#             fighter_change = True
#         if way_result:
#             way_hit[0] = way_hit[0] + 1
#             way_change = True
#         elif way_result == False:
#             way_hit[1] = way_hit[1] + 1
#             way_change = True
#         if fighter_change and way_change:
#             qualifying_results.append(result)
#             if fighter_result and way_result:
#                 both_hit[0] = both_hit[0] + 1
#             else:
#                 both_hit[1] = both_hit[1] + 1

#     try: final_fighter = fighter_hit[0] / (fighter_hit[0] + fighter_hit[1])
#     except: final_fighter = [fighter_hit[0], fighter_hit[0] + fighter_hit[1]]        
#     try: final_way = way_hit[0] / (way_hit[0] + way_hit[1])
#     except: final_way = [way_hit[0], way_hit[0] + way_hit[1]]        
#     try: final_both = both_hit[0] / (both_hit[0] + both_hit[1])
#     except: final_both = [both_hit[0], both_hit[0] + both_hit[1]]
#     both_report = [qualifying_results, (int(final_both * 100), len(qualifying_results)), weight_rr, weight_rr + ' | Accurate predictions chance of hitting BOTH: ' + str(int(final_both * 100)) + '\nAmount of BOTH predictions with ' + str(diff_fighter) + ' fighter certainty and ' + str(diff_way) + ' way certainty: ' + str(both_hit[0] + both_hit[1]) + '\n\n']
#     return both_report
def get_report_arr(results, weight_str):
    total_results = results_report(results, 0.5, 0.5, weight_str)[1][1]
    data_5 = results_report(results, 0.5, 0.5, weight_str)[1]
    data_45 = results_report(results, 0.45, 0.45, weight_str)[1]
    try:
        data_4 = results_report(results, 0.4, 0.4, weight_str)[1]
    except:
        data_4 = ['_', 0]
    data_to_45 = int((data_45[1] / total_results) * 100)
    data_to_4 = int((data_4[1] / total_results) * 100)
    final_str = weight_str + '- ' + str(data_5[0]) + ', ' + str(data_45[0]) + ', ' + str(data_4[0]) + ', ' + str(data_to_45) + '%, ' + str(data_to_4) + '%\n'
    return final_str
final_results = []
weights = ['115', '125', '135', '145', '155', '170', '185', '205', '265']
for weight_str_ in weights:
    train_data = pd.read_csv('Datasets_per_weight/SD_' + weight_str_ + '_train')
    test_data = pd.read_csv('Datasets_per_weight/SD_' + weight_str_ + '_test')

    # TRAIN
    results = []
    resultIns = []
    for col, row in train_data.iterrows():
        result = row['result']
        resultIn = row['resultIn']
        if result == 'Awins':
            results.append(1)
        else:
            results.append(0)
        if resultIn == 'Inside':
            resultIns.append(1)
        else:
            resultIns.append(0)
    train_data['result'] = results
    train_data['resultIn'] = resultIns
    new_name_df = None
    per_fighter_array = {}
    names = list(train_data.groupby('Aname').count().index)
    for name in names:
        name_df = train_data[train_data['Aname'] == name]
        name_df.drop(['Aname','event'], axis = 1, inplace = True)
        start_index = name_df.head(1).index[0]
        len_df = len(name_df)
        df_results = list(name_df['result'])
    #     df_results.insert(0, 'Bwins')
        df_results.insert(0, 0)
        df_resultIns = list(name_df['resultIn'])
    #     df_resultIns.insert(0, 'Distance')
        df_resultIns.insert(0, 0)
        none_filler = []
        for i in range(22): none_filler.append(None)
        false_df = pd.DataFrame(data = [none_filler], columns = name_df.columns)
        new_name_df = pd.concat([name_df, false_df])
        new_name_df['result'] = df_results
        new_name_df['resultIn'] = df_resultIns
        new_name_df.reset_index(drop = True, inplace = True)
        per_fighter_array[name] = new_name_df

    # TEST
    results = []
    resultIns = []
    for col, row in test_data.iterrows():
        result = row['result']
        resultIn = row['resultIn']
        if result == 'Awins':
            results.append(1)
        else:
            results.append(0)
        if resultIn == 'Inside':
            resultIns.append(1)
        else:
            resultIns.append(0)
    test_data['result'] = results
    test_data['resultIn'] = resultIns
    new_name_df = None
    per_fighter_train_array = {}
    names_train = list(train_data.groupby('Aname').count().index)
    for name in names_train:
        name_df = train_data[train_data['Aname'] == name]
        name_df.drop(['Aname','event'], axis = 1, inplace = True)
        start_index = name_df.head(1).index[0]
        len_df = len(name_df)
        df_results = list(name_df['result'])
    #     df_results.insert(0, 'Bwins')
        df_results.insert(0, 0)
        df_resultIns = list(name_df['resultIn'])
    #     df_resultIns.insert(0, 'Distance')
        df_resultIns.insert(0, 0)
        none_filler = []
        for i in range(22): none_filler.append(None)
        false_df = pd.DataFrame(data = [none_filler], columns = name_df.columns)
        new_name_df = pd.concat([name_df, false_df])
        new_name_df['result'] = df_results
        new_name_df['resultIn'] = df_resultIns
        new_name_df.reset_index(drop = True, inplace = True)
        per_fighter_train_array[name] = new_name_df
    new_name_df = None
    per_fighter_test_array = {}
    names_test = list(test_data.groupby('Aname').count().index)
    for name in names_test:
        name_df = test_data[test_data['Aname'] == name]
        name_df.drop(['Aname','event'], axis = 1, inplace = True)
        start_index = name_df.head(1).index[0]
        len_df = len(name_df)
        df_results = list(name_df['result'])
    #     df_results.insert(0, 'Bwins')
        df_results.insert(0, 0)
        df_resultIns = list(name_df['resultIn'])
    #     df_resultIns.insert(0, 'Distance')
        df_resultIns.insert(0, 0)
        none_filler = []
        for i in range(22): none_filler.append(None)
        false_df = pd.DataFrame(data = [none_filler], columns = name_df.columns)
        new_name_df = pd.concat([name_df, false_df])
        new_name_df['result'] = df_results
        new_name_df['resultIn'] = df_resultIns
        new_name_df.reset_index(drop = True, inplace = True)
        per_fighter_test_array[name] = new_name_df
    def next_batch(training_keys, what_set, step_for_test = None, get_fights_UFC = False):
        fighter_df = [0]
        if len(training_keys) > 1:
            rand_key = random.randint(0, (len(training_keys) - 1))
        else:
            name = training_keys[0]
        if what_set == 'train':
            if len(training_keys) > 1:
                fighter_df = per_fighter_train_array[training_keys[rand_key]]
            else:
                fighter_df = per_fighter_train_array[name]
        elif what_set == 'test':
            fighter_df = per_fighter_test_array[name]
        fights_UFC = []
        for row, col in fighter_df.iterrows():
            if col['Ais_UFC'] == 1:
                fights_UFC.append(row + 2)
        if step_for_test == None:
            steps = fights_UFC[random.randint(0,(len(fights_UFC) - 1))]
        else:
            steps = step_for_test
        batch = fighter_df[:steps]
        X_batch = np.array(batch[:-1]).reshape(22, (steps - 1)).reshape((steps - 1), 22).reshape(-1, (steps - 1), 22)
        y_batch = np.array(batch[1:][['result', 'resultIn']]).reshape(2, (steps - 1)).reshape((steps - 1), 2).reshape(-1, (steps - 1), 2)
    #     y_batch = np.array(batch.tail(1)[['result', 'resultIn']]).reshape(2, 1).reshape(1, 2).reshape(1, 1, 2)
        if get_fights_UFC:
            return[X_batch, y_batch, fights_UFC]
        return [X_batch, y_batch]
    tf.reset_default_graph()
    X = tf.placeholder(tf.float32, [None, None, num_inputs])
    y = tf.placeholder(tf.float32, [None, None, num_outputs])
    cell = tf.contrib.rnn.OutputProjectionWrapper(tf.contrib.rnn.GRUCell(num_units=num_neurons, activation=tf.nn.relu),output_size=num_outputs) 
    outputs, states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)
    loss = tf.reduce_mean(tf.square(outputs - y)) # MSE
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train = optimizer.minimize(loss)
    init = tf.global_variables_initializer()
    saver = tf.train.Saver()
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
    with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
        saver.restore(sess, 'Models_per_weight/SD_RNN_' + weight_str_ + '_model')
        results = []
        cou = 0
        for name in names_test:
            fights_UFC = next_batch([name], 'test', get_fights_UFC = True)[2]
            for fight in fights_UFC:
                batch = next_batch([name], 'test', fight)
                X_batch = batch[0]
                y_batch = batch[1]
                y_true = y_batch[0, -1, :]
                y_pred = sess.run(outputs, feed_dict={X: X_batch})[0, -1, :]
    #           pred_eval = test_eval(y_pred, y_true)
                results.append([y_pred, y_true])
            if (cou % 20) == 0:
                print(weight_str_ + ' | ' + str(i) + ' | Test | ' + str(int((cou / len(names_test)) * 100)))
            cou = cou + 1
    final_results.append(get_report_arr(results_report(results,0.5,0.5,weight_str_)[0], weight_str_))


# In[62]:


for i in final_results:
    print(i)

