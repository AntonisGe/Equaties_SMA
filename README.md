# Example of Back-Testing Strategies

## Find best pair of moving averages for trading equaties.
The (simple) n day moving average of a stock (sma) is the the average close of the equity in the last n days. There is a basic stragy that goes as follows.
Consider a slow moving average (say 12 day moving average) and a fast moving average (say the 5 day moving average). When the fast moving average is bigger than the slow, we go long on the equity, otherwise we have no position in the equity.

The point of this is to find the best combination of slow and fast moving averages and find if that strategy would be profitable.  
