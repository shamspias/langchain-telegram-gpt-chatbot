# Langchain Telegram GPT Chatbot | Make your own AI Telegram Chatbot with the document you have

This repository contains a Telegram chatbot powered by OpenAI's GPT-3.5-turbo and FAISS for document similarity search.
The chatbot can understand text and voice messages, providing intelligent responses based on the user's input. In
addition to its conversational capabilities, the chatbot also integrates with a document similarity search engine,
allowing users to find relevant information in a collection of documents.

## Demo

![DeadlyAI](https://t.me/deadlyaibot)

## Features

- Text and voice message support
- Conversational AI using OpenAI's GPT-3.5-turbo
- Document similarity search with FAISS
- Conversation history tracking
- Google Text-to-Speech integration

## Technologies

- Python
- OpenAI API
- FAISS
- Telebot
- Google Text-to-Speech
- SpeechRecognition
- Pydub

## Future Scope

- Support for additional languages(한국어, 日本語, বাংলা etc.)
- Integration with other messaging platforms
- More advanced conversational features (e.g., context-aware responses)
- Improved performance and scalability
- Utilizing newer versions of OpenAI's models

## Installation and Usage

### Prerequisites

- Python 3.7+
- OpenAI API key
- FAISS
- Telegram bot token

### Installation

1. Go to [Langchain Chat](https://github.com/shamspias/langchain-chat) and create a model based on your document.
2. Clone the repository

```bash
git clone https://github.com/shamspias/langchain-chat.git
cd langchain-chat
```

3. Copy the Model into `models/` directory
4. Create the virtual environment and active it Install the dependencies

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

5. Copy the example.env file and rename it to .env and give the values of the variables
6. Run the application

```bash
python chatbot.py
```

7. Start chatting with your bot!

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests to improve the chatbot's functionality, performance, or documentation.

## Acknowledgements
- OpenAI for providing the GPT-3.5-turbo model
- Facebook AI for developing the FAISS library
- The developers of the various libraries and tools used in this project