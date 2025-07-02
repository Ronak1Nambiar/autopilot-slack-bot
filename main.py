import time
import os
from datetime import datetime
from slack_utils import post_prompt, fetch_user_messages, post_summary, send_dm_reminders, post_health_ping
from summary import generate_summary
from tracker import save_summary_log, get_missing_users

print("\n============================")
print("🚀 Autopilot Agent Starting")
print("============================\n")

# 1. Post prompt
post_prompt()
print("✅ Prompt posted. Waiting 10 minutes...")
time.sleep(600)  # For demo; use 7200 for 2 hrs

# 2. Fetch replies & users
messages, all_user_ids = fetch_user_messages()
print(f"📥 {len(messages)} messages fetched.")

# 3. Generate summary
summary = generate_summary(messages)
print("📋 Summary ready.")

# 4. Post to Slack
post_summary(summary)

# 5. DM users who didn’t respond
missing_users = get_missing_users(messages, all_user_ids)
send_dm_reminders(missing_users)
print(f"📩 Reminders sent to {len(missing_users)} users.")

# 6. Save to logs
save_summary_log(summary)
print("💾 Summary saved to logs folder.")

# 7. Health ping
post_health_ping()
print("✅ Agent finished successfully.\n")
