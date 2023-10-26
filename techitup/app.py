import streamlit as st
import openai

# Initialize OpenAI API
openai.api_key = "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"

def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Provide a concise answer."},
            {"role": "user", "content": prompt}
        ],
    )
    return response['choices'][0]['message']['content']

def chatbot_interface():
    st.title("TechItUp AI-Powered Coding Learning Chatbot")

    # Welcome screen
    st.write("Welcome to the TechItUp AI-powered coding learning chatbot!")
    st.write("This chatbot will assist you in learning coding concepts. Ask any programming-related questions, and let's get started!")

    # Chat interface
    user_input = st.text_input("Type your question here...")
    
    if user_input:
        # Notify the user that the chatbot is processing the question
        with st.spinner('Processing...'):
            chatbot_response = get_gpt_response(user_input)
        st.write(f"Chatbot: {chatbot_response}")

if __name__ == "__main__":
    chatbot_interface()
