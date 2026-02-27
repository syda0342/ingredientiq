AGE_PROFILES = {
    "Teens (13-19)": {
        "good" : ["salicylic acid", "niacinamide", "benzoyl peroxide", "zinc", "tea tree"],
        "bad"  : ["mineral oil", "coconut oil", "isopropyl myristate", "cocoa butter"],
        "focus": "oil control, acne prevention",
    },
    "20s": {
        "good" : ["vitamin c", "hyaluronic acid", "niacinamide", "glycolic acid", "retinol"],
        "bad"  : ["fragrance", "alcohol denat"],
        "focus": "prevention, hydration, early antioxidants",
    },
    "30s": {
        "good" : ["retinol", "vitamin c", "peptides", "glycolic acid", "hyaluronic acid", "niacinamide"],
        "bad"  : ["fragrance", "alcohol denat", "sodium lauryl sulfate"],
        "focus": "anti-aging begins, collagen support",
    },
    "40s": {
        "good" : ["retinol", "peptides", "ceramides", "hyaluronic acid", "vitamin c", "coenzyme q10"],
        "bad"  : ["fragrance", "alcohol denat", "sodium lauryl sulfate", "mineral oil"],
        "focus": "anti-aging, firming, deep hydration",
    },
    "50+": {
        "good" : ["ceramides", "peptides", "hyaluronic acid", "retinol", "squalane", "coenzyme q10"],
        "bad"  : ["fragrance", "alcohol denat", "sodium lauryl sulfate"],
        "focus": "barrier repair, intense hydration, anti-aging",
    },
}

