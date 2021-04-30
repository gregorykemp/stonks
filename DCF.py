# DCF.py
#
# Experimenting with projecting growth rates from cash flows.
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

    # Loop through the list of command line arguments provided.
    for ticker in (sys.argv[1:]):
        print("{}:".format(ticker))
        
        # Now users do dumb shit, like look for data on tickers that don't exist,
        # and sometimes they make typos.  Allow for this, gracefully.  We know
        # stonks will return a KeyError if we can't find the ticker in the 
        # database.  Catch it, and continue, in case there are more arguments 
        # to be processed.
        try:
            thisStonk = stonks(ticker, api_key)
        except KeyError:
            print("Could not find " + ticker + " in database.")
            continue

        growthRate = thisStonk.estimateGrowthRate()
        intrinsicValue = thisStonk.discountedCashFlow(growthRate)
        print("{}: {:.02f}% ${:2.02f}".format(ticker, (growthRate*100), intrinsicValue))
        print("{}".format(thisStonk.getApiCount()))

if __name__ == "__main__":
    main()