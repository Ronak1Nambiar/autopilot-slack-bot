# slack_utils.py
import os
from slack_sdk import WebClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Prompt message
PROMPT_TEXT = (
    ":sunrise: *Good morning!*\n"
    "Please reply with your daily standup update:\n"
    "• What did you do yesterday?\n"
    "• What are you doing today?\n"
    "• Any blockers?"
)

def post_prompt():
    slack_client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=PROMPT_TEXT)

def fetch_user_messages():
    since = datetime.now() - timedelta(hours=12)
    response = slack_client.conversations_history(channel=SLACK_CHANNEL_ID, oldest=str(since.timestamp()))
    messages = []
    all_user_ids = set()
    for msg in response['messages']:
        if 'user' in msg and 'bot_id' not in msg:
            if len(msg['text']) > 10 and any(c.isalpha() for c in msg['text']):
                messages.append({'user': msg['user'], 'text': msg['text']})
            all_user_ids.add(msg['user'])
    return messages, all_user_ids

def post_summary(summary):
    slack_client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=f":memo: *Standup Summary:*\n{summary}")

def send_dm_reminders(user_ids):
    for user_id in user_ids:
        try:
            dm = slack_client.conversations_open(users=user_id)
            slack_client.chat_postMessage(channel=dm['channel']['id'], text="👋 Just a reminder to post your standup update in the channel!")
        except Exception as e:
            print(f"❌ Failed to DM {user_id}: {e}")

def post_health_ping():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    slack_client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=f"✅ Autopilot Agent completed at {now}")
