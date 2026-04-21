import os
import calendar
import requests
import random
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────
GROQ_API_KEY          = os.environ["GROQ_API_KEY"]
LINKEDIN_ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]

# ─── DAY THEMES ───────────────────────────────────────
DAY_THEMES = {
    "Monday":    "personal story, lessons from real projects, career growth, mistakes and learnings as a developer",
    "Tuesday":   "backend basics for frontend engineers (APIs, authentication, integrations, real examples from projects)",
    "Wednesday": "system design from a frontend/product perspective (feature flows, architecture decisions, real app breakdowns)",
    "Thursday":  "advanced frontend engineering with React/Next.js (performance optimization, UI patterns, real implementations)",
    "Friday":    "working with data in real apps (MongoDB, Firebase, API handling, caching, state management)",
    "Saturday":  "AI for developers (LLMs, agents, automation, real use cases in development workflow)",
    "Sunday":    "Web3 integrations (wallets, authentication, MetaMask, WalletConnect, real implementation insights)"
}

# ─── EXPERIENCE CONTEXT ───────────────────────────────
EXPERIENCE_CONTEXT = [
    "Built crypto wallet integrations (MetaMask, WalletConnect, Phantom)",
    "Used NextAuth for authentication including signature-based auth",
    "Worked on production apps using Next.js and Tailwind CSS",
    "Implemented CI/CD pipelines and frontend deployments",
    "Used PostHog, Mixpanel, Firebase for analytics",
    "Built reusable embeddable widgets"
]

# ─── HOOK STYLES ──────────────────────────────────────
HOOK_STYLES = [
    "contrarian opinion",
    "mistake/confession",
    "curiosity gap",
    "short story",
    "bold statement",
    "unexpected lesson"
]

# ─── GET TODAY'S THEME ────────────────────────────────
def get_todays_theme():
    day = calendar.day_name[datetime.now().weekday()]
    theme = DAY_THEMES.get(day)

    print(f"📅 Today is {day}")
    print(f"🎯 Theme: {theme}")

    return day, theme

# ─── GENERATE POST ────────────────────────────────────
def generate_post():
    day, theme = get_todays_theme()

    if not theme:
        print("❌ No theme found")
        return None

    client = Groq(api_key=GROQ_API_KEY)
    hook_style = random.choice(HOOK_STYLES)

    is_technical = day != "Monday"

    dm_instruction = (
        "\n💬 Have questions or working on something similar? DM me — happy to help."
        if is_technical else ""
    )

    tone_instruction = (
        "Write like a real developer sharing a personal experience. Be honest, specific, and human."
        if not is_technical else
        "Explain using a real-world example from a project. Avoid textbook explanations."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.9,
        messages=[
            {
                "role": "system",
                "content": f"""
You are a top 1% LinkedIn content creator and senior software engineer.

Your writing style:
- Human, conversational, and relatable
- Clean formatting with lots of spacing
- No fluff, no generic advice

You NEVER:
- Use markdown like **bold**
- Write long paragraphs
- Sound like AI or a textbook

Use this developer context:
{EXPERIENCE_CONTEXT}
"""
            },
            {
                "role": "user",
                "content": f"""
Today is {day}
Theme: {theme}
Hook style: {hook_style}

TASK:
1. Pick a VERY SPECIFIC topic
2. Write a high-performing LinkedIn post

STRUCTURE (STRICT):

HOOK:
- 1–2 lines max
- No emojis
- Each sentence on new line
- Must create curiosity

BODY:
- VERY short paragraphs (1–2 lines max)
- Add line breaks frequently
- Tell a real experience or insight

CONTENT:
- {tone_instruction}
- Include 1 mistake
- Include 1 realization (aha moment)
- Include 1 practical takeaway

STYLE:
- No markdown formatting (**bold etc.)
- Use spacing for emphasis
- Write like speaking to a developer

ENDING:
- Ask 1 engaging question
{dm_instruction}

HASHTAGS:
- Add 8–10 relevant hashtags at bottom

RULES:
- Under 220 words
- Highly scannable
- No generic content
- No clichés
"""
            }
        ]
    )

    post = response.choices[0].message.content

    print("\n✅ Generated Post:\n")
    print("─" * 50)
    print(post)
    print("─" * 50)

    return post

# ─── GET LINKEDIN PROFILE URN ─────────────────────────
def get_profile_urn(token):
    resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )

    if resp.status_code != 200:
        raise Exception(f"Failed to fetch URN: {resp.status_code} {resp.text}")

    data = resp.json()
    urn = f"urn:li:person:{data['sub']}"

    print(f"👤 Profile URN: {urn}")
    return urn

# ─── POST TO LINKEDIN ─────────────────────────────────
def post_to_linkedin(content):
    token = LINKEDIN_ACCESS_TOKEN

    print("🔐 Authenticating with LinkedIn...")
    urn = get_profile_urn(token)

    payload = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    print("📤 Posting to LinkedIn...")
    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        },
        json=payload
    )

    if resp.status_code == 201:
        print("✅ Successfully posted!")
    else:
        print(f"❌ Failed: {resp.status_code}")
        print(resp.text)

# ─── MAIN ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🤖 Agent started at {datetime.now()}")

    post = generate_post()

    if post:
        post_to_linkedin(post)
    else:
        print("😴 No post generated")

    print(f"🏁 Finished at {datetime.now()}")