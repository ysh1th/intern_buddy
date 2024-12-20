from dotenv import load_dotenv

import sys
import json
import os
import chainlit as cl
import atexit

from chatbot_logic import generate_behavioral_questions, generate_follow_up_question, response_analysis
from database.db_queries import store_first_question, store_first_response, store_follow_up_question, store_follow_up_response, store_analysis, fetch_first_question, fetch_first_response, fetch_follow_up_question, fetch_follow_up_response, remove_db # import python file that contains database queries for sqlite3
from database.chat_db import initialize_db

# store session id for db use
# user_id = 1234

json_file_path = '../interview_data.json'

if os.path.exists(json_file_path):
    with open(json_file_path, "r") as file:
        data = json.load(file)  # Extract JSON content into 'data'
        user_skills = data["skills"]
        job_requirements = data["requirements"]
        job_title = data["job title"]
else:
    raise FileNotFoundError(f"Data file not found at {json_file_path}")

# else:
#     print(f"Data file not found at {json_file_path}")

load_dotenv()

perplex_api_key = os.getenv("PERPLEX_API")

session_context = {
    "previous_responses": [],
    "current_question": None,
    "questions_asked": [],
    "counter": 0
}

# just a sample data, can be removed
# user_skills = ["Python", "Deep Learning", "Data Cleaning", "SQL", "Statistical Analysis", "Time Series Forecasting"]
# job_requirements = ["Critical Thinking", "Data Storytelling", "Problem Solving", "Statistical Modeling", "Machine Learning Algorithms"]

# job_title = "Data Scientist"


async def starter_first_question():
        
        session_context["counter"] += 1
        # Generate initial questions
        question = generate_behavioral_questions(
            user_skills, 
            job_requirements,
            job_title
        )

        if question is None:
            await cl.Message(content="Sorry, the interviewer has left the chat.").send()
            return
        
        store_first_question(question)
        
        # session_context["current_question"] = questions # store first question if using db
        # session_context["questions_asked"].extend(questions) # remove if using db

        # first_question = session_context["questions_asked"][1]
        # print(first_question)

        await cl.Message(content=f"Let's start!\n \n {question}").send()


async def starter_followup_question():
        session_context["counter"] += 1

        first_question = fetch_first_question()
        first_response = fetch_first_response()
        
        # fetch first q and first r if using db
        follow_up_question = generate_follow_up_question(
             first_question, 
             first_response
        )

        if follow_up_question is None:
          await cl.message(content="That's it for today, have a nice day.").send()
          return

        store_follow_up_question(follow_up_question)

        # session_context["current_question"] = follow_up_question # store follow up q if using db
        # session_context["questions_asked"].append(follow_up_question) #remove this for db

        await cl.Message(content=f"{follow_up_question}").send()


async def interview_analysis():
        session_context["counter"] += 1

        first_question = fetch_first_question()
        first_response = fetch_first_response()
        follow_up_question = fetch_follow_up_question()
        follow_up_response = fetch_follow_up_response()

        # fetch first q, r & followup q, r if using db
        analysis = response_analysis(
            job_requirements,
            first_question,
            first_response,
            follow_up_question,
            follow_up_response
        )

        if analysis is None:
          await cl.message(content="That's it for today, have a nice day.").send()
          return
        
        # store_analysis(analysis)

        # session_context["current_question"] = analysis # store analysis if using db
        # session_context["questions_asked"].append(analysis) #remove this for db

        await cl.Message(content=f"Here's the analysis of your performance:\n {analysis}").send()

@cl.on_message
async def responser(message: cl.Message):
    user_response = message.content

    session_context["previous_responses"].append(user_response)

    if session_context["counter"] == 0:
        await starter_first_question()  

    elif session_context["counter"] == 1:
        print(user_response)
        store_first_response(user_response)
        fr = fetch_first_response()
        print(fr)
        await starter_followup_question() 
        

    elif session_context["counter"] == 2:
        store_follow_up_response(user_response)
        await interview_analysis()
        # End the interview
        # session_context["counter"] += 1
    # elif session_context["counter"] == 3:
        await cl.Message(content="That's it for today, have a nice day.\n\nThanks for doing the mock behavioral interview. You can check out the analysis of your performance in the Streamlit app.").send()

        res = await cl.AskActionMessage(
            content="Want to try again?",
            actions=[
                cl.Action(name="restart", value="restart", label="✅ Restart"),
                cl.Action(name="cancel", value="cancel", label="❌ Cancel"),
            ],
        ).send()

        if res and res.get("value") == "restart":
            # await starter(cl.Message(content="Start"))
            remove_database()
            initialize_db() 
            if os.path.exists("chat_responses.db"):
                print('App created & db file created/exists!')
            else:
                print("Database file does not exist.")
            session_context["counter"]  = 0
            session_context["current_question"] = None
            session_context["previous_responses"] = []
            session_context["questions_asked"] = []


            await starter_first_question()
        else:
            await cl.Message(content="You chose to cancel.").send()
            remove_database()
            # data_cleanup()  ######## uncomment this if using the json file extraction method ########
            # data_cleanup()
            await close_session()  

            
async def close_session():
    import os
    import sys
    await cl.Message(content="Closing the session...").send()
    os._exit(0)

@cl.on_chat_start
async def main():

    initialize_db() 
    if os.path.exists("chat_responses.db"):
        print('App created & db file created/exists!')
    else:
        print("Database file does not exist.")

    res = await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="start", value="start", label="✅ Start"),
            cl.Action(name="cancel", value="cancel", label="❌ Cancel"),
        ],
    ).send()

    if res and res.get("value") == "start":

        await starter_first_question()
    else:
        await cl.Message(content="You chose to cancel.").send()
        remove_database()

        await close_session()
    

def remove_database(db_path="chat_responses.db"):
    if os.path.exists(db_path):
        try:
            remove_db()

            print(f"table {db_path} removed successfully.")
        except Exception as e:
            print(f"Error removing table: {e}")
    else:
        print(f"Database {db_path} does not exist.")

# def data_cleanup():
#     # import atexit
#     import os

#     if os.path.exists("../interview_data.json"):   

    # atexit.register(cleanup)


# @cl.on_chat_stop
# async def on_session_end():
#     print("Session closed. Performing cleanup.")
#     # Remove database if needed
#     remove_database()  # Example cleanup (delete DB, reset, etc.)
#     await cl.Message(content="Goodbye! The session is now closed.").send()
        
# if __name__ == "__main__":
#     initialize_db()
#     if os.path.exists(db_path="chat_responses.db"):
#         print('App created & db file created/exists!')
#     else:
#         print("Database file does not exist.")