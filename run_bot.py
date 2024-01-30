import telebot
from langchain.globals import set_debug
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import os
import json
from utils import parse_response_into_objects, parse_conversation_to_string, prune_conversation_to_token_limit
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# EDIT THESE YOUR variables here
YOUR_NAME = os.getenv("YOUR_NAME")
YOUR_TELEGRAM_BOT_API_TOKEN = os.getenv("YOUR_TELEGRAM_BOT_API_TOKEN")
YOUR_MODEL_ENDPOINT = os.getenv("YOUR_MODEL_ENDPOINT")

# Set your OpenAI API key if you want to use OpenAI if not langchain still needs it for some reason for local LLM model endpoints
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

set_debug(True)

# To continue adding to this full string template as conversation continues
template = """
<|im_start|>system
>>> you are {assistant}, continue the conversation and reply {user} with as many messages to keep the conversation going. You are to have a coherent conversation with {user}<|im_end|>
<|im_start|>{user}
>>> hey<|im_end|>
<|im_start|>{assistant}
>>> hey<|im_end|>
"""

model = OpenAI(base_url=YOUR_MODEL_ENDPOINT, top_p=0.75, temperature=0.98, frequency_penalty=0, presence_penalty=0, best_of=1, max_tokens=256)

# Store the for each user
conversations = {}

# Store id_map for each user
id_map = {}

bot = telebot.TeleBot(YOUR_TELEGRAM_BOT_API_TOKEN)

@bot.message_handler(commands=["start", "help"])
def start(message):
    if message.text.startswith("/help"):
        bot.reply_to(message, "/clear - Clears old Messages")
        pass
    else:
        bot.reply_to(message, "Just start chatting with me to begin! Type /help for more commands to run.")



def generate_response_chat(conversation_history: list, user_name) -> str:
  """
  Generate a response to a user's message
  :param conversation_history: list of dict
  :return: str
  """
  full_string = parse_conversation_to_string(conversation_history) + "<|im_start|>{assistant}\n"
  full_string = template + full_string
  prompt = PromptTemplate(template=full_string, input_variables=["user", "assistant"])
  chain = prompt | model
  response =chain.invoke({"user": f"{user_name}", "assistant": f"{YOUR_NAME}"})
  return response

def generate_response_with_conversation_tracking(text_message: str, user_id, user_name):
  """
  Main function to generate response to a user's message\n
  Remembers messages up to a certain context window
  :param old_model: Open AI model
  :param user_id: telegram user id
  :param text_message: text message
  :return: str
  """
  # Store latest user message to global conversations history
  global conversations
  conversations[user_id] = conversations.get(user_id, [])
  conversations[user_id] += [{"role": "{user}", "content": text_message}]

  # Get the last messages that can fit into context window and responses for this user
  conversation_history = prune_conversation_to_token_limit(conversations[user_id], 1024, "cl100k_base")

  # Generate response
  response = generate_response_chat(conversation_history, user_name)

  response = parse_response_into_objects(response)

  # Store the updated conversations and responses for this user
  conversations[user_id] += response

  return response


@bot.message_handler(func=lambda message: True)
def reply_message(message):
    user_id = message.chat.id
    user_name = message.chat.first_name
    username = message.chat.username

    id_map[user_id] = username

    # Handle /clear command
    if message.text == '/clear':
        conversations[user_id] = []
        bot.reply_to(message, "Conversations and responses cleared!")
        return

    response = generate_response_with_conversation_tracking(message.text, user_id, user_name)

    # Reply to message
    for message in response:
      bot.send_message(user_id, message['content'])
    print(conversations)


    with open("logs.json", 'w+') as f:
        json.dump(conversations, f)

    with open("id-map.json", 'w+') as f:
        json.dump(id_map, f)

bot.infinity_polling()