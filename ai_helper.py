import os
import json
import requests
from groq import Groq


# ── Key reader ────────────────────────────────────────────────────
def get_key(name):
    val = os.environ.get(name)
    if val:
        return val
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line.startswith(name) and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def _groq():
    return Groq(api_key=get_key("GROQ_API_KEY"))


# ── OCR ───────────────────────────────────────────────────────────
def extract_ingredients_from_image(image_path):
    try:
        api_key = get_key("OCR_API_KEY")
        with open(image_path, "rb") as f:
            img_data = f.read()

        resp = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("image.jpg", img_data, "image/jpeg")},
            data={
                "apikey"            : api_key,
                "language"          : "eng",
                "isOverlayRequired" : False,
                "detectOrientation" : True,
                "scale"             : True,
                "OCREngine"         : 2,
            },
            timeout=30,
        )
        result = resp.json()
        if result.get("IsErroredOnProcessing"):
            return None
        raw_text = result["ParsedResults"][0]["ParsedText"]

        clean = _groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role"   : "user",
                "content": (
                    "From this product label text, extract ONLY the ingredients list.\n"
                    "Return them as a comma-separated list. If none found, return: NOT_FOUND\n\n"
                    f"Label text:\n{raw_text}"
                ),
            }],
            max_tokens=500,
        )
        ingredients = clean.choices[0].message.content.strip()
        if "NOT_FOUND" in ingredients or len(ingredients) < 10:
            return None
        return ingredients
    except Exception as e:
        print(f"OCR error: {e}")
        return None


# ── AI report ─────────────────────────────────────────────────────
def generate_report(product_name, ingredient_results, profile, score):
    try:
        safe    = [r["ingredient"] for r in ingredient_results if r["status"] == "safe"]
        caution = [r["ingredient"] for r in ingredient_results if r["status"] == "caution"]
        avoid   = [r["ingredient"] for r in ingredient_results if r["status"] == "avoid"]

        cond_lines = []
        if profile.get("skin_condition"):
            cond_lines.append(f"Skin condition: {profile['skin_condition']}")
        if profile.get("hair_condition"):
            cond_lines.append(f"Hair condition: {profile['hair_condition']}")

        prompt = f"""You are a dermatologist and skincare expert. Write a personalised product analysis.

Product: {product_name}
User profile:
- Skin type: {profile.get('skin_type')} skin
- Hair type: {profile.get('hair_type')} hair
- Age: {profile.get('age_range')}
- Skin concerns: {', '.join(profile.get('skin_concerns', []) or ['none'])}
- Hair concerns: {', '.join(profile.get('hair_concerns', []) or ['none'])}
- Allergies: {profile.get('allergies') or 'none'}
{chr(10).join(cond_lines)}

Ingredient analysis:
- Safe: {', '.join(safe[:10])}
- Caution: {', '.join(caution[:5]) or 'none'}
- Avoid: {', '.join(avoid[:5]) or 'none'}
- Score: {score}/10

Write 4-5 sentences. Be specific to their exact profile. Address any specific skin or hair condition directly.
Be friendly. Address the user as 'you'."""

        resp = _groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Verdict generation failed: {e}"


# ── Reddit reviews ────────────────────────────────────────────────
def get_reddit_reviews(product_name):
    try:
        headers = {"User-Agent": "IngredientIQ/1.0 (skincare research app)"}
        subs    = "SkincareAddiction+IndianSkincareAddicts+AsianBeauty"
        url     = f"https://www.reddit.com/r/{subs}/search.json"
        params  = {"q": product_name, "sort": "top", "t": "year",
                   "limit": 10, "restrict_sr": True}
        resp    = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        posts   = resp.json().get("data", {}).get("children", [])
        reviews = []
        for post in posts[:5]:
            p = post["data"]
            if p.get("selftext") and len(p["selftext"]) > 50:
                reviews.append({
                    "title"       : p.get("title", ""),
                    "text"        : p.get("selftext", "")[:400],
                    "score"       : p.get("score", 0),
                    "subreddit"   : p.get("subreddit", ""),
                    "url"         : f"https://reddit.com{p.get('permalink','')}",
                    "num_comments": p.get("num_comments", 0),
                })
        return reviews
    except Exception as e:
        print(f"Reddit error: {e}")
        return []


# ── Recommended ingredients — separated by focus ──────────────────
def get_recommended_ingredients(profile, focus="skincare"):
    """
    focus: "skincare" | "haircare" | "both"
    Returns accurate recommendations without mixing skin/hair ingredients.
    """
    try:
        if focus == "skincare":
            focus_text = f"""Focus ONLY on SKINCARE ingredients.
- Skin type: {profile.get('skin_type')} skin
- Skin concerns: {', '.join(profile.get('skin_concerns', []) or ['none'])}
- Age: {profile.get('age_range')}
- Skin condition: {profile.get('skin_condition') or 'none'}
- Allergies to avoid: {profile.get('allergies') or 'none'}
DO NOT suggest hair care ingredients like coconut oil, castor oil, argan oil etc."""

        elif focus == "haircare":
            focus_text = f"""Focus ONLY on HAIRCARE ingredients.
- Hair type: {profile.get('hair_type')} hair
- Hair concerns: {', '.join(profile.get('hair_concerns', []) or ['none'])}
- Hair condition: {profile.get('hair_condition') or 'none'}
- Allergies to avoid: {profile.get('allergies') or 'none'}
DO NOT suggest skin care ingredients like retinol, niacinamide, AHAs etc."""

        else:  # both
            focus_text = f"""Focus on both SKINCARE and HAIRCARE ingredients.
- Skin type: {profile.get('skin_type')} skin
- Hair type: {profile.get('hair_type')} hair
- Skin concerns: {', '.join(profile.get('skin_concerns', []) or ['none'])}
- Hair concerns: {', '.join(profile.get('hair_concerns', []) or ['none'])}
- Allergies to avoid: {profile.get('allergies') or 'none'}"""

        prompt = f"""Based on this profile, list the TOP 5 most important ingredients to look for.

{focus_text}

Return ONLY a JSON array of 5 ingredient names:
["ingredient1", "ingredient2", "ingredient3", "ingredient4", "ingredient5"]

No explanation, just the JSON array."""

        resp = _groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        text  = resp.choices[0].message.content.strip()
        start = text.find("[")
        end   = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])[:5]

        # fallback
        if focus == "haircare":
            return ["biotin", "keratin", "zinc pyrithione", "panthenol", "argan oil"]
        return ["niacinamide", "hyaluronic acid", "glycerin", "ceramides", "vitamin c"]

    except Exception as e:
        print(f"Ingredient recommendation error: {e}")
        if focus == "haircare":
            return ["biotin", "keratin", "zinc pyrithione", "panthenol", "argan oil"]
        return ["niacinamide", "hyaluronic acid", "glycerin", "ceramides", "vitamin c"]


