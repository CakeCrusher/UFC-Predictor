
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns
import datetime as dt
from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests
from dateutil.parser import parse
import cfscrape
import time
from sklearn.externals import joblib 


# In[2]:


# Reference timer
startTime = datetime.now()
def timer():
    global startTime
    secondsPassed = (datetime.now() - startTime).seconds
    def addzero(x):
        if len(x) == 1:
            x = '0' + x
        return x
    sec = addzero(str(int(secondsPassed % 60)))
    minu = addzero(str(int((secondsPassed/60) % 60)))
    hr = addzero(str(int(secondsPassed/60/60)))
    return '[' + str(hr) + ':' + str(minu) + ':' + str(sec) + '] '
# Fighter variables
event = None
name = None
date_of_fight = None
date_born = None
is_male = 0
height = None
weight = None
is_UFC = None

prev_fight_length = 0
win_stk = 0
win_gra = 0
win_dec = 0
loss_stk = 0
loss_gra = 0
loss_dec = 0

def resetInfo():
    global event
    global name
    global date_of_fight
    global date_born
    global is_male
    global height
    global weight
    global is_UFC

    global prev_fight_length
    global win_stk
    global win_gra
    global win_dec
    global loss_stk
    global loss_gra
    global loss_dec

    event = None
    name = None
    date_of_fight = None
    date_born = None
    is_male = 0
    height = None
    weight = None
    is_UFC = None

    prev_fight_length = 0
    win_stk = 0
    win_gra = 0
    win_dec = 0
    loss_stk = 0
    loss_gra = 0
    loss_dec = 0
# Base for scraping Sherdog
def getHTML(link):
    scraper = cfscrape.create_scraper(delay = 10)
    req = scraper.get(link).content
#     print('Sleeping...')
#     time.sleep(5)
    return bs(req)
def getHistoryIns(html, start = 'new'):
    fighter = html
    historyFull = None
    for i in fighter.find_all('div', {'class': 'module fight_history'}):
        if 'Fight History - Pro' == i.find_all('h2')[0].text:
            historyFull = i
    historyIns = historyFull.find_all('tr')[1:]
    if start == 'new':
        historyIns.reverse()
    elif start == 'old':
        pass
    return historyIns
# Functions to get variables given a history instance
def isWin(historyIns):
    getResult = historyIns.find_all('span', {'class': 'final_result'})[0].text
    if getResult == 'win':
        return True
    elif getResult == 'loss':
        return False
    else:
        return 'NC'

def isUFC(historyIns, update = False):
    getUFC = historyIns.find_all('td')[2].text
    if update:
        global is_UFC
        if 'UFC' in getUFC :
            if 'UFCF' in getUFC:
                is_UFC = 0
            else:
                is_UFC = 1
        else:
            is_UFC = 0
    else:
        if 'UFC' in getUFC :
            if 'UFCF' in getUFC:
                return False
            else:
                return True
        else:
            return False
    
def resultBy(historyIns, update = False):
    getResult = isWin(historyIns)
    getBy = historyIns.find_all('td')[3].text
    getBy = getBy.split('(')[0][:-1]
    forStk = ['KO', 'TKO']
    forGra = ['Submission', 'Technical Submission']
    forDec = ['Decision', 'Decision']
    if update:
        global win_stk
        global win_gra
        global win_dec
        global loss_stk
        global loss_gra
        global loss_dec
        for r in range(2):
            if getResult:
                if forStk[r] in getBy:
                    win_stk = win_stk + 1
                    break
                elif forGra[r] in getBy:
                    win_gra = win_gra + 1
                    break
                elif forDec[r] in getBy:
                    win_dec = win_dec + 1
                    break
                else:
                    pass
            elif getResult == False:
                if forStk[r] in getBy:
                    loss_stk = loss_stk + 1
                    break
                elif forGra[r] in getBy:
                    loss_gra = loss_gra + 1
                    break
                elif forDec[r] in getBy:
                    loss_dec = loss_dec + 1
                    break
                else:
                    pass
            else:
                pass
    else:
        for r in range(2):
            if getResult == True:
                if forStk[r] in getBy:
                    return 'win_stk'
                    break
                elif forGra[r] in getBy:
                    return 'win_gra'
                    break
                elif forDec[r] in getBy:
                    return 'win_dec'
                    break
                else:
                    return 'NC'
            elif getResult == False:
                if forStk[r] in getBy:
                    return 'loss_stk'
                    break
                elif forGra[r] in getBy:
                    return 'loss_gra'
                    break
                elif forDec[r] in getBy:
                    return 'loss_dec'
                    break
                else:
                    return 'NC'
            elif getResult == 'NC':
                return 'NC'
    
