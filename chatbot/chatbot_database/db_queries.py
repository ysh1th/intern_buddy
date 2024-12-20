import sqlite3
import chainlit as cl

current_interview_id = None

# # Function to fetch responses from the database
# def fetch_responses(user_id):
#     conn = sqlite3.connect("chat_responses.db")
#     cursor = conn.cursor()

#     cursor.execute("""
#     SELECT question, user_response, bot_response, timestamp
#     FROM chat_responses
#     WHERE user_id = ?
#     ORDER BY timestamp DESC
#     """, (user_id,))

#     results = cursor.fetchall()
#     conn.close()

#     return results

def store_first_question(first_question):
    conn = sqlite3.connect("chat_responses.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO interview (first_question) 
    VALUES (?)
    """, (first_question,))
    conn.commit()
    global current_interview_id
    current_interview_id = cursor.lastrowid

    
    conn.close()

# Function to store the first response
def store_first_response(first_response):
    global current_interview_id

    if current_interview_id is None:
        print('interview id not created\n')
        return

    conn = sqlite3.connect("chat_responses.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE interview 
    SET first_response = ? 
    WHERE interview_id = ?
    """, (first_response, current_interview_id))
    conn.commit()
    
    conn.close()

# Function to store the follow-up question
def store_follow_up_question(follow_up_question):
    global current_interview_id

    if current_interview_id is None:
        print('interview id not created\n')
        return

    conn = sqlite3.connect("chat_responses.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE interview 
    SET follow_up_question = ? 
    WHERE interview_id = ?
    """, (follow_up_question, current_interview_id))
    conn.commit()
    
    conn.close()

# Function to store the follow-up response
def store_follow_up_response(follow_up_response):
    global current_interview_id

    if current_interview_id is None:
        print('interview id not created\n')
        return

    conn = sqlite3.connect("chat_responses.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE interview 
    SET follow_up_response = ? 
    WHERE interview_id = ?
    """, (follow_up_response, current_interview_id))
    conn.commit()
    
    conn.close()

# Function to store the analysis
def store_analysis(analysis):
    global current_interview_id

    if current_interview_id is None:
        print('interview id not created\n')
        return

    conn = sqlite3.connect("chat_responses.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE interview 
    SET analysis = ? 
    WHERE interview_id = ?
    """, (analysis, current_interview_id))
    conn.commit()
    
    conn.close()


############################## fetching ##############################

def fetch_first_question():
    global current_interview_id

    try:
        conn = sqlite3.connect("chat_responses.db")
        cursor = conn.cursor()

        # Query to fetch the first question based on interview_id
        cursor.execute("SELECT first_question FROM interview WHERE interview_id = ?", (current_interview_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the first question
        else:
            return "No question found for this interview."
    except sqlite3.Error as e:
        print(f"Error fetching first question: {e}")
        return None
    finally:
        conn.close()

def fetch_first_response():
    global current_interview_id

    try:
        conn = sqlite3.connect("chat_responses.db")
        cursor = conn.cursor()

        # Query to fetch the first response based on interview_id
        cursor.execute("SELECT first_response FROM interview WHERE interview_id = ?", (current_interview_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the first response
        else:
            return "No response found for this interview."
    except sqlite3.Error as e:
        print(f"Error fetching first response: {e}")
        return None
    finally:
        conn.close()


def fetch_follow_up_question():
    global current_interview_id

    try:
        conn = sqlite3.connect("chat_responses.db")
        cursor = conn.cursor()

        # Query to fetch the follow-up question based on interview_id
        cursor.execute("SELECT follow_up_question FROM interview WHERE interview_id = ?", (current_interview_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the follow-up question
        else:
            return "No follow-up question found for this interview."
    except sqlite3.Error as e:
        print(f"Error fetching follow-up question: {e}")
        return None
    finally:
        conn.close()

def fetch_follow_up_response():
    global current_interview_id

    try:
        conn = sqlite3.connect("chat_responses.db")
        cursor = conn.cursor()

        # Query to fetch the follow-up response based on interview_id
        cursor.execute("SELECT follow_up_response FROM interview WHERE interview_id = ?", (current_interview_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the follow-up response
        else:
            return "No follow-up response found for this interview."
    except sqlite3.Error as e:
        print(f"Error fetching follow-up response: {e}")
        return None
    finally:
        conn.close()



def remove_db():

    try:
        conn = sqlite3.connect("chat_responses.db")
        cursor = conn.cursor()

        # Query to fetch the follow-up response based on interview_id
        cursor.execute("DELETE FROM interview;")

    except sqlite3.Error as e:
        print(f"Error fetching follow-up response: {e}")
        return None
    finally:
        conn.commit()
        conn.close()
        print("Table emptied successfully.")