# ── SerpAPI shopping ──────────────────────────────────────────────
def search_products(query, budget, api_key):
    try:
        params = {
            "engine" : "google_shopping",
            "q"      : f"{query} under {budget}",
            "api_key": api_key,
            "gl"     : "in",
            "hl"     : "en",
            "num"    : 10,
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = resp.json()
        products = []
        for item in data.get("shopping_results", [])[:10]:
            # Make sure we always have a usable link
            link = item.get("link") or item.get("product_link") or ""
            products.append({
                "title"    : item.get("title", "Unknown Product"),
                "price"    : item.get("price", ""),
                "source"   : item.get("source", ""),
                "link"     : link,
                "thumbnail": item.get("thumbnail", ""),
                "rating"   : item.get("rating", ""),
            })
        return products
    except Exception as e:
        print(f"SerpAPI error: {e}")
        return []


# ── Groq product recommendations — ROBUST PARSER ─────────────────
def get_groq_product_recommendations(profile, budget, focus="skincare"):
    """
    Returns a list of dicts: [{name, ingredients, why, price}, ...]
    Uses JSON output so parsing is always reliable.
    """
    try:
        if focus == "skincare":
            focus_text = f"""SKINCARE products only.
Skin type: {profile.get('skin_type')} skin
Skin concerns: {', '.join(profile.get('skin_concerns', []) or ['none'])}
Skin condition: {profile.get('skin_condition') or 'none'}"""
        elif focus == "haircare":
            focus_text = f"""HAIRCARE products only.
Hair type: {profile.get('hair_type')} hair
Hair concerns: {', '.join(profile.get('hair_concerns', []) or ['none'])}
Hair condition: {profile.get('hair_condition') or 'none'}"""
        else:
            focus_text = f"""Both SKINCARE and HAIRCARE products.
Skin type: {profile.get('skin_type')} skin, Hair type: {profile.get('hair_type')} hair
Skin concerns: {', '.join(profile.get('skin_concerns', []) or ['none'])}
Hair concerns: {', '.join(profile.get('hair_concerns', []) or ['none'])}"""

        cond_lines = []
        if profile.get("skin_condition"):
            cond_lines.append(f"Skin condition: {profile['skin_condition']}")
        if profile.get("hair_condition"):
            cond_lines.append(f"Hair condition: {profile['hair_condition']}")

        prompt = f"""You are a skincare/haircare expert. Recommend exactly 5 specific products available in India.

{focus_text}
Age: {profile.get('age_range')}
Allergies to avoid: {profile.get('allergies') or 'none'}
{chr(10).join(cond_lines)}
Budget: Under ₹{budget}

Respond with ONLY a JSON array. No explanation, no markdown, just the array:
[
  {{
    "name": "Brand + Product Name",
    "ingredients": "2-3 key beneficial ingredients",
    "why": "One sentence why it suits this profile",
    "price": "₹approximate price"
  }}
]"""

        resp = _groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        text  = resp.choices[0].message.content.strip()
        # Strip any markdown code fences
        text  = text.replace("```json", "").replace("```", "").strip()
        start = text.find("[")
        end   = text.rfind("]") + 1
        if start >= 0 and end > start:
            picks = json.loads(text[start:end])
            return picks[:5]
        return []

    except Exception as e:
        print(f"AI picks error: {e}")
        return []


# ── Compare products AI verdict ───────────────────────────────────
def compare_products_ai(products_data, profile):
    try:
        products_text = ""
        for i, p in enumerate(products_data):
            products_text += f"""
Product {i+1}: {p['name']}
Score: {p['score']}/10
Safe: {', '.join(p['safe'][:5])}
Caution: {', '.join(p['caution'][:3]) or 'none'}
Avoid: {', '.join(p['avoid'][:3]) or 'none'}
"""
        cond_lines = []
        if profile.get("skin_condition"):
            cond_lines.append(f"Skin condition: {profile['skin_condition']}")
        if profile.get("hair_condition"):
            cond_lines.append(f"Hair condition: {profile['hair_condition']}")

        prompt = f"""Compare these skincare/haircare products for this specific user.

User: {profile.get('skin_type')} skin, {profile.get('hair_type')} hair
Skin concerns: {', '.join(profile.get('skin_concerns', []) or ['none'])}
Hair concerns: {', '.join(profile.get('hair_concerns', []) or ['none'])}
{chr(10).join(cond_lines)}

{products_text}

Write 3-4 sentences. State clearly which product is BEST and why. Be specific to their exact concerns."""

        resp = _groq().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Comparison failed: {e}"