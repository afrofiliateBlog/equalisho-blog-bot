import os
import json
import re
import base64
import requests
import random
from datetime import datetime

# ── credentials ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WP_URL            = os.environ["WP_URL"].rstrip("/")
WP_USERNAME       = os.environ["WP_USERNAME"]
WP_APP_PASSWORD   = os.environ["WP_APP_PASSWORD"]

# ── 5 pillar topic clusters ───────────────────────────────────
PILLARS = {
    "Workplace DEI Strategy": [
        "How to build a DEI strategy from scratch in 2026",
        "Measuring the impact of your diversity and inclusion programme",
        "Why most DEI initiatives fail and how to fix yours",
        "How to get leadership buy-in for your DEI strategy",
        "DEI budgeting: how much should you be spending",
        "How to run a diversity audit of your organisation",
        "Building an inclusive culture that outlasts DEI trends",
        "How to set meaningful DEI targets and actually hit them",
        "The difference between diversity equity and inclusion in practice",
        "How to communicate your DEI progress to employees and stakeholders",
    ],
    "Employee Wellbeing and Mental Health": [
        "How to build a workplace mental health strategy in 2026",
        "Why employee burnout is a leadership problem not an individual one",
        "How to create psychological safety in your team",
        "Practical mindfulness techniques for busy professionals",
        "How to support employees with anxiety and depression at work",
        "Building a financial wellness programme for your employees",
        "How flexible working improves employee mental health",
        "The ROI of investing in employee wellbeing",
        "How to train managers to support mental health at work",
        "Creating a culture where asking for help is encouraged",
    ],
    "ESG and Corporate Responsibility": [
        "How to build an ESG framework your investors will respect",
        "The social pillar of ESG: what it means for your workforce",
        "How to align your DEI goals with your ESG reporting",
        "ESG reporting requirements UK employers need to know in 2026",
        "How supplier diversity supports your ESG score",
        "Measuring social impact: a practical guide for HR teams",
        "How CSR programmes improve employee engagement",
        "Building a community investment strategy that creates real value",
        "How to communicate ESG progress to employees authentically",
        "The link between ESG performance and talent attraction",
    ],
    "Inclusive Hiring and Retention": [
        "How to remove bias from your hiring process",
        "Writing job adverts that attract diverse candidates",
        "How to build an inclusive onboarding experience",
        "Why diverse employees leave and how to retain them",
        "Building a diverse leadership pipeline from within",
        "How to conduct fair and inclusive performance reviews",
        "Sponsorship vs mentorship: what underrepresented employees actually need",
        "How to make internal promotions more equitable",
        "Inclusive interviewing techniques every hiring manager needs",
        "How to build pay equity into your compensation strategy",
    ],
    "Workplace Culture and Belonging": [
        "How to build a workplace where everyone feels they belong",
        "The difference between diversity and belonging explained",
        "How to celebrate cultural diversity at work authentically",
        "Building ERGs that create real change not just community",
        "How to support LGBTQ+ employees beyond Pride Month",
        "Religious inclusion at work: a practical employer guide",
        "How to bridge generational divides in a diverse team",
        "Creating an inclusive remote and hybrid work culture",
        "How to handle microaggressions in the workplace",
        "Building a speak-up culture where employees feel genuinely safe",
    ],
}

# ── Pexels search queries ─────────────────────────────────────
IMAGE_QUERIES = [
    "diverse workplace team",
    "inclusive office environment",
    "workplace wellness meditation",
    "diverse business meeting",
    "employee wellbeing office",
    "multiracial team collaboration",
    "workplace inclusion diversity",
    "professional woman of colour office",
    "mindfulness at work",
    "diverse leadership team",
    "employee mental health support",
    "inclusive hiring interview",
    "workplace community culture",
    "diverse professionals working together",
    "employee engagement team",
    "Black professional workplace",
    "Asian professional office",
    "diverse employees smiling",
    "workplace flexibility remote work",
    "team building diverse group",
]


