
# coding: utf-8

# In[1]:


# User input
upFightURLSD = 'https://www.sherdog.com/events/UFC-Fight-Night-150-Jacare-vs-Hermansson-73337'
upFightURLUG = 'https://www.mixedmartialarts.com/events/UFC-on-ESPN-8:B4B6BFAF-DE6B-4006-85C4-DF5F441E81F3'
upFightSexArrSD = [1,1,1,1,1,1,1,1,0,1,0,1,1]
upFightSexArrUG = [1,1,1,1,1,1,1,0,1,1,1,0,1]


# In[23]:


# Imports
import bs4
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
from datetime import datetime
import requests
from dateutil.relativedelta import relativedelta
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from sklearn.externals import joblib


# In[3]:


startTime = datetime.now()


# In[4]:


# Reference timer
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


# In[70]:


# Fighter variables
age = None
height = None
weight = None
timePro = None
timeUFC = None

wins = 0
losses = 0
winStk = 0
winGra = 0
winDec = 0
winOtr = 0
lossStk = 0
lossGra = 0
lossDec = 0
lossOtr = 0
ufcCount = 0
avgLength = 0
streak = 0
isMale = 0
l3Wins = 0
l3Losses = 0
l3WinStk = 0
l3WinGra = 0
l3WinDec = 0
l3WinOtr = 0
l3LossStk = 0
l3LossGra = 0
l3LossDec = 0
l3LossOtr = 0

event = None
name = None
def resetInfo():
    global age
    global height
    global weight
    global timePro
    global timeUFC
    global wins
    global losses
    global winStk
    global winGra
    global winDec
    global winOtr
    global lossStk
    global lossGra
    global lossDec
    global lossOtr
    global ufcCount
    global avgLength
    global streak
    global isMale
    global l3Wins
    global l3Losses
    global l3WinStk
    global l3WinGra
    global l3WinDec
    global l3WinOtr
    global l3LossStk
    global l3LossGra
    global l3LossDec
    global l3LossOtr
    global event
    global name
    age = None
    height = None
    weight = None
    timePro = None
    timeUFC = None
    wins = 0
    losses = 0
    winStk = 0
    winGra = 0
    winDec = 0
    winOtr = 0
    lossStk = 0
    lossGra = 0
    lossDec = 0
    lossOtr = 0
    ufcCount = 0
    avgLength = 0
    streak = 0
    isMale = 0
    l3Wins = 0
    l3Losses = 0
    l3WinStk = 0
    l3WinGra = 0
    l3WinDec = 0
    l3WinOtr = 0
    l3LossStk = 0
    l3LossGra = 0
    l3LossDec = 0
    l3LossOtr = 0
    event = None
    name = None


# In[71]:


# Base for scraping Sherdog
def getHTMLSD(link):
    return bs(requests.get(link).content)
def getHistoryInsSD(link, start = 'new'):
    fighter = getHTMLSD(link)
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


# In[72]:


# Base navigators
def getHTMLUG(link):
    return bs(requests.get(link).content)
def getHistoryInsUG(link, start = 'new'):
    fighter = getHTMLUG(link)
    histories = fighter.find_all('div', {'class': 'section-wrapper mma-record'})
    historyFull = histories[0].find_all('tbody')[0].find_all('tr')
    for ins in histories:
        if 'UFC' in str(ins):
            historyFull = ins.find_all('tbody')[0].find_all('tr')
    historyIns = historyFull
#     if 'TBD' in str(historyFull[0]):
#         historyIns = historyFull[1:]
    if start == 'new':
        historyIns.reverse()
    elif start == 'old':
        pass
    return historyIns


# In[73]:


# Functions to get variables given a history instance
def isWinSD(historyIns, update = True, updateWhich = 'all'):
    global wins
    global losses
    global l3Wins
    global l3Losses
    getResult = historyIns.find_all('span', {'class': 'final_result'})[0].text
    if update:
        if updateWhich == 'all':
            if getResult == 'win':
                wins = wins + 1
            elif getResult == 'loss':
                losses = losses + 1
            else:
                pass
        elif updateWhich == 'l3':
            if getResult == 'win':
                l3Wins = l3Wins + 1
            elif getResult == 'loss':
                l3Losses = l3Losses + 1
            else:
                pass
    else:
        if getResult == 'win':
            return True
        elif getResult == 'loss':
            return False
        else:
            return None

def isUFCSD(historyIns, update = True):
    global ufcCount
    getUFC = historyIns.find_all('td')[2].text[0:3]
    if update:
        if getUFC == 'UFC':
            ufcCount = ufcCount + 1
        else:
            pass
    else:
        if getUFC == 'UFC':
            return True
        else:
            return False
    
def resultBySD(historyIns, update = True, updateWhich = 'all'):
    global winStk
    global winGra
    global winDec
    global winOtr
    global lossStk
    global lossGra
    global lossDec
    global lossOtr
    global l3WinStk
    global l3WinGra
    global l3WinDec
    global l3WinOtr
    global l3LossStk
    global l3LossGra
    global l3LossDec
    global l3LossOtr
    getResult = isWinSD(historyIns, False)
    getBy = historyIns.find_all('td')[3].text
    getBy = getBy.split('(')[0][:-1]
    forStk = ['KO', 'TKO']
    forGra = ['Submission', 'Technical Submission']
    forDec = ['Decision']
    forOtr = ['DQ']
    if update:
        if updateWhich == 'all':
            if getResult:
                if getBy in forStk:
                    winStk = winStk + 1
                elif getBy in forGra:
                    winGra = winGra + 1
                elif getBy in forDec:
                    winDec = winDec + 1
                elif getBy in forOtr:
                    winOtr = winOtr + 1
                else:
                    pass
            elif getResult == False:
                if getBy in forStk:
                    lossStk = lossStk + 1
                elif getBy in forGra:
                    lossGra = lossGra + 1
                elif getBy in forDec:
                    lossDec = lossDec + 1
                elif getBy in forOtr:
                    lossOtr = lossOtr + 1
                else:
                    pass
        elif updateWhich == 'l3':
            if getResult:
                if getBy in forStk:
                    l3WinStk = l3WinStk + 1
                elif getBy in forGra:
                    l3WinGra = l3WinGra + 1
                elif getBy in forDec:
                    l3WinDec = l3WinDec + 1
                elif getBy in forOtr:
                    l3WinOtr = l3WinOtr + 1
                else:
                    pass
            elif getResult == False:
                if getBy in forStk:
                    l3LossStk = l3LossStk + 1
                elif getBy in forGra:
                    l3LossGra = l3LossGra + 1
                elif getBy in forDec:
                    l3LossDec = l3LossDec + 1
                elif getBy in forOtr:
                    l3LossOtr = l3LossOtr + 1
                else:
                    pass
        else:
            pass
    else:
        if getResult == 'win':
            if getBy in forStk:
                return 'winStk'
            elif getBy in forGra:
                return 'winGra'
            elif getBy in forDec:
                return 'winDec'
            elif getBy in forOtr:
                return 'winOtr'
            else:
                pass
        elif getResult == 'loss':
            if getBy in forStk:
                return 'lossStk'
            elif getBy in forGra:
                return 'lossGra'
            elif getBy in forDec:
                return 'lossDec'
            elif getBy in forOtr:
                return 'lossOtr'
            else:
                pass
        else:
            pass
    
def addTimeSD(historyIns, update = True):
    global avgLength
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
    tTime = roundToSec + timeToSecM + timeToSecS
    if update:
        avgLength = avgLength + tTime
    else:
        return tTime
def matchStreakSD(historyIns, update = True):
    global streak
    if update:
        if isWinSD(historyIns, False):
            if streak >= 0:
                streak = streak + 1
            else:
                streak = 0
                streak = streak + 1
        elif isWinSD(historyIns, False) == False:
            if streak <= 0:
                streak = streak - 1
            else:
                streak = 0
                streak = streak - 1
        else:
            pass
    else:
        return streak
def resultInSD(historyIns):
    by = resultBySD(historyIns, False)
    if by == 'winDec' or by == 'lossDec':
        return 0
    else:
        return 1
def getDateSD(historyIns):
    return datetime.strptime(historyIns.find_all('td')[2].find_all('span',{'class':'sub_line'})[0].text, '%b / %d / %Y')


# In[74]:


# Fight info navigators
def isWinUG(historyIns, update = True, updateWhich = 'all'):
    global wins
    global losses
    global l3Wins
    global l3Losses
    getResult = historyIns.find_all('td')[2].find_all('span')[0].text.replace(' ', '')
    if update:
        if updateWhich == 'all':
            if getResult == 'W':
                wins = wins + 1
            elif getResult == 'L':
                losses = losses + 1
            else:
                pass
        elif updateWhich == 'l3':
            
            if getResult == 'W':
                l3Wins = l3Wins + 1
            elif getResult == 'L':
                l3Losses = l3Losses + 1
            else:
                pass
    else:
        if getResult == 'W':
            return True
        elif getResult == 'L':
            return False
        else:
            return None

def isUFCUG(historyIns, update = True):
    global ufcCount
    getUFC = historyIns.find_all('td')[5].find_all('a')[0].text[0:3]
    getFTV = historyIns.find_all('td')[5].find_all('a')[0].text[0:7]
    if update:
        if getUFC == 'UFC' or getFTV == 'Fuel TV':
            ufcCount = ufcCount + 1
        else:
            pass
    else:
        if getUFC == 'UFC' or getFTV == 'Fuel TV':
            return True
        else:
            return False
    
