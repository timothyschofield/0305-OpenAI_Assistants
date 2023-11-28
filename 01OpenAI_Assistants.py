"""
OpenAI Assistants

OpenAI_Assistants.py

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

Note: "User" does NOT exist as an entity

Here is how to use them to create powerful, stateful experiences.

=== Setup ===
Python SDK
Note: We've updated our Python SDK to add support for the Assistants API, 
so you'll need to update it to the latest version (1.2.3 at time of writing).


"""
# pip install --upgrade openai
# pip show openai
# Version: 1.3.5
from openai import OpenAI
from _Assistants_helper_module import *

client = OpenAI()

# ========================== ASSISTANT ============================
# Note: It is the Assistant that contains a reference to the Model
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-4-1106-preview",
)
# show_json(assistant)

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

# ========================== THREAD ============================
# Note: No arguments
thread = client.beta.threads.create()
# show_json(thread)
"""
{'id': 'thread_kKjvORn1Fes4LNKPO2T2s8oN', 
'created_at': 1700761741, 
'metadata': {}, 
'object': 'thread'}
"""

# ========================== MESSAGE ============================
# Create a message and add it to the thread:
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

# ========================== RUNS ============================
"""
Notice how the Thread we created is NOT associated with the Assistant we created earlier! 
Threads exist independently from Assistants.

To get a COMPLETION from an Assistant for a given Thread, we must create a Run. 
Creating a Run will indicate to an Assistant it should look at 
the messages in the Thread and take action: either by adding a single response, or using tools.

To get our Assistant to respond to the user, let's create the Run. 
As mentioned earlier, you must specify both the Assistant and the Thread.

     ⬐------[Assistant] (has general role)
[Run]←-------[Thread]←------[Message] (has specific task + role)

"""
run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
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

run = wait_on_run(client, run, thread) # Why do we need to pass it thread - it already has thread!
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
# ========================== MESSAGES ON RUN COMPLETION ============================
messages = client.beta.threads.messages.list(thread_id=thread.id)
# show_json(messages)
"""
{
  "data": [
    {
      "id": "msg_KlQJJuK6TOeGx8qnFHaFdes9",
      "assistant_id": "asst_yVBRRMtRt0Lte2YukTMor5C0",
      "content": [
        {
          "text": {
            "annotations": [],
            "value": "Yes, subtract 11 from both sides to get `3x = 3` and then divide both sides by 3 to find `x = 1`."
          },
          "type": "text"
        }
      ],
      "created_at": 1700817312,
      "file_ids": [],
      "metadata": {},
      "object": "thread.message",
      "role": "assistant",
      "run_id": "run_fbzcqmAVwrb0S11S4tJV50ir",
      "thread_id": "thread_UL43Zp2LOrPT08KLUh2FO9OS"
    },
   
     {
      "id": "msg_Mke5Q3Rtjkb8pDCSxd6Agz5l",
      "assistant_id": null,
      "content": [
        {
          "text": {
            "annotations": [],
            "value": "I need to solve the equation `3x + 11 = 14`. Can you help me?"
          },
          "type": "text"
        }
      ],
      "created_at": 1700817311,
      "file_ids": [],
      "metadata": {},
      "object": "thread.message",
      "role": "user",
      "run_id": null,
      "thread_id": "thread_UL43Zp2LOrPT08KLUh2FO9OS"
    }
  ],
  "object": "list",
  "first_id": "msg_KlQJJuK6TOeGx8qnFHaFdes9",
  "last_id": "msg_Mke5Q3Rtjkb8pDCSxd6Agz5l",
  "has_more": false
}

"""
# Messages are ordered in reverse-chronological order (Most recent results at the top, unlike Chat Completion and usual the error logs etc.). 
# This is done so the most recent results are always on the first page (since results can be paginated).

# Let's ask our Assistant to explain the result a bit further! So its the same thread of conversation
# Create a message to append to our thread
message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="Could you explain this to me?")
"""
     ⬐------[Assistant] (has general role)
[Run]←-------[Thread]←------[Message] (has specific task + role) (Could you explain this to me?)
"""

# Execute our run for claification
run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant.id)

# Wait for completion
wait_on_run(client, run, thread)

