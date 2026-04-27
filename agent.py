import os
import calendar
import requests
import random
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

from snippet_library import select_post_spec

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
# FRONTEND CONTENT THEMES (LinkedIn — senior UI / web platform engineers)
# =====================================================
DAY_THEMES = {
    "Monday": "components, design systems, and maintainable UI boundaries",

    "Tuesday": "React / Next.js architecture, data fetching, and client patterns",

    "Wednesday": "auth UX on the web, secure client–server boundaries, forms",

    "Thursday": "Core Web Vitals, rendering cost, bundles, and perceived performance",

    "Friday": "instrumentation, experiments, and product signals from the frontend",

    "Saturday": "DX, AI-assisted UI work, and shipping faster without quality debt",

    "Sunday": "accessibility, responsive design, and inclusive interaction patterns",
}


# =====================================================
# PROFESSIONAL POST FORMATS
# =====================================================
POST_FORMATS = [
    "contrarian take",
    "UI architecture breakdown",
    "technical tradeoff",
    "implementation insight in the browser",
    "performance / UX lesson",
    "scaling lesson for frontend teams",
    "engineering opinion for product engineers",
]


# =====================================================
# EXPERIENCE CONTEXT
# =====================================================
EXPERIENCE_CONTEXT = """
Real frontend / product engineering experience (ground your post here):
- Production SaaS and dashboards in Next.js, React, and TypeScript
- Tailwind and component libraries; design-system-minded CSS
- Embeddable widgets, iframes, and third-party script boundaries
- NextAuth and secure session patterns; API layers and retries
- PostHog / Mixpanel-style product analytics wired from the UI
- Performance work: bundles, lazy routes, list virtualization, Core Web Vitals
- Accessibility reviews, forms, and keyboard-first flows
"""


# =====================================================
# GET TODAY INFO
# =====================================================
def get_today_info():
    day = calendar.day_name[datetime.now().weekday()]
    theme = DAY_THEMES.get(day)
    spec = select_post_spec(day)
    topic = spec["topic"]
    format_type = random.choice(POST_FORMATS)

    print(f"\n📅 Today: {day} (frontend channel)")
    print(f"🎯 Theme: {theme}")
    print(f"🧠 Topic: {topic}")
    print(f"✍️ Format: {format_type}")

    return day, theme, topic, format_type, spec


# =====================================================
# GENERATE POST
# =====================================================
def generate_post():
    day, theme, topic, format_type, spec = get_today_info()

    print(
        f"📎 Code plan: {spec['title']} ({spec['language']}) — {spec['angle']}"
    )

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a top LinkedIn creator for senior frontend and product engineers (React/Next ecosystem, CSS, a11y, performance, UX implementation).

Write like someone who ships and maintains real browser-facing products — not generic career advice.

TOPIC:
{topic}

THEME:
{theme}

FORMAT:
{format_type}

YOUR EXPERIENCE:
{EXPERIENCE_CONTEXT}

AUDIENCE:
- Frontend engineers, UI engineers, and tech leads
- Keep the narrative anchored in components, the DOM, networks, CSS, TypeScript, and user-visible tradeoffs

CODE BLOCK (you write it — must match this post, not a generic template):
- Suggested filename to mention or imply in prose: {spec["title"]}
- Fence language id (exactly): {spec["language"]}
- What the code must demonstrate (same story as the topic): {spec["angle"]}
- Invent concrete, readable code (realistic names, one clear scenario) that a senior frontend engineer would ship as an example in a blog post. It must directly illustrate the TOPIC and the angle above—not filler unrelated to your hook and body.

RULES:
- Sound like an experienced frontend or product engineer
- Focus on UI architecture, rendering, DX, accessibility, or performance as they show up in real apps
- Discuss tradeoffs (bundle size vs. DX, client vs. server, a11y vs. speed, etc.)
- Avoid backend-only or DevOps-only tangents unless they directly affect the UI
- Avoid fake storytelling, beginner tropes, "I spent hours debugging", generic advice, and empty motivation
- Be concise and sharp
- Include exactly ONE markdown fenced code block: opening ``` then the language id must be exactly {spec["language"]}, newline, then your original code, then closing ``` on its own line. Do not use any other fence language. The code must be the proof for your argument about this topic (you may shorten with `// …` or `<!-- … -->` where helpful).

STRUCTURE:
1. Strong hook (1-2 lines)
2. Insightful body (place the code block where it supports the argument — usually after 1–2 short paragraphs)
3. Brief commentary right after the code (what it proves in production)
4. Specific takeaway
5. End with a thoughtful question

STYLE:
- Short paragraphs
- Highly scannable
- Professional
- Human
- Technical but accessible

LENGTH:
- Prose (everything except the fenced code block): at most ~220 words
- Code block: at most ~25 lines; prefer readable over exhaustive

Add 5 relevant hashtags only (after the question, not inside the code fence).
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write high-performing LinkedIn posts for experienced frontend and product engineers "
                        "(React, Next.js, TypeScript, CSS, HTML, accessibility, performance). "
                        "Every post includes exactly one markdown fenced code block (javascript, typescript, html, or css only). "
                        "You compose original code for that post's topic—never paste unrelated catalog examples; the block must prove the post's specific claim."
                    ),
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


def should_auto_post_linkedin() -> bool:
    """Post without prompting in CI, or when LINKEDIN_AUTO_POST is enabled locally."""
    if os.getenv("GITHUB_ACTIONS", "").strip().lower() == "true":
        return True
    return os.getenv("LINKEDIN_AUTO_POST", "").strip().lower() in ("1", "true", "yes")


# =====================================================
# MAIN
# =====================================================
def main():
    print(f"\n🤖 Agent started at {datetime.now()}")

    post = generate_post()

    if not post:
        print("❌ No post generated")
        return

    # Turn fenced code into a PNG (Ray.so). Public URL when Cloudinary env is set; else local file path.
    skip_img = os.getenv("SKIP_CODE_SNIPPET_IMAGE", "").strip().lower() in ("1", "true", "yes")
    if not skip_img:
        from codeFunctions import (
            _cloudinary_configured,
            generate_code_image_from_post,
            save_code_image_from_post_local,
        )

        image_url = None
        if _cloudinary_configured():
            result = generate_code_image_from_post(post, None)
            if result and result.get("image_url"):
                image_url = result["image_url"]
                print(f"\n📷 Code snippet image URL:\n{image_url}\n")
            else:
                local_path = save_code_image_from_post_local(post)
                if local_path:
                    print(
                        f"\n📷 Saved locally (upload failed or skipped):\n{local_path}\n"
                    )
        else:
            local_path = save_code_image_from_post_local(post)
            if local_path:
                print(f"\n📷 Code snippet image saved (local file):\n{local_path}\n")
                print(
                    "Tip: set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and "
                    "CLOUDINARY_API_SECRET in .env to get a shareable HTTPS link.\n"
                )

    print("\n-----------------------------------")

    if should_auto_post_linkedin():
        if os.getenv("GITHUB_ACTIONS", "").strip().lower() == "true":
            print("🚀 Auto post: GitHub Actions → publishing to LinkedIn")
        else:
            print("🚀 Auto post: LINKEDIN_AUTO_POST enabled → publishing to LinkedIn")
        post_to_linkedin(post)
    else:
        approval = input("Post this to LinkedIn? (y/n): ").strip().lower()

        if approval == "y":
            post_to_linkedin(post)
        else:
            print("📝 Post skipped. Set LINKEDIN_AUTO_POST=true in .env to skip this prompt.")

    print(f"\n🏁 Finished at {datetime.now()}")


if __name__ == "__main__":
    main()