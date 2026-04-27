import os
import calendar
import random
from pathlib import Path

import requests
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
# LINKEDIN IMAGE UPLOAD (Share on LinkedIn — feed image asset)
# =====================================================
def _linkedin_v2_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def register_linkedin_feed_image_upload(person_urn: str) -> tuple[str, str, dict[str, str]]:
    """
    Register a feed-share image upload. Returns (upload_url, digitalmedia_asset_urn, extra_upload_headers).
    See: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
    """
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    response = requests.post(url, headers=_linkedin_v2_headers(), json=body, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(
            f"registerUpload failed: {response.status_code} {response.text}"
        )
    data = response.json().get("value") or {}
    mechanism = (
        data.get("uploadMechanism", {}).get(
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
        )
    )
    upload_url = mechanism.get("uploadUrl")
    asset = data.get("asset")
    extra_headers = mechanism.get("headers") or {}
    if not upload_url or not asset:
        raise RuntimeError(f"registerUpload missing uploadUrl/asset: {data!r}")
    return upload_url, asset, extra_headers


def upload_binary_to_linkedin_image_url(
    upload_url: str,
    image_path: str,
    extra_headers: dict[str, str],
) -> None:
    """PUT image bytes to LinkedIn-hosted uploadUrl (curl --upload-file semantics)."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(image_path)
    data = path.read_bytes()
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream",
        **{k: str(v) for k, v in extra_headers.items()},
    }
    # Docs: curl --upload-file → typically PUT with raw body; some endpoints accept POST.
    response = requests.put(upload_url, headers=headers, data=data, timeout=120)
    if response.status_code == 405:
        response = requests.post(upload_url, headers=headers, data=data, timeout=120)
    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Image binary upload failed: {response.status_code} {response.text[:500]}"
        )


# =====================================================
# POST TO LINKEDIN
# =====================================================
def post_to_linkedin(content: str, local_image_path: str | None = None) -> bool:
    """
    Publish a UGC post. If local_image_path is set, register + upload the PNG to LinkedIn
    then attach it (shareMediaCategory IMAGE). Text should omit the markdown code fence
    when attaching so the snippet appears only as the image.
    """
    try:
        print("\n🔐 Authenticating LinkedIn...")
        urn = get_profile_urn(LINKEDIN_ACCESS_TOKEN)

        image_asset_urn: str | None = None
        if local_image_path:
            try:
                upload_url, asset, extra = register_linkedin_feed_image_upload(urn)
                upload_binary_to_linkedin_image_url(
                    upload_url, local_image_path, extra
                )
                image_asset_urn = asset
                print("📎 Code PNG registered and uploaded for this post")
            except Exception as exc:
                print(f"❌ LinkedIn image upload failed: {exc}")
                return False

        share_inner: dict = {
            "shareCommentary": {"text": content},
            "shareMediaCategory": "NONE",
        }
        if image_asset_urn:
            share_inner["shareMediaCategory"] = "IMAGE"
            share_inner["media"] = [
                {
                    "status": "READY",
                    "description": {"text": "Code snippet"},
                    "media": image_asset_urn,
                    "title": {"text": "Code snippet"},
                }
            ]

        payload = {
            "author": urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {"com.linkedin.ugc.ShareContent": share_inner},
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=_linkedin_v2_headers(),
            json=payload,
            timeout=60,
        )

        if response.status_code == 201:
            print("✅ Successfully posted to LinkedIn!")
            return True
        print(f"❌ Failed posting: {response.status_code}")
        print(response.text)
        return False

    except Exception as e:
        print(f"❌ LinkedIn posting failed: {e}")
        return False


def publish_linkedin_post(post: str, local_png_path: str | None) -> None:
    """
    Post to LinkedIn: attach Ray.so PNG when available (strip inline ``` fence from body).
    Set SKIP_LINKEDIN_IMAGE_ATTACH=true to keep markdown code in the text and no image.
    """
    skip_attach = os.getenv("SKIP_LINKEDIN_IMAGE_ATTACH", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    use_image = bool(local_png_path) and not skip_attach

    if use_image:
        from codeFunctions import remove_fenced_code_block

        body = remove_fenced_code_block(post)
        if len(body.strip()) < 30:
            print(
                "⚠️ Body too short after removing code block — posting full text with inline code."
            )
            post_to_linkedin(post)
            return
        ok = post_to_linkedin(body, local_image_path=local_png_path)
        if not ok:
            print(
                "⚠️ LinkedIn publish failed (no duplicate post sent). "
                "Fix token/scopes or API errors above and re-run if needed."
            )
        return

    post_to_linkedin(post)


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

    # One Ray.so render: PNG for optional Cloudinary + LinkedIn image attachment.
    local_png_path: str | None = None
    skip_img = os.getenv("SKIP_CODE_SNIPPET_IMAGE", "").strip().lower() in ("1", "true", "yes")
    if not skip_img:
        from codeFunctions import _cloudinary_configured, save_code_image_from_post_local

        local_png_path = save_code_image_from_post_local(post)
        if local_png_path:
            print(f"\n📷 Code snippet PNG:\n{local_png_path}\n")
        if local_png_path and _cloudinary_configured():
            from codeFunctions import upload_to_cloudinary

            try:
                public_url = upload_to_cloudinary(local_png_path)
                print(f"☁️ Cloudinary (optional share link):\n{public_url}\n")
            except Exception as e:
                print(f"⚠️ Cloudinary upload failed: {e}")

    print("\n-----------------------------------")

    if should_auto_post_linkedin():
        if os.getenv("GITHUB_ACTIONS", "").strip().lower() == "true":
            print("🚀 Auto post: GitHub Actions → publishing to LinkedIn")
        else:
            print("🚀 Auto post: LINKEDIN_AUTO_POST enabled → publishing to LinkedIn")
        publish_linkedin_post(post, local_png_path)
    else:
        approval = input("Post this to LinkedIn? (y/n): ").strip().lower()

        if approval == "y":
            publish_linkedin_post(post, local_png_path)
        else:
            print("📝 Post skipped. Set LINKEDIN_AUTO_POST=true in .env to skip this prompt.")

    print(f"\n🏁 Finished at {datetime.now()}")


if __name__ == "__main__":
    main()