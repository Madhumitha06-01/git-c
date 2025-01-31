import streamlit as st
import google.generativeai as genai

# Initialize Google Generative AI with the API key (replace with your actual API key)
genai.configure(api_key="AIzaSyA_GQN7iJ8KlygRvX5E-vJqrdkkhiHb8pU")

# Specify the model to use for text generation
MODEL = "gemini/gemini-1.5-flash"  # Correct model name

# Function to get bot's response based on user input and context
def get_bot_response(user_input, history):
    # Combine chat history with user input to maintain context
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    conversation = f"{context}\nuser: {user_input}\nassistant:"

    # Generate the response based on the context
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([conversation])
    return response.text

# Streamlit app
def main():
    st.title("Chatbot with Memory using Google Generative AI")

    # Initialize session state for chat messages if not already initialized
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you today?"}]

    # Display chat messages from the session state
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle user input
    if user_input := st.chat_input("Type your question here..."):
        # Add user input to the conversation
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Get bot response with context
        bot_response = get_bot_response(user_input, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Display the bot's response
        st.chat_message("assistant").write(bot_response)

if __name__ == "__main__":
    main()
