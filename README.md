# Telegram bot for clone doppleganger
A Telegram bot you can deploy to mimick the way you talk! Fine tune a LLM on your own telegram messages.

Credits and inspiration to [fusiousteabag](https://github.com/furiousteabag) who helped me with the fine tuning - [repo](https://github.com/furiousteabag/doppelganger)

Credits and inspiration to [shamspias](https://github.com/shamspias) on how to build a telegram bot with langchain - [repo](https://github.com/shamspias/langchain-telegram-gpt-chatbot)

## Installation
### Requirements
- Python 3.11 was used (best to create a virtual environment using conda on venv)
- run pip install -r requirements.txt
- run your own local open source LLM api endpoint server (for this project i used [textgen-webui](https://github.com/oobabooga/text-generation-webui)). You will need to start your textgen-webui server with the `--api` flag to generate an api endpoint that the bot will call to generate responses. Refer to the [textgen-webui](https://github.com/oobabooga/text-generation-webui) repo for more details.
- create a `.env` file and update your variables with your own telegram bot token, your own name, your own LLM api endpoint. refer to `.env.example` for the variables you need to set. Your final `.env` file should look like the `.env.example` except with your own variables.
- refer to [this](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) to get your own telegram bot token

## Running the bot
run the following command
```
python run_bot.py
```

## Fine Tuning
Refer more to furiousteabag [repo](https://github.com/furiousteabag/doppelganger) and [blog](https://asmirnov.xyz/doppelganger) to see how he got his telegram messages and prepared the dataset for fine tuning. The methods used for fine tuning he also discussed and evaluated in his blog. Brilliant stuff!

## Libraries used
- tiktoken (to calculate tokens)
- langchain (easy api to connect llm endpoints in python)
- pyTelegramBotAPI (python api to interface with telegram)
