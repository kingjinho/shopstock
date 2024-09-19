from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pyfolio import timeseries

from prompts.prompts import prompt_template


def generate_price_report(ticker, ticker_prices, spy_prices, volumes_data):
    ticker_yearly_cagr = calculate_quotes_yearly_cagr(ticker_prices)
    spy_yearly_cagr = calculate_quotes_yearly_cagr(spy_prices)

    ticker_cagr_analysis = f"""CAGR of {ticker} from {ticker_prices.index[0].year} to {ticker_prices.index[-1].year} is {ticker_yearly_cagr} every year."""
    spy_cagr_analysis = f"""CAGR of {ticker} from {spy_prices.index[0].year} to {spy_prices.index[-1].year} is {spy_yearly_cagr} every year."""

    ytd_year = ticker_prices.index[-1].year
    year_3 = ytd_year - 2
    year_5 = ytd_year - 4
    year_10 = ytd_year - 9

    # ytd
    ticker_ytd = ticker_prices[ticker_prices.index.year >= ytd_year]['price']
    spy_ytd = spy_prices[spy_prices.index.year >= ytd_year]['price']

    ticker_ytd_growth = "{:.2%}".format((ticker_ytd[-1] - ticker_ytd[0]) / ticker_ytd[0])
    spy_ytd_growth = "{:.2%}".format((spy_ytd[-1] - spy_ytd[0]) / spy_ytd[0])

    ticker_ytd_analysis = f"""YTD growth of {ticker} is {ticker_ytd_growth} in {ytd_year}."""
    spy_ytd_analysis = f"""YTD growth of SPY is {spy_ytd_growth} in {ytd_year}."""

    # 3 year
    ticker_3year = ticker_prices[ticker_prices.index.year >= year_3]['price']
    spy_3year = spy_prices[spy_prices.index.year >= year_3]['price']

    ticker_3year_growth = "{:.2%}".format((ticker_3year[-1] - ticker_3year[0]) / ticker_3year[0])
    spy_3year_growth = "{:.2%}".format((spy_3year[-1] - spy_3year[0]) / spy_3year[0])

    ticker_3year_analysis = f"""3-year growth of {ticker} is {ticker_3year_growth} from {year_3} to {ytd_year}."""
    spy_3year_analysis = f"""3-year growth of SPY is {spy_3year_growth} from {year_3} to {ytd_year}."""

    # 5 year
    ticker_5year = ticker_prices[ticker_prices.index.year >= year_5]['price']
    spy_5year = spy_prices[spy_prices.index.year >= year_5]['price']

    ticker_5year_growth = "{:.2%}".format((ticker_5year[-1] - ticker_5year[0]) / ticker_5year[0])
    spy_5year_growth = "{:.2%}".format((spy_5year[-1] - spy_5year[0]) / spy_5year[0])

    ticker_5year_analysis = f"""5-year growth of {ticker} is {ticker_5year_growth} from {year_5} to {ytd_year}."""
    spy_5year_analysis = f"""5-year growth of SPY is {spy_5year_growth} from {year_5} to {ytd_year}."""

    # 10 year
    ticker_10year = ticker_prices[ticker_prices.index.year >= year_10]['price']
    spy_10year = spy_prices[spy_prices.index.year >= year_10]['price']
    ticker_10year_growth = "{:.2%}".format((ticker_10year[-1] - ticker_10year[0]) / ticker_10year[0])
    spy_10year_growth = "{:.2%}".format((spy_10year[-1] - spy_10year[0]) / spy_10year[0])

    ticker_10year_analysis = f"""10-year growth of {ticker} is {ticker_10year_growth} from {year_10} to {ytd_year}."""
    spy_10year_analysis = f"""10-year growth of SPY is {spy_10year_growth} from {year_10} to {ytd_year}."""




    # compare with SPY
    ticker_mdd_list = calculate_mdds(ticker_prices)
    spy_mdd_list = calculate_mdds(spy_prices)

    docs = [Document(page_content=f"""
        {ticker_cagr_analysis}
        {ticker_ytd_analysis}
        {ticker_3year_analysis}
        {ticker_5year_analysis}
        {ticker_10year_analysis}
        
        {spy_cagr_analysis}
        {spy_ytd_analysis}
        {spy_3year_analysis}
        {spy_5year_analysis}
        {spy_10year_analysis}""")]

    vectorstore = Chroma.from_documents(
        docs,
        embedding=OpenAIEmbeddings(),
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
    )
    # 2. Create model
    model = ChatOpenAI()
    # 3. Create parser
    parser = StrOutputParser()
    # 4. Create chain
    chain = {'context': retriever, 'question': RunnablePassthrough()} | prompt_template | model | parser
    # 5. Invoke chain
    question = generate_quotes_question(ticker)
    resp = chain.invoke(question)

    return resp

def calculate_quotes_yearly_cagr(ticker_prices):
    start = ticker_prices['price'].iloc[0]
    end = ticker_prices['price'].iloc[-1]
    years = ticker_prices.index[-1].year - ticker_prices.index[0].year
    return "{:.2%}".format((end/start) ** (1 / years) - 1)

def calculate_quotes_yoy_growth(prices):
    return ""

def calculate_volume_growth():
    return ""

def calculate_mdds(quotes):
    df = timeseries.gen_drawdown_table(quotes['price'].pct_change(), top=3)
    # df.rename(columns={"Net drawdown in %" : "낙폭(%)",
    #            "Peak date" : "고점 날짜",
    #            "Valley date": "저점 날짜",
    #            "Recovery date" : "회복 날짜",
    #            "Duration":"기간(일)"}, inplace=True)
    # df['낙폭(%)'] = df['낙폭(%)'].map('{:.1f}%'.format)
    # df['고점 날짜'] = df['고점 날짜'].dt.strftime('%y/%m/%d')
    # df['저점 날짜'] = df['저점 날짜'].dt.strftime('%y/%m/%d')
    # df['회복 날짜'] = df['회복 날짜'].dt.strftime('%y/%m/%d')
    df['Net drawdown in %'] = df['Net drawdown in %'].map('{:.1f}%'.format)
    df['Peak date'] = df['Peak date'].dt.strftime('%y/%m/%d')
    df['Valley date'] = df['Valley date'].dt.strftime('%y/%m/%d')
    df['Recovery date'] = df['Recovery date'].dt.strftime('%y/%m/%d')
    return df

def calculate_price_trend(quotes):
    return ""

def generate_quotes_question(ticker):
    return f"""
    Based on data of {ticker} stock and SPY stock, analyze the performance of {ticker} stock.
    your answer should be within 400 words.
    when 
    you should also translate it in korean.    
    """