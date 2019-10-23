
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
def getFights(fighterA_html, upcomingFighterB_html, date_of_upcoming_fight, sex, ins = 1):
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
#         try:
        if True:
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
# ------For upcoming cards
    fighterAinfo = getFightInfo(fighterA_html, sex)
    fighterApreviousLength = fightDuration(getHistoryIns(fighterA_html)[-1])
    
    fighterBinfo = getFightInfo(upcomingFighterB_html, sex)
    fighterBpreviousLength = fightDuration(getHistoryIns(upcomingFighterB_html)[-1])
    data = [[fighterAinfo['name'], 
                   fighterAinfo['date_born'], 
                   fighterAinfo['is_male'], 
                   fighterAinfo['height'], 
                   fighterAinfo['weight'], 
                   date_of_upcoming_fight, 
                   1, 
                   fighterApreviousLength, 
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
                   date_of_upcoming_fight, 
                   1, 
                   fighterBpreviousLength, 
                   fighterBinfo['win_stk'], 
                   fighterBinfo['win_gra'], 
                   fighterBinfo['win_dec'], 
                   fighterBinfo['loss_stk'], 
                   fighterBinfo['loss_gra'], 
                   fighterBinfo['loss_dec'],
                   fighterAinfo['name'] + ' vs. ' + fighterBinfo['name'],
                   None,
                   None]]
    dfIns = pd.DataFrame(data =data, columns = columns)
    df = df.append(dfIns)
# -------------------------------
    return df    
# Get upcoming fight card fighter info
def getUpcomingCard(html, sex):
    fighter1List = []
    fighter2List = []
    sexList = sex
    getLink = html
    getDate = getLink.findAll('div', {'class': 'event_detail'})[0].findAll('span', {'class': 'date'})[0].text
    date = datetime.strptime(getDate, '%b %d, %Y')
    getEvent = getLink.find_all('div', {'class': 'event_detail'})[0]
    getEvent = getEvent.find_all('span', {'itemprop': 'name'})[0]
    getEvent = str(getEvent).split('<br/>')
    getEvent = getEvent[0].split('<span itemprop="name">')[1] + ' - ' + getEvent[1].split('</span>')[0]
    getMainCard = getLink.find_all('div', {'class': 'content event'})[0]
    getMainCard = getMainCard.find_all('div', {'class', 'fight'})[0]
    getMainCardF1 = getMainCard.find_all('div', {'class': 'fighter left_side'})[0]
    getMainCardF2 = getMainCard.find_all('div', {'class': 'fighter right_side'})[0]
    getMainCardF1L = getMainCardF1.find_all('a')[0]['href']
    getMainCardF2L = getMainCardF2.find_all('a')[0]['href']
    getMainCardF1L = 'https://www.sherdog.com' + getMainCardF1L
    getMainCardF2L = 'https://www.sherdog.com' + getMainCardF2L
    fighter1List.append(getMainCardF1L)
    fighter2List.append(getMainCardF2L)
    restFights = getLink.find_all('div', {'class': 'module event_match'})[0].find_all('tr')[1:]
    for i in restFights:
        rfF1L = i.find_all('a', {'itemprop': 'url'})[0]['href']
        rfF2L = i.find_all('a', {'itemprop': 'url'})[1]['href']
        rfF1L = 'https://www.sherdog.com' + rfF1L
        rfF2L = 'https://www.sherdog.com' + rfF2L
        fighter1List.append(rfF1L)
        fighter2List.append(rfF2L)
    return [fighter1List, fighter2List, sexList, date,  getEvent]


# In[3]:


