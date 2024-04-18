import requests, pandas as pd
from datetime import datetime, timedelta

def get_price(symbol, start_date, end_date, api_key):
    url = f"https://eodhistoricaldata.com/api/eod/{symbol}"
    params = {
        "from": start_date,        "to": end_date,
        "fmt": "json",        "api_token": api_key,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date']).dt.date
        return df
    else:
        print("Failed to fetch stock data:", response.status_code)
        return pd.DataFrame()  # Return an empty DataFrame in case of failure


def get_news(symbol, start_date, end_date, api_key):
    all_news = []
    current_end_date = end_date

    while True:
        url = "https://eodhistoricaldata.com/api/news"
        params = {
            "s": symbol,
            "from": start_date,
            "to": current_end_date,
            "api_token": api_key,
            "limit": 1000,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break  # Break the loop if no data is returned
            all_news.extend(data[::-1])  # Reverse the data to maintain chronological order
            # Assuming the news data is sorted by date, get the date of the first news item in the batch
            first_news_date = data[-1]['date']
            first_news_date_obj = datetime.strptime(first_news_date.split("T")[0], "%Y-%m-%d").date()
            # If the first news date is the start date, break the loop
            if first_news_date_obj <= datetime.strptime(start_date, "%Y-%m-%d").date():
                break
            # Set the next end date to the day before the first news date in the current batch
            next_end_date_obj = first_news_date_obj - timedelta(days=1)
            current_end_date = next_end_date_obj.strftime("%Y-%m-%d")
        else:
            print("Failed to fetch news data:", response.status_code)
            break  # Exit the loop in case of failure

    df = pd.DataFrame(all_news)
    df['date'] = pd.to_datetime(df['date']).dt.date  # Convert to date to match stock data
    return df