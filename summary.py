# summary.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(messages):
    if not messages:
        return "No updates were posted today."

    full_text = "\n".join([m['text'] for m in messages])
    print("📤 Sending to OpenAI...")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "You're summarizing standup updates."
                " Ignore random noise or nonsense."
                " Only include valid tasks or blockers in clear bullet points."
                " If everything is junk, respond: 'Some replies were unclear or unusable.'"
            )},
            {"role": "user", "content": full_text}
        ]
    )

    return response.choices[0].message.content