# cards = {'UFC_240': ['https://www.sherdog.com/events/UFC-240-Holloway-vs-Edgar-76577', [1,0,1,1,1,0,1,1,1,0,1,1]],
#         'UFC_239': ['https://www.sherdog.com/events/UFC-239-Jones-vs-Santos-75113', [1,0,1,1,1,1,1,0,1,1,1,0]],
#         'UFC_FN_155': ['https://www.sherdog.com/events/UFC-Fight-Night-155-De-Randamie-vs-Ladd-76573', [0,1,1,1,1,1,1,0,1,1,0,1]],
#         'UFC_FN_154': ['https://www.sherdog.com/events/UFC-Fight-Night-154-Moicano-vs-The-Korean-Zombie-73349', [1,1,1,0,1,1,0,1,1,0,1]],
#         'UFC_ESPN_4': ['https://www.sherdog.com/events/UFC-on-ESPN-4-Dos-Anjos-vs-Edwards-76575', [1,1,1,1,1,1,1,0,1,0,1,1,1]],
#         'UFC_ESPN_3': ['https://www.sherdog.com/events/UFC-on-ESPN-3-Ngannou-vs-Dos-Santos-73351', [1,1,1,1,1,1,1,1,1,1,0,1]]}
cards = {'w': ['https://www.sherdog.com/events/UFC-242-Khabib-vs-Poirier-76401', [1,1,1,1,1,0,1,0,1,1,1,1,1]]}
for card_name in cards:
    upcomingCard = getUpcomingCard(getHTML(cards[card_name][0]), cards[card_name][1])

    columns = ['Aname', 'Adate_born', 'Ais_male', 'Aheight', 'Aweight', 'Adate_of_fight', 'Ais_UFC', 'Aprev_fight_length', 'Awin_stk', 'Awin_gra', 'Awin_dec', 'Aloss_stk', 'Aloss_gra', 'Aloss_dec','Bname', 'Bdate_born', 'Bis_male', 'Bheight', 'Bweight', 'Bdate_of_fight','Bis_UFC', 'Bprev_fight_length', 'Bwin_stk', 'Bwin_gra', 'Bwin_dec', 'Bloss_stk', 'Bloss_gra', 'Bloss_dec','event','result','resultIn']
    upcomingCardDF = pd.DataFrame(columns = columns)
#     ['_A_unfinished', '_B_unfinished']
    sets = ['_A_unfinished', '_B_unfinished']
    for i in sets:
        upcomingCardDF = pd.DataFrame(columns = columns)
        if i == '_A_unfinished':
            for itr in range(len(upcomingCard[0])):
                fightDF = getFights(getHTML(upcomingCard[0][itr]), getHTML(upcomingCard[1][itr]), upcomingCard[3], upcomingCard[2][itr], 100)
                upcomingCardDF = upcomingCardDF.append(fightDF)
        elif i == '_B_unfinished':
            for itr in range(len(upcomingCard[0])):
                fightDF = getFights(getHTML(upcomingCard[1][itr]), getHTML(upcomingCard[0][itr]), upcomingCard[3], upcomingCard[2][itr], 100)
                upcomingCardDF = upcomingCardDF.append(fightDF)
        upcomingCardDF.to_csv('Upcoming_card_datasets/SD_' + card_name + i +'.csv', index = False)
# --->


# In[4]:


