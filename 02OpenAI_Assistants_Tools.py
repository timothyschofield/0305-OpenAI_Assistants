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
# show_json(assistant)

user_input = "Generate the first 20 fibbonaci numbers with code."
thread, run = create_thread_and_run(client, MATH_ASSISTANT_ID, user_input)

run = wait_on_run(client, run, thread)
# pretty_print(get_response(client, thread))
"""
# Messages
user: Generate the first 20 fibbonaci numbers with code.
assistant: The first 20 Fibonacci numbers are:
\[ 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181 \]
"""

# And that's it! The Assistant used Code Interpreter in the background, and gave us a final response.
# For some use cases this may be enough.
# However, if we want more details on what precisely an Assistant is doing we can take a look at a Run's Steps.

"""
######################################### Steps #########################################
A Run is composed of one or more Steps. Like a Run, each Step has a status that you can query.
"""

"""
######################################### Retrieval #####################################
Another powerful tool in the Assistants API is Retrieval: the ability to upload files that 
the Assistant will use as a knowledge base when answering questions. 
"""
# Upload the file
file = client.files.create(
    file=open(
        "data/language_models_are_unsupervised_multitask_learners.pdf",
        "rb",
    ),
    purpose="assistants",
)

# Update Assistant
assistant = client.beta.assistants.update(
    MATH_ASSISTANT_ID,
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
    file_ids=[file.id],
)
# show_json(assistant)


user_input = "What are some cool math concepts behind this ML paper pdf? Explain in two sentences."
thread, run = create_thread_and_run(client, MATH_ASSISTANT_ID, user_input)

run = wait_on_run(client, run, thread)
# pretty_print(get_response(client, thread))
"""
# Messages
user: What are some cool math concepts behind this ML paper pdf? Explain in two sentences.
assistant: Cool math concepts behind the paper include probabilistic frameworks 
for modeling conditional distributions like \( p(output \,|\, input) \) and 
enhancements like self-attention architectures for computing such probabilities, illustrating advances in expressiveness and 
tractability in machine learning models【11†source】. 
Additionally, task conditioning has been formalized in multitask and meta-learning settings, 
emphasizing the role of language to specify tasks, inputs, and outputs in a flexible and unified sequence of symbols, 
demonstrating mathematical elegance in machine learning algorithm design【11†source】.
"""

"""
######################################### Functions #########################################
As a final powerful tool for your Assistant, you can specify custom Functions 
(much like the Function Calling in the Chat Completions API). 
During a Run, the Assistant can then indicate it wants to call one or more functions you specified. 
You are then responsible for calling the Function, and providing the output back to the Assistant.
"""

# Let's take a look at an example by defining a display_quiz() Function for our Math Tutor.
# This function will take a title and an array of questions, 
# display the quiz, and get input from the user for each:

    # title
    # questions
        # question_text
        # question_type: [MULTIPLE_CHOICE, FREE_RESPONSE]
        # choices: ["choice 1", "choice 2", ...]

"""
username = input("Enter username:")
print("Username is: " + username)
"""
# Unfortunately I don't know how to get user input within a Python Notebook, 
# so I'll be mocking out responses with get_mock_response.... This is where you'd get the user's actual input.


def get_mock_response_from_user_multiple_choice():
    return "a"


def get_mock_response_from_user_free_response():
    return "I don't know."


def display_quiz(title, questions):
    print("Quiz:", title)
    print()
    responses = []

    for q in questions:
        print(q["question_text"])
        response = ""

        # If multiple choice, print options
        if q["question_type"] == "MULTIPLE_CHOICE":
            for i, choice in enumerate(q["choices"]):
                print(f"{i}. {choice}")
            response = get_mock_response_from_user_multiple_choice()

        # Otherwise, just get response
        elif q["question_type"] == "FREE_RESPONSE":
            response = get_mock_response_from_user_free_response()

        responses.append(response)
        print()

    return responses


"""
This is a sample quiz,
The assistant is going to make up its own version of a quiz
"""

responses = display_quiz(
    "Sample Quiz",
    [
        {"question_text": "What is your name?", "question_type": "FREE_RESPONSE"},
        {
            "question_text": "What is your favorite color?",
            "question_type": "MULTIPLE_CHOICE",
            "choices": ["Red", "Blue", "Green", "Yellow"],
        },
    ],
)
# print("Responses:", responses)

# Now, let's define the interface of this function in JSON format, so our Assistant can call it:
function_json = {
    "name": "display_quiz",
    "description": "Displays a quiz to the student, and returns the student's response. A single quiz can have multiple questions.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "questions": {
                "type": "array",
                "description": "An array of questions, each with a title and potentially options (if multiple choice).",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "question_type": {
                            "type": "string",
                            "enum": ["MULTIPLE_CHOICE", "FREE_RESPONSE"],
                        },
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["question_text"],
                },
            },
        },
        "required": ["title", "questions"],
    },
}

# Once again, let's update out Assistant either through the Dashboard or the API.
assistant = client.beta.assistants.update(
    MATH_ASSISTANT_ID,
    tools=[
        {"type": "code_interpreter"},
        {"type": "retrieval"},
        {"type": "function", "function": function_json},
    ],
)
# show_json(assistant)

# And now, we ask for a quiz.
# NOT FINISHED




























