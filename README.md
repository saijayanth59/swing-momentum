# Swing + Momentum

# **Stock Market Swing Trading Algorithm**

## **Overview**

This algorithm is designed to identify and trade on recurring "swing" patterns within stock prices, capturing gains as prices oscillate between monthly high and low values. By analyzing the trend over a sliding one-month window, the algorithm identifies optimal entry points (triggers) and sets targeted exit points to maximize profit potential while managing risk.

## **Algorithm Approach**

The algorithm leverages daily stock data, including the open, high, low, and close prices, to analyze stock behavior over a one-month window. Here’s a step-by-step breakdown of how it operates:

### **1. Identifying the Current Trend**

The first step is to determine whether the stock is in an uptrend or downtrend based on recent price movements:

- **Monthly High and Low**: For each day, calculate the highest and lowest stock prices in the last month.
- **Trend Definition**:
  - **Uptrend**: If the stock's lowest price within the month is closer to the present day than the highest price, we define the current trend as an uptrend. This implies the stock has been trending upward, making it more likely to rise toward the previous monthly high.
  - **Downtrend**: If the highest price is closer to the present day, the trend is defined as a downtrend, indicating a likelihood of the stock moving downward towards the previous month’s low.

### **2. Finding a Perfect Trigger**

After identifying the trend, the next step is to confirm a "perfect trigger" signal. A trigger signal strengthens the probability of a successful trade, indicating that the stock’s price is ready to move significantly within the expected direction.

- **Trigger for Uptrend**: When in an uptrend, a trigger signal occurs if the stock’s opening price (`open`) is approximately equal to its low price (`low`) for the day. This similarity (within a defined threshold) indicates that the price may be poised to rise, potentially swinging upward to the monthly high.
- **Trigger for Downtrend**: When in a downtrend, a trigger occurs if the stock’s opening price is approximately equal to its high price for the day. This alignment suggests that the price may swing downward, moving toward the monthly low.

If a trigger is identified, the algorithm prepares for a trade with defined entry, target, and stop-loss parameters. If no trigger is found, the algorithm waits until a potential trigger appears.

### **3. Setting Trade Parameters and Executing Orders**

Once a trigger is detected, the algorithm sets up specific trade parameters:

- **For a Buy Call (Uptrend)**:
  - **Target Price**: Set just below the previous month’s high, allowing a small buffer to account for volatility.
  - **Stop-Loss**: Set just above the previous month’s low to minimize losses if the trend does not hold.
- **For a Sell Call (Downtrend)**:
  - **Target Price**: Set just above the previous month’s low, with a small buffer for safety.
  - **Stop-Loss**: Set just below the previous month’s high to minimize losses if the trend reverses.

The algorithm places the trade with these parameters, effectively managing both the target and risk for each position.

### **4. Monitoring and Exiting Trades**

Once a trade is placed, the algorithm continuously monitors the stock’s price against the target and stop-loss levels. The position will be closed (exiting the trade) if one of the following occurs:

- **Target Hit**: If the stock price reaches the target, the trade is exited to lock in profits.
- **Stop-Loss Hit**: If the stock price falls to the stop-loss, the trade is exited to prevent further losses.

This process is repeated daily, recalculating the trend, potential triggers, and trade parameters as each day passes.

### **Example Walkthrough**

To illustrate, consider a stock with the following one-month data:

- **Monthly High**: $120
- **Monthly Low**: $100

On a particular day in an uptrend, if the day’s `open` price is approximately equal to the `low` (e.g., $101), it indicates a perfect trigger for a buy. Here’s how the trade would be set:

- **Target Price**: $118 (a few points below the monthly high)
- **Stop-Loss**: $102 (a few points above the monthly low)

If the price reaches $118, the trade closes with a profit. If it drops to $102, the stop-loss triggers, minimizing loss.

## **Advantages and Limitations**

### **Advantages**

- **Adaptability**: The sliding window ensures the algorithm consistently uses the most recent data, allowing it to adapt to current market conditions.
- **Risk Management**: By setting clear stop-losses, the algorithm minimizes potential losses if the trade does not go as expected.
- **Profitability**: The swing strategy takes advantage of predictable oscillations within the monthly range, allowing for profit potential within well-defined boundaries.

### **Limitations**

- **Volatility Sensitivity**: Highly volatile stocks may not adhere to predictable swing patterns, making it difficult for the algorithm to anticipate price movements accurately.
- **Dependence on Trend Accuracy**: Success depends on accurately identifying the trend and finding valid triggers. Misinterpreting the trend may lead to suboptimal trades.
- **Limited Scope**: The algorithm focuses on short-term swings within a one-month window, which may not capture broader trends or longer-term price movements.

## **Conclusion**

This algorithm offers a systematic approach to identifying and trading swing patterns within stock prices. By combining daily monitoring, a sliding data window, and well-defined entry and exit points, the strategy provides a practical framework for swing trading. With robust risk management, it is designed to capture profits while minimizing losses, making it an effective tool for traders seeking to capitalize on predictable oscillations in stock prices.
