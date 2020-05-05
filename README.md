# Financial Portfolio Management, Forecasting, and Optimization 

This repo explores various portfolio management theories, forecasting techniques, and optimization algorithms for financial portfolio management using ETF and macroeconomic data from Reuter's Datastream<sup>1</sup> and Wharton Research Data Services.<sup>2</sup>

The initial portfolio simulated on over 10 years is comprised of 11 ETFs and 31 additional financial and macroeconomic predictors was inspired by Obeidat et. al's<sup>3</sup> paper on adaptive portfolio asset allocation optimization. 

## CAPM Portfolio Returns vs. APT Portfolio Returns vs. Efficient Frontier Asset Returns

![](capm_and_apt_files/figure-gfm/unnamed-chunk-26-1.png)

## Deep Learning Approach with MVO

After a pre-training period of 400 business days, I make next-day predictions for all 11 ETF values based on a 10-day sliding window of previous ETF values and other macroeconomic and financial predictors and then immediately adjust the portfolio weights using a mean-variance optimization algorithm, which maximizes expected return with respect to 10-day volatility observed in each of the assets. Resulting cumulative portfolio returns are below:

![](images/mvo_returns.png)

## Citations 

<sup>1</sup> https://infobase.thomsonreuters.com/

<sup>2</sup> https://wrds-www.wharton.upenn.edu/

<sup>3</sup>  Obeidat, Samer, Shapiro, Daniel, Lemay, Mathieu, MacPherson, Mary Kate, & Bolic, Miodrag (2018). Adaptive Portfolio Asset Allocation Optimization with Deep Learning. _International Journal on Advances in Intelligent Systems, 11(1&2), 25-34_.
