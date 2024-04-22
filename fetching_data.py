import pandas as pd, requests, os, sys
import utils.get_data as gd

api_key =  os.environ.get('EODHD_API_KEY')
symbol = "IBM.US"  # Example symbol
start_date = "2024-01-01"
end_date = "2024-04-08"

stock_df = gd.get_price(symbol, start_date, end_date, api_key)
stock_df['date'] = pd.to_datetime(stock_df['date'])     # convert to datatime type
stock_df.to_csv('./data/ibm_price.csv', index=False) 

news_df = gd.get_news(symbol, start_date, end_date, api_key)
news_df["date"] = pd.to_datetime(news_df["date"])
news_df = news_df.sort_values(by="date")
news_df['polarity'] = news_df['sentiment'].apply(lambda x: x['polarity'] if x is not None else 0)
print(news_df.head(10))

# Group by date and calculate average polarity
avg_polarity_df = news_df.groupby('date')['polarity'].mean().reset_index()

# Ensure the 'date' column in both DataFrames is of the same type
avg_polarity_df['date'] = pd.to_datetime(avg_polarity_df['date'])

# Once you have both datasets, the next step is to integrate them. This can be done based on the timestamps available in the news articles and the stock price entries to align insights contextually.

combined_df = pd.merge(stock_df, avg_polarity_df, on='date', how='left')

# Fill NaN values in polarity with 0 (neutral sentiment)
combined_df['polarity'].fillna(0, inplace=True)