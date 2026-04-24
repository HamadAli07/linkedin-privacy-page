import os
import calendar
import requests
import random
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# CONFIG
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY")

if not LINKEDIN_ACCESS_TOKEN:
    raise ValueError("Missing LINKEDIN_ACCESS_TOKEN")


# =====================================================
# SENIOR CONTENT THEMES
# =====================================================
DAY_THEMES = {
    "Monday": "career growth, engineering mindset, leadership lessons",

    "Tuesday": "frontend architecture decisions from real products",

    "Wednesday": "authentication, APIs, integrations, security engineering",

    "Thursday": "performance, scalability, and system design lessons",

    "Friday": "product engineering, analytics, experimentation, user behavior",

    "Saturday": "AI workflows, automation, developer productivity",

    "Sunday": "web3 engineering, crypto wallets, blockchain UX"
}


# =====================================================
# SPECIFIC TOPIC POOLS
# =====================================================
TOPIC_POOL = {
    "Monday": [
        "What I learned transitioning from junior to product-focused engineer",
        "Why writing code isn't enough to become a better engineer",
        "How ownership changed my engineering career"
    ],

    "Tuesday": [
        "Why centralized API layers scale better in Next.js apps",
        "Why most frontend teams overcomplicate state management",
        "How reusable widget systems are built",
        "Why frontend architecture matters more than UI polish"
    ],

    "Wednesday": [
        "Lessons from implementing signature-based authentication",
        "Why OAuth implementations fail in production",
        "Handling API retries in frontend applications",
        "Authentication edge cases teams ignore"
    ],

    "Thursday": [
        "Why premature optimization hurts frontend teams",
        "Scaling React applications beyond MVP stage",
        "Performance bottlenecks in large Next.js apps",
        "How we reduced frontend deployment friction"
    ],

    "Friday": [
        "Why analytics should be part of engineering decisions",
        "What PostHog taught me about product behavior",
        "Why engineers ignore feature adoption metrics",
        "Building products based on user behavior data"
    ],

    "Saturday": [
        "How AI is improving my development workflow",
        "Automating repetitive engineering tasks with AI",
        "Building developer agents",
        "Using AI tools without becoming dependent"
    ],

    "Sunday": [
        "WalletConnect integration lessons",
        "MetaMask onboarding friction",
        "Why web3 UX still feels broken",
        "Building wallet authentication flows"
    ]
}


# =====================================================
# PROFESSIONAL POST FORMATS
# =====================================================
POST_FORMATS = [
    "contrarian take",
    "architecture breakdown",
    "technical tradeoff",
    "product lesson",
    "implementation insight",
    "scaling lesson",
    "engineering opinion"
]


# =====================================================
# EXPERIENCE CONTEXT
# =====================================================
EXPERIENCE_CONTEXT = """
Real experience:
- Built crypto wallet integrations (MetaMask, WalletConnect, Phantom)
- Implemented signature-based authentication using NextAuth
- Built production SaaS apps using Next.js and Tailwind
- Created reusable embeddable widgets
- Implemented CI/CD pipelines
- Used PostHog, Mixpanel, Firebase analytics
- Built dashboards and onboarding systems
- Worked on fintech and web3 applications
"""


# =====================================================
# GET TODAY INFO
# =====================================================
def get_today_info():
    day = calendar.day_name[datetime.now().weekday()]
    theme = DAY_THEMES.get(day)
    topic = random.choice(TOPIC_POOL[day])
    format_type = random.choice(POST_FORMATS)

    print(f"\n📅 Today: {day}")
    print(f"🎯 Theme: {theme}")
    print(f"🧠 Topic: {topic}")
    print(f"✍️ Format: {format_type}")

    return day, theme, topic, format_type


# =====================================================
# GENERATE POST
# =====================================================
def generate_post():
    day, theme, topic, format_type = get_today_info()

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a top engineering creator on LinkedIn.

Write like a senior product engineer sharing real-world insights.

TOPIC:
{topic}

THEME:
{theme}

FORMAT:
{format_type}

YOUR EXPERIENCE:
{EXPERIENCE_CONTEXT}

RULES:
- Sound like an experienced engineer
- Focus on architecture decisions
- Discuss tradeoffs
- Share implementation lessons
- Talk about scalability/product impact
- Be concise and sharp
- Avoid fake storytelling
- Avoid beginner mistakes
- Avoid "I spent hours debugging"
- Avoid generic advice
- Avoid motivational fluff

STRUCTURE:
1. Strong hook (1-2 lines)
2. Insightful body
3. Specific takeaway
4. End with thoughtful question

STYLE:
- Short paragraphs
- Highly scannable
- Professional
- Human
- Technical but accessible

MAX:
220 words

Add 5 relevant hashtags only.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            messages=[
                {
                    "role": "system",
                    "content": "You write high-performing LinkedIn content for experienced software engineers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        post = response.choices[0].message.content

        print("\n✅ Generated Post:\n")
        print("=" * 60)
        print(post)
        print("=" * 60)

        return post

    except Exception as e:
        print(f"❌ Post generation failed: {e}")
        return None


# =====================================================
# GET LINKEDIN PROFILE URN
# =====================================================
def get_profile_urn(token):
    response = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed fetching LinkedIn profile: {response.status_code} {response.text}"
        )

    data = response.json()
    urn = f"urn:li:person:{data['sub']}"

    print(f"👤 LinkedIn Profile URN: {urn}")

    return urn


# =====================================================
# POST TO LINKEDIN
# =====================================================
def post_to_linkedin(content):
    try:
        print("\n🔐 Authenticating LinkedIn...")
        urn = get_profile_urn(LINKEDIN_ACCESS_TOKEN)

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

        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            },
            json=payload
        )

        if response.status_code == 201:
            print("✅ Successfully posted to LinkedIn!")
        else:
            print(f"❌ Failed posting: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ LinkedIn posting failed: {e}")


# =====================================================
# MAIN
# =====================================================
def main():
    print(f"\n🤖 Agent started at {datetime.now()}")

    post = generate_post()

    if not post:
        print("❌ No post generated")
        return

    print("\n-----------------------------------")
    approval = input("Post this to LinkedIn? (y/n): ").strip().lower()

    if approval == "y":
        post_to_linkedin(post)
    else:
        print("📝 Post skipped.")

    print(f"\n🏁 Finished at {datetime.now()}")


if __name__ == "__main__":
    main()