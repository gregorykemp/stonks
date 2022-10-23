#  screen1.py
#
# Use Piotrosky F-score, operating cash flow growth rate, and valuation to
# find potential investment opportunities.
# 
# Uses the stonks library:
# https://github.com/gregorykemp/stonks
# 
# Copyright 2021 Gregory A. Kemp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Needed for command line argument processing.
import sys

# We need stonks!
from stonks import stonks

def main():
    # Read API key from text file. We don't validate the key here. You'll die soon enough if it's bad.
    file = open("api_key.txt", "r")
    api_key = file.read()

    apiCount = 0
    tickerList = []
    if (len(sys.argv) > 1):
        tickerList = sys.argv[1:]
    else:
        for line in sys.stdin:
            tickerList.append(line.rstrip())

    # Loop through the list of command line arguments provided.
    for ticker in tickerList:
        # This creates the stonk.  This will return a key error if the ticker 
        # doesn't exist in the Alpha Vantage database.
        try:
            thisStonk = stonks(ticker, api_key)
        except KeyError:
            print("Ticker {} not found in database.".format(ticker))
            continue

        try:
            if(thisStonk.getEPS() > 0):
                fscore = thisStonk.fScore()
                # Always print the summary score.
                print("{} f-score: {}".format(ticker, sum(fscore)))
                # If only one ticker listed, give the expanded report.
                if (len(tickerList) == 1):
                    thisStonk.fScorePrettyPrint(fscore)  
            else:
                print("{}: {} EPS is negative, we're done.".format(ticker, thisStonk.overview["EPS"]))
                continue
        except:
            print("{}: something went wrong.". format(ticker))
            continue            

        # For high scoring stonks, go a step further.
        if (sum(fscore) > 5):
            growthRate = thisStonk.estimateGrowthRate()
            intrinsicValue = thisStonk.discountedCashFlow(growthRate)
            print("{}: {:.02f}% ${:2.02f}".format(ticker, (growthRate*100), intrinsicValue))
            print("{}".format(thisStonk.getApiCount()))

            if (growthRate > 0.15):
                intrinsicValue = thisStonk.discountedCashFlow(growthRate)
                # gkemp FIXME
                # might want to wrap this up better.  All this to get recent close.
                # this reads the database and gets recent prices.
                # recentPrice = thisStonk.getRecentPrice()
                # wouldn't need daily results for this.
                # gkemp FIXME
                # also this gets me less than six months of price date.  I want that 20-year view.
                # You need weekly or monthly series for that.
                thisStonk.getDailyPrices()
                # this returns a list of dates you could index
                temp = list(thisStonk.dailyPrice)
                # and finally, this reads the dictionary in entry 0 (most recent) and returns adjusted price.
                recentPrice = float(thisStonk.dailyPrice[temp[0]]['5. adjusted close'])

                print("   intrinsic value: ${:.02f}".format(intrinsicValue))
                print("      recent price: ${:.02f}".format(recentPrice))

                # So here it is.
                if (recentPrice < intrinsicValue):
                    print("$$$ {} is a candidate!".format(ticker))

        sys.stdout.flush()
        apiCount += thisStonk.getApiCount()
        if (apiCount > 400):
            print("API count limit reached.")
            break

if __name__ == "__main__":
    main()