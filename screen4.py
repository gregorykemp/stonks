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
from stonks import screen

# Make a child class from the base screener class.

class screen1(screen):

    # extend per-screen method:

    def runScreen(self):
        print(self.thisStonk.symbol)
        
        # Count the number of screens we pass.
        passCount = 0
        
        # actual screening starts here.
        # gkemp FIXME should the values here be parameters?

        # * Revenue growth > 5%
        revenueGrowth = (float((self.thisStonk.getRevenue(year=0) - self.thisStonk.getRevenue(year=1))/self.thisStonk.getRevenue(year=1))) * 100.0
        if (revenueGrowth <= 5.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  revenue growth YoY: {:.2f}%".format(symbol, revenueGrowth))

        # * Profit growth > 7%
        profitGrowth = (float((self.thisStonk.getNetIncome(year=0) - self.thisStonk.getNetIncome(year=1))/self.thisStonk.getNetIncome(year=1))) * 100.0
        if (profitGrowth <= 7.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  profit growth YoY: {:.2f}%".format(symbol, profitGrowth))

        # * FCF / earnings > 80%
        fcfToEarnings = float(self.thisStonk.getFCF()/self.thisStonk.getNetIncome()) 
        if (fcfToEarnings <= 0.8):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  ratio of FCF to earnings: {:.2f}".format(symbol, fcfToEarnings))

        # * ROIC > 15%
        ROIC = float((self.thisStonk.getNetIncome() - self.thisStonk.getDividendsPaid())/(self.thisStonk.getTotalEquity() + self.thisStonk.getTotalDebt())) * 100.0
        if (ROIC <= 15.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  ROIC: {:.2f}%".format(symbol, ROIC))

        # * Net debt / free cash flow to firm < 5
        netDebtToFCF = float((self.thisStonk.getTotalDebt() - self.thisStonk.getCashAndEquivalents()) / self.thisStonk.getFCF()) 
        if (netDebtToFCF >= 5.0 ):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  ratio of net debt to FCF: {:.2f}".format(symbol, netDebtToFCF))

        # * Debt/equity < 80% 
        netDebtToEquity = float(self.thisStonk.getTotalDebt()/self.thisStonk.getTotalEquity()) * 100.0
        if (netDebtToEquity >= 80.0):
            symbol = "X"
        else:
            symbol = " "
            passCount = passCount + 1
        print("{}  debt to equity ratio: {:.2f}%".format(symbol, netDebtToEquity))

        print("{} passes {} of 6 checks.".format(self.thisStonk.symbol, passCount))
        if (passCount == 6): # gkemp FIXME magic number
            print ("*** {} passes the screen ***".format(self.thisStonk.symbol))

        # Flush the pipe. Helpful if debug messages are stuck in the buffer.
        sys.stdout.flush()
        self.apiCount += self.thisStonk.getApiCount()

# Define main program.

def main():

    # Make a new screener.
    myScreen = screen1()

    # Make a list of tickers to process.
    # I don't wrap this up in the screen object because some apps only use one
    # ticker at a time.
    tickerList = []
    if (len(sys.argv) > 1):
        tickerList = sys.argv[1:]
    else:
        for line in sys.stdin:
            tickerList.append(line.rstrip())

    # Loop through the list of command line arguments provided.
    for ticker in tickerList:
        print("------------------------------")
        # All the magic is wrapped up in this.  We call screen() to run the
        # screener code defined above.  If it returns False we continue.  If 
        # it returns True we're done.
        if (myScreen.screen(ticker) == True):
            break

# At some point we have to run the program.
if __name__ == "__main__":
    main()