# cards = {'UFC_240': ['https://www.sherdog.com/events/UFC-240-Holloway-vs-Edgar-76577', [1,0,1,1,1,0,1,1,1,0,1,1]],
#         'UFC_239': ['https://www.sherdog.com/events/UFC-239-Jones-vs-Santos-75113', [1,0,1,1,1,1,1,0,1,1,1,0]],
#         'UFC_FN_155': ['https://www.sherdog.com/events/UFC-Fight-Night-155-De-Randamie-vs-Ladd-76573', [0,1,1,1,1,1,1,0,1,1,0,1]],
#         'UFC_FN_154': ['https://www.sherdog.com/events/UFC-Fight-Night-154-Moicano-vs-The-Korean-Zombie-73349', [1,1,1,0,1,1,0,1,1,0,1]],
#         'UFC_ESPN_4': ['https://www.sherdog.com/events/UFC-on-ESPN-4-Dos-Anjos-vs-Edwards-76575', [1,1,1,1,1,1,1,0,1,0,1,1,1]],
#         'UFC_ESPN_3': ['https://www.sherdog.com/events/UFC-on-ESPN-3-Ngannou-vs-Dos-Santos-73351', [1,1,1,1,1,1,1,1,1,1,0,1]]}
cards = {'UFC_242': ['https://www.sherdog.com/events/UFC-242-Khabib-vs-Poirier-76401', [1,1,1,1,1,0,1,0,1,1,1,1,1]]}
for card_name in cards:
    sets = ['_A_unfinished', '_B_unfinished']
    for set_ in sets:
        print('Upcoming_card_datasets/SD_' + card_name + set_ +'.csv')
        upcomingCardDF = pd.read_csv('Upcoming_card_datasets/SD_' + card_name + set_ +'.csv')
        total_fightsB = []
        total_fightsA = []
        for i in upcomingCardDF.iterrows():
            totalB = i[1]['Bwin_stk'] + i[1]['Bwin_gra'] + i[1]['Bwin_dec'] + i[1]['Bloss_stk'] + i[1]['Bloss_gra'] + i[1]['Bloss_dec']
            total_fightsB.append(totalB)
            totalA = i[1]['Awin_stk'] + i[1]['Awin_gra'] + i[1]['Awin_dec'] + i[1]['Aloss_stk'] + i[1]['Aloss_gra'] + i[1]['Aloss_dec']
            total_fightsA.append(totalA)
        upcomingCardDF['Btotal_fights'] = total_fightsB
        upcomingCardDF['Atotal_fights'] = total_fightsA
        data = pd.read_csv('SD_dataset_for_RNN_v2_na_clean.csv')
        weight_avgs = data.groupby('Aweight').mean()
        new_heightB = []
        new_heightA = []
        for col, row in upcomingCardDF.iterrows():
            height = row['Bheight']
            weight = row['Aweight']
            if height > 0: new_heightB.append(height)
            else: new_heightB.append(int(weight_avgs[weight_avgs.index == weight]['Aheight'][weight]))
            height = row['Aheight']
            weight = row['Aweight']
            if height > 0:new_heightA.append(height)
            else:new_heightA.append(int(weight_avgs[weight_avgs.index == weight]['Aheight'][weight]))
        upcomingCardDF['Bheight'] = new_heightB
        upcomingCardDF['Aheight'] = new_heightA
        def toDT(x):
            try:
                return parse(x)
            except:
                return x
        data['Adate_born'], data['Adate_of_fight'] = (data['Adate_born'].apply(lambda x: toDT(x)), data['Adate_of_fight'].apply(lambda x: toDT(x)))
        data['Bdate_born'], data['Bdate_of_fight'] = (data['Bdate_born'].apply(lambda x: toDT(x)), data['Bdate_of_fight'].apply(lambda x: toDT(x)))
        upcomingCardDF['Adate_born'], upcomingCardDF['Adate_of_fight'] = (upcomingCardDF['Adate_born'].apply(lambda x: toDT(x)), upcomingCardDF['Adate_of_fight'].apply(lambda x: toDT(x)))
        upcomingCardDF['Bdate_born'], upcomingCardDF['Bdate_of_fight'] = (upcomingCardDF['Bdate_born'].apply(lambda x: toDT(x)), upcomingCardDF['Bdate_of_fight'].apply(lambda x: toDT(x)))
        results = []
        resultsIn = []
        for i in upcomingCardDF.iterrows():
            if (i[1]['result'] == 'Awins') or (i[1]['result'] == 'Bwins') or (i[1]['result'] == 'NC'):
                results.append(i[1]['result'])
                resultsIn.append(i[1]['resultIn'])
            else:
                results.append('Awins')
                if i[1]['Aweight'] > 150:
                    resultsIn.append('Inside')
                else:
                    resultsIn.append('Distance')
        upcomingCardDF['result'] = results
        upcomingCardDF['resultIn'] = resultsIn
        #Date Born
        clean_date_born = data.dropna(subset = ['Adate_born'])
        age_years = []
        for i in clean_date_born.iterrows():
            days_old = (i[1]['Adate_of_fight'] - i[1]['Adate_born']).days
            age_years.append(int(days_old/365))
        clean_date_born['Aage_years'] = age_years
        total_fights_avg_age = {}
        for i in clean_date_born.groupby('Atotal_fights').mean().iterrows():
            total_fights_avg_age[i[0]] = int(i[1]['Aage_years'])
        newBdate_born = []
        newAdate_born = []
        cou1 = 0
        cou2 = 0
        for col, row in upcomingCardDF.iterrows():
            if type(row['Bdate_born']) == pd._libs.tslib.Timestamp:
                newBdate_born.append(row['Bdate_born'])
            else:
                predicted_age = int(total_fights_avg_age[row['Btotal_fights']])
                predicted_date_born = row['Bdate_of_fight'] - pd.Timedelta(dt.timedelta(days = predicted_age * 365))
                newBdate_born.append(predicted_date_born)
            if type(row['Adate_born']) == pd._libs.tslib.Timestamp:
                newAdate_born.append(row['Adate_born'])
                cou1 = cou1 + 1
            else:
                predicted_age = int(total_fights_avg_age[row['Atotal_fights']])
                predicted_date_born = row['Adate_of_fight'] - pd.Timedelta(dt.timedelta(days = predicted_age * 365))
                newAdate_born.append(predicted_date_born)
                cou2 = cou2 + 1
        upcomingCardDF['Bdate_born'] = newBdate_born
        upcomingCardDF['Adate_born'] = newAdate_born
        Aages = []
        Bages = []
        for col, row in upcomingCardDF.iterrows():
            AdateB = row['Adate_born']
            AdateF = row['Adate_of_fight']
            Aage = AdateF - AdateB
            Aage = Aage.days
            Aages.append(Aage)
            BdateB = row['Bdate_born']
            BdateF = row['Bdate_of_fight']
            Bage = BdateF - BdateB
            Bage = Bage.days
            Bages.append(Bage)
        upcomingCardDF['Aage'] = Aages
        upcomingCardDF['Bage'] = Bages
        upcomingCardDF.drop(['Adate_born','Adate_of_fight','Bname', 'Bweight', 'Bdate_born','Bdate_of_fight', 'Atotal_fights', 'Btotal_fights', 'Bis_male', 'Bis_UFC'], axis = 1, inplace = True)
        weights = {'115':(0, 120), '125':(120, 130), '135':(130, 140), '145':(140, 150), '155':(150, 165), '170':(165, 180),
                             '185':(180, 195), '205':(195, 215), '265':(215, 1000)}
        scaledUpcomingCardDF = pd.DataFrame(columns = list(upcomingCardDF.columns))
        for name in list(dict.fromkeys(list(upcomingCardDF['Aname']))):
            name_df = upcomingCardDF[upcomingCardDF['Aname'] == name]
            name_weight = int(list(name_df['Aweight'])[0])
            for weight in weights:
                if name_weight > weights[weight][0] and name_weight <= weights[weight][1]:
                    weight_scalar = joblib.load('Scalar_per_weight/SD_new_2_' + weight + '_scalar.pkl')
                    scaled_df = weight_scalar.transform(name_df.drop(['Aname', 'Aweight', 'event', 'result', 'resultIn'], axis = 1))
                    name_df[['Ais_male', 'Aheight', 'Ais_UFC', 'Aprev_fight_length',
                   'Awin_stk', 'Awin_gra', 'Awin_dec', 'Aloss_stk', 'Aloss_gra',
                   'Aloss_dec', 'Bheight',
                   'Bprev_fight_length', 'Bwin_stk', 'Bwin_gra', 'Bwin_dec', 'Bloss_stk',
                   'Bloss_gra', 'Bloss_dec', 'Aage',
                   'Bage']] = scaled_df
            scaledUpcomingCardDF = pd.concat([scaledUpcomingCardDF, name_df], ignore_index=True)