def resultByUG(historyIns, update = True, updateWhich = 'all'):
    global winStk
    global winGra
    global winDec
    global winOtr
    global lossStk
    global lossGra
    global lossDec
    global lossOtr
    global l3WinStk
    global l3WinGra
    global l3WinDec
    global l3WinOtr
    global l3LossStk
    global l3LossGra
    global l3LossDec
    global l3LossOtr
    getResult = isWinUG(historyIns, False)
    getBy = historyIns.find_all('td')[5].find_all('a')[0].text
    getBy = historyIns.find_all('td')[5].text.strip()[0: - (len(getBy))]
    getBy = getBy.split('(')[0].strip()
    forStk = ['KO', 'TKO', 'TKO/RSC']
    forGra = ['Submission']
    forDec = ['Decision']
    forOtr = ['Disqualification', 'No Contest']
    if update:
        if updateWhich == 'all':
            if getResult:
                if getBy in forStk:
                    winStk = winStk + 1
                elif getBy in forGra:
                    winGra = winGra + 1
                elif getBy in forDec:
                    winDec = winDec + 1
                elif getBy in forOtr:
                    winOtr = winOtr + 1
                else:
                    pass
            elif getResult == False:
                if getBy in forStk:
                    lossStk = lossStk + 1
                elif getBy in forGra:
                    lossGra = lossGra + 1
                elif getBy in forDec:
                    lossDec = lossDec + 1
                elif getBy in forOtr:
                    lossOtr = lossOtr + 1
                else:
                    pass
        elif updateWhich == 'l3':
            if getResult:
                if getBy in forStk:
                    l3WinStk = l3WinStk + 1
                elif getBy in forGra:
                    l3WinGra = l3WinGra + 1
                elif getBy in forDec:
                    l3WinDec = l3WinDec + 1
                elif getBy in forOtr:
                    l3WinOtr = l3WinOtr + 1
                else:
                    pass
            elif getResult == False:
                if getBy in forStk:
                    l3LossStk = l3LossStk + 1
                elif getBy in forGra:
                    l3LossGra = l3LossGra + 1
                elif getBy in forDec:
                    l3LossDec = l3LossDec + 1
                elif getBy in forOtr:
                    l3LossOtr = l3LossOtr + 1
                else:
                    pass
        else:
            pass
    else:
        if getResult:
            if getBy in forStk:
                return 'winStk'
            elif getBy in forGra:
                return 'winGra'
            elif getBy in forDec:
                return 'winDec'
            elif getBy in forOtr:
                return 'winOtr'
            else:
                pass
        elif getResult == False:
            if getBy in forStk:
                return 'lossStk'
            elif getBy in forGra:
                return 'lossGra'
            elif getBy in forDec:
                return 'lossDec'
            elif getBy in forOtr:
                return 'lossOtr'
            else:
                pass
        else:
            pass
    
def addTimeUG(historyIns, update = True):
    global avgLength
    global wins
    global losses
    try:
        getRound = float(historyIns.find_all('td')[6].text.strip())
        roundToSec = float((getRound - 1) * 300)
        try:
            getTime = historyIns.find_all('td')[7].text.strip().split(':')
            timeToSecM = float(getTime[0]) * 60
            timeToSecS = float(getTime[1])
        except:
            timeToSecM = 5 * 60
            timeToSecS = 0
    except:
        timeToSecM = avgLength / (wins + losses)
        timeToSecS = 0
        roundToSec = 0
    tTime = roundToSec + timeToSecM + timeToSecS
    if update:
        avgLength = avgLength + tTime
    else:
        return int(tTime)
def matchStreakUG(historyIns, update = True):
    global streak
    if update:
        if isWinUG(historyIns, False):
            if streak >= 0:
                streak = streak + 1
            else:
                streak = 0
                streak = streak + 1
        elif isWinUG(historyIns, False) == False:
            if streak <= 0:
                streak = streak - 1
            else:
                streak = 0
                streak = streak - 1
        else:
            pass
    else:
        return streak
def resultInUG(historyIns):
    by = resultByUG(historyIns, False)
    if by == 'winDec' or by == 'lossDec':
        return 0
    else:
        return 1
def weightClassUG(historyIns, update = True):
    global weight
    wClass = historyIns.find_all('td')[4].text.split('(')[0].strip()
    if update:
        if wClass == 'SW':
            weight = 115
        elif wClass == 'FLY':
            weight = 125
        elif wClass == 'BW':
            weight = 135
        elif wClass == 'FTW':
            weight = 145
        elif wClass == 'LW':
            weight = 155
        elif wClass == 'WW':
            weight = 170
        elif wClass == 'MW':
            weight = 185
        elif wClass == 'LHW':
            weight = 205
        elif wClass == 'HW':
            weight = 265
        else:
            weight = 0
    else:
        if wClass == 'SW':
            return 115
        elif wClass == 'FLY':
            return 125
        elif wClass == 'BW':
            return 135
        elif wClass == 'FTW':
            return 145
        elif wClass == 'LW':
            return 155
        elif wClass == 'WW':
            return 170
        elif wClass == 'MW':
            return 185
        elif wClass == 'LHW':
            return 205
        elif wClass == 'HW':
            return 265
        else:
            return 0
def getEventUG(historyIns, update = True):
    global event
    ev = historyIns.find_all('td')[5].find_all('a')[0].text
    if update:
        event = ev
    else:
        return ev
def getDateUG(historyIns):
    return datetime.strptime(historyIns.find_all('td')[1].text, '%m/%d/%Y')


# In[75]:


# Gets fighters links into a dataFrame
def getFightersSD(x, isMale, depth = None, exclusiveUFC = False):
    fighterNL = []
    if depth == None:
        depth = len(x)
    for i in x[-depth:]:
        if exclusiveUFC:
            if isUFCSD(i, False):
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


# In[59]:


# Gets base fighter links
fighterLinksBaseSD = pd.DataFrame(columns = ['Name', 'Link', 'isMale'])
perWeightSD = [['https://www.sherdog.com/fighter/Demetrious-Johnson-45452', 1],
            ['https://www.sherdog.com/fighter/Cody-Garbrandt-50381', 1],
            ['https://www.sherdog.com/fighter/Max-Holloway-38671', 1],
            ['https://www.sherdog.com/fighter/Khabib-Nurmagomedov-56035', 1],
            ['https://www.sherdog.com/fighter/Tyron-Woodley-42605', 1],
            ['https://www.sherdog.com/fighter/Kelvin-Gastelum-74700', 1],
            ['https://www.sherdog.com/fighter/Jon-Jones-27944', 1],
            ['https://www.sherdog.com/fighter/Stipe-Miocic-39537', 1],
            ['https://www.sherdog.com/fighter/Rose-Namajunas-69083', 0],
            ['https://www.sherdog.com/fighter/Amanda-Nunes-31496', 0],
            ['https://www.sherdog.com/fighter/Cristiane-Justino-14477', 0]]

for icon in perWeightSD:
    fighterLinksBaseSD = fighterLinksBaseSD.append(getFightersSD(getHistoryInsSD(icon[0]), icon[1], 2))


# In[76]:


# Gets Links
def getFightersUG(fullHistoryIns, isMale, depth = None, exclusiveUFC = False):
    fighterNL = []
    if depth == None:
        depth = len(fullHistoryIns)
    for historyIns in fullHistoryIns[-depth:]:
        if exclusiveUFC:
            if isUFCUG(historyIns, False):
                link = historyIns.find_all('td')[3].find_all('a')[0]['href']
                name = link.split('/')[-1].split(':')[0].split('-')
                try:
                    name = name[0] + ' ' + name[1]
                except:
                    name = name[0]
                fighterNL.append([name,link, isMale])
        else:
            link = historyIns.find_all('td')[3].find_all('a')[0]['href']
            name = link.split('/')[-1].split(':')[0].split('-')
            try:
                name = name[0] + ' ' + name[1]
            except:
                name = name[0]
            fighterNL.append([name,link, isMale])
    return pd.DataFrame(data = fighterNL, columns = ['Name', 'Link', 'isMale'])


# In[61]:


# Base fighter links
fighterLinksBaseUG = pd.DataFrame(columns = ['Name', 'Link', 'isMale'])
perWeightUG = [['https://www.mixedmartialarts.com/fighter/Demetrious-Johnson:D681F3F25DB7BEEB', 1],
            ['https://www.mixedmartialarts.com/fighter/TJ-Dillashaw:CC7D826E1CFB164B', 1],
            ['https://www.mixedmartialarts.com/fighter/Max-Holloway:F440FE8FB69BA429', 1],
            ['https://www.mixedmartialarts.com/fighter/Khabib-Nurmagomedov:39939F242336C509', 1],
            ['https://www.mixedmartialarts.com/fighter/Kamaru-Usman:8E61AD697A432F19', 1],
            ['https://www.mixedmartialarts.com/fighter/Robert-Whittaker:7A1D476487A26725', 1],
            ['https://www.mixedmartialarts.com/fighter/Jon-Jones:54494EFC3CC798A0', 1],
            ['https://www.mixedmartialarts.com/fighter/Daniel-Cormier:53958F286CF4E375', 1],
            ['https://www.mixedmartialarts.com/fighter/Rose-Namajunas:9408C6D89D0DB238', 0],
            ['https://www.mixedmartialarts.com/fighter/Joanna-Jedrzejczyk:0051C6C13025D023', 0],
            ['https://www.mixedmartialarts.com/fighter/Carla-Esparza:B35CB0DC656CB371', 0],
            ['https://www.mixedmartialarts.com/fighter/Amanda-Nunes:15BFA19E4F6C08A5', 0],
            ['https://www.mixedmartialarts.com/fighter/Ronda-Rousey:985A093AE973B42C', 0],
            ['https://www.mixedmartialarts.com/fighter/Cris-Cyborg:693D2477DC0D92D2', 0]]

for icon in perWeightUG:
    fighterLinksBaseUG = fighterLinksBaseUG.append(getFightersUG(getHistoryInsUG(icon[0]), icon[1], 2))


# In[77]:


# Agregates fighter links to get the maximum amount of fighters
def fighterLinkAgrSD(agrFrom, times = 1):
    lastLen = len(agrFrom)
    agrNew = agrFrom
    compiledList = agrFrom
    for i in range(times):
        print(timer() + 'Total start: ' + str(len(compiledList)))
        cou = 0
        for index, row in agrNew.iterrows():
            try:
                compiledList = compiledList.append(getFightersSD(getHistoryInsSD(row[1]), row[2], 100, True))
                cou = cou + 1
                print(timer() + str(cou) + '\tAggregated: ' + str(len(compiledList) - lastLen))
            except:
                print(timer() + '!@#$%^&*)(___ERROR___)(*&^%$#@!')
        cou = 0
        print(timer() + 'Dropped: ' + str(len(compiledList) - len(compiledList.drop_duplicates('Name'))))
        compiledList.drop_duplicates('Name', inplace = True)
        lenOfNew = len(compiledList) - lastLen
        agrNew = compiledList.tail(lenOfNew)
        print(timer() + 'New: ' + str(lenOfNew))
        print(timer() + 'Total end: ' + str(len(compiledList)) + '\n')
        lastLen = len(compiledList)
        compiledList.to_csv('fighterLinks.csv')
    return compiledList


# In[63]:


fighterLinksSD = fighterLinkAgrSD(fighterLinksBaseSD, 100)
fighterLinksSD.to_csv('FP_SD_FighterLinks.csv', index = False)


# In[78]:


# Fighter links aggregator
def fighterLinkAgrUG(agrFrom, times = 1):
    lastLen = len(agrFrom)
    agrNew = agrFrom
    compiledList = agrFrom
    for i in range(times):
        print(timer() + 'Total start: ' + str(len(compiledList)))
        cou = 0
        for index, row in agrNew.iterrows():
            try:
                compiledList = compiledList.append(getFightersUG(getHistoryInsUG(row[1]), row[2], 100, True))
                cou = cou + 1
                print(timer() + str(cou) + '\tAggregated: ' + str(len(compiledList) - lastLen))
            except:
                print(timer() + '!@#$%^&*)(___ERROR___)(*&^%$#@!' + row[1])
        cou = 0
        print(timer() + 'Dropped: ' + str(len(compiledList) - len(compiledList.drop_duplicates('Name'))))
        compiledList.drop_duplicates('Name', inplace = True)
        lenOfNew = len(compiledList) - lastLen
        agrNew = compiledList.tail(lenOfNew)
        print(timer() + 'New: ' + str(lenOfNew))
        print(timer() + 'Total end: ' + str(len(compiledList)) + '\n')
        lastLen = len(compiledList)
        compiledList.to_csv('fighterLinksUG.csv')
    return compiledList


