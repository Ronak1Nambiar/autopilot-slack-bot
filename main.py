import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from slack_sdk import WebClient
from openai import OpenAI

# 🔐 Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Setup clients
slack_client = WebClient(token=SLACK_BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 1. Post daily prompt
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
    print("✅ Prompt posted.")

# 2. Fetch messages from Slack, ignore bot & prompt message
def fetch_messages():
    since = datetime.now() - timedelta(hours=12)
    response = slack_client.conversations_history(
        channel=SLACK_CHANNEL_ID,
        oldest=str(since.timestamp())
    )
    messages = []
    for msg in response["messages"]:
        if "bot_id" in msg:
            continue
        if msg["text"].startswith("🌅") or msg["text"].startswith(":sunrise:"):
            continue
        messages.append(msg["text"])
    print(f"📥 Collected {len(messages)} raw messages.")
    return messages

# 3. Filter out garbage/nonsense
def filter_messages(messages):
    filtered = [
        msg for msg in messages
        if len(msg) >= 10 and any(c.isalpha() for c in msg)
    ]
    print(f"🧹 Filtered down to {len(filtered)} valid messages.")
    return filtered

# 4. Send to OpenAI for summarization
def summarize_messages(messages):
    if not messages:
        return "No updates were posted today."

    full_text = "\n".join(messages)
    print("📤 Sending to OpenAI...")
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # use gpt-4o if you have quota
        messages=[
            {"role": "system", "content": (
                "You're summarizing team standup updates.\n"
                "Ignore random noise or gibberish. Only include meaningful bullet points.\n"
                "If updates are unclear or fake, say 'Some replies were unclear or unusable.'"
            )},
            {"role": "user", "content": full_text}
        ]
    )
    print("✅ OpenAI returned summary.")
    return response.choices[0].message.content

# 5. Post summary back to Slack
def post_summary(summary):
    slack_client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=f":memo: *Standup Summary:*\n{summary}"
    )
    print("✅ Summary posted to Slack.")

# 🔁 Main bot flow
def main():
    post_daily_prompt()
    print("⏳ Waiting 10 minutes for responses...")
    time.sleep(600)  # For testing; change to 7200 for 2 hrs in prod

    messages = fetch_messages()
    messages = filter_messages(messages)
    summary = summarize_messages(messages)
    post_summary(summary)

# 🔄 Loop daily (optional for background worker)
if __name__ == "__main__":
    while True:
        try:
            print("🚀 Running Slack AI Agent...")
            main()
            print("🕓 Sleeping for 24 hours...\n")
            time.sleep(86400)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)  # Wait 1 minute and retry
