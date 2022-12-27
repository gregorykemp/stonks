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
from stonks import screen

# Make a child class from the base screener class.

class screen1(screen):

    # extend per-screen method:

    def runScreen(self):

        # Step 1: is EPS positive?
        if(self.thisStonk.getEPS() > 0):
            fscore = self.thisStonk.fScore()
            # Always print the summary score.
            print("{} f-score: {}".format(self.thisStonk.symbol, sum(fscore)))

            # Step 2: is F-score greater than 5?
            if (sum(fscore) > 5):
                # gkemp FIXME need to scrub this method
                growthRate = self.thisStonk.estimateGrowthRate()

                # Step 3: is growth rate above 15%
                if (growthRate > 0.15):
                    recentPrice = float(self.thisStonk.getRecentPrice())
                    # gkemp FIXME need to scrub this method too
                    intrinsicValue = self.thisStonk.discountedCashFlow(growthRate)
                    print("{}: {:.02f}% ${:2.02f}".format(self.thisStonk.symbol, (growthRate*100), intrinsicValue))
                    print("   intrinsic value: ${:.02f}".format(intrinsicValue))
                    print("      recent price: ${:.02f}".format(recentPrice))

                    # Step 4: is recent price below intrinsic value?
                    if (recentPrice < intrinsicValue):
                        # No chart for batch mode.
                        bmwResult = self.thisStonk.bmwChart(chart=False)

                        print("    forecast price: ${:.02f}".format(bmwResult[3]))
                        print("        price CAGR: {:.02f}%".format(bmwResult[1]))
                        print("     forecast CAGR: {:.02f}%".format(bmwResult[0]))

                        # Here we are:
                        # 1. EPS is positive (no scrubs), and
                        # 2. F-score greater than 5 (sound balance sheet), and
                        # 3. growth rate above 15% (want growth), and
                        # 4. recent price below intrinsic value, and 
                        # 5. recent price below BMW long-term average.
                        #
                        # Looking for forecast CAGR above 10% and current price below long term trend.
                        # gkemp FIXME again the threshold should be a parameter.
                        if (bmwResult[0] > 10.0) and (bmwResult[3] > bmwResult[2]):
                            # This is the message we want to see in the log file.
                            # Flag it with $$$ since I'm looking for $$$ from my stonks.
                            print("$$$ {} is a candidate!".format(self.thisStonk.symbol))
        else:
            # Else EPS was negative, no need to look further.
            print("{}: {} EPS is negative, we're done.".format(self.thisStonk.symbol, self.thisStonk.getEPS()))
        
        # Flush the pipe. Helpful if debug messages are stuck in the buffer.
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
        print("------------------------------")
        # All the magic is wrapped up in this.  We call screen() to run the
        # screener code defined above.  If it returns False we continue.  If 
        # it returns True we're done.
        if (myScreen.screen(ticker) == True):
            break

# At some point we have to run the program.



if __name__ == "__main__":
    main()