# In[65]:


fighterLinksUG = fighterLinkAgrUG(fighterLinksBaseUG, 100)
fighterLinksUG.to_csv('FP_UG_FighterLinks.csv', index = False)


# In[79]:


# Gets fighter info at a specific event
def getFightInfoSD(link, sex, ev = 'Full', show = False):
    global age
    global height
    global weight
    global timePro
    global timeUFC
    global wins
    global losses
    global winStk
    global winGra
    global winDec
    global winOtr
    global lossStk
    global lossGra
    global lossDec
    global lossOtr
    global ufcCount
    global avgLength
    global streak
    global event
    global name
    global isMale
    global l3Wins
    global l3Losses
    global l3WinStk
    global l3WinGra
    global l3WinDec
    global l3WinOtr
    global l3LossStk
    global l3LossGra
    global l3LossDec
    global l3LossOtr
    isMale = sex
    fighter = getHTMLSD(link)
    try:
        born = datetime.strptime(fighter.find_all('span', {'itemprop': 'birthDate'})[0].text, '%Y-%m-%d')
    except:
        born =datetime.strptime('1992-09-15', '%Y-%m-%d')
    try:
        height = fighter.find_all('strong', {'itemprop': 'height'})[0].text
        heightIn = (int(height.split('\'')[0][0]) * 12) + int(height.split('\'')[1][:-1])
        height = heightIn
    except:
        height = None
    try:
        weight = fighter.find_all('strong', {'itemprop': 'weight'})[0].text
        pounds = int(weight.split(' ')[0])
        weight = pounds
    except:
        weight = None
    
    historyIns = getHistoryInsSD(link, start = 'new')
    currTime = datetime.now()
    indexOfEvent = None
    firstUFCDate = datetime.now()
    firstProDate = getDateSD(historyIns[0])
    for i in historyIns:
        if i.find_all('td')[2].find_all('a')[0].text == ev:
            indexOfEvent = historyIns.index(i)
    for i in historyIns:
        if isUFCSD(i, False):
            firstUFCDate = getDateSD(i)
            break
    if indexOfEvent == None:
        indexOfEvent = len(historyIns)
    for i in historyIns:
        if i.find_all('td')[2].find_all('a')[0].text == ev:
            currTime = getDateSD(i)
            break
        else:
            try:
                if i in historyIns[indexOfEvent-3:]:
                    isWinSD(i, updateWhich = 'l3')
                    resultBySD(i, updateWhich = 'l3')
            except:
                pass
            isWinSD(i)
            resultBySD(i)
            addTimeSD(i)
            isUFCSD(i)
            matchStreakSD(i)
            
    age = (currTime - born).days
    timePro = (currTime - firstProDate).days
    timeUFC = (currTime - firstUFCDate).days
    
    name = fighter.find_all('span', {'class': 'fn'})[0].text 
    tMatches = wins + losses
    if tMatches > 0:
        avgLength = avgLength / tMatches
    else:
        avgLength = 0
    return {'name':name, 'isMale':isMale, 'age':age, 'height':height, 'weight':weight, 'timePro':timePro, 'timeUFC': timeUFC, 'wins':wins,
            'losses':losses, 'winStk':winStk, 'winGra':winGra, 'winDec':winDec,
            'winOtr':winOtr, 'lossStk':lossStk, 'lossGra':lossGra,
            'lossDec':lossDec, 'lossOtr':lossOtr, 'ufcCount':ufcCount,
            'avgLength':int(avgLength), 'l3Wins': l3Wins, 'l3Losses': l3Losses, 'l3WinStk':l3WinStk, 'l3WinGra':l3WinGra, 'l3WinDec':l3WinDec,
            'l3WinOtr':l3WinOtr, 'l3LossStk':l3LossStk, 'l3LossGra':l3LossGra, 'l3LossDec':l3LossDec, 'l3LossOtr':l3LossOtr, 'streak':streak}
def getFightsSD(fighterALink, sex, ins = 1):
    columns = ['ID',
               'Aname', 'AisMale', 'Aage', 'Aheight', 'Aweight', 'AtimePro', 'AtimeUFC',
               'Awins', 'Alosses',
               'AwinStk','AwinGra',
               'AwinDec', 'AwinOtr',
               'AlossStk', 'AlossGra',
               'AlossDec', 'AlossOtr',
               'Al3Wins', 'Al3Losses',
               'Al3WinStk','Al3WinGra',
               'Al3WinDec', 'Al3WinOtr',
               'Al3LossStk', 'Al3LossGra',
               'Al3LossDec', 'Al3LossOtr',
               'AufcCount', 'AavgLength', 'Astreak',
               'Bname', 'BisMale', 'Bage','Bheight', 'Bweight', 'BtimePro', 'BtimeUFC',
               'Bwins', 'Blosses',
               'BwinStk', 'BwinGra',
               'BwinDec', 'BwinOtr', 
               'BlossStk', 'BlossGra',
               'BlossDec','BlossOtr',
               'Bl3Wins', 'Bl3Losses',
               'Bl3WinStk','Bl3WinGra',
               'Bl3WinDec', 'Bl3WinOtr',
               'Bl3LossStk', 'Bl3LossGra',
               'Bl3LossDec', 'Bl3LossOtr',
               'BufcCount', 'BavgLength', 'Bstreak',
               'Event', 'Result', 'ResultBy', 'ResultIn']
    df = pd.DataFrame(columns = columns)
    fightHistory = getHistoryInsSD(fighterALink, 'new')
    ev = None
    if len(fightHistory) < ins:
        ins = len(fightHistory)
    for i in range(len(fightHistory)-ins, len(fightHistory)):
        try:
            ev = fightHistory[i]
            ev = ev.find_all('td')[2]
            ev = ev.find_all('a')[0]
            ev = ev.text
            if isUFCSD(fightHistory[i], False):
                fighterBLink = getFightersSD(getHistoryInsSD(fighterALink, 'new'), sex)['Link'][i]
                resetInfo()
                fighterAInfo = getFightInfoSD(fighterALink, sex, ev)
                resetInfo()
                fighterBInfo = getFightInfoSD(fighterBLink, sex, ev)
                resetInfo()
                names = [fighterAInfo['name'], fighterBInfo['name']]
                org = sorted(names)
                index = org[0] + ' vs. ' + org[1] + ' | ' + ev
                result = None
                resultBy = None
                resultIn = None
                print(timer() + 'Ran: ' + str(fighterAInfo['name']) + ' vs. ' + str(fighterBInfo['name']) + '\tEvent: ' + str(ev))
                for j in fightHistory:
                    if ev in str(j):
                        if j.find_all('td')[0].text == 'loss':
                            result = 0
                        elif j.find_all('td')[0].text == 'win':
                            result = 1
                        elif j.find_all('td')[0].text == 'draw':
                            result = 2
                        else:
                            result = 3
                        getBy = j.find_all('td')[3].text
                        getBy = getBy.split('(')[0][:-1]
                        forDec = ['Decision']
                        forStk = ['KO', 'TKO']
                        forGra = ['Submission', 'Technical Submission']
                        if getBy in forDec:
                            resultBy = 0
                            resultIn = 0
                        elif getBy in forStk:
                            resultBy = 1
                            resultIn = 1
                        elif getBy in forGra:
                            resultBy = 2
                            resultIn = 1
                        else:
                            resultBy = 3
                            resultIn = 1
                data = [[index,
                         fighterAInfo['name'], fighterAInfo['isMale'], fighterAInfo['age'], fighterAInfo['height'], fighterAInfo['weight'], fighterAInfo['timePro'], fighterAInfo['timeUFC'],
                         fighterAInfo['wins'], fighterAInfo['losses'],
                         fighterAInfo['winStk'], fighterAInfo['winGra'],
                         fighterAInfo['winDec'], fighterAInfo['winOtr'],
                         fighterAInfo['lossStk'], fighterAInfo['lossGra'],
                         fighterAInfo['lossDec'], fighterAInfo['lossOtr'],
                         fighterAInfo['l3Wins'], fighterAInfo['l3Losses'],
                         fighterAInfo['l3WinStk'], fighterAInfo['l3WinGra'],
                         fighterAInfo['l3WinDec'], fighterAInfo['l3WinOtr'],
                         fighterAInfo['l3LossStk'], fighterAInfo['l3LossGra'],
                         fighterAInfo['l3LossDec'], fighterAInfo['l3LossOtr'],
                         fighterAInfo['ufcCount'], fighterAInfo['avgLength'], fighterAInfo['streak'],
                         fighterBInfo['name'], fighterBInfo['isMale'], fighterBInfo['age'], fighterBInfo['height'],fighterBInfo['weight'], fighterBInfo['timePro'], fighterBInfo['timeUFC'],
                         fighterBInfo['wins'], fighterBInfo['losses'],
                         fighterBInfo['winStk'], fighterBInfo['winGra'],
                         fighterBInfo['winDec'], fighterBInfo['winOtr'],
                         fighterBInfo['lossStk'], fighterBInfo['lossGra'],
                         fighterBInfo['lossDec'], fighterBInfo['lossOtr'],
                         fighterBInfo['l3Wins'], fighterBInfo['l3Losses'],
                         fighterBInfo['l3WinStk'], fighterBInfo['l3WinGra'],
                         fighterBInfo['l3WinDec'], fighterBInfo['l3WinOtr'],
                         fighterBInfo['l3LossStk'], fighterBInfo['l3LossGra'],
                         fighterBInfo['l3LossDec'], fighterBInfo['l3LossOtr'],
                         fighterBInfo['ufcCount'], fighterBInfo['avgLength'],  fighterBInfo['streak'],
                         ev, result, resultBy, resultIn]] 
                dfIns = pd.DataFrame(data =data, columns = columns)
                df = df.append(dfIns)
            else:
                pass
        except:
            print(timer() + '$%^&*()$%^&*()__PASSED__$%^&*()$%^&*()')
            pass
    return df    


# In[67]:


# Get all fights from fighterLinks fighter
unrefinedDataSD = getFightsSD('https://www.sherdog.com/fighter/Joanna-Jedrzejczyk-101411', 0, ins = 100)
couSD = 0
for index, row in fighterLinksSD.iterrows():
    couSD = couSD + 1
    print(timer() + str(couSD))
    dfNew = getFightsSD(row[1], row[2], ins = 100)
    unrefinedDataSD = unrefinedDataSD.append(dfNew)
