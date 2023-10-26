import streamlit as st
import openai
import sqlite3
import bcrypt

# Initialize OpenAI API
openai.api_key = "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"

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
conn.commit()

def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide a concise answer."},
            {"role": "user", "content": prompt}
        ],
    )
    return response['choices'][0]['message']['content']

def register_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()

def check_user(username, password):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        stored_pw = c.fetchone()
        if stored_pw and bcrypt.checkpw(password.encode('utf-8'), stored_pw[0]):
            return True
    return False

def registration_page():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password == confirm_password:
            register_user(username, password)
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
        else:
            st.error("Invalid username or password")

def assessment_page():
    st.title("Initial Assessment")
    q1 = st.radio("Which language is used for web apps?", ["Python", "JavaScript", "C++", "Java"])
    q2 = st.radio("Which of the following is a database?", ["MySQL", "HTML", "CSS", "JS"])
    if st.button("Submit"):
        # TODO: Evaluate the answers and assign a level to the user
        st.success("Assessment complete!")

def chatbot_interface():
    st.title("TechItUp AI-Powered Coding Learning Chatbot")
    st.write("Welcome to the TechItUp AI-powered coding learning chatbot!")
    st.write("This chatbot will assist you in learning coding concepts. Ask any programming-related questions, and let's get started!")
    
    # Links for additional resources
    st.markdown("[Click here for a coding challenge](https://edabit.com/challenges)")
    st.markdown("[Start a quiz](https://www.codeconquest.com/coding-quizzes/)")

    user_input = st.text_input("Type your question here...")
    if user_input:
        with st.spinner('Processing...'):
            chatbot_response = get_gpt_response(user_input)
        st.write(f"Chatbot: {chatbot_response}")

if __name__ == "__main__":
    page = st.sidebar.selectbox("Choose a page", ["Login", "Register", "Assessment", "Chat"])
    if page == "Login":
        login_page()
    elif page == "Register":
        registration_page()
    elif page == "Assessment":
        assessment_page()
    elif page == "Chat":
        chatbot_interface()