def fightDuration(historyIns, update = False):
    getRound = float(historyIns.find_all('td')[4].text)
    getTime = historyIns.find_all('td')[5].text
    try:
        roundToSec = float((getRound - 1) * 300)
    except:
        roundToSec = 0
    try:
        timeToSecM = float(float(getTime.split(':')[0]) * 60)
    except:
        timeToSecM = 0
    try:
        timeToSecS = float(getTime.split(':')[1])
    except:
        timeToSecS = 0
    tTime = int(roundToSec + timeToSecM + timeToSecS)
    if update:
        global prev_fight_length
        prev_fight_length = tTime
    else:
        return tTime
def resultIn(historyIns):
    by = resultBy(historyIns, False)
    if by == 'win_dec' or by == 'loss_dec':
        return 0
    else:
        return 1
def getDate(historyIns, update = False):
    date = historyIns.find_all('td')[2].find_all('span',{'class':'sub_line'})[0].text
    dtDate = datetime.strptime(date, '%b / %d / %Y')
    if update:
        global date_of_fight
        date_of_fight = dtDate
    else:
        return dtDate
def getEvent(historyIns, update = False):
    ev = historyIns.find_all('td')[2].find_all('a')[0].text
    if update:
        global event
        event = ev
    else:
        return ev
def getFighters(history_ins, isMale, depth = None, exclusiveUFC = False):
    fighterNL = []
    if depth == None:
        depth = len(history_ins)
    for i in history_ins[-depth:]:
        if exclusiveUFC:
            if isUFC(i, False):
                link = 'https://www.sherdog.com' + i.find_all('td')[1].find_all('a')[0]['href']
                name = link.split('/')[-1].split('-')
                try:
                    name = name[0] + ' ' + name[1]
                except:
                    name = name[0]
                fighterNL.append([name,link, isMale])
        else:
            link = 'https://www.sherdog.com' + i.find_all('td')[1].find_all('a')[0]['href']
            name = link.split('/')[-1].split('-')
            try:
                name = name[0] + ' ' + name[1]
            except:
                name = name[0]
            fighterNL.append([name,link, isMale])
    return pd.DataFrame(data = fighterNL, columns = ['Name', 'Link', 'isMale'])
# Gets fighter info at a specific event
def getFightInfo(html, is_male_in, event_in = None):
    resetInfo()
    global name
    global date_born
    global is_male
    global height
    global weight
    global event
    global date_of_fight
    global is_UFC
    global prev_fight_length
    global win_stk
    global win_gra
    global win_dec
    global loss_stk
    global loss_gra
    global loss_dec
    fighterHTML = html
    #General facts
    try:
        date_born = datetime.strptime(fighterHTML.find_all('span', {'itemprop': 'birthDate'})[0].text, '%Y-%m-%d')
    except:
        date_born = None
    try:
        height = fighterHTML.find_all('strong', {'itemprop': 'height'})[0].text
        heightIn = (int(height.split('\'')[0][0]) * 12) + int(height.split('\'')[1][:-1])
        height = heightIn
    except:
        height = None
    try:
        weight = fighterHTML.find_all('strong', {'itemprop': 'weight'})[0].text
        pounds = int(weight.split(' ')[0])
        weight = pounds
    except:
        weight = None
    name = fighterHTML.find_all('span', {'class': 'fn'})[0].text 
    is_male = is_male_in
    
    #Event Facts
    event = event_in
    historyIns = getHistoryIns(html)
    for ins in historyIns:
        index = historyIns.index(ins)
        if getEvent(ins) == event:
            getDate(ins, True)
            isUFC(ins, True)
            if index == 0:
                prev_fight_length = 0
                break
            fightDuration(historyIns[index - 1], True)
            break
        resultBy(ins, True)
    
    info = {'name': name, 'date_born': date_born, 'is_male': is_male, 'height': height, 'weight': weight, 
            'event': event, 'date_of_fight': date_of_fight, 'is_UFC': is_UFC, 'prev_fight_length': prev_fight_length, 
            'win_stk': win_stk, 'win_gra': win_gra, 'win_dec': win_dec, 'loss_stk': loss_stk, 'loss_gra': loss_gra, 'loss_dec': loss_dec}
    resetInfo()
    return info