couSD = 0
unrefinedDataSD.to_csv('FP_SD_UnrefinedData.csv', index = False)


# In[80]:


# Gets fighter info
def getFightInfoUG(link, sex, ev = 'Full', show = False):
    global age
    global height
    global weight
    global timePro
    global timeUFC
    global wins
    global losses
    global winStk
    global winGra
    global winDec
    global winOtr
    global lossStk
    global lossGra
    global lossDec
    global lossOtr
    global ufcCount
    global avgLength
    global streak
    global event
    global name
    global isMale
    global l3Wins
    global l3Losses
    global l3WinStk
    global l3WinGra
    global l3WinDec
    global l3WinOtr
    global l3LossStk
    global l3LossGra
    global l3LossDec
    global l3LossOtr
    resetInfo()
    isMale = sex
    fighter = getHTMLUG(link)
    for ins in fighter.find_all('table', {'class', 'table fighter-info'})[0].find_all('tr'):
        if 'Height' in str(ins):
            heightStr = ins.find_all('td')[0].text.replace(' ', '')
            heightStr = heightStr.split('\'')
            heightFt = int(heightStr[0]) * 12
            heightIn = int(heightStr[1].replace('\"', ''))
            height = heightFt + heightIn
        if 'Age' in str(ins):
            age = int(ins.find_all('td')[0].text)
    if height == None:
        height = 0    
    historyIns = getHistoryInsUG(link, start = 'new')
    currTime = datetime.now()
    indexOfEvent = None
    for i in historyIns:
        if getEventUG(i, False) == ev:
            indexOfEvent = historyIns.index(i)
            currTime = getDateUG(i)
    if indexOfEvent == None:
        indexOfEvent = len(historyIns)
    firstProDate = getDateUG(historyIns[0])
    firstUFCDate = currTime
    for i in historyIns:
        if isUFCUG(i, False):
            firstUFCDate = getDateUG(i)
            break
    for i in historyIns:
        if getEventUG(i, False) == ev:
            weightClassUG(i)
            break
        else:
            if indexOfEvent > 3:
                if i in historyIns[indexOfEvent-3:]:
                    isWinUG(i, updateWhich = 'l3')
                    resultByUG(i, updateWhich = 'l3')
            else:
                pass
            isWinUG(i)
            resultByUG(i)
            addTimeUG(i)
            isUFCUG(i)
            matchStreakUG(i)
    age = int((currTime - (datetime.now() - relativedelta(years = age))).days)
    timePro = int((currTime - firstProDate).days)
    timeUFC = int((currTime - firstUFCDate).days)
    if timeUFC < 0:
        timeUFC = 0
    name = link.split('/')[-1].split(':')[0].split('-')
    name = name[0] + ' ' + name[1]
    tMatches = wins + losses
    if tMatches > 0:
        avgLength = int(avgLength / tMatches)
    else:
        avgLength = 0
    allInfo = {'name':name, 'isMale':isMale, 'age':age, 'height':height, 'weight':weight, 'timePro':timePro, 'timeUFC': timeUFC, 'wins':wins,
            'losses':losses, 'winStk':winStk, 'winGra':winGra, 'winDec':winDec,
            'winOtr':winOtr, 'lossStk':lossStk, 'lossGra':lossGra,
            'lossDec':lossDec, 'lossOtr':lossOtr, 'ufcCount':ufcCount,
            'avgLength':avgLength, 'l3Wins': l3Wins, 'l3Losses': l3Losses, 'l3WinStk':l3WinStk, 'l3WinGra':l3WinGra, 'l3WinDec':l3WinDec,
            'l3WinOtr':l3WinOtr, 'l3LossStk':l3LossStk, 'l3LossGra':l3LossGra, 'l3LossDec':l3LossDec, 'l3LossOtr':l3LossOtr, 'streak':streak}
    resetInfo()
    return allInfo
def getFightsUG(fighterALink, sex, ins = 1):
    columns = ['ID',
               'Aname', 'AisMale', 'Aage', 'Aheight', 'Aweight',
               'Awins', 'Alosses',
               'AtimePro', 'AtimeUFC',
               'AwinStk','AwinGra',
               'AwinDec', 'AwinOtr',
               'AlossStk', 'AlossGra',
               'AlossDec', 'AlossOtr',
               'Al3Wins', 'Al3Losses',
               'Al3WinStk','Al3WinGra',
               'Al3WinDec', 'Al3WinOtr',
               'Al3LossStk', 'Al3LossGra',
               'Al3LossDec', 'Al3LossOtr',
               'AufcCount', 'AavgLength', 'Astreak',
               'Bname', 'BisMale', 'Bage','Bheight', 'Bweight',
               'Bwins', 'Blosses',
               'BtimePro', 'BtimeUFC',
               'BwinStk', 'BwinGra',
               'BwinDec', 'BwinOtr', 
               'BlossStk', 'BlossGra',
               'BlossDec','BlossOtr',
               'Bl3Wins', 'Bl3Losses',
               'Bl3WinStk','Bl3WinGra',
               'Bl3WinDec', 'Bl3WinOtr',
               'Bl3LossStk', 'Bl3LossGra',
               'Bl3LossDec', 'Bl3LossOtr',
               'BufcCount', 'BavgLength', 'Bstreak',
               'Event', 'Result', 'ResultBy', 'ResultIn']
    df = pd.DataFrame(columns = columns)
    fightHistory = getHistoryInsUG(fighterALink, 'new')
    if len(fightHistory) < ins:
        ins = len(fightHistory)
    for i in range(len(fightHistory)-ins, len(fightHistory)):
        try:
            if isUFCUG(fightHistory[i], False):
                ev = getEventUG(fightHistory[i], False)
                fighterBLink = getFightersUG(getHistoryInsUG(fighterALink, 'new'), sex)['Link'][i]
                fighterAInfo = getFightInfoUG(fighterALink, sex, ev)
                fighterBInfo = getFightInfoUG(fighterBLink, sex, ev)
                names = [fighterAInfo['name'], fighterBInfo['name']]
                org = sorted(names)
                index = org[0] + ' vs. ' + org[1] + ' | ' + ev
                result = None
                resBy = None
                resultIn = None
                print(timer() + 'Ran: ' + str(fighterAInfo['name']) + ' vs. ' + str(fighterBInfo['name']) + '\tEvent: ' + str(ev))
                for j in fightHistory:
                    if ev in str(j):
                        if isWinUG(j, False) == False:
                            result = 0
                        elif isWinUG(j, False):
                            result = 1
                        elif isWinUG(j, False) == None:
                            result = 2
                        else:
                            result = 3
                        getBy = resultByUG(j, False)
                        forStk = ['KO', 'TKO', 'TKO/RSC']
                        forGra = ['Submission']
                        forDec = ['Decision']
                        forOtr = ['Disqualification', 'No Contest']
                        if getBy == 'winDec' or getBy == 'lossDec':
                            resBy = 0
                            resultIn = 0
                        elif getBy == 'winStk' or getBy == 'lossStk':
                            resBy = 1
                            resultIn = 1
                        elif getBy == 'winGra' or getBy == 'lossGra':
                            resBy = 2
                            resultIn = 1
                        else:
                            resBy = 3
                            resultIn = 1
                data = [[index,
                         fighterAInfo['name'], fighterAInfo['isMale'], fighterAInfo['age'], fighterAInfo['height'], fighterAInfo['weight'],
                         fighterAInfo['wins'], fighterAInfo['losses'],
                         fighterAInfo['timePro'], fighterAInfo['timeUFC'],
                         fighterAInfo['winStk'], fighterAInfo['winGra'],
                         fighterAInfo['winDec'], fighterAInfo['winOtr'],
                         fighterAInfo['lossStk'], fighterAInfo['lossGra'],
                         fighterAInfo['lossDec'], fighterAInfo['lossOtr'],
                         fighterAInfo['l3Wins'], fighterAInfo['l3Losses'],
                         fighterAInfo['l3WinStk'], fighterAInfo['l3WinGra'],
                         fighterAInfo['l3WinDec'], fighterAInfo['l3WinOtr'],
                         fighterAInfo['l3LossStk'], fighterAInfo['l3LossGra'],
                         fighterAInfo['l3LossDec'], fighterAInfo['l3LossOtr'],
                         fighterAInfo['ufcCount'], fighterAInfo['avgLength'], fighterAInfo['streak'],
                         fighterBInfo['name'], fighterBInfo['isMale'], fighterBInfo['age'], fighterBInfo['height'],fighterBInfo['weight'],
                         fighterBInfo['wins'], fighterBInfo['losses'],
                         fighterBInfo['timePro'], fighterBInfo['timeUFC'],
                         fighterBInfo['winStk'], fighterBInfo['winGra'],
                         fighterBInfo['winDec'], fighterBInfo['winOtr'],
                         fighterBInfo['lossStk'], fighterBInfo['lossGra'],
                         fighterBInfo['lossDec'], fighterBInfo['lossOtr'],
                         fighterBInfo['l3Wins'], fighterBInfo['l3Losses'],
                         fighterBInfo['l3WinStk'], fighterBInfo['l3WinGra'],
                         fighterBInfo['l3WinDec'], fighterBInfo['l3WinOtr'],
                         fighterBInfo['l3LossStk'], fighterBInfo['l3LossGra'],
                         fighterBInfo['l3LossDec'], fighterBInfo['l3LossOtr'],
                         fighterBInfo['ufcCount'], fighterBInfo['avgLength'],  fighterBInfo['streak'],
                         ev, result, resBy, resultIn]] 
                dfIns = pd.DataFrame(data =data, columns = columns)
                df = df.append(dfIns)
            else:
                pass
        except:
            print(timer() + '!!!Fight ERROR!!!')
            pass
    return df    


# In[69]:


# Gets fights
unrefinedDataUG = getFightsUG('https://www.mixedmartialarts.com/fighter/Sara-McMann:D37357AC56DBCCE2', 0, ins = 100)
couUG = 0
for index, row in fighterLinksUG.iterrows():
        couUG = couUG + 1
        print(timer() + str(couUG))
        try:
            dfNew = getFightsUG(row[1], row[2], ins = 100)
            unrefinedDataUG = unrefinedDataUG.append(dfNew)
        except:
            print(timer() + 'Fighter Error:\t' + row[1])
couUG = 0
unrefinedDataUG.to_csv('FP_UG_UnrefinedData.csv', index = False)


# In[180]:


# Get upcoming fight card fighter info
def getUpcomingCardSD(link, sex):
    fighter1List = []
    fighter2List = []
    sexList = sex
    getLink = getHTMLSD(link)
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
    return [fighter1List, fighter2List, sexList,  getEvent]


# In[181]:


upCardSD = getUpcomingCardSD(upFightURLSD,upFightSexArrSD)


# In[182]:


