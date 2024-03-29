# basics.py
#
# Get basic stock info on a stock.
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
        # gkemp FIXME catch errors here.
        temp = stonks(ticker, api_key, verbose=True)

        # dump overview data.
        temp.dumpOverview()   
        # temp.getBalance()
        # temp.dumpBalanceSheet()
        # temp.getIncome()     
        # temp.getCashFlow()
        # print("recent price: {}".format(temp.getRecentPrice()))

        # temp.getDailyPrice()
        # growthRate = temp.estimateGrowthRate()
        # print("growth rate: {}".format(growthRate))
        # print("DCF: {}".format(temp.discountedCashFlow(growthRate)))

        # temp.bmwChart()


if __name__ == "__main__":
    main()