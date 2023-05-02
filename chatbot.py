import os
import openai
import requests
import telebot
import pickle
from langchain.vectorstores import FAISS as BaseFAISS

from dotenv import load_dotenv
from gtts import gTTS
from pydub import AudioSegment
from celery import Celery
import speech_recognition as sr

from langchain.embeddings import OpenAIEmbeddings

load_dotenv()

SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')

app = Celery('chatbot', broker=os.getenv('CELERY_BROKER_URL'))

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Store the last 10 conversations for each user
conversations = {}


class FAISS(BaseFAISS):
    @staticmethod
    def load(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)


# Load the FAISS index
faiss_obj_path = "models/" + MODEL_NAME + ".pickle"
faiss_index = FAISS.load(faiss_obj_path)


# @app.task
def generate_response_chat(message_list):
    if faiss_index:
        # Add extra text to the content of the last message
        last_message = message_list[-1]

        # Get the most similar documents to the last message
        try:
            docs = faiss_index.similarity_search(query=last_message["content"], k=2)

            updated_content = last_message["content"] + "\n\n"
            for doc in docs:
                updated_content += doc.page_content + "\n\n"
        except Exception as e:
            print(f"Error while fetching : {e}")
            updated_content = last_message["content"]

        print(updated_content)

        # Create a new HumanMessage object with the updated content
        # updated_message = HumanMessage(content=updated_content)
        updated_message = {"role": "user", "content": updated_content}

        # Replace the last message in message_list with the updated message
        message_list[-1] = updated_message

    openai.api_key = OPENAI_API_KEY
    # Send request to GPT-3 (replace with actual GPT-3 API call)
    gpt3_response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0,
        messages=[
                     {"role": "system",
                      "content": SYSTEM_PROMPT},
                 ] + message_list
    )

    assistant_response = gpt3_response["choices"][0]["message"]["content"].strip()

    return assistant_response


def conversation_tracking(text_message, user_id):
    """
    Make remember all the conversation
    :param old_model: Open AI model
    :param user_id: telegram user id
    :param text_message: text message
    :return: str
    """
    # Get the last 10 conversations and responses for this user
    user_conversations = conversations.get(user_id, {'conversations': [], 'responses': []})
    user_messages = user_conversations['conversations'][-9:] + [text_message]
    user_responses = user_conversations['responses'][-9:]

    # Store the updated conversations and responses for this user
    conversations[user_id] = {'conversations': user_messages, 'responses': user_responses}

    # Construct the full conversation history in the user:assistant, " format
    conversation_history = []

    for i in range(min(len(user_messages), len(user_responses))):
        conversation_history.append({
            "role": "user", "content": user_messages[i]
        })
        conversation_history.append({
            "role": "assistant", "content": user_responses[i]
        })

    # Add last prompt
    conversation_history.append({
        "role": "user", "content": text_message
    })
    # Generate response
    response = generate_response_chat(conversation_history)
    # task = generate_response_chat.apply_async(args=[conversation_history])
    # response = task.get()

    # Add the response to the user's responses
    user_responses.append(response)

    # Store the updated conversations and responses for this user
    conversations[user_id] = {'conversations': user_messages, 'responses': user_responses}

    return response


@bot.message_handler(commands=["start", "help"])
def start(message):
    if message.text.startswith("/help"):
        bot.reply_to(message, "/clear - Clears old "
                              "conversations\nsend text to get replay\nsend voice to do voice"
                              "conversation")
    else:
        bot.reply_to(message, "Just start chatting to the AI or enter /help for other commands")


# Define a function to handle voice messages
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    user_id = message.chat.id
    # Download the voice message file from Telegram servers
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format(
        TELEGRAM_BOT_TOKEN, file_info.file_path))

    # Save the file to disk
    with open("voice_message.ogg", "wb") as f:
        f.write(file.content)

    # Use pydub to read in the audio file and convert it to WAV format
    sound = AudioSegment.from_file("voice_message.ogg", format="ogg")
    sound.export("voice_message.wav", format="wav")

    # Use SpeechRecognition to transcribe the voice message
    r = sr.Recognizer()
    with sr.AudioFile("voice_message.wav") as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)

    # Generate response
    replay_text = conversation_tracking(text, user_id)

    # Send the question text back to the user
    # Send the transcribed text back to the user
    new_replay_text = "Human: " + text + "\n\n" + "sonic: " + replay_text

    bot.reply_to(message, new_replay_text)

    # Use Google Text-to-Speech to convert the text to speech
    tts = gTTS(replay_text)
    tts.save("voice_message.mp3")

    # Use pydub to convert the MP3 file to the OGG format
    sound = AudioSegment.from_mp3("voice_message.mp3")
    sound.export("voice_message_replay.ogg", format="mp3")

    # Send the transcribed text back to the user as a voice
    voice = open("voice_message_replay.ogg", "rb")
    bot.send_voice(message.chat.id, voice)
    voice.close()

    # Delete the temporary files
    os.remove("voice_message.ogg")
    os.remove("voice_message.wav")
    os.remove("voice_message.mp3")
    os.remove("voice_message_replay.ogg")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.chat.id

    # Handle /clear command
    if message.text == '/clear':
        conversations[user_id] = {'conversations': [], 'responses': []}
        bot.reply_to(message, "Conversations and responses cleared!")
        return

    response = conversation_tracking(message.text, user_id)

    # Reply to message
    bot.reply_to(message, response)


if __name__ == "__main__":
    print("Starting bot...")
    print("Bot Started")
    print("Press Ctrl + C to stop bot")
    bot.polling()
