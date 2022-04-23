#  screen2.py
#
# Use Piotrosky F-score, operating cash flow growth rate, and valuation to
# find potential investment opportunities. Qualify results with BMW CAGR 
# calculations.
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
            if(float(thisStonk.overview["EPS"]) > 0):
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
            # Since the goal here is to screen a number of stocks we don't spend
            # a lot of time trying to fix errors.  We log the error and move on.
            print("{}: something went wrong.". format(ticker))
            continue            

        # For high scoring stonks, go a step further.
        if (sum(fscore) > 5):
            growthRate = thisStonk.estimateGrowthRate()
            intrinsicValue = thisStonk.discountedCashFlow(growthRate)
            print("{}: {:.02f}% ${:2.02f}".format(ticker, (growthRate*100), intrinsicValue))
            # Really should label debug prints better than this.
            # print("{}".format(thisStonk.getApiCount()))

            # gkemp FIXME make the growth rate threshold a parameter.
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
                recentPrice = float(thisStonk.dailyPrice[temp[0]]['4. close'])

                print("   intrinsic value: ${:.02f}".format(intrinsicValue))
                print("      recent price: ${:.02f}".format(recentPrice))

                # Do more math if we're good so far.
                if (recentPrice < intrinsicValue):
                    # No chart for batch mode.
                    bmwResult = thisStonk.bmwChart(chart=False)

                    print("    forecast price: ${:.02f}".format(bmwResult[3]))
                    print("        price CAGR: {:.02f}%".format(bmwResult[1]))
                    print("     forecast CAGR: {:.02f}%".format(bmwResult[0]))

                    # Looking for forecast CAGR above 10% and current price below
                    # long term trend.
                    # gkemp FIXME again the threshold should be a parameter.
                    if (bmwResult[0] > 10.0) and (bmwResult[3] > bmwResult[2]):
                        # This is the message we want to see in the log file.
                        # Flag it with $$$ since I'm looking for $$$ from my stonks.
                        print("$$$ {} is a candidate!".format(ticker))

        # Flush the pipe. Helpful if debug messages are stuck in the buffer.
        sys.stdout.flush()
        apiCount += thisStonk.getApiCount()
        # gkemp FIXME again this should be a parameter. If user has premium access 
        # we don't need to throttle.
        if (apiCount > 400):
            print("API count limit reached.")
            break

if __name__ == "__main__":
    main()