# Get all of fighter's fights with history
def getFights(fighterA_html, sex, ins = 1):
    columns = ['Aname', 
               'Adate_born', 
               'Ais_male', 
               'Aheight', 
               'Aweight', 
               'Adate_of_fight', 
               'Ais_UFC', 
               'Aprev_fight_length', 
               'Awin_stk', 
               'Awin_gra', 
               'Awin_dec', 
               'Aloss_stk', 
               'Aloss_gra', 
               'Aloss_dec',
               'Bname', 
               'Bdate_born', 
               'Bis_male', 
               'Bheight', 
               'Bweight', 
               'Bdate_of_fight', 
               'Bis_UFC', 
               'Bprev_fight_length', 
               'Bwin_stk', 
               'Bwin_gra', 
               'Bwin_dec', 
               'Bloss_stk', 
               'Bloss_gra', 
               'Bloss_dec',
               'event',
               'result',
               'resultIn']
    df = pd.DataFrame(columns = columns)
    fightHistory = getHistoryIns(fighterA_html)
    ev = None
    if len(fightHistory) < ins:
        ins = len(fightHistory)
    for i in range(len(fightHistory)-ins, len(fightHistory)):
        try:
#         if True:
            ev = getEvent(fightHistory[i])
            fighterBLink = getFighters(getHistoryIns(fighterA_html), sex)['Link'][i]
            fighterAinfo = getFightInfo(fighterA_html, sex, ev)
            fighterBinfo = getFightInfo(getHTML(fighterBLink), sex, ev)
            names = sorted([fighterAinfo['name'], fighterBinfo['name']])
            index = names[0] + ' vs. ' + names[1] + ' | ' + ev
            result = None
            resultIn = None
            print(timer() + 'Ran: ' + str(fighterAinfo['name']) + ' vs. ' + str(fighterBinfo['name']) + '\tEvent: ' + str(ev))
            for j in fightHistory:
                if ev in str(j):
                    res = isWin(j)
                    if res == True:
                        result = 'Awins'
                    elif res == False:
                        result = 'Bwins'
                    elif res == 'NC':
                        result = 'NC'
                    getBy = j.find_all('td')[3].text
                    getBy = getBy.split('(')[0][:-1]
                    if 'Decision' in getBy:
                        resultIn = 'Distance'
                    else:
                        resultIn = 'Inside'
            data = [[fighterAinfo['name'], 
                   fighterAinfo['date_born'], 
                   fighterAinfo['is_male'], 
                   fighterAinfo['height'], 
                   fighterAinfo['weight'], 
                   fighterAinfo['date_of_fight'], 
                   fighterAinfo['is_UFC'], 
                   fighterAinfo['prev_fight_length'], 
                   fighterAinfo['win_stk'], 
                   fighterAinfo['win_gra'], 
                   fighterAinfo['win_dec'], 
                   fighterAinfo['loss_stk'], 
                   fighterAinfo['loss_gra'], 
                   fighterAinfo['loss_dec'],
                   fighterBinfo['name'], 
                   fighterBinfo['date_born'], 
                   fighterBinfo['is_male'], 
                   fighterBinfo['height'], 
                   fighterBinfo['weight'], 
                   fighterBinfo['date_of_fight'], 
                   fighterBinfo['is_UFC'], 
                   fighterBinfo['prev_fight_length'], 
                   fighterBinfo['win_stk'], 
                   fighterBinfo['win_gra'], 
                   fighterBinfo['win_dec'], 
                   fighterBinfo['loss_stk'], 
                   fighterBinfo['loss_gra'], 
                   fighterBinfo['loss_dec'],
                   ev,
                   result,
                   resultIn]]
            dfIns = pd.DataFrame(data =data, columns = columns)
            df = df.append(dfIns)
        except:
            print('ERROR: skipped')
    return df    


# In[3]:


fighter_links = pd.read_csv('SD_RNN_fighter_links.csv')


# In[6]:


fighter_links.tail(len(fighter_links) - 830)


# In[5]:


pd.read_csv('SD_RNN_new_full_data.csv')


# In[7]:


# fighter_main_df = pd.DataFrame(columns = ['Aname', 'Adate_born', 'Ais_male', 'Aheight', 'Aweight', 'Adate_of_fight', 'Ais_UFC', 'Aprev_fight_length', 'Awin_stk', 'Awin_gra', 'Awin_dec', 'Aloss_stk', 'Aloss_gra', 'Aloss_dec','Bname', 'Bdate_born', 'Bis_male', 'Bheight', 'Bweight', 'Bdate_of_fight','Bis_UFC', 'Bprev_fight_length', 'Bwin_stk', 'Bwin_gra', 'Bwin_dec', 'Bloss_stk', 'Bloss_gra', 'Bloss_dec','event','result','resultIn'])
fighter_main_df = pd.read_csv('SD_RNN_new_full_data.csv')
cou = 0
for col, row in fighter_links.tail(len(fighter_links) - 830).iterrows():
    fighter_df = getFights(getHTML(row['Link']), row['isMale'], 100)
    fighter_main_df = pd.concat([fighter_main_df, fighter_df], ignore_index = True)
    print(cou)
    fighter_main_df.to_csv('SD_RNN_new_full_data.csv', index = False)
    cou = cou + 1

