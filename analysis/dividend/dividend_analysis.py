from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from prompts.prompts import system_template, human_template


def generate_dividend_report(dividend_data):
    dividend_cagr = calculate_dividend_cagr(dividend_data['배당금'].iloc[0], dividend_data['배당금'].iloc[-1], len(dividend_data))
    dividend_report_question = generate_dividend_question(dividend_data["년도"].iloc[0], dividend_data["년도"].iloc[-1], dividend_cagr)
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

    return chain.invoke(dividend_report_question)

def calculate_dividend_cagr(start, end, duration):
    return "{:.2%}".format((end / start) ** (1 / duration) - 1)

def generate_dividend_question(start, end, cagr):
    return f"""Do the followings:
               1. CAGR of dividend from {start} to {end} is: {cagr}
               2. Find any dividend cuts or suspensions. if then, say "No dividend cuts". if not, show when and how much?
               3. Analyze the dividend trend and explain the trend in a 3 sentences.
    """