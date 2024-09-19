# prompt = f"""
# Write a 5-paragraph report that analyze stock {ticker}.
# this report should be written in following formats:
#  1. First paragraph should include brief introduction of a company behind {ticker} stating whether {ticker} is a buy or sell by summarizing the point.
#  2. Second paragraph describes the past performance of {ticker}, including the followings with numbers:
#     1. Performance including the followings, based on this data {quotes_data.to_string()}:
#         - CAGR, YOY growth, MDD, time it took to recover MDD, trading volume trend, 52-week high and low price,performance compared to S&P 500 index by numbers.
#     2. Dividend histories, including the followings, based on this data {dividend_data.to_string()}:
#        - Calculate dividend sum by year, YOY growth and dividend CAGR.
#        - What is DIVIDEND CAGR of this stock?
#        - Have been any dividend cuts or suspensions? if then, when and how much?
#
#  3. Third paragraph analyze the company behind the stock. this should include the following data over time:
#     Income Statement:
#         Revenue Growth: Look for consistent or growing revenue over time.
#         Net Income: Assess profitability and trends.
#         Profit Margins: Check gross, operating, and net margins for efficiency.
#
#     Balance Sheet:
#         Assets and Liabilities: Compare to evaluate financial stability.
#         Equity: Assess shareholder equity for a company’s net worth.
#         Debt Levels: Consider the debt-to-equity ratio to gauge leverage.
#
#     Cash Flow Statement:
#         Operating Cash Flow: Indicates cash generated from core business operations.
#         Investing Cash Flow: Look at capital expenditures and investment activities.
#         Financing Cash Flow: Review changes due to debt and equity financing.
#
#     Profitability Ratios:
#         Gross Margin: (Gross Profit / Revenue) indicates the percentage of revenue exceeding the cost of goods sold.
#         Operating Margin: (Operating Income / Revenue) shows efficiency in managing operations.
#         Net Profit Margin: (Net Income / Revenue) reveals the overall profitability.
#
#     Liquidity Ratios:
#         Current Ratio: (Current Assets / Current Liabilities) measures the ability to cover short-term obligations.
#         Quick Ratio: (Quick Assets / Current Liabilities) assesses immediate liquidity.
#         Leverage Ratios:
#         Debt-to-Equity Ratio: (Total Debt / Shareholder's Equity) indicates financial leverage.
#         Interest Coverage Ratio: (EBIT / Interest Expense) measures the ability to pay interest on debt.
#
#     Efficiency Ratios:
#         Asset Turnover Ratio: (Revenue / Total Assets) evaluates asset efficiency.
#         Inventory Turnover Ratio: (Cost of Goods Sold / Average Inventory) indicates inventory management efficiency.
#
#     Valuation Ratios:
#         Price-to-Earnings (P/E) Ratio: (Stock Price / Earnings Per Share) evaluates valuation relative to earnings.
#         Price-to-Book (P/B) Ratio: (Stock Price / Book Value Per Share) assesses valuation relative to net asset value.
#
# 4. Fourth paragraph summarize industrial trend over time.
#     this paragraph should examine industrial trend where {ticker} belongs to changes over time.
#     Is this {sector} sector where {ticker} belongs to increasing, or decreasing trend over time in terms of supply and demand?
#     what is there current status quo?
#     Any political or regulatory changes?
#     Are people optimistic about this {sector} sector ? or pessimistic about this {sector} sector?
#
# 5. Fifth paragraph, the last one, should summarize the whole content with stating where {ticker} is a buy or a sell.
#
# title of this report should be "Analysis of {ticker} stock" with result of buy or sell.
# note that each paragraph should not exceed more than 400 words, as well as markdown format.
# Do not make it up if you do not know the answer
# """
from langchain_core.prompts import ChatPromptTemplate

system_template = f"""You are an financial advisor to help me with analyze stock market by generating a report of a stock.
                         your report should be concise and to the point and should not make it up if you do not know.
                         if you do not know the answer, please say I do not know the answer."""

human_template = """
        Answer this question using the provided context only.
        your tone should be professional and concise, but not too formal.
        {question}

        Context: {context}
        """
prompt_template = ChatPromptTemplate.from_messages([
        ('system', system_template),
        ('user', human_template)
    ])
