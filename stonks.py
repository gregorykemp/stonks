# stonks.py
#
# A Python library to get stock data from Financial Modeling Prep.
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

# Python library for REST API requests
import requests

# This is used for fitting a line to data.
import numpy
Polynomial = numpy.polynomial.Polynomial

# charts and graphs
import matplotlib.pyplot as plt 
from matplotlib.colors import LinearSegmentedColormap
from math import ceil, floor, log10

# And this is the class itself.

class stonks:

    def __init__(self, symbol, api_key, verbose=False):
        # Set verbosity flag
        self.verbose = verbose

        # Initialize API count
        self.apiCount = 0

        # Save this, you'll need it later
        self.api_key = api_key

        # validate input symbol
        if (type(symbol) != str):
            raise ValueError("Can't understand symbol {}".format(str(symbol)))
        self.symbol = symbol.upper()

        # Sign on.
        if (self.verbose):
            print("I am a stonk and my symbol is {}".format(self.symbol))
        
        # Hit database for profile.
        temp1 = self._fmp_api("profile")
        # If the returned list is nonzero then we got something.
        if (len(temp1) > 0):
            self.overview = temp1[0]
        # else the lookup failed and we need to communicate that back to the caller.
        else:
            raise KeyError("FMP database lookup of {} failed.".format(self.symbol))

        if (self.verbose):
            print("Name: {}".format(self.overview['companyName']))
        

        # Initialize some fields.
        # Start with an empty dictionary.  We don't actually fetch these until
        # they're used to economize on API calls.
        self.income = {}
        self.balance = {}
        self.cashflow = {}
        self.annualCashflow = {}
        self.dailyPrice = {}

    # This wraps up API calls to the service.
    def _fmp_api(self, query, verbose=False):
        
        # Build an API call.
        # Symbol has to be uppercase.  We covered that in the stonk init method.
        myApiCall = "https://financialmodelingprep.com/api/v3/{}/{}".format(query, self.symbol)

        if (verbose):
            print("myApiCall = {}".format(myApiCall))
        
        # Make the API call.
        payload = {'apikey':self.api_key}
        response = requests.get(myApiCall, params=payload)

        if (verbose):
            print("status code = {}".format(response.status_code))
        
        # Process status code.  Well, mostly, blow yourself up if it's not success.
        if (response.status_code != 200):
            print("Error: bad API status code {}.".format(response.status_code))
            raise AssertionError("FMP API lookup for {} failed with error code {} ({}).".format(self.symbol, response.status_code, response.reason))
        
        # Bump API count for this stonk.
        # gkemp FIXME : refactor and move this to a singleton for all stonks.
        self.apiCount += 1

        # return the result.
        return response.json()


    # This helper function reads the income statement from Financial Modeling Prep.
    # This, and the next two functions, just return if the data has already
    # been downloaded.  I might be able to condense this down to one function
    # if I didn't need the result to go to a different member.

    def getIncome(self):
        # Only make the API call if you need to.
        if (len(self.income) == 0):
            self.income = self._fmp_api("income-statement")
            self.apiCount += 1
        
    # Related: this returns EPS.
    def getEPS(self):
        if (len(self.income) == 0):
            self.getIncome()
        # guard against list lookup failure.
        if (len(self.income) > 0):
            result = self.income[0]['eps']
        else:
            # wrong but safe
            result = 0.01
        return result


    # This helper function gets the balance sheet.

    def getBalance(self):
        # Only make the API call if you need to.
        if (len(self.balance) == 0):
            self.balance = self._fmp_api("balance-sheet-statement")
            self.apiCount += 1


    # This gets the cash flow statement.
    
    def getCashFlow(self):
        # Only make the API call if you need to.
        if (len(self.cashflow) == 0):
            self.cashflow = self._fmp_api("cash-flow-statement")
            self.apiCount += 1

    # Some screens want a recent price.  FMP gives us that on the overview.
    # So we're just wrapping that up and returning it here.  In case we 
    # need to change this again, we can hide that change here.

    def getRecentPrice(self):
        return (self.overview['price'])


    # Wrapper to get revenue.
    def getRevenue(self, year=0):
        if (len(self.income) == 0):
            self.getIncome()
        return self.income[year]['revenue']

    # Wrapper to get net income.
    def getNetIncome(self, year=0):
        if (len(self.income) == 0):
            self.getIncome()
        return self.income[year]['netIncome']

    # Wrapper to get free cash flow
    def getFCF(self, year=0):
        if (len(self.cashflow) == 0):
            self.getCashFlow()
        return self.cashflow[year]['freeCashFlow']

    # wraooer to get dividends paid
    def getDividendsPaid(self, year=0):
        if (len(self.cashflow) == 0):
            self.getCashFlow()
        # FMP stores dividends paid as a negative value
        return -1 * self.cashflow[year]['dividendsPaid']
    
    # wrapper to get total equity
    def getTotalEquity(self, year=0):
        if (len(self.balance) == 0):
            self.getBalance()
        return self.balance[year]['totalEquity']

    # wrapper to get total debt
    def getTotalDebt(self, year=0):
        if (len(self.balance) == 0):
            self.getBalance()
        return self.balance[year]['totalDebt']

    # wrapper to get cash and cash equivalents
    def getCashAndEquivalents(self, year=0):
        if (len(self.balance) == 0):
            self.getBalance()
        return self.balance[year]['cashAndCashEquivalents']

    # wrapper to return recent close
    def getRecentPrice(self):
        # I don't check overview because stonk wouldn't exist without it.
        return self.overview['price']

    # This pulls daily prices.  Well it pulls a big mess.  We should condition
    # the data into lists of dates, and closing prices.  Contrary to the docs 
    # you get all of this back per entry:
    # {'date': '2017-10-03', 'open': 38.5024986, 'high': 38.7724991, 'low': 38.4775009, 'close': 38.6199989, 'adjClose': 36.6528969, 'volume': 64921200.0, 'unadjustedVolume': 64921200.0, 'change': -1.8496, 'changePercent': -4.804, 'vwap': 37.96763, 'label': 'October 03, 17', 'changeOverTime': -0.04804}
    # Also inconveniently we only get five years of prices on the free tier 
    # of service.
    #
    # I think the only place this is used right now is in the BMW method
    # function.  See what that needs for input data conditioning and do
    # that here.

    def getDailyPrice(self):
        if (len(self.dailyPrice) == 0):
            self.dailyPrice = self._fmp_api("historical-price-full")
            self.apiCount += 1
        
        # So we get a list of tuples, date and adjClose.  From newest ([0]) on
        # down to the oldest.  We work backwards from the end to build the list
        # used in the BMW analysis.

            self.dateList = []
            self.priceList = []

            temp = list(self.dailyPrice['historical'])
            for i in range((len(temp)-1),0,-1):
                self.dateList.append(temp[i]['date'])
                self.priceList.append(temp[i]['adjClose'])

        if (self.verbose):
            for i in range(0,len(self.dateList)):
                print("{}: {:.2f}".format(self.dateList[i], self.priceList[i]))


    # This gets the earnings data from Financial Modeling Prep.

    # this seems to be obsolete and has a problem (we don't import time anymore)
    # gkemp FIXME remove obsolete code.
    # def getAnnualCashflow(self):
    #     while (len(self.annualCashflow.keys()) == 0):
    #         try:
    #             # This throws a warning but the code is correct.
    #             self.annualCashflow, self.annualCashflow_meta = self.fundamentals.get_cash_flow_annual(symbol=self.symbol)
    #         except ValueError:
    #             print("Sleeping for 1 minute.")
    #             time.sleep(60)
    #     self.apiCount += 1

    # This returns the API access count
    def getApiCount(self):
        return self.apiCount

    # This helper dumps the overview.
    def dumpOverview(self):
        for key in self.overview:
            print("{}: {}".format(key, self.overview[key]))


    # This helper dumps out the balance sheet.
    def dumpBalanceSheet(self):
        for i in range(0,len(self.balance)):
            print("i = {}".format(i))
        
            for key in self.balance[i]:
                print("{} : {}".format(key, self.balance[i][key]))


    # This returns f score term #1 - is return on assets above zero this year?
    # net income / current assets > 0
    def __fscore1(self):
        self.getIncome()
        self.getBalance()
        netIncome = int(self.income[0]["netIncome"])
        # Don't risk the denominator being 0.
        currentAssets = max(int(self.balance[0]["totalCurrentAssets"]),1)

        # gkemp FIXME this simplifies to netIncome is > 0.
        if ((netIncome/currentAssets) > 0):
            result = 1
        else:
            result = 0

        # Verbose report
        if (self.verbose):
            print("fscore1: return on assets is positive: {}".format(result))
            print("\tnet income = {:,}".format(netIncome))
            print("\tcurrent assets = {:,}".format(currentAssets))

        return result
        
    # This returns f score term #2 - is operating cash flow positive in this year?
    # Operating Cash Flow = Operating Income + Depreciation – Taxes + Change in Working Capital 
    # This is also documented on the cash flow statement.

    def __fscore2(self):
        self.getCashFlow()
        if (int(self.cashflow[0]["operatingCashFlow"]) > 0):
            result = 1
        else:
            result = 0
        
        # verbose report
        if (self.verbose):
            print("fscore2: operating cash flow is positive: {}".format(result))
            print("\toperating cash flow = {:,}".format(int(self.cashflow["operatingCashflow"][0])))
        
        return result

    # This returns f score term #3.  Return on assets needs to be greater this
    # year vs. last year.  I'm using float() instead of int() because this may
    # return a fractional number.

    def __fscore3(self):
        self.getIncome()
        self.getBalance()

        # Read the index as "N years ago".
        # Catch error if current assets returns 0.  Could be database error.
        try:
            roaThisYear = float(self.income[0]["netIncome"]) / float(self.balance[0]["totalCurrentAssets"])
            roaLastYear = float(self.income[1]["netIncome"]) / float(self.balance[1]["totalCurrentAssets"])

            # I deviate slightly from Piotrosky here.  I award a point if ROA stays even.
            if (roaThisYear >= roaLastYear):
                result = 1
            else:
                result = 0
            
            # verbose report
            if (self.verbose):
                print("fscore3: ROA greater this year than last year: {}".format(result))
                print("\tROA this year: {}".format(roaThisYear))
                print("\tROA last year: {}".format(roaLastYear))
        
        # Something bad happened.  Catch and log the error, and return a 
        # useable result.
        except ZeroDivisionError as err:
            print("fscore3: ROA greater this year than last year: ERROR: {}".format(err))
            result = 0

        return result

    # This returns f score term #4.
    # Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise) 

    def __fscore4(self):
        self.getIncome()
        self.getBalance()
        # Putting everything to float so I don't have to do a second integer-to-
        # float conversion later in the if statement.
        operatingCashflow = float(self.cashflow[0]["operatingCashFlow"])

        try:
            totalAssets = float(self.balance[0]["totalAssets"])
            roaThisYear = float(self.income[0]["netIncome"]) / float(self.balance[0]["totalCurrentAssets"])

            if ((operatingCashflow/totalAssets) > roaThisYear):
                result = 1
            else:
                result = 0
            
            # verbose report
            if (self.verbose):
                print("fscore4: operating cash flow/total assets > ROA: {}".format(result))
                print("\toperating cash flow = {:,}".format(int(self.cashflow[0]["operatingCashflow"])))
                print("\ttotal assets = {:,}".format(int(totalAssets)))
                print("\tROA this year = {}".format(roaThisYear))
        
        # Something bad happened.  Catch and log the error.  Return a useable result.
        except ZeroDivisionError as err:
            print("fscore4: operating cash flow/total assets > ROA: ERROR: {}".format(err))
            result = 0

        return result

    # This returns f score term #5.
    # You get one point if this year's long-term leverage ratio is less than last year's.
    # long-term leverage ratio = long-term debt / total assets

    def __fscore5(self):
        self.getBalance()
        # Do we encode no debt as zero debt?  Hell Naw.  That would be easy.
        # if ((type(self.balance[0]["longTermDebt"]) == "str") and (self.balance[0]["longTermDebt"].lower() == "none")):
        #     thisYearLTLR = 0.0
        # else:
        thisYearLTLR = float(self.balance[0]["longTermDebt"]) / float(self.balance[0]["totalAssets"])

        # if (self.balance[1]["longTermDebt"].lower() == "none"):
        #     lastYearLTLR = 0.0
        # else:
        lastYearLTLR = float(self.balance[1]["longTermDebt"]) / float(self.balance[1]["totalAssets"])

        # We have to compare <= instead of < to cover the case where debt is zero
        # in both years.  We want to reward that behavior, not punush it.
        if (thisYearLTLR <= lastYearLTLR):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("fscore5: long-term leverage ratio is lower this year vs. last year: {}".format(result))
            print("\tthis year's LTLR = {}".format(thisYearLTLR))
            print("\tlast year's LTLR = {}".format(lastYearLTLR))

        return result

    # This returns f score term #6:
    # Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    # I will say current ratio is one of my favorite indicators.

    def __fscore6(self):
        self.getBalance()

        try:
            currentRatioThisYear = float(self.balance[0]["totalCurrentAssets"]) / float(self.balance[0]["totalCurrentLiabilities"])
            currentRatioLastYear = float(self.balance[1]["totalCurrentAssets"]) / float(self.balance[1]["totalCurrentLiabilities"])

            # Intentionally not giving a pass to current ratio being equal.
            if (currentRatioThisYear > currentRatioLastYear):
                result = 1
            else:
                result = 0

            # verbose report
            if (self.verbose):
                print("fscore6: current ratio higher this year vs. last year: {}".format(result))
                print("\tcurrent ratio this year = {}".format(currentRatioThisYear))
                print("\tcurrent ratio last year = {}".format(currentRatioLastYear))

        # Something bad happened.  Catch and log the error.  Return a useable result.
        except ZeroDivisionError as err:
            print("fscore6: current ratio higher this year vs. last year: ERROR: {}".format(err))
            result = 0
            
        return result

    # This returns f score term #7: not issuing stock.
    # Change in the number of shares (1 point if no new shares were issued during the last year)

    def __fscore7(self):
        self.getBalance()
        sharesThisYear = int(self.balance[0]["commonStock"])
        sharesLastYear = int(self.balance[1]["commonStock"])

        if (sharesThisYear <= sharesLastYear):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("fscore7: not issuing stock: {}".format(result))
            print("\tsharesThisYear = {:,}".format(sharesThisYear))
            print("\tsharesLastYear = {:,}".format(sharesLastYear))


        return result
    
    # This returns f score term #8: change in gross margin
    # Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)

    def __fscore8(self):
        self.getIncome()
        
        # Now you'd think this would never fail, but sometimes the database 
        # returns bad data.  So wrap this up so we return something instead
        # of blowing ourselves up.
        try:
            grossMarginThisYear = (float(self.income[0]["revenue"]) - float(self.income[0]["costOfRevenue"])) / float(self.income[0]["revenue"])
            grossMarginLastYear = (float(self.income[1]["revenue"]) - float(self.income[1]["costOfRevenue"])) / float(self.income[1]["revenue"])

            if (grossMarginThisYear > grossMarginLastYear):
                result = 1
            else:
                result = 0

            # verbose report
            if (self.verbose):
                print("fscore8: gross margin higher this year vs. last year: {}".format(result))
                print("\ttotal revenue this year: {:,}".format(float(self.income[0]["totalRevenue"])))
                print("\ttotal revenue last year: {:,}".format(float(self.income[1]["totalRevenue"])))
                print("\tcost of sales this year: {:,}".format(float(self.income[0]["costOfRevenue"])))
                print("\tcost of sales last year: {:,}".format(float(self.income[1]["costOfRevenue"])))

        # Something bad happened.  Log the error and return a usable result.
        except ZeroDivisionError as err:
            print("fscore8: gross margin higher this year vs. last year: ERROR: {}".format(err))
            result = 0
        
        return result

    # This returns f score term #9: 
    # Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    # asset turnover is net sales divided by average total assets

    def __fscore9(self):
        self.getBalance()
        self.getIncome()
        avgTotalAssetsThisYear = (float(self.balance[0]["totalAssets"]) + float(self.balance[1]["totalAssets"])) / 2.0
        avgTotalAssetsLastYear = (float(self.balance[1]["totalAssets"]) + float(self.balance[2]["totalAssets"])) / 2.0

        assetTurnoverThisYear = float(self.income[0]["revenue"]) / avgTotalAssetsThisYear
        assetTurnoverLastYear = float(self.income[1]["revenue"]) / avgTotalAssetsLastYear

        if (assetTurnoverThisYear > assetTurnoverLastYear):
            result = 1
        else:
            result = 0

        # verbose report
        if (self.verbose):
            print("fscore9: asset turnover ratio higher this year vs. last year: {}".format(result))
            print("\taverage total assets this year: {}".format(avgTotalAssetsThisYear))
            print("\taverage total assets last year: {}".format(avgTotalAssetsLastYear))
            print("\tasset turnover this year: {:,}".format(assetTurnoverThisYear))
            print("\tasset turnover last year: {:,}".format(assetTurnoverLastYear))

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
        
        # get historical cash flows from database
        # self.getAnnualCashflow()
        self.getCashFlow()

        # Indexing self.annualCashflow returns a pandas object, not a real list.
        # So there's some shenanigans getting the data how we want it.

        # Let there be lists!
        myDateList = []
        myFlowList = []

        # Make a list explicitly from the pandas data frame, casting things to 
        # the type we need them to be.
        for index in range(0, len(self.cashflow)):
            myDateList.append(self.cashflow[index]['date'])
            myFlowList.append(self.cashflow[index]['operatingCashFlow'])

        # But the lists are backwards.  Reverse them.
        myDateList.reverse()
        myFlowList.reverse()

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
       
        # Can't assume this has been called previously.
        if (len(self.income) == 0):
            self.getIncome()
        cashFlowPerShare = float(self.income[0]['eps'])
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

    # This method draws a BMW Chart for the stonk.
    # More info here: https://invest.kleinnet.com/bmw1/
    # Summary is we fit a line to the log of the historical share price to make price predictions.

    def bmwChart(self, chart=True):

        # Get historical price data.
        self.getDailyPrice()
        
        # gkemp FIXME : I don't like that we do this here.  Not sure how to address
        # that here, though.
        years = float(len(self.dateList)/365)

        # I need a numpy array, not a list.
        myPrices = numpy.array(self.priceList)
        # And because the data grows geometrically we want the log of the original data.
        # log returns natural log.
        myLogPrices = numpy.log(myPrices)

        # Now that we're in arithmetic space we can fit a simple line.
        pfit = Polynomial.fit(range(0, len(self.priceList)), myLogPrices, 1, window=(0, len(self.dateList)), domain=(0, len(self.dateList)))
        # extract results
        m = float(pfit.coef[1])
        b = float(pfit.coef[0])

        # Define a range for the plot, would prefer it was dates.
        x = numpy.arange(0, len(self.priceList))
        
        # I don't know that this is necessary. It does make the linter happy.
        myLogLineList = []
        myLogPlus1Sigma = []
        myLogPlus2Sigma = []
        myLogMinus1Sigma = []
        myLogMinus2Sigma = []

        # I need min and max values across all five data series. Since we're 
        # building them here, compute min and max along the way. I'll use this
        # later to label the Y axis of the chart.
        yAxisMin = 1000000000
        yAxisMax = 0
        
        # Make a list of log predicted price points.
        for index in range(0, len(self.priceList)):
            temp = m*index + b
            myLogLineList.append(temp)
            yAxisMin = min(yAxisMin, temp)
            yAxisMax = max(yAxisMax, temp)

        # I also want the standard deviation of the difference between the 
        # prices vs. the expected values. There is probably a better way of 
        # doing this. I need the root mean square here. I'm not convinced 
        # numpy is doing exactly what I want. I need the square of the 
        # differences between the actual and predicted values. That's what we 
        # do here:
        tempList = []
        for index in range(0, len(self.priceList)):
            tempList.append((myLogPrices[index] - myLogLineList[index]) ** 2)
        # Now I take the square root of the average of the contents of the list.
        # For a weakly typed language, I sure do have to do a lot of type 
        # conversions to make these things work out.
        sigma = float(numpy.sqrt(numpy.average(numpy.array(tempList))))
        
        if (self.verbose):
            print("debug: sigma={}".format(sigma))

        # Use the previously computed predicted price points and sigma to 
        # compute +/- RMS lines, too.  Still in log space.
        for index in range(0, len(self.priceList)):
            myLogPlus1Sigma.append(myLogLineList[index] + sigma)
            myLogPlus2Sigma.append(myLogLineList[index] + 2 * sigma)
            myLogMinus1Sigma.append(myLogLineList[index] - sigma)
            myLogMinus2Sigma.append(myLogLineList[index] - 2* sigma)
            yAxisMin = min(yAxisMin, myLogPlus1Sigma[index])
            yAxisMax = max(yAxisMax, myLogPlus1Sigma[index])
            yAxisMin = min(yAxisMin, myLogPlus2Sigma[index])
            yAxisMax = max(yAxisMax, myLogPlus2Sigma[index])
            yAxisMin = min(yAxisMin, myLogMinus1Sigma[index])
            yAxisMax = max(yAxisMax, myLogMinus1Sigma[index])
            yAxisMin = min(yAxisMin, myLogMinus2Sigma[index])
            yAxisMax = max(yAxisMax, myLogMinus2Sigma[index])

        # Convert lists to arrays.
        myLogLineArray = numpy.array(myLogLineList)
        myLogPlus1Array = numpy.array(myLogPlus1Sigma)
        myLogPlus2Array = numpy.array(myLogPlus2Sigma)
        myLogMinus1Array = numpy.array(myLogMinus1Sigma)
        myLogMinus2Array = numpy.array(myLogMinus2Sigma)

        # We use this repeatedly, save it here.
        last = len(self.dateList) - 1

        # CAGRs, needed whether we draw a chart or not.
        trueCAGR = float(((myPrices[last]/myPrices[0]) ** (1/years) - 1) * 100)
        fitCAGR = float(((numpy.exp(myLogLineArray[last])/numpy.exp(myLogLineArray[0])) ** (1/years) - 1) * 100)

        # So we have to return something now.  Chart is optional.
        result = []                                                 # a de facto type declaration
        result.append(fitCAGR)                                      # the CAGR of the line we fit to the log of the prices
        result.append(trueCAGR)                                     # the CAGR of the actual price data
        result.append(float(myPrices[last]))                        # the last price we got from FMP
        result.append(float(numpy.exp(myLogLineArray[last])))       # the last price on the line fit to the log of the prices

        # Draw a linear graph, maybe.
        if chart:
            # FIXME list:
            # Plot two charts, one log and one linear, stacked vertically.
            # Set legend location outside of plot area.

            # Determine range for y axis.
            yAxisMinimum = 10*floor(numpy.exp(yAxisMin)/10)
            yAxisMaximum = 10*ceil(numpy.exp(yAxisMax)/10)
            yAxisLabelsFull = [ 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000 ]

            # Search up for lower bound.
            lowerBound = 0
            while (yAxisMinimum > yAxisLabelsFull[lowerBound]):
                lowerBound += 1
            
            # Repeat for upper bound.
            upperBound = 0
            while (yAxisMaximum > yAxisLabelsFull[upperBound]):
                upperBound += 1
            upperBound += 1

            # It's this easy, right?
            yAxisTicks = yAxisLabelsFull[lowerBound:upperBound]

            # Now make text labels for this.
            yAxisLabels = []
            for index in yAxisTicks:
                yAxisLabels.append("${}".format(index))

            # Plot actual historical prices.
            plt.plot(x, myPrices, label="price", color="blue")
            plt.text(x[last], myPrices[last], "${:.02f}".format(myPrices[last]), color="blue")
            # Plot best fit line.
            plt.plot(x, numpy.exp(myLogLineArray), label="best fit line", color="black")
            plt.text(x[last], numpy.exp(myLogLineArray)[last], "${:.02f}".format(numpy.exp(myLogLineArray)[last]), color="black")
            # And the +/- sigma lines.
            plt.plot(x, numpy.exp(myLogPlus1Array), label="+1 RMS", color="red", linestyle='dashed')
            plt.text(x[last], numpy.exp(myLogPlus1Array)[last], "${:.02f}".format(numpy.exp(myLogPlus1Array)[last]), color="red")
            plt.plot(x, numpy.exp(myLogPlus2Array), label="+2 RMS", color="red", linestyle='solid')
            plt.text(x[last], numpy.exp(myLogPlus2Array)[last], "${:.02f}".format(numpy.exp(myLogPlus2Array)[last]), color="red")
            plt.plot(x, numpy.exp(myLogMinus1Array), label="-1 RMS", color="green", linestyle='dashed')
            plt.text(x[last], numpy.exp(myLogMinus1Array)[last], "${:.02f}".format(numpy.exp(myLogMinus1Array)[last]), color="green")
            plt.plot(x, numpy.exp(myLogMinus2Array), label="-2 RMS", color="green", linestyle='solid')
            plt.text(x[last], numpy.exp(myLogMinus2Array)[last], "${:.02f}".format(numpy.exp(myLogMinus2Array)[last]), color="green")
            # Set tick scale for Y axis.
            plt.yscale("log")
            # yticks is what I want. This sets the values and labels for the y axis. 
            # Didn't expect I'd need to build this myself.
            plt.yticks(yAxisTicks, yAxisLabels, color="gray")
            # Set tick labels for X axis.  Limit the number of labels printed.
            plt.xticks(numpy.arange(0, len(self.dateList)), self.dateList)
            plt.locator_params(axis='x', nbins=10)
            # Set chart title.
            plt.title("BMW Chart for {} ({})".format(self.overview['companyName'], self.symbol.upper()))
            # Turn on grids.  I want heaver grid action on the Y axis.
            plt.grid(b=True, axis='x', which='major')
            plt.grid(b=True, axis='y', which='both')
            # CAGRs        
            plt.plot(0, 0, label="true CAGR: {:.02f}%".format(trueCAGR), color="white")
            plt.plot(0, 0, label="fit CAGR: {:.02f}%".format(fitCAGR), color="white")
            # Yes, legends.
            plt.legend()
            plt.show()            
        
        # Always return this result, though.
        return result

    # end of bmwChart

# end of class stonks


# This class is a base class used by screener apps.

class screen:

    # We always do these things at the beginning of a screen.  Move them to the
    # init function of the screen class.  Creating the child screener class will
    # initialize these housekeeping variables.

    def __init__(self):
        # Read API key from text file. We don't validate the key here. You'll die soon enough if it's bad.
        # gkemp FIXME add file error handling here.
        api_file = open("api_key.txt", "r")
        self.api_key = api_file.read()

        self.apiCount = 0

    # This is the standard wrapper.  It runs for all screens.

    def screen(self, ticker) -> bool:
        # This creates the stonk.  This will return a key error if the ticker 
        # doesn't exist in the database.  If the ticker exists, call the 
        # extendable method to run this particular screen.
        try:
            self.thisStonk = stonks(ticker, self.api_key)
            self.runScreen()
        except KeyError:
            print("Ticker {} not found in database.".format(ticker))

        # Return whether we're over the API limit.
        # gkemp FIXME make the API limit a parameter of __init__()
        return (self.apiCount > 400)            

    # This is the method the user is expected to extend.

    def runScreen(self):
        pass

# end of class screen