# Get upcoming fights
def getUpcomingCardUG(link, sex):
    fighter1List = []
    fighter2List = []
    sexList = sex
    getLink = getHTMLUG(link)
    getEvent = getLink.find_all('h1', {'class': 'pageHeader'})[0].text
    cardFights = getLink.find_all('div', {'id': 'event-panel'})[0].find_all('div', {'class': 'fight-item'})
    for fight in cardFights:
        bothF = fight.find_all('div', {'class': 'row names'})[0].find_all('a')
        f1L = bothF[0]['href']
        f2L = bothF[1]['href']
        fighter1List.append(f1L)
        fighter2List.append(f2L)
    return [fighter1List, fighter2List, sexList,  getEvent]


# In[183]:


upCardUG = getUpcomingCardUG(upFightURLUG, upFightSexArrUG)


# In[184]:


def getUpcomingFightSD(f1, f2, sex, ev = 'None'):
    global age
    global height
    global weight
    global timePro
    global timeUFC
    global wins
    global losses
    global winStk
    global winGra
    global winDec
    global winOtr
    global lossStk
    global lossGra
    global lossDec
    global lossOtr
    global ufcCount
    global avgLength
    global streak
    global event
    global name
    global l3Wins
    global l3Losses
    global l3WinStk
    global l3WinGra
    global l3WinDec
    global l3WinOtr
    global l3LossStk
    global l3LossGra
    global l3LossDec
    global l3LossOtr
    columns = ['ID',
               'Aname', 'AisMale', 'Aage', 'Aheight', 'Aweight', 'AtimePro', 'AtimeUFC',
               'Awins', 'Alosses',
               'AwinStk','AwinGra',
               'AwinDec', 'AwinOtr',
               'AlossStk', 'AlossGra',
               'AlossDec', 'AlossOtr',
               'Al3Wins', 'Al3Losses',
               'Al3WinStk','Al3WinGra',
               'Al3WinDec', 'Al3WinOtr',
               'Al3LossStk', 'Al3LossGra',
               'Al3LossDec', 'Al3LossOtr',
               'AufcCount', 'AavgLength', 'Astreak',
               'Bname', 'BisMale', 'Bage','Bheight', 'Bweight', 'BtimePro', 'BtimeUFC',
               'Bwins', 'Blosses',
               'BwinStk', 'BwinGra',
               'BwinDec', 'BwinOtr', 
               'BlossStk', 'BlossGra',
               'BlossDec','BlossOtr',
               'Bl3Wins', 'Bl3Losses',
               'Bl3WinStk','Bl3WinGra',
               'Bl3WinDec', 'Bl3WinOtr',
               'Bl3LossStk', 'Bl3LossGra',
               'Bl3LossDec', 'Bl3LossOtr',
               'BufcCount', 'BavgLength', 'Bstreak',
               'Event', 'Result', 'ResultBy', 'ResultIn']
    df = pd.DataFrame(columns = columns)
    for i in range(len(f1)):
        resetInfo()
        fighterAInfo = getFightInfoSD(f1[i],ev = ev ,sex = sex[i])
        resetInfo()
        fighterBInfo = getFightInfoSD(f2[i],ev = ev , sex = sex[i])
        resetInfo()
        index = fighterAInfo['name'] + ' vs. ' + fighterBInfo['name']
        ev = ev
        result = 'None'
        resultBy = 'None'
        resultIn = 'None'
        fightHistory = getHistoryInsSD(f1[i])
        for j in fightHistory:
            if ev in str(j):
                if j.find_all('td')[0].text == 'loss':
                    result = 0
                elif j.find_all('td')[0].text == 'win':
                    result = 1
                elif j.find_all('td')[0].text == 'draw':
                    result = 2
                else:
                    result = 3
                getBy = j.find_all('td')[3].text
                getBy = getBy.split('(')[0][:-1]
                forDec = ['Decision']
                forStk = ['KO', 'TKO']
                forGra = ['Submission', 'Technical Submission']
                if getBy in forDec:
                    resultBy = 0
                    resultIn = 0
                elif getBy in forStk:
                    resultBy = 1
                    resultIn = 1
                elif getBy in forGra:
                    resultBy = 2
                    resultIn = 1
                else:
                    resultBy = 3
                    resultIn = 1
        print(timer() + 'Ran: ' + str(fighterAInfo['name']) + ' vs. ' + str(fighterBInfo['name']) + '\tEvent: ' + str(ev))
        data = [[index,
                         fighterAInfo['name'], fighterAInfo['isMale'], fighterAInfo['age'], fighterAInfo['height'], fighterAInfo['weight'], fighterAInfo['timePro'], fighterAInfo['timeUFC'],
                         fighterAInfo['wins'], fighterAInfo['losses'],
                         fighterAInfo['winStk'], fighterAInfo['winGra'],
                         fighterAInfo['winDec'], fighterAInfo['winOtr'],
                         fighterAInfo['lossStk'], fighterAInfo['lossGra'],
                         fighterAInfo['lossDec'], fighterAInfo['lossOtr'],
                         fighterAInfo['l3Wins'], fighterAInfo['l3Losses'],
                         fighterAInfo['l3WinStk'], fighterAInfo['l3WinGra'],
                         fighterAInfo['l3WinDec'], fighterAInfo['l3WinOtr'],
                         fighterAInfo['l3LossStk'], fighterAInfo['l3LossGra'],
                         fighterAInfo['l3LossDec'], fighterAInfo['l3LossOtr'],
                         fighterAInfo['ufcCount'], fighterAInfo['avgLength'], fighterAInfo['streak'],
                         fighterBInfo['name'], fighterBInfo['isMale'], fighterBInfo['age'], fighterBInfo['height'],fighterBInfo['weight'], fighterBInfo['timePro'], fighterBInfo['timeUFC'],
                         fighterBInfo['wins'], fighterBInfo['losses'],
                         fighterBInfo['winStk'], fighterBInfo['winGra'],
                         fighterBInfo['winDec'], fighterBInfo['winOtr'],
                         fighterBInfo['lossStk'], fighterBInfo['lossGra'],
                         fighterBInfo['lossDec'], fighterBInfo['lossOtr'],
                         fighterBInfo['l3Wins'], fighterBInfo['l3Losses'],
                         fighterBInfo['l3WinStk'], fighterBInfo['l3WinGra'],
                         fighterBInfo['l3WinDec'], fighterBInfo['l3WinOtr'],
                         fighterBInfo['l3LossStk'], fighterBInfo['l3LossGra'],
                         fighterBInfo['l3LossDec'], fighterBInfo['l3LossOtr'],
                         fighterBInfo['ufcCount'], fighterBInfo['avgLength'],  fighterBInfo['streak'],
                         ev, result, resultBy, resultIn]] 
        dfIns = pd.DataFrame(data =data, columns = columns)
        df = df.append(dfIns)
    return df


# In[185]:


upFightDataSD = getUpcomingFightSD(upCardSD[0], upCardSD[1], upCardSD[2], upCardSD[3])
upFightDataSD.dropna(inplace = True)
upFightDataSD.to_csv('FP_SD_UpFightData.csv', index = False)


# In[186]:


def getUpcomingFightUG(f1, f2, sex, ev = 'None'):
    columns = ['ID',
               'Aname', 'AisMale', 'Aage', 'Aheight', 'Aweight',
               'Awins', 'Alosses',
               'AtimePro', 'AtimeUFC',
               'AwinStk','AwinGra',
               'AwinDec', 'AwinOtr',
               'AlossStk', 'AlossGra',
               'AlossDec', 'AlossOtr',
               'Al3Wins', 'Al3Losses',
               'Al3WinStk','Al3WinGra',
               'Al3WinDec', 'Al3WinOtr',
               'Al3LossStk', 'Al3LossGra',
               'Al3LossDec', 'Al3LossOtr',
               'AufcCount', 'AavgLength', 'Astreak',
               'Bname', 'BisMale', 'Bage','Bheight', 'Bweight',
               'Bwins', 'Blosses',
               'BtimePro', 'BtimeUFC',
               'BwinStk', 'BwinGra',
               'BwinDec', 'BwinOtr', 
               'BlossStk', 'BlossGra',
               'BlossDec','BlossOtr',
               'Bl3Wins', 'Bl3Losses',
               'Bl3WinStk','Bl3WinGra',
               'Bl3WinDec', 'Bl3WinOtr',
               'Bl3LossStk', 'Bl3LossGra',
               'Bl3LossDec', 'Bl3LossOtr',
               'BufcCount', 'BavgLength', 'Bstreak',
               'Event', 'Result', 'ResultBy', 'ResultIn']
    df = pd.DataFrame(columns = columns)
    ev = ev
    for i in range(len(f1)):
        try:
            fighterAInfo = getFightInfoUG(f1[i], sex = sex[i], ev = ev)
            fighterBInfo = getFightInfoUG(f2[i], sex = sex[i], ev = ev)
            names = [fighterAInfo['name'], fighterBInfo['name']]
            org = sorted(names)
            index = org[0] + ' vs. ' + org[1] + ' | ' + ev
            result = 'None'
            resBy = 'None'
            resultIn = 'None'
            print(timer() + 'Ran: ' + str(fighterAInfo['name']) + ' vs. ' + str(fighterBInfo['name']) + '\tEvent: ' + str(ev))
            data = [[index,
                        fighterAInfo['name'], fighterAInfo['isMale'], fighterAInfo['age'], fighterAInfo['height'], fighterAInfo['weight'],
                        fighterAInfo['wins'], fighterAInfo['losses'],
                        fighterAInfo['timePro'], fighterAInfo['timeUFC'],
                        fighterAInfo['winStk'], fighterAInfo['winGra'],
                        fighterAInfo['winDec'], fighterAInfo['winOtr'],
                        fighterAInfo['lossStk'], fighterAInfo['lossGra'],
                        fighterAInfo['lossDec'], fighterAInfo['lossOtr'],
                        fighterAInfo['l3Wins'], fighterAInfo['l3Losses'],
                        fighterAInfo['l3WinStk'], fighterAInfo['l3WinGra'],
                        fighterAInfo['l3WinDec'], fighterAInfo['l3WinOtr'],
                        fighterAInfo['l3LossStk'], fighterAInfo['l3LossGra'],
                        fighterAInfo['l3LossDec'], fighterAInfo['l3LossOtr'],
                        fighterAInfo['ufcCount'], fighterAInfo['avgLength'], fighterAInfo['streak'],
                        fighterBInfo['name'], fighterBInfo['isMale'], fighterBInfo['age'], fighterBInfo['height'],fighterBInfo['weight'],
                        fighterBInfo['wins'], fighterBInfo['losses'],
                        fighterBInfo['timePro'], fighterBInfo['timeUFC'],
                        fighterBInfo['winStk'], fighterBInfo['winGra'],
                        fighterBInfo['winDec'], fighterBInfo['winOtr'],
                        fighterBInfo['lossStk'], fighterBInfo['lossGra'],
                        fighterBInfo['lossDec'], fighterBInfo['lossOtr'],
                        fighterBInfo['l3Wins'], fighterBInfo['l3Losses'],
                        fighterBInfo['l3WinStk'], fighterBInfo['l3WinGra'],
                        fighterBInfo['l3WinDec'], fighterBInfo['l3WinOtr'],
                        fighterBInfo['l3LossStk'], fighterBInfo['l3LossGra'],
                        fighterBInfo['l3LossDec'], fighterBInfo['l3LossOtr'],
                        fighterBInfo['ufcCount'], fighterBInfo['avgLength'],  fighterBInfo['streak'],
                        ev, result, resBy, resultIn]] 
            dfIns = pd.DataFrame(data =data, columns = columns)
            df = df.append(dfIns)
        except:
            print(timer() + 'ERROR\t' + f1[i])
            pass
    return df   


