import streamlit as st
import openai
import sqlite3
import bcrypt

# Initialize OpenAI API
openai.api_key = "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"

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, 
        password TEXT, 
        interest TEXT, 
        goal TEXT,
        assessment_score INTEGER
    )
''')
conn.commit()

# At the beginning of the script, initialize the session state for username if it doesn't exist yet
if 'username' not in st.session_state:
    st.session_state.username = None


def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide a concise answer."},
            {"role": "user", "content": prompt}
        ],
    )
    return response['choices'][0]['message']['content']

def register_user(username, password, interest, goal):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, interest, goal) VALUES (?, ?, ?, ?)", 
                  (username, hashed_pw, interest, goal))
        conn.commit()

def check_user(username, password):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        stored_pw = c.fetchone()
        if stored_pw and bcrypt.checkpw(password.encode('utf-8'), stored_pw[0]):
            return True
    return False

def store_assessment_result(username, score):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET assessment_score = ? WHERE username = ?", (score, username))
        conn.commit()

def registration_page():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    interest = st.text_input("Your primary coding interest (e.g. Web Development, Data Science, etc.)")
    goal = st.text_area("What are your coding goals?")
    if st.button("Register"):
        if password == confirm_password:
            register_user(username, password, interest, goal)
            st.success("Registration successful!")
        else:
            st.error("Passwords do not match!")

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_user(username, password):
            st.success("Logged in successfully!")
            st.session_state.username = username  # Update the session state
            return "Chat"  # Return the next page to navigate to
        else:
            st.error("Invalid username or password")
    return "Login"  # By default, stay on the Login page

def assessment_page(username):
    st.title("Initial Assessment")
    questions = {
        "Which language is used for web apps?": ["Python", "JavaScript", "C++", "Java"],
        "Which of the following is a database?": ["MySQL", "HTML", "CSS", "JS"],
        "What does HTML stand for?": ["High Transfer Machine Language", "Hyperlinking Text Management Language", "Hyper Text Markup Language", "Hyper Transfer Markup Language"],
        "Which of the following is not an OOP principle?": ["Inheritance", "Polymorphism", "Duplication", "Encapsulation"],
        "What command is used to install packages in Python?": ["npm install", "yarn add", "pip install", "dotnet add"]
    }
    correct_answers = {
        "Which language is used for web apps?": "JavaScript",
        "Which of the following is a database?": "MySQL",
        "What does HTML stand for?": "Hyper Text Markup Language",
        "Which of the following is not an OOP principle?": "Duplication",
        "What command is used to install packages in Python?": "pip install"
    }
    user_answers = {}
    for question, options in questions.items():
        user_answers[question] = st.radio(question, options)
    if st.button("Submit"):
        correct_count = sum([1 for question, answer in user_answers.items() if answer == correct_answers[question]])
        store_assessment_result(username, correct_count)  # Store the user's score
        st.success(f"You answered {correct_count} out of {len(questions)} questions correctly!")
        if correct_count > len(questions) // 2:
            st.write("Great job! You have a good understanding of basic programming concepts.")
        else:
            st.write("Keep practicing! You'll get better with time.")

def chatbot_interface(username=None):
    st.title("TechItUp AI-Powered Coding Learning Chatbot")
    st.write("Welcome to the TechItUp AI-powered coding learning chatbot!")
    st.write("This chatbot will assist you in learning coding concepts. Ask any programming-related questions, and let's get started!")
    st.markdown("[Click here for a coding challenge](https://edabit.com/challenges)")
    st.markdown("[Start a quiz](https://www.codeconquest.com/coding-quizzes/)")
    user_input = st.text_input("Type your question here...")
    if user_input:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute("SELECT assessment_score FROM users WHERE username = ?", (username,))
            score = c.fetchone()[0]
            if score and score < 3:
                user_input = f"beginner {user_input}"
        with st.spinner('Processing...'):
            chatbot_response = get_gpt_response(user_input)
        st.write(f"Chatbot: {chatbot_response}")

if __name__ == "__main__":
    default_page = "Chat" if st.session_state.username else "Login"  # Default to Chat if logged in
    page = st.sidebar.selectbox("Choose a page", ["Login", "Register", "Assessment", "Chat"], index=["Login", "Register", "Assessment", "Chat"].index(default_page))
    
    if page == "Login":
        next_page = login_page()
        if next_page != page:
            page = next_page
            st.experimental_rerun()  # Rerun the app to update the page
    elif page == "Register":
        registration_page()
    elif page == "Assessment":
        if st.session_state.username:
            assessment_page(st.session_state.username)
        else:
            st.warning("Please log in before taking the assessment.")
    elif page == "Chat":
        chatbot_interface(st.session_state.username)
