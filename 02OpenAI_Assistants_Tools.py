"""
OpenAI Assistants Tools

OpenAI_Assistants_Tools.py

27 November 2023

https://cookbook.openai.com/examples/assistants_api_overview_python

"""
# Tools
# A key feature of the Assistants API is the ability to equip our Assistants with Tools, 
# like Code Interpreter, Retrieval, and custom Functions. 
# Let's take a look at each.

# Let's equip our Math Tutor with the Code Interpreter so it can write and run Python code.

# pip install --upgrade openai
# pip show openai
# Version: 1.3.5

from openai import OpenAI
from _Assistants_helper_module import *

client = OpenAI()
"""
     ⬐------[Assistant] (has general role)
[Run]←-------[Thread]←------[Message] (has specific task + role)
"""
# ========================== ASSISTANT ============================
# Note: It is the Assistant that contains a reference to the Model
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-4-1106-preview",
)

# Update the assistant with a tool
MATH_ASSISTANT_ID = assistant.id

assistant = client.beta.assistants.update(MATH_ASSISTANT_ID, tools=[{"type": "code_interpreter"}])
show_json(assistant)

