# In[187]:


upFightDataUG = getUpcomingFightUG(upCardUG[0], upCardUG[1], upCardUG[2], upCardUG[3])
upFightDataUG.dropna(inplace = True)
upFightDataUG.to_csv('FP_UG_UpFightData.csv', index = False)


# In[78]:


# Clean fight data
refinedDataSD = unrefinedDataSD
refinedDataSD = refinedDataSD.sample(frac = 1)
refinedDataSD.dropna(inplace = True)
refinedDataSD.drop_duplicates('ID', inplace = True)
refinedDataSD = refinedDataSD.infer_objects()
refinedDataSD = refinedDataSD[(refinedDataSD['Result'] == 0) | (refinedDataSD['Result'] == 1)]
refinedDataSD.to_csv('FP_SD_RefinedData.csv', index = False)


# In[7]:


refinedDataSD = pd.read_csv('FP_SD_RefinedData.csv')
newArr = []
for index, row in refinedDataSD.iterrows():
    if row['Result'] == 1 and row['ResultIn'] == 0:
        newArr.append('aDec')
    elif row['Result'] == 1 and row['ResultIn'] == 1:
        newArr.append('aIns')
    elif row['Result'] == 0 and row['ResultIn'] == 0:
        newArr.append('bDec')
    elif row['Result'] == 0 and row['ResultIn'] == 1:
        newArr.append('bIns')
refinedDataSD['TResult'] = newArr
refinedDataSD.drop(['Result', 'ResultBy', 'ResultIn'], axis = 1, inplace = True)


# In[79]:


# Clean fight data
refinedDataUG = unrefinedDataUG
refinedDataUG = refinedDataUG.sample(frac = 1)
refinedDataUG.dropna(inplace = True)
refinedDataUG.drop_duplicates('ID', inplace = True)
refinedDataUG = refinedDataUG.infer_objects()
refinedDataUG = refinedDataUG[(refinedDataUG['Result'] == 0) | (refinedDataUG['Result'] == 1)]
refinedDataUG.to_csv('FP_UG_RefinedData.csv', index = False)


# In[9]:


refinedDataUG = pd.read_csv('FP_UG_RefinedData.csv')
newArr = []
for index, row in refinedDataUG.iterrows():
    if row['Result'] == 1 and row['ResultIn'] == 0:
        newArr.append('aDec')
    elif row['Result'] == 1 and row['ResultIn'] == 1:
        newArr.append('aIns')
    elif row['Result'] == 0 and row['ResultIn'] == 0:
        newArr.append('bDec')
    elif row['Result'] == 0 and row['ResultIn'] == 1:
        newArr.append('bIns')
refinedDataUG['TResult'] = newArr
refinedDataUG.drop(['Result', 'ResultBy', 'ResultIn'], axis = 1, inplace = True)


# In[12]:


modelDataSD = refinedDataSD
modelDataSD.drop(['ID', 'Aname', 'Bname', 'Event'], axis = 1, inplace = True)


# In[13]:


modelDataUG = refinedDataUG
modelDataUG.drop(['ID', 'Aname', 'Bname', 'Event'], axis = 1, inplace = True)


# In[14]:


# Get all general and specific datasets for models
dataMaleSD = modelDataSD[modelDataSD['AisMale'] == 1]
dataMaleSD.drop(['AisMale', 'BisMale'], axis = 1, inplace = True)
dataM125SD = dataMaleSD[(dataMaleSD['Aweight'] > 0) & (dataMaleSD['Aweight'] <= 125)].drop(['Aweight','Bweight'], axis = 1)
dataM135SD = dataMaleSD[(dataMaleSD['Aweight'] > 125) & (dataMaleSD['Aweight'] <= 135)].drop(['Aweight','Bweight'], axis = 1)
dataM145SD = dataMaleSD[(dataMaleSD['Aweight'] > 135) & (dataMaleSD['Aweight'] <= 145)].drop(['Aweight','Bweight'], axis = 1)
dataM155SD = dataMaleSD[(dataMaleSD['Aweight'] > 145) & (dataMaleSD['Aweight'] <= 155)].drop(['Aweight','Bweight'], axis = 1)
dataM170SD = dataMaleSD[(dataMaleSD['Aweight'] > 155) & (dataMaleSD['Aweight'] <= 170)].drop(['Aweight','Bweight'], axis = 1)
dataM185SD = dataMaleSD[(dataMaleSD['Aweight'] > 170) & (dataMaleSD['Aweight'] <= 185)].drop(['Aweight','Bweight'], axis = 1)
dataM205SD = dataMaleSD[(dataMaleSD['Aweight'] > 185) & (dataMaleSD['Aweight'] <= 205)].drop(['Aweight','Bweight'], axis = 1)
dataM265SD = dataMaleSD[dataMaleSD['Aweight'] > 205].drop(['Aweight','Bweight'], axis = 1)
dataFemaleSD = modelDataSD[modelDataSD['AisMale'] == 0]
dataFemaleSD.drop(['AisMale', 'BisMale'], axis = 1, inplace = True)
dataF115SD = dataFemaleSD[(dataFemaleSD['Aweight'] > 0) & (dataFemaleSD['Aweight'] <= 115)].drop(['Aweight','Bweight'], axis = 1)
dataF125SD = dataFemaleSD[(dataFemaleSD['Aweight'] > 115) & (dataFemaleSD['Aweight'] <= 125)].drop(['Aweight','Bweight'], axis = 1)
dataF135SD = dataFemaleSD[(dataFemaleSD['Aweight'] > 125) & (dataFemaleSD['Aweight'] <= 135)].drop(['Aweight','Bweight'], axis = 1)


# In[15]:


# Sorted Data
dataMaleUG = modelDataUG[modelDataUG['AisMale'] == 1]
dataMaleUG.drop(['AisMale', 'BisMale'], axis = 1, inplace = True)
dataM125UG = dataMaleUG[dataMaleUG['Aweight'] == 125].drop(['Aweight','Bweight'], axis = 1)
dataM135UG = dataMaleUG[dataMaleUG['Aweight'] == 135].drop(['Aweight','Bweight'], axis = 1)
dataM145UG = dataMaleUG[dataMaleUG['Aweight'] == 145].drop(['Aweight','Bweight'], axis = 1)
dataM155UG = dataMaleUG[dataMaleUG['Aweight'] == 155].drop(['Aweight','Bweight'], axis = 1)
dataM170UG = dataMaleUG[dataMaleUG['Aweight'] == 170].drop(['Aweight','Bweight'], axis = 1)
dataM185UG = dataMaleUG[dataMaleUG['Aweight'] == 185].drop(['Aweight','Bweight'], axis = 1)
dataM205UG = dataMaleUG[dataMaleUG['Aweight'] == 205].drop(['Aweight','Bweight'], axis = 1)
dataM265UG = dataMaleUG[dataMaleUG['Aweight'] == 265].drop(['Aweight','Bweight'], axis = 1)
dataFemaleUG = modelDataUG[modelDataUG['AisMale'] == 0]
dataFemaleUG.drop(['AisMale', 'BisMale'], axis = 1, inplace = True)
dataF115UG = dataFemaleUG[dataFemaleUG['Aweight'] == 115].drop(['Aweight','Bweight'], axis = 1)
dataF125UG = dataFemaleUG[dataFemaleUG['Aweight'] == 125].drop(['Aweight','Bweight'], axis = 1)
dataF135UG = dataFemaleUG[dataFemaleUG['Aweight'] == 135].drop(['Aweight','Bweight'], axis = 1)


# In[122]:


def getToNum(stri, rep):
    startStri = rep.find(stri)
    lenStri = len(stri)
    startNum = startStri + lenStri + 7
    return startNum

def toInt(passRes):
    if passRes == '1.00':
        return 100
    elif passRes == '0.00':
        return 0
    else:
        return int(passRes[-2:])  
    
def makeModel(data):
    def cleanRes(passRep):
        try:
            aDec = toInt(passRep[getToNum('aDec', passRep):getToNum('aDec', passRep) + 4])
            aIns = toInt(passRep[getToNum('aIns', passRep):getToNum('aIns', passRep) + 4])
            bDec = toInt(passRep[getToNum('bDec', passRep):getToNum('bDec', passRep) + 4])
            bIns = toInt(passRep[getToNum('bIns', passRep):getToNum('bIns', passRep) + 4])
            full = toInt(passRep[getToNum('avg / total', passRep):getToNum('avg / total', passRep) + 4])
            # Check for too many Zeros
            resArr = [aDec,aIns,bDec,bIns]
            couOfZ = 0
            for i in resArr:
                if i == 0:
                    couOfZ = couOfZ + 1
                if couOfZ >= 3:
                    return 0
            if abs(aDec - bDec) >=30 or abs(aIns - bIns) >=30:
                return 0
            if couOfZ <= 1:
                return full
            if (aDec <= 10 and bDec <= 10) or (aIns <= 10 and bIns <= 10):
                return full
            else:
                return 0
        except:
            return 0
    X = data.drop(['TResult'], axis = 1)
    y = data['TResult']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    dataModel = LinearSVC()
    dataModel.fit(X_train, y_train)
    pred = dataModel.predict(X_test)
    rep = classification_report(y_test, pred)
    repAvg = cleanRes(rep)
    return [[dataModel, rep], repAvg]
def bestModel(tm, nm):
    if tm[1] >= nm[1]:
        return tm
    else:
        return nm
def getBestModel(data, dataStr, getFullData = False):
    fullData = []
    topModel = makeModel(data)
    for i in range(2000):
        newModel = makeModel(data)
        topModel = bestModel(topModel, newModel)
        fullData.append(newModel[1])
    print(timer() + '\n' + timer() + dataStr + '\tTResult\tMeasure: ' + str(topModel[1]))
    print(topModel[0][1])
    if getFullData:
        return [topModel[0], fullData]
    else:
        return topModel[0]
