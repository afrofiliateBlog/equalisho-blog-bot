# EqualiShop Blog Bot 🤖

Automatically generates and publishes SEO-optimised blog posts every day — powered by Claude AI and GitHub Actions (free).

---

## How it works

1. GitHub Actions triggers the script every day at 7am UTC
2. On Monday, Wednesday and Friday an additional SEO pillar post is also generated
3. The script picks a topic from a curated pool covering DEI, ESG, CSR, workplace wellness and inclusion
4. Claude generates a full 950–1,150 word blog post in natural, human-sounding English
5. A relevant diverse workplace image is fetched from Pexels and uploaded automatically
6. The post is published to the site

> ⚠️ **Note:** EqualiShop is a custom PHP site. The current code uses placeholder WordPress API calls. When the EqualiShop blog endpoint is built (`/api/blog/create.php`), update the `publish_post` function in both `generate_post.py` and `seo.py`. All `TODO` comments mark the exact lines to update.

---

## Setup (one-time, ~10 minutes)

### Step 1 — Create the GitHub repo

1. Go to [github.com](https://github.com) and sign in
2. Create a new **private** repository called `equalisho-blog-bot`
3. Upload these files:
   - `generate_post.py`
   - `seo.py`
   - `.github/workflows/daily_blog.yml`

---

### Step 2 — Add GitHub Secrets

1. In your GitHub repo go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add these:

| Secret name         | Value                                          |
|---------------------|------------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Claude API key from console.anthropic.com |
| `WP_URL`            | EqualiShop URL e.g. https://www.equalisho.com  |
| `WP_USERNAME`       | Placeholder — update when endpoint is ready    |
| `WP_APP_PASSWORD`   | Placeholder — update when endpoint is ready    |
| `PEXELS_API_KEY`    | Your free Pexels API key from pexels.com/api   |

---

### Step 3 — Test it manually

1. Go to your repo → **Actions** tab
2. Click **EqualiShop Daily Blog Post Generator**
3. Click **Run workflow** → **Run workflow**
4. Watch the logs to confirm it runs successfully

---

## Topic coverage

**generate_post.py** covers general topics across:
- DEI (employer and employee perspectives)
- CSR
- ESG
- Workplace wellness and mindfulness
- Inclusion and culture

**seo.py** covers 5 SEO content pillars:
- Workplace DEI Strategy
- Employee Wellbeing and Mental Health
- ESG and Corporate Responsibility
- Inclusive Hiring and Retention
- Workplace Culture and Belonging

---

## Posting schedule

| Day            | What runs                        |
|----------------|----------------------------------|
| Monday         | Normal post + SEO pillar post    |
| Tuesday        | Normal post only                 |
| Wednesday      | Normal post + SEO pillar post    |
| Thursday       | Normal post only                 |
| Friday         | Normal post + SEO pillar post    |
| Saturday       | Normal post only                 |
| Sunday         | Normal post only                 |

Up to **10 posts per week** total.

---

## Customising topics

Open `generate_post.py` or `seo.py` and edit the `TOPICS` or `PILLARS` lists to add your own ideas.

---

## Changing the schedule

Edit `.github/workflows/daily_blog.yml` and change the cron expression:

```
'0 7 * * *'      → every day at 7am UTC
'0 9 * * 1'      → every Monday at 9am UTC
'0 8 * * 1,3,5'  → Mon/Wed/Fri at 8am UTC
```

Use [crontab.guru](https://crontab.guru) to build your own schedule.

---
