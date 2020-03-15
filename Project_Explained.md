## Download Data
If we chose to back test only the equities of companies that are big right now it would be unfair, since those firms are big right now because they were successful in the past, hence their corresponding stock went up. So we want to find all stocks and their market caps for the years we examine. The file DataProcessing.ipynb does that. It explains how that can be found for 10 stocks. I have done it for 545 stocks on my computer and uploaded it.

## Find the best pair of moving averages
If we start brute force calculating all possible combinations, it will take some time. To counter that I did few things. Firstly everytime the script calculates a moving average it stores the results locally. And next time it calculates any moving average, it will first check if that moving average has already been calculated (and stored.) A second thing is that it uses multiprocessing. Each stock's result is independent of the other stocks, so for 545 stocks it is a good idea to multiprocess it. Lastly, I used a self made version of gradient descent. So instead of calculating all possible pairs, it calculates pairs based on gradient descent. Multiple starting points where used.

## Results
Two kinds of results were stored. <br/>
1. Files such as 12_31 has all the trades that were made for slow moving average 31 and fast moving average 31. <br/>
2. A file that contains all the results for all trades I calculated <br/>

## Also
This is simple back test strategy that is not expected to be profitable and is uploaded as an example. Thankfully the website that had the historic data for number of shares had also a lot of other historica data for free, so there are a lot more that can be done.  
