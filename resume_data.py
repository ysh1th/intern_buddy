import sqlite3

conn = sqlite3.connect("resume_db.db")
cursor = conn.cursor()

# Create the resumes table
cursor.execute('''
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    location TEXT,
    technical_skills TEXT
)
''')

conn.commit()
conn.close()
print("Database and table created successfully!")

