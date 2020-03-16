# Basic logic: For each ticker I have saved a csv file in a folder (the path to that file is 'D:\Back_Test\SMAs\Data_sma\{}.csv').
# Now to save time, each time a moving average is calcualted, it will store the result in that file under the column name sma{}.format(moving average). def sma() does that.
# Then we will make a function <def profits(ticker,sma1,sma2)> that will go to that file and if that moving average has not been calculated and stored, it will do exactly that. Then it will calculate the profit for that ticker.
# Then we will make a function <def metric(*args)> that using multiprocessing it will do the above function for all tickers that we have.
# Lastly we will have the gradient descent said.

# To run this, you need to have a folder name Temp_Results and one named Results, in the same directory as the py script and also change the path of the data right below.
# All other files will be self created if they do not exist.

import pandas as pd
import numpy as np
import multiprocessing
import os,glob

path_to_data_sma='D:\Back_Test\SMAs\Data_sma\{}.csv'
tickers=pd.read_csv('D:\Back_Test\list.csv')['List']

#==============================================================================================================================

# Each function is used recursively in the function below.

#This will find out if a file was a sma column.

def check(ticker,n):
    file=pd.read_csv(path_to_data_sma.format(ticker))
    try:
        a=file['sma{}'.format(n)]
        return(True)
    except:
        return(False)

#This function returns the file given with an added column of a sma with value n.

def sma(ticker,n):
    if not check(ticker,n):     #Check if that moving average has already been calculated. Otherwise add it.
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
    
    sma(ticker,sma1)   # Check and add if sma1 has been stored in the file. Similarly for sma2.
    sma(ticker,sma2)   

    file=pd.read_csv(path_to_data_sma.format(ticker))
    
    stocks=[0 for i in range(max(sma1,sma2))] # Stocks is a list that holds 0 or 1 for each date. If we have 1=> we are long.
    for i in range(max(sma1,sma2),file.shape[0]-1):
        if file['sma{}'.format(sma1)][i]>file['sma{}'.format(sma2)][i] and file['Rank'][i]<100:  #Condition to be long.
            stocks.append(1)
        else:
            stocks.append(0)
    stocks.append(0)

    profit=[]
    time=[]
    dates=[]
    closing_dates=[]
    
    for k in range(1,len(stocks)):
        if stocks[k-1]==0 and stocks[k]==1:      #if yesterday we had no position in a stock and today we are supposed to be long
            stock_owned=100/file['Close'][k]          # Then add to our position 100 dollars worth of stock based on today's close.
            dates.append(file['Date'][k])

        elif stocks[k-1]==1 and stocks[k]==0:              #Similary to close a position.
            profit.append(stock_owned * file['Close'][k]-100)
            date1=pd.to_datetime(dates[-1]).date()
            date2=pd.to_datetime(file['Date'][k]).date()
            time.append(np.busday_count(date1,date2))
            closing_dates.append(file['Date'][k])
            
    save=pd.DataFrame()
    save['Ticker']=[ticker for i in range(len(profit))]
    save['Date']=[i for i in dates]
    save['Last date']=[i for i in closing_dates]
    save['Time']=[i for i in time]
    save['Profit']=[i for i in profit]
    save.to_csv('Temp_Results\{}.csv'.format(ticker),index=False)   # Save that trade in a 'TEMP FILE'. We have to do this to make multiprocessing work.
    

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
                    os.remove(f)   # Clean up our temp file. We have stored the results in our permanent file already.
    
    return(sum(df['Profit'])/sum(df['Time'])) # This is what we want to maximize. Profit made each day.

#===================================================================================================================================================================

# Now everything is done. We just write metric(sma1,sma2) and it calculates the result.
# To find the best result, we can either use a brute force approach or use a version of gradient descent.

# Gradient Descent.

if __name__=='__main__':
    
    sma_one=25
    sma_two=80 # starting point

    f=metric(sma_one,sma_two) # Function we want to max

    list_of_pairs_tried=[[sma_one,sma_two]]
    results_of_pairs_tried=[f]

    found_max=False

    list_of_pairs_tried_in_previous_scripts_runs=[]
    list_of_f_values_in_previous_scripts_runs=[]
    if os.path.isfile('result.csv'):
        old_results=pd.read_csv('result.csv')
        for i in range(old_results.shape[0]):
            list_of_pairs_tried_in_previous_scripts_runs.append([old_results['sma_one'][i],old_results['sma_two'][i]])
            list_of_f_values_in_previous_scripts_runs.append(old_results['result'][i])

        

    while not found_max:
        current_sma_one=sma_one  # current_value is where the best value is stored for this itteration.
        current_sma_two=sma_two
        current_f=f
        for i in range(sma_one-5,sma_one+6,3):
            for j in range(sma_two-5,sma_two+6,3): # values checked for sma2.
                if i<j and [i,j] not in list_of_pairs_tried:
                    if [i,j] not in list_of_pairs_tried_in_previous_scripts_runs:
                        now_f=metric(i,j)
                    else: # if we have calculated that pair in previous script run, just take it ready from before.
                        now_f=list_of_f_values_in_previous_scripts_runs[list_of_pairs_tried_in_previous_scripts_runs.index([i,j])]
                        
                    list_of_pairs_tried.append([i,j])
                    results_of_pairs_tried.append(now_f)
                    if now_f>current_f:  # if that value that was just calculated is better than the current best in this itteration.
                        current_f=now_f
                        current_sma_one=i
                        current_sma_two=j

                        
        if current_f==f: #Now if the best value in this itteration did not change then we are done.
            print('Result found: {} and {} with f={}'.format(current_sma_one,current_sma_two,current_f))
            found_max=True
        else: # Otherwise change sma_one and sma_two
            print('{} and {} with f={}'.format(sma_one,sma_two,f))
            sma_one=current_sma_one
            sma_two=current_sma_two
            f=current_f

    # Saving Results
    
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


#                                                                                 THANK YOU FOR WATCHING IT!
