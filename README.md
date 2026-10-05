Black-Scholes Pricing app that pulls historical data for apparent volatilities of real stocks to calculate Call and Put prices through the Black-Scholes model, and draws heatmaps to showcase different Call and Put prices as well as P&L.


Black-Scholes pricing app that estimates volatility from historical stock data to calculate call and put prices through the Black-Scholes model, and draws heatmaps of call and put prices as well as P&L.

## The math

For spot price $S$, strike $K$, risk-free rate $r$, volatility $\sigma$, and time to expiry $\tau = T - t$ (in years):

$$
d_1 = \frac{\ln(S/K) + \left(r + \frac{\sigma^2}{2}\right)\tau}{\sigma\sqrt{\tau}}, \qquad
d_2 = d_1 - \sigma\sqrt{\tau}
$$

$$
C = S\,N(d_1) - K e^{-r\tau} N(d_2)
$$

$$
P = K e^{-r\tau} N(-d_2) - S\,N(-d_1) = C - S + K e^{-r\tau}
$$

where $N(\cdot)$ is the standard normal cumulative distribution function.

Historical volatility is the annualized standard deviation of daily log returns:

$$
\sigma = \operatorname{std}\!\left(\ln\frac{P_t}{P_{t-1}}\right)\sqrt{252}
$$

Prices European options under Black-Scholes (no dividends, constant volatility). US equity options are typically American-style, so values are approximate, especially for puts.

For a given current stock/spot price, strike price, maturity time, risk-free interest rate, the app calculates the call and put prices according to the Black-Scholes model, where the volatility can either be manually selected, or the trader can input a stock symbol (case insensitive) and a time period in order to calculate the volatility for that stock price throughout the given time period (if we choose "AAPL" and "30", the app will calculate the volatility of the Apple stocks in the last 30 trading days). The app also displays, once a stock is selected, the last closing value for that stock, in order for the trader to be able to select that as their current stock price.

The heatmap graphs display the various call and put values for a given range of spot and volatility or interest rate values. Not that whatever values aren't selected to have a range will be selected through the inputs above (for example, the strike price).
In addition to the call and put price heatmaps, the trader can enter purchase prices for the call and put options for that stock, and the new drawn heatmap graphs will display the P&L of the trader. If the trader is making profit, the graph shows green, while a loss is displayed through red values. Note that there is an option to change the color-gradient for color-blind traders.


