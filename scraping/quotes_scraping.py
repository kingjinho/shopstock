import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread import Worksheet
import matplotlib.pyplot as plt
import os
import plotly.graph_objects as go

worksheet: Worksheet
df_prices: pd.DataFrame
df_volumes: pd.DataFrame
col_date = 'date'
col_price = 'price'
col_volumes = 'volumes'
file_path_prefix = "../files"
file_ext = "png"
sheet_name="quotes"

def init_worksheet():
    global worksheet
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file("./files/credentials/service_credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name)
    worksheet = sheet.get_worksheet(0)


def get_prices(ticker):
    global df_prices
    date_cell_range = "A2:A"
    price_cell_range = "B2:B"
    worksheet.update_acell('A1', f'=GOOGLEFINANCE("{ticker}","price",DATE(2000, 01, 01),TODAY())')
    worksheet.batch_format([
        {
            "range": date_cell_range,
            "format": {
                "numberFormat": {
                    "type": "DATE",
                    "pattern": "mm-dd-yyyy"
                }
            }
        },
        {
            "range": price_cell_range,
            "format": {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": "#,##0.00"
                }
            }
        },
    ])

    df_prices = pd.DataFrame(
        data={ col_price: [float(item[0]) for item in worksheet.get_values("B2:B")]},
        index=[datetime.datetime.strptime(item[0], "%m-%d-%Y") for item in worksheet.get_values("A2:A")]
    )

    return df_prices


def get_volumes(ticker):
    global df_volumes
    date_cell_range = "D2:D"
    worksheet.update_acell('D1', f'=GOOGLEFINANCE("{ticker}","volume",DATE(2000, 01, 01),TODAY())')
    worksheet.batch_format([
        {
            "range": date_cell_range,
            "format": {
                "numberFormat": {
                    "type": "DATE",
                    "pattern": "mm-dd-yyyy"
                }
            }
        },
    ])

    df_volumes = pd.DataFrame(
        data={col_volumes: [int(item[0]) for item in worksheet.get_values("E2:E")]},
        index = [datetime.datetime.strptime(item[0], "%m-%d-%Y") for item in worksheet.get_values("D2:D")]
    )

    return df_volumes


def save_prices_as_image(ticker):
    if not os.path.exists(f"{file_path_prefix}/{ticker}"):
        os.mkdir(f"{file_path_prefix}/{ticker}")
    if os.path.isfile(f"{file_path_prefix}/{ticker}/{ticker}_price.{file_ext}"):
        os.remove(f"{file_path_prefix}/{ticker}/{ticker}_price.{file_ext}")

    fig = go.Figure([go.Scatter(x=df_prices[col_date], y=df_prices[col_price])])
    fig.update_layout(
        autosize = False,
        yaxis_tickformat='$,.2f',
    )

    fig.show()
    fig.write_image(f"{file_path_prefix}/{ticker}/{ticker}_price.{file_ext}")



def save_volumes_as_image(ticker):
    if not os.path.exists(f"{file_path_prefix}/{ticker}"):
        os.mkdir(f"{file_path_prefix}/{ticker}")
    if os.path.isfile(f"{file_path_prefix}/{ticker}/{ticker}_volumes.{file_ext}"):
        os.remove(f"{file_path_prefix}/{ticker}/{ticker}_volumes.{file_ext}")

    fig = go.Figure([go.Scatter(x=df_volumes[col_date], y=df_volumes[col_volumes])])
    fig.show()

    plt.savefig(f"{file_path_prefix}/{ticker}/{ticker}_volumes.{file_ext}", dpi=300)

def get_quotes(ticker):
    global worksheet
    try:
        init_worksheet()
        return get_prices(ticker)
    except Exception as e:
        print(e)
    finally:
        if worksheet is not None:
            worksheet.clear()