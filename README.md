# stonks

This repo is a project I'm working on for stock analysis, in Pyhton, using Financial Modeling Prep as the data source.  My goal is to get a program that can sift through potential investments and flag them for further review.

## About Alpha Vantage

[Financial Modeling Prep website.](https://site.financialmodelingprep.com/)

You'll need to get an API key.  Save this key in `api_key.txt`.  Get your own key; it's free.

The free tier of service is enough for basic use.  A year of "Starter" tier service works out to $10.50 a month and lists most of the limits you'll run in to as an individual investor.  My goal here was to keep this usable on the free tier.

## Other Packages Used

If you're using stonks you will also need these Python libraries:
* math,
* matplotlib,
* numpy, and
* requests.
These are used inside stonks.  You do not have to use them directly.

## F-Score

I use Piotrosky's F-Score as a proxy for fundamental health of the business.  [The definition is available on Wikipedia.](https://en.wikipedia.org/wiki/Piotroski_F-score)  In summary, you get one point for each of the following:

Profitability
*  Return on Assets (1 point if it is positive in the current year, 0 otherwise);
*  Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise);
*  Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one, 0 otherwise);
*  Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise);

Leverage, Liquidity and Source of Funds
* Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one, 0 otherwise);
* Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise);
* Change in the number of shares (1 point if no new shares were issued during the last year);

Operating Efficiency
* Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise);
* Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise);

Overall a given stock gets a score from 0 to 9.
* A score of 0-3 indicates weak fundamentals, and you should stay away.
* A score of 7-9 indicates strong fundamentals.
* And 4-6 is somewhere in between.

The scoring touches on the income statement, balance sheet, and cash flow statement.  I like this because we don't get hung up on particular points.

## Growth Rate Estimate

I fit a line to the available operating cash flow numbers to get an estimate of growth rate.  This uses historical data so it can't anticipate future trends.  That's OK; you can't anticipate those trends, either.  We're going with what we know.

## Discounted Cash Flow

If you assume a growth rate, you can project potential earnings, discount those future earnings back to present value, and sum them up to get a theoretically correct intrinsic value.  There are a few problems with this:
* Predictions are difficult, especially about the future.  You think you know the growth rate, but you don't, really.
* DCF assumes a small terminal value for growth rate.  And this is probably wrong.  Most successful businesses keep coming up with new ideas and keep growing.

So with these limitations in mind, we follow the recipe and predict an intrinsic value based on a provided growth rate estimate.  We use current EPS for earnings.  Ideally we'd use free cash flow, but that's harder to estimate, requires more API reads (respect the free tier), and in the end provides a degree of accuracy you really can't assume here.  For value investing, you want to buy at a discount to intrinsic value.  We don't have to be exactly right on this.  Mostly right will do.

## BMW Charts

BMW charts are hard to explain succinctly.  Summary is we fit a line to the log of the historical share price to make price predictions.  Based on standard deviations, we can estimate if the price is too high or too low.

More info here: https://invest.kleinnet.com/bmw1/


# Other programs

Other programs in this repo make use of stonks:
* stonks.py -- library defining the class, used by other programs.
* basics.py -- dumps out overview information on stocks listed on command line.
* fscore.py -- reports Piotrosky f-score for stocks listed on command line.
* screen1.py -- looks for stocks with high f-scores whose recent price is below estimated intrinsic value.
* screen2.py -- improved version of screen1, adds check that recent price is below long-term trends.
* bmw1.py -- draws a BMW chart for the named stocks.
