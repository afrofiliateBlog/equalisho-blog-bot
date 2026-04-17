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

# ── topic pool ───────────────────────────────────────────────
TOPICS = [
    # DEI - Employer Side
    "How to build a genuinely inclusive workplace in 2026",
    "Why diversity hiring isn't enough — what comes after recruitment",
    "How to create a DEI strategy that actually works",
    "The business case for diversity: what the data says in 2026",
    "How to measure inclusion in your workplace",
    "Why psychological safety matters for diverse teams",
    "How to tackle unconscious bias in your hiring process",
    "Building an inclusive onboarding experience for new employees",
    "How to retain diverse talent once you've hired them",
    "What inclusive leadership actually looks like day to day",
    "How to run more inclusive meetings",
    "Pay equity audits: what they are and why every employer needs one",
    "How to support neurodivergent employees in the workplace",
    "Creating an accessible workplace for employees with disabilities",
    "How to build a diverse leadership pipeline",
    "Why your DEI training isn't working and what to do instead",
    "How to handle discrimination complaints properly as an employer",
    "Building ERGs that actually make a difference",
    "How to make your job adverts more inclusive",
    "What suppliers diversity means and why it matters for your ESG goals",

    # DEI - Employee Side
    "How to navigate being the only person of colour in your workplace",
    "What to do if you experience discrimination at work",
    "How to find your voice in an environment that doesn't always listen",
    "Imposter syndrome in diverse employees: how to overcome it",
    "How to advocate for yourself as a diverse employee",
    "Finding community and belonging in a non-inclusive workplace",
    "How to build allies at work as a minority employee",
    "Career progression tips for underrepresented employees",
    "How to raise DEI concerns with your manager",
    "Understanding your rights as an employee facing discrimination",

    # CSR
    "What is CSR and why it matters more than ever in 2026",
    "How small businesses can build a meaningful CSR strategy",
    "The link between CSR and employee retention",
    "How to report on your company's social impact",
    "Community investment strategies that actually make a difference",
    "How to align your CSR strategy with your brand values",
    "Supplier diversity as a CSR initiative: a practical guide",
    "How to engage employees in your CSR programmes",
    "Measuring the ROI of your CSR activities",
    "How CSR builds customer trust and brand loyalty",

    # ESG
    "ESG explained: what every business leader needs to know in 2026",
    "How to build an ESG framework for your organisation",
    "The S in ESG: why social responsibility is the hardest part",
    "How investors are using ESG scores to make decisions",
    "ESG reporting requirements UK businesses need to know",
    "How to improve your company's ESG score",
    "The link between ESG and long-term business performance",
    "How to align your DEI strategy with your ESG goals",
    "Green workplace initiatives that also boost employee wellbeing",
    "How to communicate your ESG progress to stakeholders",

    # Workplace Wellness & Mindfulness
    "How to build a workplace wellness programme that employees actually use",
    "Mental health at work: what employers are legally required to do",
    "How to support employees with anxiety and depression at work",
    "Mindfulness at work: practical tips for busy professionals",
    "How to reduce burnout in your team before it happens",
    "The link between employee wellbeing and business performance",
    "How to create a psychologically safe team environment",
    "Financial wellness programmes: why employers should care",
    "How to support employees going through difficult life events",
    "Building a culture of rest and recovery in a busy workplace",
    "How to make flexible working actually work for everyone",
    "The four day work week: what the evidence says",
    "How to spot signs of burnout in your team",
    "Menopause in the workplace: how employers can provide better support",
    "How to support parents and carers in the workplace",

    # Inclusion & Culture
    "How to celebrate cultural diversity in the workplace authentically",
    "Religious inclusion at work: a practical guide for employers",
    "How to support LGBTQ+ employees year round not just in June",
    "Age diversity in the workplace: bridging the generational gap",
    "How to create an inclusive culture for remote and hybrid teams",
    "The difference between diversity equity and inclusion explained simply",
    "How to build a speak-up culture where employees feel safe",
    "Inclusive communication: how to make everyone feel heard",
    "How to conduct an inclusion audit of your workplace",
    "Building a culture where difference is genuinely valued",
]

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


def generate_post(topic):
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    prompt = f"""You are an expert content writer for EqualiShop — a platform dedicated to workplace equality, diversity, inclusion, employee wellbeing and corporate social responsibility.

Today's date is {current_date}. Always refer to {current_year} as the current year. Never reference any past year as the current year.

Write a complete, SEO-optimised blog post on this topic:
"{topic}"

WRITING STYLE REQUIREMENTS:
- Write warmly and knowledgeably — like a trusted HR consultant or DEI expert talking to peers
- MIX sentence lengths deliberately: some short punchy ones, some longer ones that build an argument
- Use contractions naturally (you're, it's, don't, we've)
- Start at least 2 paragraphs with something other than "The" or "If"
- Include at least ONE specific real-world example with a real company name
- Include at least ONE specific stat or data point with a source (e.g. CIPD, McKinsey, Deloitte, ONS)
- NO AI giveaways: avoid "In today's landscape", "In conclusion", "It's worth noting", "Leverage", "Delve", "Comprehensive", "Robust"
- End naturally with a strong final paragraph and CTA
- Write for both UK and US audiences where relevant

CONTENT REQUIREMENTS:
- Word count: 950-1,150 words
- Structure: strong intro paragraph, 4-5 H2 sections, strong closing paragraph
- Naturally mention EqualiShop at least twice
- End with a CTA inviting readers to visit EqualiShop
- Add 1-2 external links to real credible sources (CIPD, McKinsey, Deloitte, Harvard Business Review, ONS, etc.)

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


def publish_post(post):
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    auth_header = {"Authorization": f"Basic {token}"}

    category_map = {
        "dei":        "DEI",
        "diversity":  "DEI",
        "inclusion":  "DEI",
        "csr":        "CSR",
        "esg":        "ESG",
        "wellness":   "Workplace Wellness",
        "wellbeing":  "Workplace Wellness",
        "mindful":    "Workplace Wellness",
        "mental":     "Workplace Wellness",
        "burnout":    "Workplace Wellness",
        "employee":   "Employee Experience",
        "employer":   "Employer Resources",
        "hiring":     "Employer Resources",
        "culture":    "Workplace Culture",
        "inclusive":  "DEI",
    }

    title_lower = post["title"].lower()
    category = "Workplace Inclusion"
    for keyword, cat_name in category_map.items():
        if keyword in title_lower:
            category = cat_name
            break

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
    topic = random.choice(TOPICS)
    print(f"📝 Generating post: {topic}")

    post = generate_post(topic)
    print(f"✅ Generated: {post['title']}")

    url = publish_post(post)
    print(f"🚀 Live at: {url}")


if __name__ == "__main__":
    main()
