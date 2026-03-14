import pandas as pd

class AnalysisAgent:

    def moving_average(self,prices,window=14):
         series=pd.Series(prices)
         return series.rolling(window).mean().iloc[-1]
    
    
    def volatility(self,prices):
         series=pd.Series(prices)
         return series.pct_change().std()
    
    def rsi(self,prices,window=14):
         series=pd.Series(prices)
         delta=series.diff() # calculate price change 

         gain=delta.clip(lower=0) # only positive value

         loss=-delta.clip(upper=0) # only negative value

         avg_gain=gain.rolling(window).mean()
         avg_loss=loss.rolling(window).mean()

         avg_loss=avg_loss.replace(0,1e-10)# prevent divison by 0

         rs=avg_gain/avg_loss

         rsi=100-(100/(1+rs))

         return rsi.iloc[-1]
    
    def analyse(self,stock_data):
         prices=stock_data["prices"]

         return{
              "RSI": float(self.rsi(prices)),
              "MA14":float(self.moving_average(prices)),
              "volatility":float(self.volatility(prices))
         }
    