SKIN_TYPE_MAP = {
    "oily": {
        "good": ["niacinamide", "salicylic acid", "glycolic acid", "zinc", "kaolin",
                 "bentonite", "hyaluronic acid", "glycerin", "retinol", "tea tree", "witch hazel"],
        "bad" : ["coconut oil", "mineral oil", "isopropyl myristate", "cocoa butter",
                 "lanolin", "petrolatum", "beeswax", "shea butter"],
    },
    "dry": {
        "good": ["ceramides", "hyaluronic acid", "glycerin", "squalane", "shea butter",
                 "petrolatum", "dimethicone", "panthenol", "aloe vera", "jojoba oil"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate", "benzoyl peroxide",
                 "salicylic acid", "witch hazel"],
    },
    "sensitive": {
        "good": ["aloe vera", "ceramides", "hyaluronic acid", "oat extract", "centella asiatica",
                 "panthenol", "allantoin", "glycerin", "niacinamide"],
        "bad" : ["fragrance", "alcohol denat", "essential oils", "retinol", "glycolic acid",
                 "benzoyl peroxide", "sodium lauryl sulfate", "witch hazel", "citrus extract"],
    },
    "combination": {
        "good": ["niacinamide", "hyaluronic acid", "glycerin", "salicylic acid",
                 "vitamin c", "centella asiatica", "panthenol"],
        "bad" : ["coconut oil", "mineral oil", "isopropyl myristate", "alcohol denat"],
    },
    "normal": {
        "good": ["hyaluronic acid", "niacinamide", "vitamin c", "glycerin",
                 "ceramides", "retinol", "peptides"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate"],
    },
}

SKIN_CONCERN_MAP = {
    "acne": {
        "good": ["salicylic acid", "benzoyl peroxide", "niacinamide", "zinc",
                 "tea tree", "retinol", "glycolic acid", "adapalene"],
        "bad" : ["coconut oil", "isopropyl myristate", "cocoa butter", "lanolin"],
    },
    "pigmentation": {
        "good": ["vitamin c", "niacinamide", "alpha arbutin", "kojic acid", "azelaic acid",
                 "tranexamic acid", "glycolic acid", "retinol"],
        "bad" : ["fragrance"],
    },
    "sensitivity": {
        "good": ["ceramides", "centella asiatica", "aloe vera", "oat extract", "allantoin", "panthenol"],
        "bad" : ["fragrance", "alcohol denat", "essential oils", "citrus extract", "menthol"],
    },
    "dryness": {
        "good": ["hyaluronic acid", "ceramides", "glycerin", "squalane", "panthenol", "shea butter"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate"],
    },
    "redness": {
        "good": ["centella asiatica", "aloe vera", "niacinamide", "allantoin", "green tea extract"],
        "bad" : ["fragrance", "alcohol denat", "menthol", "witch hazel"],
    },
    "oiliness": {
        "good": ["niacinamide", "salicylic acid", "zinc", "kaolin", "witch hazel"],
        "bad" : ["coconut oil", "mineral oil", "shea butter", "cocoa butter"],
    },
}

HAIR_CONCERN_MAP = {
    "hairfall": {
        "good": ["biotin", "caffeine", "niacinamide", "onion extract", "keratin",
                 "argan oil", "castor oil", "rosemary extract", "saw palmetto"],
        "bad" : ["sodium lauryl sulfate", "alcohol denat", "parabens", "mineral oil"],
    },
    "dandruff": {
        "good": ["zinc pyrithione", "selenium sulfide", "ketoconazole", "salicylic acid",
                 "tea tree", "piroctone olamine"],
        "bad" : ["heavy oils", "sodium lauryl sulfate"],
    },
    "dryness": {
        "good": ["argan oil", "coconut oil", "shea butter", "keratin", "panthenol", "glycerin"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate"],
    },
    "frizz": {
        "good": ["argan oil", "glycerin", "silicones", "keratin", "shea butter"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate"],
    },
    "scalp issues": {
        "good": ["salicylic acid", "zinc pyrithione", "tea tree", "niacinamide", "centella asiatica"],
        "bad" : ["fragrance", "alcohol denat", "sodium lauryl sulfate"],
    },
    "breakage": {
        "good": ["keratin", "protein", "biotin", "panthenol", "ceramides", "silk amino acids"],
        "bad" : ["alcohol denat", "bleach", "hydrogen peroxide"],
    },
}

HAIR_TYPE_MAP = {
    "oily": {
        "good": ["salicylic acid", "zinc pyrithione", "tea tree", "peppermint", "niacinamide"],
        "bad" : ["argan oil", "coconut oil", "castor oil", "shea butter"],
    },
    "dry": {
        "good": ["argan oil", "coconut oil", "shea butter", "keratin", "panthenol",
                 "glycerin", "aloe vera", "jojoba oil"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate"],
    },
    "damaged": {
        "good": ["keratin", "protein", "argan oil", "panthenol", "ceramides",
                 "biotin", "collagen", "silk amino acids"],
        "bad" : ["alcohol denat", "sodium lauryl sulfate", "hydrogen peroxide"],
    },
    "color-treated": {
        "good": ["keratin", "argan oil", "panthenol", "vitamin e", "silk proteins"],
        "bad" : ["sodium lauryl sulfate", "alcohol denat", "hydrogen peroxide", "ammonia"],
    },
    "normal": {
        "good": ["panthenol", "glycerin", "keratin", "argan oil"],
        "bad" : ["sodium lauryl sulfate", "alcohol denat"],
    },
}


def classify_ingredient(ingredient, profile):
    ing = ingredient.lower().strip()

    allergies     = [a.strip().lower() for a in profile.get("allergies", "").split(",") if a.strip()]
    age_range     = profile.get("age_range", "20s")
    skin_type     = profile.get("skin_type", "normal").lower()
    hair_type     = profile.get("hair_type", "normal").lower()
    skin_concerns = [c.lower() for c in profile.get("skin_concerns", [])]
    hair_concerns = [c.lower() for c in profile.get("hair_concerns", [])]

    # 1. Allergens first
    for allergen in allergies:
        if allergen and allergen in ing:
            return "avoid", f"You listed '{allergen}' as an allergen"

    # 2. Age profile
    ap = AGE_PROFILES.get(age_range, AGE_PROFILES["20s"])
    for g in ap["good"]:
        if g in ing:
            return "safe", f"Beneficial for {age_range} — {ap['focus']}"
    for b in ap["bad"]:
        if b in ing:
            return "caution", f"Less ideal for {age_range} — {ap['focus']}"

    # 3. Skin concerns
    for concern in skin_concerns:
        if concern in SKIN_CONCERN_MAP:
            for g in SKIN_CONCERN_MAP[concern]["good"]:
                if g in ing:
                    return "safe", f"Beneficial for {concern}"
            for b in SKIN_CONCERN_MAP[concern]["bad"]:
                if b in ing:
                    return "avoid", f"Can worsen {concern}"

    # 4. Hair concerns
    for concern in hair_concerns:
        if concern in HAIR_CONCERN_MAP:
            for g in HAIR_CONCERN_MAP[concern]["good"]:
                if g in ing:
                    return "safe", f"Beneficial for {concern}"
            for b in HAIR_CONCERN_MAP[concern]["bad"]:
                if b in ing:
                    return "avoid", f"Can worsen {concern}"

    # 5. Skin type
    if skin_type in SKIN_TYPE_MAP:
        for g in SKIN_TYPE_MAP[skin_type]["good"]:
            if g in ing:
                return "safe", f"Beneficial for {skin_type} skin"
        for b in SKIN_TYPE_MAP[skin_type]["bad"]:
            if b in ing:
                return "caution", f"May not suit {skin_type} skin"

    # 6. Hair type
    if hair_type in HAIR_TYPE_MAP:
        for g in HAIR_TYPE_MAP[hair_type]["good"]:
            if g in ing:
                return "safe", f"Beneficial for {hair_type} hair"
        for b in HAIR_TYPE_MAP[hair_type]["bad"]:
            if b in ing:
                return "caution", f"May not suit {hair_type} hair"

    return "safe", "Generally considered safe"


def analyze_ingredients(ingredient_list, profile):
    results = []
    for ingredient in ingredient_list:
        if ingredient.strip():
            status, reason = classify_ingredient(ingredient, profile)
            results.append({"ingredient": ingredient.strip(), "status": status, "reason": reason})
    return results


def calculate_score(results):
    if not results:
        return 0.0
    total   = len(results)
    safe    = sum(1 for r in results if r["status"] == "safe")
    caution = sum(1 for r in results if r["status"] == "caution")
    score   = ((safe * 1.0) + (caution * 0.5)) / total * 10
    return round(score, 1)