#         for weight in weights:
#             weight_df = upcomingCardDF[(upcomingCardDF['Aweight'] > weights[weight][0]) & (upcomingCardDF['Aweight'] <= weights[weight][1])]
#             if len(weight_df) > 0:
#                 weight_scalar = joblib.load('Scalar_per_weight/SD_' + weight + '_scalar.pkl')
#                 scaled_df = weight_scalar.transform(weight_df.drop(['Aname', 'Aweight', 'event', 'result', 'resultIn'], axis = 1))
#                 weight_df[['Ais_male', 'Aheight', 'Ais_UFC', 'Aprev_fight_length',
#                'Awin_stk', 'Awin_gra', 'Awin_dec', 'Aloss_stk', 'Aloss_gra',
#                'Aloss_dec', 'Bheight',
#                'Bprev_fight_length', 'Bwin_stk', 'Bwin_gra', 'Bwin_dec', 'Bloss_stk',
#                'Bloss_gra', 'Bloss_dec', 'Aage',
#                'Bage']] = scaled_df
#             scaledUpcomingCardDF = pd.concat([scaledUpcomingCardDF, weight_df], ignore_index=True)
        if '_A_unfinished' == set_:
            scaledUpcomingCardDF.to_csv('Upcoming_card_datasets/SD_' + card_name + '_A.csv', index = False)
        elif '_B_unfinished' == set_:
            scaledUpcomingCardDF.to_csv('Upcoming_card_datasets/SD_' + card_name + '_B.csv', index = False)

