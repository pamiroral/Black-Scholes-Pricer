from scipy.stats import norm
import math
import random
import numpy as np


def BlackScholes(stock_price, exercise_price, short_term_interest, time_remaining, volatility) -> float:
    if stock_price <= 0 or exercise_price <= 0 or short_term_interest <= 0 or time_remaining <= 0 or volatility <= 0:
        raise ValueError("S, K, T, r, and volatility must all be positive.")
    d_1 = (math.log(stock_price / exercise_price) + (short_term_interest + volatility**2 /2)*time_remaining) / (volatility * math.sqrt(time_remaining))
    d_2 = d_1 - volatility*math.sqrt(time_remaining)
    call_price = stock_price * norm.cdf(d_1) - exercise_price * math.exp(-short_term_interest * time_remaining) * norm.cdf(d_2)

    return call_price





