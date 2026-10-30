
import requests
import json
import os

# Ollama API Configuration
OLLAMA_API = "http://localhost:11434/api/chat"
MEMORY_FILE = "conversation.json"

# AI System Instructions
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an expert AI DevOps Assistant. "
        "Help users with Docker, Kubernetes, K3s, Jenkins, "
        "CI/CD, Linux, Azure and DevOps troubleshooting. "
        "Give practical and technically accurate answers. "
        "Never invent commands or configurations. "
        "Clearly mention when something needs verification."
    )
}


# Load Previous Conversation
def load_memory():

    if os.path.exists(MEMORY_FILE):

        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)

            if isinstance(history, list):
                return history

        except (json.JSONDecodeError, OSError):
            print("Warning: Could not load conversation history.")

    return []


# Save Conversation to JSON
def save_memory():

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            messages[1:],
            file,
            indent=4,
            ensure_ascii=False
        )


# Initialize Conversation
messages = [SYSTEM_PROMPT] + load_memory()


# Send Question to Ollama
def ask_ai(question):

    messages.append({
        "role": "user",
        "content": question
    })

    payload = {
        "model": "llama3.2",
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_API,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        answer = result["message"]["content"]

        messages.append({
            "role": "assistant",
            "content": answer
        })

        save_memory()

        return answer

    except requests.exceptions.RequestException as error:

        messages.pop()

        return f"Connection error: {error}"


# Display Conversation History
def show_history():

    print("\n========== Conversation History ==========")

    history = messages[1:]

    if not history:
        print("No conversation history found.")
        return

    for message in history:

        role = message["role"].upper()
        content = message["content"]

        print(f"\n{role}: {content}")

    print("\n===========================================")


# Clear Conversation Memory
def clear_memory():

    messages[:] = [SYSTEM_PROMPT]

    save_memory()

    print("\nConversation history cleared successfully!")


# Main Application
if __name__ == "__main__":

    print("================================")
    print("       AI DevOps Assistant")
    print("================================")

    print("Persistent Memory: Enabled")
    print("Type 'history' to view conversation.")
    print("Type 'clear' to delete conversation.")
    print("Type 'exit' to quit.")

    print(
        f"\nPrevious conversation messages: "
        f"{len(messages) - 1}"
    )

    while True:

        question = input("\nYou: ").strip()

        # Exit Chatbot
        if question.lower() == "exit":

            print("\nAI Assistant: Goodbye!")

            break

        # Show Conversation History
        if question.lower() == "history":

            show_history()

            continue

        # Clear Conversation History
        if question.lower() == "clear":

            clear_memory()

            continue

        # Handle Empty Input
        if not question:

            print("Please enter a question.")

            continue

        # Get AI Response
        print("\nAI is thinking...\n")

        answer = ask_ai(question)

        print("\nAI Assistant:", answer)