def fetch_and_upload_image(query, auth_header):
    PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
    if not PEXELS_API_KEY:
        print("⚠️ No Pexels API key found")
        return None

    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={
                "query": query,
                "per_page": 15,
                "orientation": "landscape",
                "size": "large",
            },
            timeout=30,
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            print(f"⚠️ No Pexels results for: {query}")
            return None

        photo = random.choice(photos)
        photo_id = photo["id"]
        photographer = photo["photographer"]

        dl = requests.get(
            f"https://api.pexels.com/v1/photos/{photo_id}",
            headers={"Authorization": PEXELS_API_KEY},
            timeout=30,
        )
        dl.raise_for_status()
        img_url = dl.json()["src"]["medium"]
        print(f"📸 Photo by {photographer} on Pexels: {img_url}")

        img = requests.get(img_url, timeout=30)
        if img.status_code != 200:
            print(f"⚠️ Image fetch failed: {img.status_code}")
            return None

        upload = requests.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            headers={
                **auth_header,
                "Content-Disposition": "attachment; filename=blog-image.jpg",
                "Content-Type": "image/jpeg",
            },
            data=img.content,
            timeout=60,
        )
        if upload.status_code in (200, 201):
            media_id = upload.json()["id"]
            print(f"✅ Image uploaded: ID {media_id}")
            return media_id

        print(f"⚠️ WordPress upload failed: {upload.status_code}")
        return None

    except Exception as e:
        print(f"⚠️ Image error: {e}")
        return None


def generate_post(topic, pillar):
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    prompt = f"""You are an expert content writer for EqualiShop — a platform dedicated to workplace equality, diversity, inclusion, employee wellbeing and corporate social responsibility.

Today's date is {current_date}. Always refer to {current_year} as the current year. Never reference any past year as the current year.

Write a complete, SEO-optimised blog post on this topic:
"{topic}"

This post is part of our content pillar: "{pillar}"

WRITING STYLE REQUIREMENTS:
- Write warmly and knowledgeably — like a trusted HR consultant or DEI expert talking to peers
- MIX sentence lengths deliberately: some short punchy ones, some longer ones
- Use contractions naturally (you're, it's, don't, we've)
- Start at least 2 paragraphs with something other than "The" or "If"
- Include at least ONE specific real-world example with a real company name
- Include at least ONE specific stat or data point with a source (CIPD, McKinsey, Deloitte, Harvard Business Review, ONS)
- NO AI giveaways: avoid "In today's landscape", "In conclusion", "It's worth noting", "Leverage", "Delve", "Comprehensive", "Robust"
- End naturally with a strong final paragraph and CTA
- Write for both UK and US audiences where relevant

CONTENT REQUIREMENTS:
- Word count: 950-1,150 words
- Structure: strong intro paragraph, 4-5 H2 sections, strong closing paragraph
- Naturally mention EqualiShop at least twice
- End with a CTA inviting readers to visit EqualiShop
- Add 1-2 external links to real credible sources

IMPORTANT: Respond ONLY with a valid JSON object. No markdown fences, no extra text.

Format:
{{"title": "SEO blog post title", "excerpt": "1-2 sentence meta description under 160 chars", "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"], "html_content": "Full blog post as clean HTML using h2, p, ul, li, strong, a tags only. No images. Escape all special characters properly."}}"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    response.raise_for_status()

    raw = response.json()["content"][0]["text"].strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error: {e}")
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def publish_post(post, pillar):
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    auth_header = {"Authorization": f"Basic {token}"}

    pillar_category_map = {
        "Workplace DEI Strategy":          "DEI",
        "Employee Wellbeing and Mental Health": "Workplace Wellness",
        "ESG and Corporate Responsibility": "ESG",
        "Inclusive Hiring and Retention":  "Hiring & Retention",
        "Workplace Culture and Belonging":  "Workplace Culture",
    }
    category = pillar_category_map.get(pillar, "Workplace Inclusion")

    query = random.choice(IMAGE_QUERIES)
    featured_media_id = fetch_and_upload_image(query, auth_header)

    payload = {
        "title":   post["title"],
        "content": post["html_content"],
        "excerpt": post.get("excerpt", ""),
        "status":  "publish",
        "meta":    {"blog_category": category},
    }

    if featured_media_id:
        payload["featured_media"] = featured_media_id

    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        headers={**auth_header, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    post_url = data.get("link", "")
    print(f"✅ Post published: {post_url}")
    return post_url


def main():
    pillar = random.choice(list(PILLARS.keys()))
    topic = random.choice(PILLARS[pillar])
    print(f"📌 Pillar: {pillar}")
    print(f"📝 Generating post: {topic}")

    post = generate_post(topic, pillar)
    print(f"✅ Generated: {post['title']}")

    url = publish_post(post, pillar)
    print(f"🚀 Live at: {url}")


if __name__ == "__main__":
    main()