def beatModel(toBeat, data):
    full = toInt()
    scoreToBeat = toInt(toBeat[1][getToNum('avg / total', toBeat[1]):getToNum('avg / total', toBeat[1]) + 4])
    for i in range(30000):
        newMod = makeModel(data)
        newModScore = toInt(newMod[0][1][getToNum('avg / total', newMod[0][1]):getToNum('avg / total', newMod[0][1]) + 4])
        if newModScore > scoreToBeat:
            print('\nBEAT\n' + newMod[0][1] + '\n')
            return newMod[0]
    print('\nFailed\n')
    return 'Failed'
        


# In[123]:


dataM125ResultModelSD = getBestModel(dataM125SD, 'dataM125')
# joblib.dump(dataM125ResultModelSD, 'FP_SD_M125_ResultModel.pkl')

dataM135ResultModelSD = getBestModel(dataM135SD, 'dataM135')
# joblib.dump(dataM135ResultModelSD, 'FP_SD_M135_ResultModel.pkl')

dataM145ResultModelSD = getBestModel(dataM145SD, 'dataM145')
# joblib.dump(dataM145ResultModelSD, 'FP_SD_M145_ResultModel.pkl')

dataM155ResultModelSD = getBestModel(dataM155SD, 'dataM155')
# joblib.dump(dataM155ResultModelSD, 'FP_SD_M155_ResultModel.pkl')

dataM170ResultModelSD = getBestModel(dataM170SD, 'dataM170')
# joblib.dump(dataM170ResultModelSD, 'FP_SD_M170_ResultModel.pkl')

dataM185ResultModelSD = getBestModel(dataM185SD, 'dataM185')
# joblib.dump(dataM185ResultModelSD, 'FP_SD_M185_ResultModel.pkl')

dataM205ResultModelSD = getBestModel(dataM205SD, 'dataM205')
# joblib.dump(dataM205ResultModelSD, 'FP_SD_M205_ResultModel.pkl')

dataM265ResultModelSD = getBestModel(dataM265SD, 'dataM265')
# joblib.dump(dataM265ResultModelSD, 'FP_SD_M265_ResultModel.pkl')

dataMaleResultModelSD = getBestModel(dataMaleSD, 'dataMale')
# joblib.dump(dataMaleResultModelSD, 'FP_SD_Male_ResultModel.pkl')

dataF115ResultModelSD = getBestModel(dataF115SD, 'dataF115')
# joblib.dump(dataF115ResultModelSD, 'FP_SD_F115_ResultModel.pkl')

try:
    dataF125ResultModelSD = getBestModel(dataF125SD, 'dataF125')
#     joblib.dump(dataF125ResultModelSD, 'FP_SD_F125_ResultModel.pkl')
except:
    pass
    
dataF135ResultModelSD = getBestModel(dataF135SD, 'dataF135')
# joblib.dump(dataF135ResultModelSD, 'FP_SD_F135_ResultModel.pkl')

dataFemaleResultModelSD = getBestModel(dataFemaleSD, 'dataFemale')
# joblib.dump(dataFemaleResultModelSD, 'FP_SD_Female_ResultModel.pkl')


# In[ ]:


# Import models
dataM125ResultModelSD = joblib.load('FP_SD_M125_ResultModel.pkl')
dataM125ResultInModelSD = joblib.load('FP_SD_M125_ResultInModel.pkl')
dataM135ResultModelSD = joblib.load('FP_SD_M135_ResultModel.pkl')
dataM135ResultInModelSD = joblib.load('FP_SD_M135_ResultInModel.pkl')
dataM145ResultModelSD = joblib.load('FP_SD_M145_ResultModel.pkl')
dataM145ResultInModelSD = joblib.load('FP_SD_M145_ResultInModel.pkl')
dataM155ResultModelSD = joblib.load('FP_SD_M155_ResultModel.pkl')
dataM155ResultInModelSD = joblib.load('FP_SD_M155_ResultInModel.pkl')
dataM170ResultModelSD = joblib.load('FP_SD_M170_ResultModel.pkl')
dataM170ResultInModelSD = joblib.load('FP_SD_M170_ResultInModel.pkl')
dataM185ResultModelSD = joblib.load('FP_SD_M185_ResultModel.pkl')
dataM185ResultInModelSD = joblib.load('FP_SD_M185_ResultInModel.pkl')
dataM205ResultModelSD = joblib.load('FP_SD_M205_ResultModel.pkl')
dataM205ResultInModelSD = joblib.load('FP_SD_M205_ResultInModel.pkl')
dataM265ResultModelSD = joblib.load('FP_SD_M265_ResultModel.pkl')
dataM265ResultInModelSD = joblib.load('FP_SD_M265_ResultInModel.pkl')
dataMaleResultModelSD = joblib.load('FP_SD_Male_ResultModel.pkl')
dataMaleResultInModelSD = joblib.load('FP_SD_Male_ResultInModel.pkl')
dataF115ResultModelSD = joblib.load('FP_SD_F115_ResultModel.pkl')
dataF115ResultInModelSD = joblib.load('FP_SD_F115_ResultInModel.pkl')
dataF125ResultModelSD = joblib.load('FP_SD_F125_ResultModel.pkl')
dataF125ResultInModelSD = joblib.load('FP_SD_F125_ResultInModel.pkl')
dataF135ResultModelSD = joblib.load('FP_SD_F135_ResultModel.pkl')
dataF135ResultInModelSD = joblib.load('FP_SD_F135_ResultInModel.pkl')
dataFemaleResultModelSD = joblib.load('FP_SD_Female_ResultModel.pkl')
dataFemaleResultInModelSD = joblib.load('FP_SD_Female_ResultInModel.pkl')


# In[25]:


modArr = [[dataM125ResultModelSD,'M125','Result'],
[dataM125ResultInModelSD,'M125','ResultIn'],
[dataM135ResultModelSD,'M135','Result'],
[dataM135ResultInModelSD,'M135','ResultIn'],
[dataM145ResultModelSD,'M145','Result'],
[dataM145ResultInModelSD,'M145','ResultIn'],
[dataM155ResultModelSD,'M155','Result'],
[dataM155ResultInModelSD,'M155','ResultIn'],
[dataM170ResultModelSD,'M170','Result'],
[dataM170ResultInModelSD,'M170','ResultIn'],
[dataM185ResultModelSD,'M185','Result'],
[dataM185ResultInModelSD,'M185','ResultIn'],
[dataM205ResultModelSD,'M205','Result'],
[dataM205ResultInModelSD,'M205','ResultIn'],
[dataM265ResultModelSD,'M265','Result'],
[dataM265ResultInModelSD,'M265','ResultIn'],
[dataMaleResultModelSD,'Male','Result'],
[dataMaleResultInModelSD,'Male','ResultIn'],
[dataF115ResultModelSD,'F115','Result'],
[dataF115ResultInModelSD,'F115','ResultIn'],
[dataF125ResultModelSD,'F125','Result'],
[dataF125ResultInModelSD,'F125','ResultIn'],
[dataF135ResultModelSD,'F135','Result'],
[dataF135ResultInModelSD,'F135','ResultIn'],
[dataFemaleResultModelSD,'Female','Result'],
[dataFemaleResultInModelSD,'Female','ResultIn']]
modRes = ''
for i in modArr:
    modRes = modRes + i[1] + '\t' + i[2] + '\n'
    modRes = modRes + str(i[0][1]) + '\n\n'
print(modRes)


# In[124]:


dataM125ResultModelUG = getBestModel(dataM125UG, 'dataM125')
# joblib.dump(dataM125ResultModelUG, 'FP_UG_M125_ResultModel.pkl')

dataM135ResultModelUG = getBestModel(dataM135UG, 'dataM135')
# joblib.dump(dataM135ResultModelUG, 'FP_UG_M135_ResultModel.pkl')

dataM145ResultModelUG = getBestModel(dataM145UG, 'dataM145')
# joblib.dump(dataM145ResultModelUG, 'FP_UG_M145_ResultModel.pkl')

dataM155ResultModelUG = getBestModel(dataM155UG, 'dataM155')
# joblib.dump(dataM155ResultModelUG, 'FP_UG_M155_ResultModel.pkl')

dataM170ResultModelUG = getBestModel(dataM170UG, 'dataM170')
# joblib.dump(dataM170ResultModelUG, 'FP_UG_M170_ResultModel.pkl')

dataM185ResultModelUG = getBestModel(dataM185UG, 'dataM185')
# joblib.dump(dataM185ResultModelUG, 'FP_UG_M185_ResultModel.pkl')

dataM205ResultModelUG = getBestModel(dataM205UG, 'dataM205')
# joblib.dump(dataM205ResultModelUG, 'FP_UG_M205_ResultModel.pkl')

dataM265ResultModelUG = getBestModel(dataM265UG, 'dataM265')
# joblib.dump(dataM265ResultModelUG, 'FP_UG_M265_ResultModel.pkl')

dataMaleResultModelUG = getBestModel(dataMaleUG, 'dataMale')
# joblib.dump(dataMaleResultModelUG, 'FP_UG_Male_ResultModel.pkl')

dataF115ResultModelUG = getBestModel(dataF115UG, 'dataF115')
# joblib.dump(dataF115ResultModelUG, 'FP_UG_F115_ResultModel.pkl')

try:
    dataF125ResultModelUG = getBestModel(dataF125UG, 'dataF125')
#     joblib.dump(dataF125ResultModelUG, 'FP_UG_F125_ResultModel.pkl')
except:
    pass
    
dataF135ResultModelUG = getBestModel(dataF135UG, 'dataF135')
# joblib.dump(dataF135ResultModelUG, 'FP_UG_F135_ResultModel.pkl')

dataFemaleResultModelUG = getBestModel(dataFemaleUG, 'dataFemale')
# joblib.dump(dataFemaleResultModelUG, 'FP_UG_Female_ResultModel.pkl')


# In[189]:


