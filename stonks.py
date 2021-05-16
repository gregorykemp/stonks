# stonks.py
#
# A Python library to get stock data from Alpha Vantage.
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

# We The alpha_vantage class returns data in JSON format.  Also sometimes pandas
# although you'll never touch the pandas results.
import json
# Here we pull the class to get fundamentals data from Alpha Vantage.
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries
# We use the sleep method on this object.
import time
# This is used for fitting a line to data.
import numpy
Polynomial = numpy.polynomial.Polynomial

# charts and graphs
# import matplotlib.pyplot as plt 

# And this is the class itself.

class stonks:

    def __init__(self, symbol, api_key, verbose=False):
        # Set verbosity flag
        self.verbose = verbose

        # Initialize API count
        self.apiCount = 0

        # validate input symbol
        if (type(symbol) != str):
            raise ValueError("Can't understand symbol {}".format(str(symbol)))
        self.symbol = symbol

        # Sign on.
        if (self.verbose):
            print("I am a stonk and my symbol is {}".format(self.symbol))

        # Make connection to Alpha Vantage.
        self.fundamentals = FundamentalData(key=api_key, output_format='json')
        self.timeSeries = TimeSeries(key=api_key, output_format='json')
        if (self.verbose):
            print("Debug: {}", self.fundamentals.output_format)

        # Initialize some fields.
        # Start with an empty dictionary.
        self.overview = {}
        self.income = {}
        self.balance = {}
        self.cashflow = {}
        self.annualCashflow = {}
        self.dailyPrice = {}

        # Do this as many times as we have to to get a valid result.
        retryFlag = 0
        while ((not self.overview) and (retryFlag < 2)):
            try:
                # This throws a warning but the code is correct.
                self.overview, self.overview_meta = self.fundamentals.get_company_overview(symbol=self.symbol)
            except ValueError:
                # This likely means we hit the API access limit.  Wait one minute.
                # gkemp FIXME need to make this an option in case users have paid access.
                # In that case we can pop out immediately on ValueError.
                time.sleep(60)
                retryFlag += 1
        self.apiCount += 1

        # Try to validate results of the above retry loop.
        if (len(self.overview.keys()) == 0):
            raise KeyError("Count not find " + symbol + " in Alpha Vantage.")

        # verify we have a valid ticker before proceeding.  This should be
        # redundant code.
        if (self.overview["Symbol"].lower() != self.symbol.lower()):
            raise ValueError("couldn't find symbol "+ self.symbol + " in Alpha Vantage")


    # This helper function reads the income statement from Alpha Vantage.
    # This, and the next two functions, just return if the data has already
    # been downloaded from AlphaVantage.

    def getIncome(self):
        # I should be able to do "while (not self.income)" but that returned 
        # a weird, vague error: "The truth value of a DataFrame is ambiguous."
        # gkemp FIXME : there needs to be a retry limit here or you just hang.
        while (len(self.income.keys()) == 0):
            try:
                # This throws a warning but the code is correct.
                self.income, self.income_meta = self.fundamentals.get_income_statement_annual(symbol=self.symbol)
            except ValueError:
                print("Sleeping for 1 minute.")
                time.sleep(60)
        self.apiCount += 1

    # This helper function gets the balance sheet from Alpha Vantage.

    def getBalance(self):
        while (len(self.balance.keys()) == 0):
            try:
                # This throws a warning but the code is correct.
                self.balance, self.balance_meta = self.fundamentals.get_balance_sheet_annual(symbol=self.symbol)
            except ValueError:
                print("Sleeping for 1 minute.")
                time.sleep(60)
        self.apiCount += 1

    # This gets the cash flow statement from Alpha Vantage.
    
    def getCashFlow(self):
        while (len(self.cashflow.keys()) == 0):
            try:
                # This throws a warning but the code is correct.
                self.cashflow, self.cashflow_meta = self.fundamentals.get_cash_flow_annual(symbol=self.symbol)
            except ValueError:
                print("Sleeping for 1 minute.")
                time.sleep(60)
        self.apiCount += 1

    # This is similar, getting price history (adjusted for splits and dividends)
    # if needed. 

    def getDailyPrices(self):
        while (len(self.dailyPrice.keys()) == 0):
            try:
                self.dailyPrice, self.dailyPrice_meta = self.timeSeries.get_daily_adjusted(symbol=self.symbol)
            except ValueError:
                print("Sleeping for 1 minute.")
                time.sleep(60)
            self.apiCount += 1

    # This gets the earnings data from Alpha Vantage.

    def getAnnualCashflow(self):
        while (len(self.annualCashflow.keys()) == 0):
            try:
                # This throws a warning but the code is correct.
                self.annualCashflow, self.annualCashflow_meta = self.fundamentals.get_cash_flow_annual(symbol=self.symbol)
            except ValueError:
                print("Sleeping for 1 minute.")
                time.sleep(60)
        self.apiCount += 1

    # This returns the API access count
    def getApiCount(self):
        return self.apiCount

    # This helper dumps the overview.
    def dumpOverview(self):
        for key in self.overview:
            print("{}: {}".format(key, self.overview[key]))

    # This helper dumps out the balance sheet.
    def dumpBalanceSheet(self):
        for key in self.balance:
            print("{}:\n{}".format(key, self.balance[key]))


    # This returns f score term #1 - is return on assets above zero this year?
    # net income / current assets > 0
    def __fscore1(self):
        self.getIncome()
        self.getBalance()
        netIncome = int(self.income["netIncome"][0])
        currentAssets = int(self.balance["totalCurrentAssets"][0])

        # gkemp FIXME this simplifies to netIncome is > 0.
        if ((netIncome/currentAssets) > 0):
            result = 1
        else:
            result = 0

        # Verbose report
        if (self.verbose):
            print("\tdebug: net income = {:,}".format(netIncome))
            print("\tdebug: current assets = {:,}".format(currentAssets))

        return result
        
    # This returns f score term #2 - is operating cash flow positive in this year?
    # Operating Cash Flow = Operating Income + Depreciation – Taxes + Change in Working Capital 
    # This is also documented on the cash flow statement.

    def __fscore2(self):
        self.getCashFlow()
        if (int(self.cashflow["operatingCashflow"][0]) > 0):
            result = 1
        else:
            result = 0
        
        # verbose report
        if (self.verbose):
            print("\tdebug: operating cash flow = {:,}".format(int(self.cashflow["operatingCashflow"][0])))
        
        return result

    # This returns f score term #3.  Return on assets needs to be greater this
    # year vs. last year.  I'm using float() instead of int() because this may
    # return a fractional number.

    def __fscore3(self):
        self.getIncome()
        self.getBalance()
        # Read the index as "N years ago".
        roaThisYear = float(self.income["netIncome"][0]) / float(self.balance["totalCurrentAssets"][0])
        roaLastYear = float(self.income["netIncome"][1]) / float(self.balance["totalCurrentAssets"][1])

        # I deviate slightly from Piotrosky here.  I award a point if ROA stays even.
        if (roaThisYear >= roaLastYear):
            result = 1
        else:
            result = 0
        
        # verbose report
        if (self.verbose):
            print("\tdebug: ROA this year: {}".format(roaThisYear))
            print("\tdebug: ROA last year: {}".format(roaLastYear))

        return result

    # This returns f score term #4.
    # Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise) 

    def __fscore4(self):
        self.getIncome()
        self.getBalance()
        # Putting everything to float so I don't have to do a second integer-to-
        # float conversion later in the if statement.
        operatingCashflow = float(self.cashflow["operatingCashflow"][0])
        totalAssets = float(self.balance["totalAssets"][0])
        roaThisYear = float(self.income["netIncome"][0]) / float(self.balance["totalCurrentAssets"][0])

        if ((operatingCashflow/totalAssets) > roaThisYear):
            result = 1
        else:
            result = 0
        
        # verbose report
        if (self.verbose):
            print("\tdebug: operating cash flow = {:,}".format(int(self.cashflow["operatingCashflow"][0])))
            print("\tdebug: total assets = {:,}".format(int(totalAssets)))
            print("\tdebug: ROA this year = {}".format(roaThisYear))

        return result

    # This returns f score term #5.
    # You get one point if this year's long-term leverage ratio is less than last year's.
    # long-term leverage ratio = long-term debt / total assets

    def __fscore5(self):
        self.getBalance()
        # Do we encode no debt as zero debt?  Hell Naw.  That would be easy.
        if (self.balance["longTermDebt"][0].lower() == "none"):
            thisYearLTLR = 0.0
        else:
            thisYearLTLR = float(self.balance["longTermDebt"][0]) / float(self.balance["totalAssets"][0])

        if (self.balance["longTermDebt"][1].lower() == "none"):
            lastYearLTLR = 0.0
        else:
            lastYearLTLR = float(self.balance["longTermDebt"][1]) / float(self.balance["totalAssets"][1])

        # We have to compare <= instead of < to cover the case where debt is zero
        # in both years.  We want to reward that behavior, not punush it.
        if (thisYearLTLR <= lastYearLTLR):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("\tdebug: this year's LTLR = {}".format(thisYearLTLR))
            print("\tdebug: last year's LTLR = {}".format(lastYearLTLR))

        return result

    # This returns f score term #6:
    # Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    # I will say current ratio is one of my favorite indicators.

    def __fscore6(self):
        self.getBalance()
        currentRatioThisYear = float(self.balance["totalCurrentAssets"][0]) / float(self.balance["totalCurrentLiabilities"][0])
        currentRatioLastYear = float(self.balance["totalCurrentAssets"][1]) / float(self.balance["totalCurrentLiabilities"][1])

        # Intentionally not giving a pass to current ratio being equal.
        if (currentRatioThisYear > currentRatioLastYear):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("\tdebug: current ratio this year = {}".format(currentRatioThisYear))
            print("\tdebug: current ratio last year = {}".format(currentRatioLastYear))

        return result

    # This returns f score term #7: not issuing stock.
    # Change in the number of shares (1 point if no new shares were issued during the last year)

    def __fscore7(self):
        self.getBalance()
        sharesThisYear = int(self.balance["commonStock"][0])
        sharesLastYear = int(self.balance["commonStock"][1])

        if (sharesThisYear <= sharesLastYear):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("\tdebug: sharesThisYear = {:,}".format(sharesThisYear))
            print("\tdebug: sharesLastYear = {:,}".format(sharesLastYear))


        return result
    
    # This returns f score term #8: change in gross margin
    # Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)

    def __fscore8(self):
        self.getIncome()
        grossMarginThisYear = (float(self.income["totalRevenue"][0]) - float(self.income["costOfRevenue"][0])) / float(self.income["totalRevenue"][0])
        grossMarginLastYear = (float(self.income["totalRevenue"][1]) - float(self.income["costOfRevenue"][1])) / float(self.income["totalRevenue"][1])

        if (grossMarginThisYear > grossMarginLastYear):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("\tdebug: total revenue this year: {:,}".format(self.income["totalRevenue"][0]))
            print("\tdebug: total revenue last year: {:,}".format(self.income["totalRevenue"][1]))
            print("\tdebug: cost of sales this year: {:,}".format(self.income["costOfRevenue"][0]))
            print("\tdebug: cost of sales last year: {:,}".format(self.income["costOfRevenue"][1]))
        
        return result

    # This returns f score term #9: 
    # Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    # asset turnover is net sales divided by average total assets

    def __fscore9(self):
        self.getBalance()
        self.getIncome()
        avgTotalAssetsThisYear = (float(self.balance["totalAssets"][0]) + float(self.balance["totalAssets"][1])) / 2.0
        avgTotalAssetsLastYear = (float(self.balance["totalAssets"][1]) + float(self.balance["totalAssets"][2])) / 2.0

        assetTurnoverThisYear = float(self.income["totalRevenue"][0]) / avgTotalAssetsThisYear
        assetTurnoverLastYear = float(self.income["totalRevenue"][1]) / avgTotalAssetsLastYear

        if (assetTurnoverThisYear > assetTurnoverLastYear):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("\tdebug: average total assets this year: {}".format(avgTotalAssetsThisYear))
            print("\tdebug: average total assets last year: {}".format(avgTotalAssetsLastYear))

        return result


    # This public method calls the private individual methods and returns a list
    # of results.  
    # gkemp FIXME should we add this up here and return an integer?
    # Caller can use sum(stonk.fscore()) if they want that, though.

    def fScore(self):
        print("Calculating F score for {}.".format(self.symbol))

        # The problem with weakly typed languages is that you still need to 
        # declare types, you just end up doing it indirectly, like this.
        result = []

        result.append(self.__fscore1())
        result.append(self.__fscore2())
        result.append(self.__fscore3())
        result.append(self.__fscore4())
        result.append(self.__fscore5())
        result.append(self.__fscore6())
        result.append(self.__fscore7())
        result.append(self.__fscore8())
        result.append(self.__fscore9())

        return result

    # This is sugar to pretty print the f-score result.
    def fScorePrettyPrint(self, fScore):
        # gkemp FIXME validate fScore input

        print("F-score results:")

        print("Profitability:")
        print("{}\tReturn on Assets is positive in the current year.".format(fScore[0]))
        print("{}\tOperating Cash Flow is positive in the current year.".format(fScore[1]))
        print("{}\tReturn of Assets (ROA) higher in the current year compared to previous one.".format(fScore[2]))
        print("{}\tOperating Cash Flow/Total Assets is higher than ROA in the current year.".format(fScore[3]))

        print("Leverage, Liquidity and Source of Funds:")
        print("{}\tLong-term debt ratio lower this year compared to previous one.".format(fScore[4]))
        print("{}\tCurrent ratio higher in the current year compared to previous.".format(fScore[5]))
        print("{}\tNo new shares were issued during the last year.".format(fScore[6]))

        print("Operating Efficiency:")
        print("{}\tGross Margin higher in the current year compared to previous one.".format(fScore[7]))
        print("{}\tAsset Turnover ratio higher in the current year compared to previous.".format(fScore[8]))


    # This tries to compute the growth rate of the underlying business.
    def estimateGrowthRate(self):
        
        # get historical cash flows from Alpha Vantage
        self.getAnnualCashflow()

        # Indexing self.annualCashflow returns a pandas object, not a real list.
        # So there's some shenanigans getting the data how we want it.

        # Let there be lists!
        myDateList = []
        myFlowList = []

        # Make a list explicitly from the pandas data frame, casting things to 
        # the type we need them to be.
        for index in self.annualCashflow["fiscalDateEnding"].keys():
            myDateList.append(str(self.annualCashflow["fiscalDateEnding"][index]))
            # myFlowList.append(math.log(float(self.annualCashflow["operatingCashflow"][index])))
            myFlowList.append((float(self.annualCashflow["operatingCashflow"][index])))

        # But the lists are backwards.  Reverse them.
        myDateList.reverse()
        myFlowList.reverse()

        # Dump out what's in there.
        # for index in range(0, len(myDateList)):
            # print("{}: {}: {:,}".format(index, myDateList[index], myFlowList[index]))

        # Now, finally, make numpy arrays from the lists of conditioned data.
        # myDates = numpy.array(myDateList) # not used
        myFlows = numpy.array(myFlowList)

        # 1. Fit a line to this data.
        # pfit.coef is a list of coefficients: y = coef[0] + coef[1] * x
        pfit = Polynomial.fit(range(0, len(myDateList)), myFlows, 1, window=(0, len(myDateList)), domain=(0,len(myDateList)))
        
        # 2. Print the results.  Can't use the y-intercept for the denominator
        # because it may be negative (was with TTD).  From this I can swag a
        # growth rate estimate.
        growthRate = (float(pfit.coef[1])/float(myFlowList[0]))
        
        if(self.verbose):
            print("growth rate? {:.2f}%".format(growthRate * 100))

        return growthRate

    # This method takes a growth rate (you could use the method above....)
    # and projects an intrinsic value using DCF.  
    # terminal growth rate defaults to 2%.  Long-term inflation and GDP growth rate.
    # discount rate defaults to 9%.  Stock index funds return 8% basically for free.
    # I set years of growth at 10 years, which maybe is too high.

    def discountedCashFlow(self, growthRate, terminalRate=0.02, discountRate=0.09, yearsOfGrowth=10):

        # A little bit of validation.
        if (type(growthRate) != float):
            raise ValueError("Expected growthRate to be a float.")

        # then use growth rate to attempt a DCF analysis.
        # I use EPS here because
        #   1. Actually calculating free cash flow is hard, and
        #   2. DCF involves so much guesswork, even under ideal circumatances,
        #      that accuracy here is pointless.
        # The idea here is to get the DCF roughly right.
        
        cashFlowPerShare = float(self.overview["EPS"])
        # print("DEBUG: cashFlowPerShare = {:.02f}".format(cashFlowPerShare))

        # set up entry 0 in the array.
        discountArray = []
        discountArray.append(cashFlowPerShare)

        # compute growth rate for growth window.
        for year in range(1,(yearsOfGrowth+1),1):
            discountArray.append(discountArray[(year-1)] * (1 + growthRate))

        # compute terminal growth.
        for year in range((yearsOfGrowth+1),40,1):
            discountArray.append(discountArray[(year-1)] * (1 + terminalRate))
        
        # but need to discount those values.
        # gkemp FIXME make discount rate a parameter
        for year in range(1,40,1):
            discountArray[year] = discountArray[year] / ((1 + discountRate) ** year)

        # print("DEBUG: discount array = {}".format(discountArray))
        
        # Adding up the discounted values is this easy.
        discountedCashFlow = sum(discountArray)

        if (self.verbose):
            print("DCF intrinsic value estimate: {:.02f}".format(discountedCashFlow))

        return discountedCashFlow  
