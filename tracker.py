# tracker.py
import os
from datetime import datetime

# Save the summary to logs/standup-YYYY-MM-DD.txt
def save_summary_log(summary):
    os.makedirs("logs", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"logs/standup-{today}.txt", "w") as f:
        f.write(summary)

# Get users who did NOT post
# Requires all_user_ids = all seen in channel
# messages = list of {"user": "U123", "text": "..."}
def get_missing_users(messages, all_user_ids):
    responded = {m['user'] for m in messages}
    return list(all_user_ids - responded)
