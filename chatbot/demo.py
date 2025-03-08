from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import ollama
import streamlit as st

st.title("Madumitha's chat bot")

# Set up session state for previous input and response history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Function to update and display the conversation
def update_conversation(user_input, response):
    st.session_state.conversation.append({"role": "user", "content": user_input})
    st.session_state.conversation.append({"role": "assistant", "content": response})

# Define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [("system", "You are the helpful AI assistant. Your name is Madumitha's Assistant"),
     ("user", "User query: {query}")]
)

# Initialize the output parser
output_parser = StrOutputParser()

# Display the conversation history
for message in st.session_state.conversation:
    if message['role'] == 'user':
        st.write(f"User: {message['content']}")
    else:
        st.write(f"Assistant: {message['content']}")

# Get user input
input_txt = st.text_input("Hey hi😊...say your queries to me I'm here to help")

# Handle response generation when user submits a question
if input_txt:
    # Send the input text to the Llama model
    response = ollama.chat(model='llama2', messages=[
        {'role': 'system', 'content': "You are the helpful AI assistant. Your name is Madumitha's Assistant"},
        {'role': 'user', 'content': input_txt}
    ])
    
    # Get and parse the response
    ai_response = response['message']['content']
    
    # Display the assistant's response
    st.write(f"Assistant: {ai_response}")
    
    # Update the conversation history
    update_conversation(input_txt, ai_response)