# Import models
dataM125ResultModelUG = joblib.load('FP_UG_M125_ResultModel.pkl')
dataM125ResultInModelUG = joblib.load('FP_UG_M125_ResultInModel.pkl')
dataM135ResultModelUG = joblib.load('FP_UG_M135_ResultModel.pkl')
dataM135ResultInModelUG = joblib.load('FP_UG_M135_ResultInModel.pkl')
dataM145ResultModelUG = joblib.load('FP_UG_M145_ResultModel.pkl')
dataM145ResultInModelUG = joblib.load('FP_UG_M145_ResultInModel.pkl')
dataM155ResultModelUG = joblib.load('FP_UG_M155_ResultModel.pkl')
dataM155ResultInModelUG = joblib.load('FP_UG_M155_ResultInModel.pkl')
dataM170ResultModelUG = joblib.load('FP_UG_M170_ResultModel.pkl')
dataM170ResultInModelUG = joblib.load('FP_UG_M170_ResultInModel.pkl')
dataM185ResultModelUG = joblib.load('FP_UG_M185_ResultModel.pkl')
dataM185ResultInModelUG = joblib.load('FP_UG_M185_ResultInModel.pkl')
dataM205ResultModelUG = joblib.load('FP_UG_M205_ResultModel.pkl')
dataM205ResultInModelUG = joblib.load('FP_UG_M205_ResultInModel.pkl')
dataM265ResultModelUG = joblib.load('FP_UG_M265_ResultModel.pkl')
dataM265ResultInModelUG = joblib.load('FP_UG_M265_ResultInModel.pkl')
dataMaleResultModelUG = joblib.load('FP_UG_Male_ResultModel.pkl')
dataMaleResultInModelUG = joblib.load('FP_UG_Male_ResultInModel.pkl')
dataF115ResultModelUG = joblib.load('FP_UG_F115_ResultModel.pkl')
dataF115ResultInModelUG = joblib.load('FP_UG_F115_ResultInModel.pkl')
dataF125ResultModelUG = joblib.load('FP_UG_F125_ResultModel.pkl')
dataF125ResultInModelUG = joblib.load('FP_UG_F125_ResultInModel.pkl')
dataF135ResultModelUG = joblib.load('FP_UG_F135_ResultModel.pkl')
dataF135ResultInModelUG = joblib.load('FP_UG_F135_ResultInModel.pkl')
dataFemaleResultModelUG = joblib.load('FP_UG_Female_ResultModel.pkl')
dataFemaleResultInModelUG = joblib.load('FP_UG_Female_ResultInModel.pkl')


# In[24]:


modArr = [[dataM125ResultModelUG,'M125','Result'],
[dataM125ResultInModelUG,'M125','ResultIn'],
[dataM135ResultModelUG,'M135','Result'],
[dataM135ResultInModelUG,'M135','ResultIn'],
[dataM145ResultModelUG,'M145','Result'],
[dataM145ResultInModelUG,'M145','ResultIn'],
[dataM155ResultModelUG,'M155','Result'],
[dataM155ResultInModelUG,'M155','ResultIn'],
[dataM170ResultModelUG,'M170','Result'],
[dataM170ResultInModelUG,'M170','ResultIn'],
[dataM185ResultModelUG,'M185','Result'],
[dataM185ResultInModelUG,'M185','ResultIn'],
[dataM205ResultModelUG,'M205','Result'],
[dataM205ResultInModelUG,'M205','ResultIn'],
[dataM265ResultModelUG,'M265','Result'],
[dataM265ResultInModelUG,'M265','ResultIn'],
[dataMaleResultModelUG,'Male','Result'],
[dataMaleResultInModelUG,'Male','ResultIn'],
[dataF115ResultModelUG,'F115','Result'],
[dataF115ResultInModelUG,'F115','ResultIn'],
[dataF125ResultModelUG,'F125','Result'],
[dataF125ResultInModelUG,'F125','ResultIn'],
[dataF135ResultModelUG,'F135','Result'],
[dataF135ResultInModelUG,'F135','ResultIn'],
[dataFemaleResultModelUG,'Female','Result'],
[dataFemaleResultInModelUG,'Female','ResultIn']]
modRes = ''
for i in modArr:
    modRes = modRes + i[1] + '\t' + i[2] + '\n'
    modRes = modRes + str(i[0][1]) + '\n\n'
print(modRes)
    


# In[190]:


def adjToFeed(row, byWeight = True):
    if byWeight:
        return row.drop(['ID', 'Aname', 'Bname', 'Event', 'AisMale', 'BisMale', 'Aweight', 'Bweight', 'TResult'])
    else:
        return row.drop(['ID', 'Aname', 'Bname', 'Event', 'AisMale', 'BisMale', 'TResult'])


# In[191]:


def useResultDataSD(passData):
    resultsStr = 'Card Results\n---------------------------------------------\n'
    for index, row in passData.iterrows():
        result = None
        altResult = None
        if 1 == 2:
            pass
        else:
            if row['AisMale'] == 1:
                if row['Aweight'] <= 125:
                    result = int(dataM125ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 135:
                    result = int(dataM135ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 145:
                    result = int(dataM145ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 155:
                    result = int(dataM155ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 170:
                    result = int(dataM170ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 185:
                    result = int(dataM185ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 205:
                    result = int(dataM205ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] >= 230:
                    result = int(dataM265ResultModelSD[0].predict([adjToFeed(row)])[0])
                altResult = int(dataMaleResultModelSD[0].predict([adjToFeed(row, False)])[0])
            elif row['AisMale'] == 0:
                if row['Aweight'] <= 115:
                    result = int(dataF115ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 125:
                    result = int(dataF125ResultModelSD[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] >= 135:
                    result = int(dataF135ResultModelSD[0].predict([adjToFeed(row)])[0])
                altResult = int(dataFemaleResultModelSD[0].predict([adjToFeed(row, False)])[0])
            if result == 'aDec':
                resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
            elif result == 'aIns':
                resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
            elif result == 'bDec':
                resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
            elif result == 'bIns':
                resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
            else:
                resultsStr = resultsStr + 'Error >>' + str(result) + '<<'
            difference = ''
            if result == altResult and resultIn == altResultIn:
                resultsStr = resultsStr + '\t|(Same)|\n\n'
            else:
                if result == altResult:
                    difference = '\t|(ResultIn Difference)|\t'
                elif resultIn == altResultIn:
                    difference = '\t|(Result Difference)|\t'
                elif result != altResult and resultIn != altResultIn:
                    difference = '\t|(Full Difference)|\t'
                else:
                    resultsStr = '!@#$%^&*()___FAILED___!@#$%^&*()'
                resultsStr = resultsStr + difference
                if result == 'aDec':
                    resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
                elif result == 'aIns':
                    resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
                elif result == 'bDec':
                    resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
                elif result == 'bIns':
                    resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
                else:
                    resultsStr = resultsStr + 'Error >>' + str(result) + '<<'
    return resultsStr


# In[192]:


testDataSD = pd.read_csv('FP_SD_TestData.csv')


# In[193]:


upFightPredsSD = useResultDataSD(upFightDataSD)


# In[194]:


def useResultDataUG(passData):
    resultsStr = 'Card Results\n---------------------------------------------\n'
    for index, row in passData.iterrows():
        result = None
        altResult = None
        if 1 == 2:
            pass
        else:
            if row['AisMale'] == 1:
                if row['Aweight'] <= 125:
                    result = int(dataM125ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 135:
                    result = int(dataM135ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 145:
                    result = int(dataM145ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 155:
                    result = int(dataM155ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 170:
                    result = int(dataM170ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 185:
                    result = int(dataM185ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 205:
                    result = int(dataM205ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] >= 230:
                    result = int(dataM265ResultModelUG[0].predict([adjToFeed(row)])[0])
                altResult = int(dataMaleResultModelUG[0].predict([adjToFeed(row, False)])[0])
            elif row['AisMale'] == 0:
                if row['Aweight'] <= 115:
                    result = int(dataF115ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] <= 125:
                    result = int(dataF125ResultModelUG[0].predict([adjToFeed(row)])[0])
                elif row['Aweight'] >= 135:
                    result = int(dataF135ResultModelUG[0].predict([adjToFeed(row)])[0])
                altResult = int(dataFemaleResultModelUG[0].predict([adjToFeed(row, False)])[0])
            if result == 'aDec':
                resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
            elif result == 'aIns':
                resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
            elif result == 'bDec':
                resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
            elif result == 'bIns':
                resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
            else:
                resultsStr = resultsStr + 'Error >>' + str(result) + '<<'
            difference = ''
            if result == altResult and resultIn == altResultIn:
                resultsStr = resultsStr + '\t|(Same)|\n\n'
            else:
                if result == altResult:
                    difference = '\t|(ResultIn Difference)|\t'
                elif resultIn == altResultIn:
                    difference = '\t|(Result Difference)|\t'
                elif result != altResult and resultIn != altResultIn:
                    difference = '\t|(Full Difference)|\t'
                else:
                    resultsStr = '!@#$%^&*()___FAILED___!@#$%^&*()'
                resultsStr = resultsStr + difference
                if result == 'aDec':
                    resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
                elif result == 'aIns':
                    resultsStr = resultsStr + row['Aname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
                elif result == 'bDec':
                    resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by DECISION'
                elif result == 'bIns':
                    resultsStr = resultsStr + row['Bname'] + '(' + str(row['Bweight']) + ')' + ' WINS' + ' by INSIDE the distance'
                else:
                    resultsStr = resultsStr + 'Error >>' + str(result) + '<<'
    return resultsStr


# In[197]:


upFightPredsUG = useResultDataUG(upFightDataUG)


# In[125]:


# Gets most accurate per prediction category
def getMostAcc(repSD, repUG):
    resultSD = [toInt(repSD[getToNum('avg / total', repSD):getToNum('avg / total', repSD) + 4]), 'SD']
    resultUG = [toInt(repUG[getToNum('avg / total', repUG):getToNum('avg / total', repUG) + 4]), 'UG']
    if resultSD[0] >= resultUG[0]:
        return resultSD[1] + '(' + str(resultSD[0]) + ')'
    elif resultUG[0] >= resultSD[0]:
        return resultUG[1] + '(' + str(resultUG[0]) + ')'
    return 'ERROR >>'
def compareReports(modelListSD, modelListUG):
    mainStr = ''
    for i in range(len(modelListSD)):
        mostAcc = getMostAcc(modelListSD[i][0][1], modelListUG[i][0][1])
        mainStr = mainStr + modelListSD[i][1] + ' = ' + mostAcc + '\n'
    return mainStr


# In[126]:


listSD = [[dataM125ResultModelSD, 'M125'],
            [dataM135ResultModelSD, 'M135'],
            [dataM145ResultModelSD, 'M145'],
            [dataM155ResultModelSD, 'M155'],
            [dataM170ResultModelSD, 'M170'],
            [dataM185ResultModelSD, 'M185'],
            [dataM205ResultModelSD, 'M205'],
            [dataM265ResultModelSD, 'M265'],
            [dataMaleResultModelSD, 'Male'],
            [dataF115ResultModelSD, 'F115'],
            [dataF125ResultModelSD, 'F125'],
            [dataF135ResultModelSD, 'F135'],
            [dataFemaleResultModelSD, 'Female']]
listUG = [[dataM125ResultModelUG, 'M125'],
            [dataM135ResultModelUG, 'M135'],
            [dataM145ResultModelUG, 'M145'],
            [dataM155ResultModelUG, 'M155'],
            [dataM170ResultModelUG, 'M170'],
            [dataM185ResultModelUG, 'M185'],
            [dataM205ResultModelUG, 'M205'],
            [dataM265ResultModelUG, 'M265'],
            [dataMaleResultModelUG, 'Male'],
            [dataF115ResultModelUG, 'F115'],
            [dataF125ResultModelUG, 'F125'],
            [dataF135ResultModelUG, 'F135'],
            [dataFemaleResultModelUG, 'Female']]
finalRep = compareReports(listSD, listUG)


# In[127]:


print(finalRep)

