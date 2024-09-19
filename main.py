import clipboard
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from analysis.dividend.dividend_analysis import generate_dividend_report
from analysis.quotes.price_analysis import calculate_mdds, generate_price_report
from prompts.prompts import system_template, human_template
from scraping.dividend_scraping import get_dividend
from scraping.quotes_scraping import get_quotes, get_volumes


def generate_report():
    ticker = input("Please input your ticker")
    sector = input("Which sector does it belong to?")

    print("generating a report...")

    load_dotenv()

    dividend_data = get_dividend(ticker)
    dividend_report = generate_dividend_report(dividend_data)

    ticker_price_data = get_quotes(ticker)
    spy_price_data = get_quotes("SPY")
    volume_data = get_volumes(ticker)
    quotes_report = generate_price_report(ticker, ticker_price_data, spy_price_data, volume_data)

    question = f"""Do the followings:
               1. CAGR of dividend from {dividend_data["년도"].iloc[0]} to {dividend_data["년도"].iloc[-1]} is: {dividend_cagr}
               2. Find any dividend cuts or suspensions. if then, say "No dividend cuts". if not, show when and how much?
               3. Analyze the dividend trend and explain the trend in a 3 sentences.
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ('system', system_template),
        ('user', human_template)
    ])

    docs = []
    for row in dividend_data.itertuples():
        docs.append(Document(page_content=f"""{row[2]}""",
                             metadata={"date": f"{row[1]}"}))

    vectorstore = Chroma.from_documents(
        docs,
        embedding=OpenAIEmbeddings(),
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={'k': len(docs)}
    )
    # 2. Create model
    model = ChatOpenAI()
    # 3. Create parser
    parser = StrOutputParser()
    # 4. Create chain
    chain = {'context': retriever, 'question': RunnablePassthrough()} | prompt_template | model | parser
    # 5. Invoke chain
    resp = chain.invoke(question)

    print(f"""
    {dividend_data.to_string(index=False)}
    {resp}
    """
        )


generate_report()
