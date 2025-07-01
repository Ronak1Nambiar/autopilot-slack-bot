import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from slack_sdk import WebClient
from openai import OpenAI

# 🔐 Load secrets from Replit's environment
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Setup clients
slack_client = WebClient(token=SLACK_BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 1. Post the daily standup prompt
def post_daily_prompt():
    slack_client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=(
            "🌅 *Good morning!*\n"
            "Please reply with your daily standup update:\n"
            "• What did you do yesterday?\n"
            "• What are you doing today?\n"
            "• Any blockers?"
        )
    )
    print("✅ Standup prompt sent.")

# 2. Fetch all replies from the last 12 hours
def fetch_messages():
    since = datetime.now() - timedelta(hours=12)
    response = slack_client.conversations_history(
        channel=SLACK_CHANNEL_ID,
        oldest=str(since.timestamp())
    )
    messages = [msg['text'] for msg in response['messages'] if 'bot_id' not in msg]
    print(f"📥 Collected {len(messages)} messages.")
    return messages

# 3. Summarize using OpenAI GPT-4o
def summarize_messages(messages):
    if not messages:
        print("❗ No messages to summarize.")
        return "No updates were posted today."

    full_text = "\n".join(messages)
    print("📤 Sending to OpenAI...\n", full_text)  # DEBUG

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # safer for quota
        messages=[
            {"role": "system", "content": "Summarize the following standup updates into clean, clear bullet points."},
            {"role": "user", "content": full_text}
        ]
    )
    print("✅ OpenAI returned a response.")  # DEBUG
    return response.choices[0].message.content

# 4. Post summary back to Slack
def post_summary(summary):
    slack_client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=f"📝 *Standup Summary:*\n{summary}"
    )
    print("✅ Summary posted.")

# 🔁 Main logic
def main():
    post_daily_prompt()
    print("⏳ Waiting 10 minutes for responses...")

    # Sleep for demo (change to 7200 for 2 hrs)
    time.sleep(600)

    messages = fetch_messages()
    summary = summarize_messages(messages)
    post_summary(summary)

# 🔄 Run
if __name__ == "__main__":
    main()
