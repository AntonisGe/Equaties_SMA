# We will have two folders. On one folder we will put all csv's from equities
# that have their sma values (in order to speed up calculations). On the other
# folder we are going to put all csv's that will have the trades.
# We are going to make a third file with the results.

import pandas as pd
import numpy as np
import multiprocessing
import os,glob

path_to_data_sma='D:\Back_Test\SMAs\Data_sma\{}.csv'
path_to_data='D:\Back_Test\SMAs\Data\{}.csv'
tickers=pd.read_csv('D:\Back_Test\list.csv')['List']

#====================STEP 1: SOME FUNCTIONS THAT WILL HELP======================

#This will find out if a file was a sma column. Used for time saving reasons.
def check(ticker,n):
    file=pd.read_csv(path_to_data_sma.format(ticker))
    try:
        a=file['sma{}'.format(n)]
        return(True)
    except:
        return(False)

#This function returns the file given with an added column of a sma with value n.
def sma(ticker,n):
    if not check(ticker,n):
        file=pd.read_csv(path_to_data_sma.format(ticker))
        if file.shape[0]>n:
            sma=['NA' for i in range(n)]
            for j in range(n,file.shape[0]):
                sma.append(sum([file['Close'][j-k] for k in range(n)])/n)
            file['sma{}'.format(n)]=sma
            file.to_csv(path_to_data_sma.format(ticker),index=False)
        else:
            sma=['NA' for i in range(file.shape[0])]
            file['sma{}'.format(n)]=sma
            file.to_csv(path_to_data_sma.format(ticker),index=False)

#This function will return a list of profits,time,dates of each trade
def profits(ticker_sma1_sma2): # we make it as one argument to make it easier for multiprocessing later
    
    ticker=ticker_sma1_sma2.split('_')[0]
    sma1=int(ticker_sma1_sma2.split('_')[1])
    sma2=int(ticker_sma1_sma2.split('_')[2])
    
    sma(ticker,sma1)
    sma(ticker,sma2)

    file=pd.read_csv(path_to_data_sma.format(ticker))
    
    stocks=[0 for i in range(max(sma1,sma2))]
    for i in range(max(sma1,sma2),file.shape[0]-1):
        if file['sma{}'.format(sma1)][i]>file['sma{}'.format(sma2)][i] and file['Rank'][i]<100:
            stocks.append(1)
        else:
            stocks.append(0)
    stocks.append(0)

    profit=[]
    time=[]
    dates=[]
    
    for k in range(1,len(stocks)):
        if stocks[k-1]==0 and stocks[k]==1:
            stock_owned=100/file['Close'][k]
            dates.append(file['Date'][k])

        elif stocks[k-1]==1 and stocks[k]==0:
            profit.append(stock_owned * file['Close'][k]-100)
            date1=pd.to_datetime(dates[-1]).date()
            date2=pd.to_datetime(file['Date'][k]).date()
            time.append(np.busday_count(date1,date2))
            
    save=pd.DataFrame()
    save['Ticker']=[ticker for i in range(len(profit))]
    save['Date']=[i for i in dates]
    save['Time']=[i for i in time]
    save['Profit']=[i for i in profit]
    save.to_csv('Temp_Results\{}.csv'.format(ticker),index=False)

#This function will calculate all profits for a pair of SMA's and return the metric
def metric(sma1,sma2):

    arguments=['{}_{}_{}'.format(i,sma1,sma2) for i in tickers]
    
    pool=multiprocessing.Pool()
    pool.map(profits,arguments)
    pool.close()  # After this evyrthing will have been stored in the Temp file we created.

    df=pd.read_csv('Temp_Results\{}.csv'.format(tickers[0]))
    for ticker in tickers[1:]:
        df=pd.concat([df,pd.read_csv('Temp_Results\{}.csv'.format(ticker))])

    df.to_csv('Results\{}_{}.csv'.format(sma1,sma2),index=False)
        
    files=glob.glob('Temp_Results/*.csv')
    for f in files:
                    os.remove(f)
    return(sum(df['Profit'])/sum(df['Time'])) # This is what we want to maximize. Profit made each day.

#===============================STEP 2==========================================

# Now everything is done. We just write metric(sma1,sma2) and it calculates the result.
# To find the best result, we can either use a brute force approach or use a version of gradient descent.

# Gradient Descent.

if __name__=='__main__':
    sma_one=12
    sma_two=41 # starting point

    f=metric(sma_one,sma_two) # Function we want to max

    list_of_pairs_tried=[[sma_one,sma_two]]
    results_of_pairs_tried=[f]

    found_max=False

    while not found_max:
        current_sma_one=sma_one
        current_sma_two=sma_two
        current_f=f
        for i in range(sma_one-1,sma_one+2):
            for j in range(sma_two-2,sma_two+3):
                if i<j and [i,j] not in list_of_pairs_tried:
                    now_f=metric(i,j)
                    list_of_pairs_tried.append([i,j])
                    results_of_pairs_tried.append(now_f)
                    if now_f>current_f:
                        current_f=now_f
                        current_sma_one=i
                        current_sma_two=j
        if current_f==f:
            print('Result found: {} and {} with f={}'.format(current_sma_one,current_sma_two,current_f))
            found_max=True
        else:
            print('{} and {} with f={}'.format(sma_one,sma_two,f))
            sma_one=current_sma_one
            sma_two=current_sma_two
            f=current_f

    save=pd.DataFrame()
    save['sma_one']=[i[0] for i in list_of_pairs_tried]
    save['sma_two']=[i[1] for i in list_of_pairs_tried]
    save['result']=[i for i in results_of_pairs_tried]

    if os.path.isfile('result.csv'):
        df=pd.read_csv('result.csv')
        df=pd.concat([df,save])
        df.drop_duplicates(inplace=True)
        df.to_csv('result.csv',index=False)
    else:
        save.to_csv('result.csv',index=False)

            
            










