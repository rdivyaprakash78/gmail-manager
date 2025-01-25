from pydantic import BaseModel, Field, field_validator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from dotenv import load_dotenv
import pandas as pd
from itertools import chain
import numpy as np

load_dotenv()

class Email(BaseModel):
    subject : str = Field(description = "Subject of the email")
    body : str = Field(description = "Body of the email")

class Emails(BaseModel):
    emails : List[Email] = Field(description = "List of emails")

    @field_validator("emails")
    def check_category_length(cls, value):
        if len(value) != 25:
            raise ValueError("The 'email' list must contain exactly 25 items.")
        return value
    
system_message = """
    You are given with the task to balance a dataset. The Dataset contains emails that are classified into
    different categories. The category "expecting_reply" contains very less number of emails as compared to the
    other categories. Your task is to balance the dataset by producing synthetic data.

    Dont use any placeholders. This synthetic data is used for model development purpose, so it should
    replicate the actual inbox of the user.

    These are emails that expects reply from the user. You should give the subject and body.

    You should return 25 emails.
"""

human_message = """Give me 25 emails"""

template = [
    ("system", system_message),
    ("user", human_message), 
]

prompt = ChatPromptTemplate.from_messages(template)

percentage = 0
steps = np.linspace(0, 0.3, 4)
synthetic_emails = []

for i in steps:
    print(f"Generating syntetic emails ({percentage}% completed)...")
    llm = ChatOpenAI(model="gpt-4o",temperature=i)
    llm_with_tools = llm.bind_tools([Emails], strict=True)
    chain_ = prompt | llm_with_tools
    result = chain_.invoke({})
    percentage += 25
    synthetic_emails.append(result.tool_calls[0]["args"]["emails"])

print(synthetic_emails)
synthetic_emails = list(chain.from_iterable(synthetic_emails))
print(synthetic_emails)
synthetic_data = []
category = []

for i in synthetic_emails:
    synthetic_data.append("Subject : " + i["subject"] + "\n" + "Body : " + i["body"])
    category.append("expecting_reply")

data_dict = {
    "text" : synthetic_data,
    "category" : category
}

sub_df = pd.DataFrame(data_dict)
data = pd.read_csv("classified_emails.csv")
data = data.drop(["Unnamed: 0", "from", "received_time", "keywords", "body", "subject"], axis=1)
data = data.rename(columns={"body and subject": "text", "categories": "category"})
final_data = pd.concat([sub_df, data], ignore_index=True)
final_data.to_csv("balanced_emails.csv", index=False)