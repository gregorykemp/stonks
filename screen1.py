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
from stonks import screen

# Make a child class from the base screener class.

class screen1(screen):

    # Interesting.  VScode adds this:
    #    return super().runScreen()        
    # when I type this:
    #    def runScreen(self):
    # even when I don't want that.

    def runScreen(self):

        # Step 1: is EPS positive?
        if(self.thisStonk.getEPS() > 0):

            # Step 2: is F-score greater than 5?
            fscore = self.thisStonk.fScore()
            # Always print the summary score.
            print("{} f-score: {}".format(self.thisStonk.symbol, sum(fscore)))

            # Step 3: is growth rate above 15%?
            if (sum(fscore) > 5):
                growthRate = self.thisStonk.estimateGrowthRate()
                intrinsicValue = self.thisStonk.discountedCashFlow(growthRate)
                print("{}: {:.02f}% ${:2.02f}".format(self.thisStonk.symbol, (growthRate*100), intrinsicValue))

                if (growthRate > 0.15):
                    intrinsicValue = self.thisStonk.discountedCashFlow(growthRate)
                    recentPrice = self.thisStonk.getRecentPrice()

                    print("   intrinsic value: ${:.02f}".format(intrinsicValue))
                    print("      recent price: ${:.02f}".format(recentPrice))

                    # So here it is:
                    # 1. Positive EPS, and
                    # 2. F-score above 5, and 
                    # 3. Growth rate above 15%, and
                    # 4. Recent price below intrinsic value.

                    if (recentPrice < intrinsicValue):
                        print("$$$ {} is a candidate!".format(self.thisStonk.symbol))

        else:
            # Else EPS was negative, no need to look further.
            print("{}: {} EPS is negative, we're done.".format(self.thisStonk.symbol, self.thisStonk.overview["EPS"]))


        sys.stdout.flush()
        self.apiCount += self.thisStonk.getApiCount()


# This defines the main program.  Process the list of tickers on the command
# line and print the results.

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
        # All the magic is wrapped up in this.  We call screen() to run the
        # screener code defined above.  If it returns True we continue.  If 
        # it returns False we're done.
        if (myScreen.screen(ticker) == False):
            break

# At some point we have to run the program.

if __name__ == "__main__":
    main()