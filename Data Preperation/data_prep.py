import os
import pandas as pd
from pydantic import BaseModel, Field, field_validator
from typing import Literal, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import time
from itertools import chain

load_dotenv()

data = pd.read_csv(r"cleaned_emails.csv")

class Category(BaseModel):
    category: Literal["application_confirmation", "rejection", "expecting_reply", "default"] = Field(description="Category of the email")

llm = ChatOpenAI(model="gpt-4o",temperature=0,)

system_message = """

    You are an experienced gmail classifier. You are hired by Google, be professional in doing your job. Your job is
    to classify incoming email as one of the following categories:

    1. "application_confirmation" : Email confirming the user's job application.
    2. "rejection" : Email notifying the user about their job rejection.
    3. "expecting_reply" : Email requesting the user to reply.
    4. "default" : All other emails.

    Be very careful in classifying the emails if there's any error in your classification, you will be fired.

    You should return a list of these categories matching the list of emails provided to you.

"""

human_message = """Here's the email you need to classify: {email}"""

template = [
    ("system", system_message),
    ("user", human_message), 
]

prompt = ChatPromptTemplate.from_messages(template)
llm_with_tools = llm.bind_tools([Category], strict=True)

count = 0

def classify(x):
    global count
    prompt_value_dict = {"email" : x}
    count += 1
    print(f"({count}/300) emails processed...")
    chain = prompt | llm_with_tools
    result = chain.invoke(prompt_value_dict)
    if result.content == "":
        category = result.tool_calls[0]["args"]["category"]
    else:
        category = result.content
    return category

data["body and subject"] = data.apply(lambda row: "subject : " + row["subject"] + "\n" + "body : " + row["body"], axis=1)
data["categories"] = data["body and subject"].apply(classify)

data.to_csv("classified_emails.csv", index=True)







