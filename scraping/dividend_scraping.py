import datetime

import clipboard
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_dividend(ticker):
    start_date = datetime.datetime(2006, 1, 1).timestamp()
    end_date = datetime.datetime.now().timestamp()

    headers = {'authority': 'finance.yahoo.com',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
               }
    url = f"https://finance.yahoo.com/quote/{ticker}/history/?filter=div&period1={start_date}&period2={end_date}"
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    rows = soup.select("tbody tr")

    dates = []
    amounts = []
    for row in rows:
        dates.append(datetime.datetime.strptime(row.select("td")[0].text, '%b %d, %Y').strftime('%Y'))
        amounts.append(float(row.select("td")[1].text.replace("Dividend", "")))


    col_date = '년도'
    col_amount = "배당금"
    col_yoy = "YOY 성장률(%)"
    data = {col_date: dates, col_amount: amounts}
    df = pd.DataFrame(data=data)

    amounts = df.groupby(col_date)[col_amount].sum().values
    dates = df[col_date].unique()
    # calculate yoy growth
    yoys = calculate_yoy_growth(amounts)
    dates.sort()

    data = {col_date: dates, col_amount: amounts, col_yoy: yoys}
    df = pd.DataFrame(data=data)
    clipboard.copy(df.to_string(col_space=10))
    return df

def calculate_yoy_growth(amounts):
    yoy = []
    for i in range(0, len(amounts)):
        if i == 0:
            yoy.append("-")
        elif i == len(amounts)-1:
            yoy.append("-")
        else:
            yoy.append(format((amounts[i] - amounts[i - 1]) / amounts[i - 1] * 100, ".2f") + "%")
    return yoy