# Retrieve all the messages added after our last user message (Could you explain...)
# So the thread maintains the context in which the Math Tutor  elusidates
messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc", after=message.id)
# show_json(messages)

# This may feel like a lot of steps to get a response back, especially for this simple example. 
# However, you'll soon see how we can add very powerful functionality to our Assistant without changing much code at all! - go to OpenAI_Assistant2.py
"""
{
  "data": [
    {
      "id": "msg_AMvlXfBVGNUzRaA3OboyB65d",
      "assistant_id": "asst_ECOfltssrDxrlDv7RwyfWbes",
      "content": [
        {
          "text": {
            "annotations": [],
            "value": "Certainly! To solve the equation `3x + 11 = 14`:\n\n1. Subtract 11 from both sides to isolate the term with the variable: `3x + 11 - 11 = 14 - 11`, which simplifies to `3x = 3`.\n2. Divide both sides by 3 to solve for x: `3x / 3 = 3 / 3`, which simplifies to `x = 1`.\n\nSo the solution is `x = 1`."
          },
          "type": "text"
        }
      ],
      "created_at": 1700820614,
      "file_ids": [],
      "metadata": {},
      "object": "thread.message",
      "role": "assistant",
      "run_id": "run_4MBlrObvvC7zExHs0Al3WE26",
      "thread_id": "thread_Fp6hCqxmHIgYFiYvWgOqU6Gg"
    }
  ],
  "object": "list",
  "first_id": "msg_AMvlXfBVGNUzRaA3OboyB65d",
  "last_id": "msg_AMvlXfBVGNUzRaA3OboyB65d",
  "has_more": false
}
"""
############################### PART 2 ###################################

"""
24 and 25 November 2023

The previouse example may feel like a lot of steps to get a response back, 
especially for this simple example. 
However, you'll soon see how we can add very powerful functionality to our 
Assistant without changing much code at all!

Example

Let's take a look at how we could potentially put all of this together. 
Below is all the code you need to use an Assistant you've created.

"""
"""
     ⬐------[Assistant] (has a general role)
[Run]←-------[Thread]←------[Message] (has specific task + role) (user: Could you explain this to me?)
"""
# Save the Maths Assistant id
MATH_ASSISTANT_ID = assistant.id

# Emulating concurrent user requests
# All these Threads are new but they are all requests by "user" to MATH_ASSISTANT
thread1, run1 = create_thread_and_run(client, MATH_ASSISTANT_ID, "I need to solve the equation `3x + 11 = 14`. Can you help me?")
thread2, run2 = create_thread_and_run(client, MATH_ASSISTANT_ID, "Could you explain linear algebra to me?")
thread3, run3 = create_thread_and_run(client, MATH_ASSISTANT_ID, "I don't like math. What can I do?")

# Wait for Run 1
run1 = wait_on_run(client, run1, thread1)
pretty_print(get_response(client, thread1))

# Wait for Run 2
run2 = wait_on_run(client, run2, thread2)
pretty_print(get_response(client, thread2))

# Wait for Run 3
run3 = wait_on_run(client, run3, thread3)
pretty_print(get_response(client, thread3))

# Thank our assistant on Thread 3
run4 = submit_message(client, MATH_ASSISTANT_ID, thread3, "Thank you!")
run4 = wait_on_run(client, run4, thread3)
pretty_print(get_response(client, thread3))

# Messages
# user: I need to solve the equation `3x + 11 = 14`. Can you help me?
# assistant: Yes, subtract 11 from both sides to get `3x = 3`, then divide both sides by 3 to find `x = 1`.

# Messages
# user: Could you explain linear algebra to me?
# assistant: Linear algebra is the branch of mathematics concerning linear equations, linear functions, and their representations through matrices and vector spaces.

# Messages
# user: I don't like math. What can I do?
# assistant: Find aspects of math that relate to your interests or everyday life, try different learning tools like games or apps, and consider working with a tutor who can personalize your learning experience to make it more enjoyable.

# Messages
# user: I don't like math. What can I do?
# assistant: Find aspects of math that relate to your interests or everyday life, try different learning tools like games or apps, and consider working with a tutor who can personalize your learning experience to make it more enjoyable.
# user: Thank you!
# assistant: You're welcome! If you have any more questions or need help with math, feel free to ask!

# END









