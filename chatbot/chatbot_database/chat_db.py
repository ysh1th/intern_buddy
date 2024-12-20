import sqlite3

def initialize_db():
    conn = sqlite3.connect("chat_responses.db")
    cursor = conn.cursor()

    # # companies data
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS companies (
    #   company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #   company_name TEXT NOT NULL,
    #   job_requirements TEXT NOT NULL,
    #   job_title TEXT
    # )
    # """)

    # # users data
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS user (
    #   user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #   user_skills TEXT NOT NULL,
    # )
    # """)

    # Create table for storing responses
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS interview (
    #   interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #   user_id INTEGER NOT NULL,
    #   company_id INTEGER NOT NULL,
    #   first_question TEXT,
    #   first_response TEXT,
    #   follow_up_question TEXT,
    #   follow_up_response TEXT,
    #   analysis TEXT,
    #   FOREIGN KEY (user_id) REFERENCES user(user_id)
    #   FOREIGN KEY (company_id) REFERENCES companies(company_id)
    # )
    # """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview (
      interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
      first_question TEXT,
      first_response TEXT,
      follow_up_question TEXT,
      follow_up_response TEXT,
      analysis TEXT
    )
    """)
###### insert user data query ##### if no streamlit

###### insert user data query ##### if no streamlit

    conn.commit()
    conn.close()
