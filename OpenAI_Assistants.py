"""
OpenAI Assistants

23 November 2023

https://cookbook.openai.com/examples/assistants_api_overview_python

The new Assistants API is a stateful evolution of our Chat Completions API meant to simplify 
the creation of assistant-like experiences, and enable developer access to powerful tools like Code Interpreter and Retrieval. (!?)

=== Chat Completions API vs Assistants API ===

The primitives of the Chat Completions API are "Messages", 
on which you perform a Completion with a Model.

It is lightweight and powerful, but inherently STATELESS, 
which means you have to manage conversation state, tool definitions, retrieval documents, and code execution manually.

The primitives of the Assistants API are

"Assistants": which encapsulate a base model, instructions, tools, and (context) documents
"Threads": which represent the state of a conversation
"Runs": which power the execution of an Assistant on a Thread, including textual responses and multi-step tool use

Here is how to use them to create powerful, stateful experiences.

=== Setup ===
Python SDK
Note: We've updated our Python SDK to add support for the Assistants API, 
so you'll need to update it to the latest version (1.2.3 at time of writing).

=== Complete Example with Assistants API ===
"""
# pip install --upgrade openai
# pip show openai
# Version: 1.3.5
from openai import OpenAI
import json
from IPython.display import display

# can't hand strings!
def show_json(obj):
    xxx = json.loads(obj.model_dump_json())
    yyy = json.dumps(xxx, indent=2)
    print(yyy)




client = OpenAI()

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-4-1106-preview",
)

show_json(assistant)

"""
{'id': 'asst_MH2ZB7A5v8Azc2mwTi5XuKKv', 
'created_at': 1700761220, 
'description': None, 
'file_ids': [], 
'instructions': 'You are a personal math tutor. Answer questions briefly, in a sentence or less.', 
'metadata': {}, 
'model': 'gpt-4-1106-preview', 
'name': 'Math Tutor', 
'object': 'assistant', 
'tools': []}
"""

"""
You refer to your Assistant throughout Threads and Runs, using its id.

Next, we'll create a new Thread and add a Message to it. 
This will hold the state of our conversation, 
so we don't have re-send the entire message history each time.
"""

thread = client.beta.threads.create()
# show_json(thread)
"""
{'id': 'thread_kKjvORn1Fes4LNKPO2T2s8oN', 
'created_at': 1700761741, 
'metadata': {}, 
'object': 'thread'}
"""

# Then add the Message to the thread:
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
)
# show_json(message)
"""
{'id': 'msg_WEprN8asufB4PI4Qyj5ofQww', 
'assistant_id': None, 
'content': [{'text': {'annotations': [], 
        'value': 'I need to solve the equation `3x + 11 = 14`. Can you help me?'},
        'type': 'text'}], 
'created_at': 1700761927, 
'file_ids': [], 
'metadata': {}, 
'object': 'thread.message', 
'role': 'user', 
'run_id': None, 
'thread_id': 'thread_kKjvORn1Fes4LNKPO2T2s8oN'}
"""
# ========================== Runs ============================
"""
Notice how the Thread we created is NOT associated with the Assistant we created earlier! 
Threads exist independently from Assistants.

[Assistant]                 (Assistant is indipendant for the moment)
[Thread]<------[Message]    (Thread has a Message)
"""
"""
To get a COMPLETION from an Assistant for a given Thread, we must create a Run. 
Creating a Run will indicate to an Assistant it should look at 
the messages in the Thread and take action: either by adding a single response, or using tools.

To get our Assistant to respond to the user, let's create the Run. 
As mentioned earlier, you must specify both the Assistant and the Thread.

     ⬐------[Assistant]
[Run]←-------[Thread]←------[Message]
↷
"""
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)
# show_json(run)
"""
{'id': 'run_nUnwNbShNF05h3N7vvnuaqsJ', 
'assistant_id': 'asst_tQkdfZNa2UPLlg8JID5BwdoK', 
'cancelled_at': None, 
'completed_at': None, 
'created_at': 1700765031, 
'expires_at': 1700765631, 
'failed_at': None, 
'file_ids': [], 
'instructions': 'You are a personal math tutor. Answer questions briefly, in a sentence or less.', 
'last_error': None, 
'metadata': {}, 
'model': 'gpt-4-1106-preview', 
'object': 'thread.run', 
'required_action': None, 
'started_at': None, 
'status': 'queued', 
'thread_id': 'thread_A1vgvpYNacYGLpLrPkH3skLA', 
'tools': []}
"""
# Creating a Run is an asynchronous operation. 
# It will return immediately with the Run's metadata, which includes a status that will initially be set to queued. 
# The status will be updated as the Assistant performs operations (like using tools and adding messages).

# To know when the Assistant has completed processing, we can poll the Run in a loop.
# run.status can be: 
# queued, in_progress, requires_action, cancelling, cancelled, failed, completed, or expired 
# These are called "Steps"


# In practive we only need to check for queued or in_progress

import time

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

run = wait_on_run(run, thread) # Why do we need to pass it thread - it already has thread!
# show_json(run)
"""
{'id': 'run_o8mgxeokBtikgUAudeKNM1Gp', 
'assistant_id': 'asst_OYRVM0QT01a9FQ5zoXefVCAY', 
'cancelled_at': None, 
'completed_at': 1700766630, 
'created_at': 1700766627, 
'expires_at': None, 
'failed_at': None, 
'file_ids': [], 
'instructions': 'You are a personal math tutor. Answer questions briefly, in a sentence or less.', 
'last_error': None, 
'metadata': {}, 
'model': 'gpt-4-1106-preview', 
'object': 'thread.run', 
'required_action': None, 
'started_at': 1700766628, 
'status': 'completed', 
'thread_id': 'thread_VdyQsAgw8jUGrdvPI8z9M1YZ', 
'tools': []}
"""

# Messages
# Now that the Run has completed, 
# we can list the Messages in the Thread to see what got added by the Assistant.

messages = client.beta.threads.messages.list(thread_id=thread.id)
# show_json(messages)


















