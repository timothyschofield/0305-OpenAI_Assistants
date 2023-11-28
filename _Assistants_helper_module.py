"""
_Assistants_helper_module.py

Contains a few helper functions for the other py files in this directory

26 November 2023

=====================================================================================
====================================== Modules ======================================
=====================================================================================

https://www.datacamp.com/tutorial/modules-in-python

Imagin we have a file called calculation.py and a file called main.py in the same (working) directory.
In the following explanations, the main.py file, imports the calculation.py file.

#### Intro to Modules ####

1)
  import calculation

Here calculation refers to a file calculation.py which contains functions, add(a, b) and sub(a, b)
Both the functions add(a, b) and sub(a, b) are imported
you use the functions thus:

  calculation.add(a, b)
  calculation.sub(a, b)

2)
  from calcualtion import add

Here only the add function is imported. You use it thus:

  add(a, b)  # No "calculation" nessessary

You can also import multiple functions thus:

  from calcualtion import add, sub

3)
You can import all the functions thus:
  from calcualtion import *

  add(a, b)
  sub(a, b)

4) 
You can rename the module you import. This is usualy done to save typing.

    import calculation as cal

    cal.add(a, b)

#### Module Search Path ####

You my need to have modeules in various different programs/projects and their
physical location and directory my be different from the code that imports them.

When you import a module named calculation, the Python interpreter first searches for a "built-in" module with that name. 
Examples of built-in models are the OS module of operating system interactions, the Datetime model, the Math, 
Csv, JSON and Urlib modules, etc.

If not found, Python then searches for a file named calculation.py in a list of directories given by the variable sys.path.
sys.path contains these locations:

    - the directory containing the input script (or the current directory).
    - PYTHONPATH (a list of directory names, with the same syntax as the shell variable PATH).
    - the installation-dependent default.

- Let's say you move calculation.py to the /home/test/ directory, 
so it is no-longer in the working directory together with main.py.

To import calculation.py, you need to add calculation.py's directory to sys.path thus:

  import sys
  sys.path.append("/home/test/")

  import calculation

#### Byte Compiled Files ####

To speed module loading, Python can create byte-compiled files with the extension .pyc.
When a Python source file (module) is imported during an execution for the first time, 
the appropriate .pyc file is created automatically in a folder called __pycache__ (also created automaticaly). 
If the same module is imported again, then the already created .pyc file is used. 
These __pycache__ folder and .pyc files is/are usually created in the same directory as the corresponding .py files.

The pyc files contain bytecode, which is an intermediary between Python code and machine code.
They are platform independent, as the conversion from bytecode to machine code, 
gets done at runtime by the Python interpreter on the actual machine.

#### The dir() function ####

The dir() function is used to find out all the names (of functions etc.) defined in a module. 
It returns a sorted list of strings containing the names defined in a module.

e.g.
  import json

  print(dir(json)) # This can be useful for exploring what a module contains and what functions are available for use.

['JSONDecodeError', 'JSONDecoder', 'JSONEncoder', '__all__', '__author__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', 
'__name__', '__package__', '__path__', '__spec__', '__version__', '_default_decoder', '_default_encoder', 
'codecs', 'decoder', 'detect_encoding', 'dump', 'dumps', 'encoder', 'load', 'loads', 'scanner']

Attribute __name__ contains the name of the module. 
All attributes beginning with an underscore are default python attributes associated with a module.

"""
import json
import time

"""
"""
def show_json(obj):

    if isinstance(obj,  (float, int, str, list, dict, tuple)): 
       print(obj)
       return
    
    print(obj.model_dump_json(indent=2))
# eo show_json

"""
  Creating a Run is an asynchronous operation. 
  It will return immediately with the Run's metadata, which includes a status that will initially be set to queued. 
  The status will be updated as the Assistant performs operations (like using tools and adding messages).

  To know when the Assistant has completed processing, we can poll the Run in a loop.
  run.status can be: 
  queued, in_progress, requires_action, cancelling, cancelled, failed, completed, or expired 
  These are called "Steps"

  In practive we only need to check for "queued" or "in_progress"
"""
def wait_on_run(client, run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
# eo wait_for_run

"""
  Pretty printing helper
"""
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()
# eo pretty_print

"""
  After a Run has returned, this returns the list of messages in a Thread
"""
def get_response(client, thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")
# eo get_response

"""
"""
def create_thread_and_run(client, assistant_id, user_input):

    # Creates a new Thread of conversation
    thread = client.beta.threads.create()

    # Submits the Thead of conversation to the MATH_ASSISTANT, with the user input
    run = submit_message(client, assistant_id, thread, user_input)
    return thread, run
# eo create_thread_and_run

"""
  Creates a Message on a Thread and returns a Run
"""
def submit_message(client, assistant_id, thread, user_message):

    # The users request is indipendant of who they ask
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)

    # The Assistant is associated with the user_message only at the time creating a Run
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
    return run
# eo submit_message


