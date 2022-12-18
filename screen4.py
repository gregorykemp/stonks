# screen4.py
#
# An idea I saw on Twitter a few months ago:
# * Revenue growth > 5%
# * Profit growth > 7%
# * FCF / earnings > 80%
# * ROIC > 15%
# * Net debt / free cash flow to firm < 5
# * Debt/equity < 80% 
# 
# Uses the stonks library:
# https://github.com/gregorykemp/stonks
# 
# Copyright 2022 Gregory A. Kemp
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

# gkemp FIXME the screeners have a lot of code in common.  It might be a good
# idea to refactor the code so that the screener is a class, and the individual
# screener implementations subclass the implementation.

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
        print(ticker)
        # This creates the stonk.  This will return a key error if the ticker 
        # doesn't exist in the Alpha Vantage database.
        try:
            thisStonk = stonks(ticker, api_key)
        except KeyError:
            print("Ticker {} not found in database.".format(ticker))
            continue

        # Count the number of screens we pass.
        passCount = 0
        
        # actual screening starts here.
        # gkemp FIXME should the values here be parameters?

        # * Revenue growth > 5%
        revenueGrowth = (float((thisStonk.getRevenue(year=0) - thisStonk.getRevenue(year=1))/thisStonk.getRevenue(year=1))) * 100.0
        if (revenueGrowth <= 5.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  revenue growth YoY: {:.2f}%".format(symbol, revenueGrowth))

        # * Profit growth > 7%
        profitGrowth = (float((thisStonk.getNetIncome(year=0) - thisStonk.getNetIncome(year=1))/thisStonk.getNetIncome(year=1))) * 100.0
        if (profitGrowth <= 7.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  profit growth YoY: {:.2f}%".format(symbol, profitGrowth))

        # * FCF / earnings > 80%
        fcfToEarnings = float(thisStonk.getFCF()/thisStonk.getNetIncome()) 
        if (fcfToEarnings <= 0.8):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  ratio of FCF to earnings: {:.2f}".format(symbol, fcfToEarnings))

        # * ROIC > 15%
        ROIC = float((thisStonk.getNetIncome() - thisStonk.getDividendsPaid())/(thisStonk.getTotalEquity() + thisStonk.getTotalDebt())) * 100.0
        if (ROIC <= 15.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  ROIC: {:.2f}%".format(symbol, ROIC))

        # * Net debt / free cash flow to firm < 5
        netDebtToFCF = float((thisStonk.getTotalDebt() - thisStonk.getCashAndEquivalents()) / thisStonk.getFCF()) 
        if (netDebtToFCF >= 5.0 ):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  ratio of net debt to FCF: {:.2f}".format(symbol, netDebtToFCF))

        # * Debt/equity < 80% 
        netDebtToEquity = float(thisStonk.getTotalDebt()/thisStonk.getTotalEquity()) * 100.0
        if (netDebtToEquity >= 80.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  debt to equity ratio: {:.2f}%".format(symbol, netDebtToEquity))

        print("{} passes {} of 6 checks.".format(ticker, passCount))
        if (passCount == 6): # gkemp FIXME magic number
            print ("*** {} passes the screen ***".format(ticker))


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