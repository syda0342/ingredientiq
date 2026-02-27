import streamlit as st
from PIL import Image
import tempfile
import os

from database import (
    init_db, save_profile, load_profile,
    save_analysis, load_history,
    save_comparison, load_compare_history,
    save_product_bookmark, load_saved_products, delete_saved_product,
)
from ml_model import analyze_ingredients, calculate_score
from ai_helper import (
    extract_ingredients_from_image, generate_report,
    get_reddit_reviews, get_recommended_ingredients,
    search_products, get_groq_product_recommendations,
    compare_products_ai, get_key,
)

# ── Init ──────────────────────────────────────────────────────────
init_db()

st.set_page_config(page_title="IngredientIQ", page_icon="🧴", layout="wide")

st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Cards ── */
.ing-safe    {background:linear-gradient(135deg,#0d2818,#1a3a2a);border-left:4px solid #22c55e;
              padding:10px 14px;border-radius:8px;margin:5px 0;transition:transform .15s;}
.ing-safe:hover {transform:translateX(3px);}
.ing-caution {background:linear-gradient(135deg,#2a2000,#3a3000);border-left:4px solid #f59e0b;
              padding:10px 14px;border-radius:8px;margin:5px 0;transition:transform .15s;}
.ing-caution:hover {transform:translateX(3px);}
.ing-avoid   {background:linear-gradient(135deg,#2a0d0d,#3a1a1a);border-left:4px solid #ef4444;
              padding:10px 14px;border-radius:8px;margin:5px 0;transition:transform .15s;}
.ing-avoid:hover {transform:translateX(3px);}

/* ── Reddit ── */
.rcrd {background:#1a1207;border:1px solid #ff4500;border-left:4px solid #ff4500;
       padding:14px;border-radius:8px;margin:8px 0;}

/* ── AI product card ── */
.pcard {background:linear-gradient(135deg,#0f172a,#1e293b);
        border:1px solid #334155;border-radius:12px;
        padding:16px;margin-bottom:14px;
        transition:transform .2s,box-shadow .2s;}
.pcard:hover {transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,0,0,.4);}

/* ── Shop card ── */
.shopcard {background:#0f172a;border:1px solid #1e3a5f;
           border-radius:10px;padding:12px;margin-bottom:10px;}

/* ── Profile tag pill ── */
.ptag {display:inline-block;background:rgba(34,197,94,.12);
       border:1px solid rgba(34,197,94,.4);
       padding:4px 12px;border-radius:20px;
       font-size:0.8rem;margin:3px;color:#86efac;font-weight:500;}

/* ── Score badge ── */
.score-box {text-align:center;padding:24px;
            background:linear-gradient(135deg,#0f172a,#1e293b);
            border-radius:16px;border:1px solid #334155;}

/* ── Section header accent ── */
.section-pill {display:inline-block;background:linear-gradient(90deg,#22c55e,#16a34a);
               color:white;padding:4px 14px;border-radius:20px;
               font-size:0.78rem;font-weight:700;letter-spacing:.5px;margin-bottom:8px;}

/* ── Buy button ── */
.buy-btn {display:inline-block;background:linear-gradient(135deg,#16a34a,#15803d);
          color:white!important;padding:6px 16px;border-radius:8px;
          text-decoration:none!important;font-weight:600;font-size:0.85rem;
          margin-top:6px;transition:opacity .2s;}
.buy-btn:hover {opacity:.85;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0a0f1e,#0d1b2a)!important;}
[data-testid="stSidebar"] .stRadio label {color:#cbd5e1!important;}

/* ── Metric cards ── */
.metric-card {background:#0f172a;border:1px solid #1e293b;border-radius:10px;
              padding:14px;text-align:center;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
        <div style='font-size:2.5rem;'>🧴</div>
        <h2 style='color:#22c55e;margin:4px 0;font-weight:700;'>IngredientIQ</h2>
        <p style='color:#64748b;font-size:0.78rem;margin:0;'>AI-Powered Skincare Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigation", [
        "👤 My Profile",
        "🔍 Analyze Product",
        "🛍️ Find Products",
        "⚖️ Compare Products",
        "🔖 Saved Products",
        "📚 My History",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
    <div style='color:#475569;font-size:0.72rem;text-align:center;padding:4px;'>
        Powered by Groq · OCR.space · SerpAPI<br>
        <span style='color:#22c55e;'>●</span> Live
    </div>""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────
def profile_tags(profile):
    tags = [f"🧴 {profile['skin_type']} skin", f"💇 {profile['hair_type']} hair",
            f"🎂 {profile['age_range']}"]
    if profile.get("skin_concerns"):
        tags.append("⚠️ Skin: " + ", ".join(profile["skin_concerns"]))
    if profile.get("hair_concerns"):
        tags.append("💆 Hair: " + ", ".join(profile["hair_concerns"]))
    if profile.get("allergies"):
        tags.append("🚫 " + profile["allergies"][:28])
    if profile.get("skin_condition"):
        tags.append("🔬 " + profile["skin_condition"][:30])
    if profile.get("hair_condition"):
        tags.append("🔬 " + profile["hair_condition"][:30])
    return " ".join(f"<span class='ptag'>{t}</span>" for t in tags)

def safe_idx(lst, val):
    return lst.index(val) if val in lst else 0

def store_color(store):
    s = store.lower()
    if "nykaa"    in s: return "#FF3F6C"
    if "amazon"   in s: return "#FF9900"
    if "flipkart" in s: return "#2874F0"
    if "myntra"   in s: return "#FF3F6C"
    if "meesho"   in s: return "#9c27b0"
    return "#94a3b8"

def save_image_as_jpeg(img):
    """Convert any PIL image (including RGBA/PNG) to JPEG-safe RGB and save to temp file."""
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    tmp = tempfile.mktemp(suffix=".jpg")
    img.save(tmp, format="JPEG", quality=90)
    return tmp

def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style='padding:10px 0 20px;'>
        <h1 style='font-size:2rem;font-weight:700;margin:0;'>
            {icon} {title}
        </h1>
        {'<p style="color:#64748b;margin:4px 0 0;font-size:0.9rem;">'+subtitle+'</p>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 1 – MY PROFILE
# ══════════════════════════════════════════════════════════════════
if page == "👤 My Profile":
    page_header("👤", "My Profile", "The more detail you provide, the more personalised your analysis.")

    ex = load_profile()

    with st.form("profile_form"):
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("<div class='section-pill'>SKIN & HAIR</div>", unsafe_allow_html=True)
            skin_opts = ["Oily", "Dry", "Combination", "Sensitive", "Normal"]
            skin_type = st.selectbox("Skin Type", skin_opts,
                index=safe_idx(skin_opts, (ex or {}).get("skin_type", "Oily").capitalize()))

            hair_opts = ["Oily", "Dry", "Damaged", "Color-treated", "Normal"]
            hair_type = st.selectbox("Hair Type", hair_opts,
                index=safe_idx(hair_opts, (ex or {}).get("hair_type", "Normal").capitalize()))

            age_opts  = ["Teens (13-19)", "20s", "30s", "40s", "50+"]
            age_range = st.selectbox("Age Range", age_opts,
                index=safe_idx(age_opts, (ex or {}).get("age_range", "20s")))

            age_focus = {"Teens (13-19)":"oil control · acne prevention",
                         "20s":"hydration · early prevention",
                         "30s":"antioxidants · early anti-aging",
                         "40s":"firming · collagen support",
                         "50+":"barrier repair · intense hydration"}
            st.caption(f"✨ Focus: {age_focus.get(age_range,'')}")

            budget = st.slider("Budget (₹)", 100, 5000,
                int((ex or {}).get("budget", 1000)), 100)

        with col2:
            st.markdown("<div class='section-pill'>CONCERNS & CONDITIONS</div>", unsafe_allow_html=True)
            valid_sc = ["Acne","Sensitivity","Pigmentation","Dryness","Redness","Oiliness"]
            valid_hc = ["Hairfall","Dandruff","Dryness","Frizz","Scalp Issues","Breakage"]

            skin_concerns = st.multiselect("Skin Concerns", valid_sc,
                default=[x for x in (ex or {}).get("skin_concerns",[]) if x in valid_sc])

            hair_concerns = st.multiselect("Hair Concerns", valid_hc,
                default=[x for x in (ex or {}).get("hair_concerns",[]) if x in valid_hc])

            allergies = st.text_area("Allergies / Ingredients to Avoid",
                value=(ex or {}).get("allergies",""),
                placeholder="e.g. fragrance, parabens, sulfates", height=68)

            skin_condition = st.text_area("Specific Skin Condition",
                value=(ex or {}).get("skin_condition",""),
                placeholder="e.g. Rosacea, Eczema, Keratosis Pilaris…", height=62)

            hair_condition = st.text_area("Specific Hair / Scalp Condition",
                value=(ex or {}).get("hair_condition",""),
                placeholder="e.g. Scalp Psoriasis, Seborrheic Dermatitis…", height=62)

        submitted = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)

    if submitted:
        save_profile(skin_type, hair_type, age_range,
                     skin_concerns, hair_concerns,
                     allergies, skin_condition, hair_condition, budget)
        for k in ["fp_recommended","fp_ai_picks","fp_products","fp_focus","fp_budget"]:
            st.session_state.pop(k, None)
        st.success("✅ Profile saved! Head to Analyze Product to get started.")
        st.rerun()

    # Preview
    if ex:
        st.markdown("---")
        st.markdown("**Your current profile:**")
        st.markdown(profile_tags(ex), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 2 – ANALYZE PRODUCT
# ══════════════════════════════════════════════════════════════════
elif page == "🔍 Analyze Product":
    page_header("🔍", "Analyze Product", "Scan any skincare or haircare product against your profile.")

    profile = load_profile()
    if not profile:
        st.warning("⚠️ Please complete your profile first.")
        st.stop()

    st.markdown(profile_tags(profile), unsafe_allow_html=True)
    st.markdown("")

    with st.container():
        product_name = st.text_input("Product Name",
            placeholder="e.g. Cetaphil Moisturizing Cream",
            help="Enter the exact product name for Reddit reviews")

        method = st.radio("How do you want to enter ingredients?",
                          ["📝 Type / Paste", "📷 Upload label photo"], horizontal=True)

    if "ingredients_text" not in st.session_state:
        st.session_state.ingredients_text = ""

    if method == "📝 Type / Paste":
        st.session_state.ingredients_text = st.text_area(
            "Paste ingredient list",
            value=st.session_state.ingredients_text, height=150,
            placeholder="Aqua, Glycerin, Niacinamide, Fragrance, Cetearyl Alcohol…",
            help="Copy the full ingredient list from the product packaging or website")
    else:
        up = st.file_uploader("Upload product label photo", type=["jpg","jpeg","png","webp"])
        if up:
            img = Image.open(up)
            col_img, col_btn = st.columns([1,2])
            with col_img:
                st.image(img, caption="Uploaded label", use_container_width=True)
            with col_btn:
                st.markdown("**Photo uploaded ✅**")
                st.caption("Click below to extract ingredients using OCR")
                if st.button("🔍 Extract Ingredients", type="primary"):
                    with st.spinner("Reading label with AI OCR…"):
                        tmp = save_image_as_jpeg(img)   # ← RGBA fix
                        ext = extract_ingredients_from_image(tmp)
                        try: os.unlink(tmp)
                        except: pass
                    if ext:
                        st.session_state.ingredients_text = ext
                        st.success("✅ Ingredients extracted!")
                    else:
                        st.warning("Couldn't read clearly — paste manually below.")

        st.session_state.ingredients_text = st.text_area(
            "Extracted / Edited ingredients:",
            value=st.session_state.ingredients_text, height=120)

    st.markdown("")
    analyze_btn = st.button("🧪 Analyze Ingredients", type="primary", use_container_width=True)

    if analyze_btn:
        raw = st.session_state.ingredients_text.strip()
        if not raw:
            st.error("No ingredients to analyse.")
            st.stop()

        ing_list = [i.strip() for i in raw.replace("\n",",").split(",") if i.strip()]

        with st.spinner("🔬 Analysing your ingredients…"):
            results = analyze_ingredients(ing_list, profile)
            score   = calculate_score(results)
            report  = generate_report(product_name or "This product", results, profile, score)

        save_analysis(product_name or "Unknown", raw, report, score)

        # ── Score banner ──
        st.markdown("---")
        color   = "#22c55e" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
        bg      = "#0d2818" if score >= 7 else "#2a2000" if score >= 5 else "#2a0d0d"
        verdict = ("Great match for you! 🎉" if score >= 7
                   else "Use with caution ⚠️" if score >= 5
                   else "Not recommended for you ❌")

        _, mid, _ = st.columns([1,2,1])
        with mid:
            st.markdown(f"""<div class='score-box' style='border-color:{color}40;background:{bg};'>
                <div style='color:#94a3b8;font-size:0.82rem;font-weight:600;letter-spacing:1px;
                            text-transform:uppercase;margin-bottom:8px;'>Compatibility Score</div>
                <div style='color:{color};font-size:4rem;font-weight:700;line-height:1;'>{score}</div>
                <div style='color:#475569;font-size:1.2rem;margin:2px 0;'>out of 10</div>
                <div style='color:{color};font-weight:600;font-size:1rem;margin-top:8px;'>{verdict}</div>
                <div style='color:#475569;font-size:0.78rem;margin-top:4px;'>
                    Based on your full skin & hair profile</div>
            </div>""", unsafe_allow_html=True)

        # ── Summary metrics ──
        safe_l    = [r for r in results if r["status"] == "safe"]
        caution_l = [r for r in results if r["status"] == "caution"]
        avoid_l   = [r for r in results if r["status"] == "avoid"]

        st.markdown("")
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val, c in [
            (m1, "Total Ingredients", len(results), "#94a3b8"),
            (m2, "✅ Safe", len(safe_l), "#22c55e"),
            (m3, "⚠️ Caution", len(caution_l), "#f59e0b"),
            (m4, "❌ Avoid", len(avoid_l), "#ef4444"),
        ]:
            with col:
                st.markdown(f"""<div class='metric-card'>
                    <div style='font-size:1.8rem;font-weight:700;color:{c};'>{val}</div>
                    <div style='color:#64748b;font-size:0.78rem;'>{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["📋 Ingredient Breakdown", "💬 Your Verdict", "🗣️ What Users Say"])

        with tab1:
            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                st.markdown(f"### ✅ Safe ({len(safe_l)})")
                for r in safe_l:
                    st.markdown(f"<div class='ing-safe'>"
                                f"<b style='color:#86efac;'>{r['ingredient']}</b>"
                                f"<br><small style='color:#6ee7b7;opacity:.8;'>{r['reason']}</small>"
                                f"</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"### ⚠️ Caution ({len(caution_l)})")
                for r in caution_l:
                    st.markdown(f"<div class='ing-caution'>"
                                f"<b style='color:#fcd34d;'>{r['ingredient']}</b>"
                                f"<br><small style='color:#fde68a;opacity:.8;'>{r['reason']}</small>"
                                f"</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"### ❌ Avoid ({len(avoid_l)})")
                for r in avoid_l:
                    st.markdown(f"<div class='ing-avoid'>"
                                f"<b style='color:#fca5a5;'>{r['ingredient']}</b>"
                                f"<br><small style='color:#fecaca;opacity:.8;'>{r['reason']}</small>"
                                f"</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown(f"""<div style='background:linear-gradient(135deg,#0f172a,#1e293b);
                border:1px solid #334155;border-radius:12px;padding:20px;
                color:#cbd5e1;line-height:1.7;font-size:0.95rem;'>
                💬 {report}
            </div>""", unsafe_allow_html=True)
            notes = []
            if profile.get("skin_condition"):  notes.append(profile["skin_condition"])
            if profile.get("hair_condition"):  notes.append(profile["hair_condition"])
            if notes:
                st.caption("🔬 Factored in: " + " & ".join(notes))

        with tab3:
            if product_name:
                with st.spinner("🔍 Searching Reddit communities…"):
                    reviews = get_reddit_reviews(product_name)
                if reviews:
                    st.markdown(f"**Found {len(reviews)} discussions from Reddit skincare communities:**")
                    for r in reviews:
                        st.markdown(f"""<div class='rcrd'>
                            <div style='font-weight:600;color:#ff6534;margin-bottom:4px;'>{r['title'][:80]}</div>
                            <div style='color:#475569;font-size:0.78rem;margin-bottom:8px;'>
                                📍 r/{r['subreddit']} &nbsp;·&nbsp; ⬆️ {r['score']} upvotes
                                &nbsp;·&nbsp; 💬 {r['num_comments']} comments
                            </div>
                            <div style='color:#94a3b8;font-size:0.88rem;'>{r['text'][:300]}…</div>
                            <a href='{r["url"]}' target='_blank'
                               style='color:#ff4500;font-size:0.82rem;font-weight:600;'>
                               Read full post →
                            </a>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No Reddit reviews found for this specific product.")
            else:
                st.info("💡 Enter a product name above to fetch real Reddit reviews.")

        st.success("✅ Analysis saved to history!")


# ══════════════════════════════════════════════════════════════════
# PAGE 3 – FIND PRODUCTS
# ══════════════════════════════════════════════════════════════════
elif page == "🛍️ Find Products":
    page_header("🛍️", "Find Products For You", "Get AI-curated recommendations matched to your exact profile.")

    profile = load_profile()
    if not profile:
        st.warning("⚠️ Please complete your profile first.")
        st.stop()

    st.markdown(profile_tags(profile), unsafe_allow_html=True)
    st.markdown("---")

    col_a, col_b = st.columns([1,2], gap="large")
    with col_a:
        budget = st.slider("💰 Budget (₹)", 100, 5000, int(profile.get("budget",1000)), 100)
    with col_b:
        search_focus = st.radio("Search focus:",
            ["Skincare products","Haircare products","Both"], horizontal=True)

    focus_key = {"Skincare products":"skincare","Haircare products":"haircare","Both":"both"}
    fk = focus_key[search_focus]

    if st.button("🔍 Find Products For Me", type="primary", use_container_width=True):
        st.session_state.fp_focus  = fk
        st.session_state.fp_budget = budget
        with st.spinner("🧬 Analysing your profile for best ingredients…"):
            st.session_state.fp_recommended = get_recommended_ingredients(profile, focus=fk)
        with st.spinner("🤖 Generating personalised picks…"):
            st.session_state.fp_ai_picks = get_groq_product_recommendations(profile, budget, focus=fk)
        serp_key = get_key("SERP_API_KEY")
        if serp_key:
            sc_str = " ".join(profile.get("skin_concerns",[])[:2])
            hc_str = " ".join(profile.get("hair_concerns",[])[:2])
            if fk == "skincare":
                q = (f"{profile['skin_condition']} skincare India" if profile.get("skin_condition")
                     else f"{profile['skin_type']} skin {sc_str} moisturizer serum India")
            elif fk == "haircare":
                q = (f"{profile['hair_condition']} hair care India" if profile.get("hair_condition")
                     else f"{profile['hair_type']} hair {hc_str} shampoo conditioner India")
            else:
                q = f"{profile['skin_type']} skin {profile['hair_type']} hair {sc_str} India"
            with st.spinner("🛒 Fetching live products from Google Shopping…"):
                st.session_state.fp_products = search_products(q, budget, serp_key)
        else:
            st.session_state.fp_products = []

    if "fp_recommended" in st.session_state:
        col1, col2 = st.columns(2, gap="large")
        flabel = {"skincare":"Skincare","haircare":"Haircare","both":"Skincare & Haircare"}
        with col1:
            st.markdown(f"<div class='section-pill'>BEST {flabel.get(st.session_state.fp_focus,'').upper()} INGREDIENTS</div>",
                        unsafe_allow_html=True)
            for i, ing in enumerate(st.session_state.fp_recommended, 1):
                st.markdown(f"""<div style='background:#0f172a;border:1px solid #1e3a5f;
                    border-radius:8px;padding:8px 14px;margin:5px 0;'>
                    <span style='color:#22c55e;font-weight:700;'>{i}.</span>
                    <span style='color:#e2e8f0;'> {ing}</span>
                </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='section-pill'>YOUR PROFILE</div>", unsafe_allow_html=True)
            items = [
                ("Skin", f"{profile['skin_type']} · {', '.join(profile.get('skin_concerns') or ['no concerns'])}"),
                ("Hair", f"{profile['hair_type']} · {', '.join(profile.get('hair_concerns') or ['no concerns'])}"),
                ("Age", profile['age_range']),
                ("Budget", f"₹{st.session_state.get('fp_budget', budget)}"),
            ]
            if profile.get("skin_condition"):  items.append(("Skin Condition", profile["skin_condition"]))
            if profile.get("hair_condition"):  items.append(("Hair Condition", profile["hair_condition"]))
            for k, v in items:
                st.markdown(f"""<div style='display:flex;justify-content:space-between;
                    background:#0f172a;border-radius:6px;padding:7px 12px;margin:4px 0;'>
                    <span style='color:#64748b;font-size:0.85rem;'>{k}</span>
                    <span style='color:#e2e8f0;font-size:0.85rem;font-weight:500;'>{v}</span>
                </div>""", unsafe_allow_html=True)

        # AI Picks
        st.markdown("---")
        st.markdown("<div class='section-pill'>🤖 PERSONALISED AI PICKS</div>", unsafe_allow_html=True)
        st.caption(f"Curated for your profile · Under ₹{st.session_state.get('fp_budget', budget)}")
        st.markdown("")

        picks = st.session_state.get("fp_ai_picks", [])
        if picks:
            pcols = st.columns(3, gap="medium")
            for i, p in enumerate(picks):
                with pcols[i % 3]:
                    st.markdown(f"""<div class='pcard'>
                        <div style='font-weight:700;color:#f1f5f9;font-size:0.95rem;
                                    margin-bottom:10px;line-height:1.3;'>
                            🧴 {p.get("name","")}
                        </div>
                        <div style='background:#1e293b;border-radius:6px;padding:8px;margin-bottom:8px;'>
                            <div style='color:#64748b;font-size:0.72rem;font-weight:600;
                                        letter-spacing:.5px;margin-bottom:3px;'>KEY INGREDIENTS</div>
                            <div style='color:#7dd3fc;font-size:0.83rem;'>{p.get("ingredients","")}</div>
                        </div>
                        <div style='color:#94a3b8;font-size:0.83rem;margin-bottom:10px;
                                    line-height:1.4;'>{p.get("why","")}</div>
                        <div style='color:#22c55e;font-weight:700;font-size:1rem;'>
                            💰 {p.get("price","")}
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("No picks generated. Try clicking Find Products For Me again.")

        # Live Shopping
        products = st.session_state.get("fp_products", [])
        if products:
            st.markdown("---")
            st.markdown("<div class='section-pill'>🛒 LIVE SHOPPING RESULTS</div>", unsafe_allow_html=True)
            st.caption(f"{len(products)} products found from Nykaa · Amazon · Flipkart · More")
            st.markdown("")

            shop_cols = st.columns(3, gap="medium")
            for i, p in enumerate(products):
                with shop_cols[i % 3]:
                    st.markdown("<div class='shopcard'>", unsafe_allow_html=True)
                    if p.get("thumbnail"):
                        try: st.image(p["thumbnail"], width=150)
                        except: pass
                    title = p["title"][:55] + "…" if len(p["title"]) > 55 else p["title"]
                    st.markdown(f"<div style='font-weight:600;color:#e2e8f0;font-size:0.88rem;"
                                f"margin:6px 0;line-height:1.3;'>{title}</div>",
                                unsafe_allow_html=True)
                    info_parts = []
                    if p.get("price"):
                        info_parts.append(f"<span style='color:#22c55e;font-weight:700;font-size:1rem;'>"
                                          f"💰 {p['price']}</span>")
                    if p.get("rating"):
                        info_parts.append(f"<span style='color:#fbbf24;'>⭐ {p['rating']}</span>")
                    if info_parts:
                        st.markdown(" &nbsp; ".join(info_parts), unsafe_allow_html=True)
                    if p.get("source"):
                        c = store_color(p["source"])
                        st.markdown(f"<span style='color:{c};font-weight:600;font-size:0.82rem;'>"
                                    f"🏪 {p['source']}</span>", unsafe_allow_html=True)
                    if p.get("link"):
                        st.markdown(f"<a href='{p['link']}' target='_blank' class='buy-btn'>"
                                    f"🛒 View & Buy →</a>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("")
                    if st.button("🔖 Save", key=f"sv_{i}_{p.get('title','')[:8]}"):
                        save_product_bookmark(p.get("title",""), p.get("price",""),
                                              p.get("source",""), p.get("link",""),
                                              p.get("thumbnail",""))
                        st.toast("✅ Bookmarked!")
                    st.markdown("---")
        elif "fp_products" in st.session_state:
            st.info("💡 Add `SERP_API_KEY` to `.env` for live shopping results. Free at serpapi.com")


# ══════════════════════════════════════════════════════════════════
# PAGE 4 – COMPARE PRODUCTS
# ══════════════════════════════════════════════════════════════════
elif page == "⚖️ Compare Products":
    page_header("⚖️", "Compare Products", "Side-by-side analysis of 2–3 products against your profile.")

    profile = load_profile()
    if not profile:
        st.warning("⚠️ Please complete your profile first.")
        st.stop()

    if "cmp" not in st.session_state:
        st.session_state.cmp = [{"name":"","ingredients":""},{"name":"","ingredients":""}]

    # Load from history
    history = load_history()
    if history:
        with st.expander("📂 Load from analysis history"):
            hlabels = ["— select —"] + [f"{r[1]}  ({r[5]})" for r in history]
            sel  = st.selectbox("Select product", hlabels, key="hsel")
            slot = st.radio("Load into:", ["Product 1","Product 2","Product 3"], horizontal=True)
            if st.button("Load →") and sel != "— select —":
                idx = hlabels.index(sel) - 1
                si  = int(slot.split()[1]) - 1
                while len(st.session_state.cmp) <= si:
                    st.session_state.cmp.append({"name":"","ingredients":""})
                st.session_state.cmp[si]["name"]        = history[idx][1]
                st.session_state.cmp[si]["ingredients"] = history[idx][2]
                st.rerun()

    bc1, bc2 = st.columns([1,5])
    with bc1:
        if len(st.session_state.cmp) < 3:
            if st.button("➕ Add 3rd product"):
                st.session_state.cmp.append({"name":"","ingredients":""})
                st.rerun()
    with bc2:
        if len(st.session_state.cmp) > 2:
            if st.button("➖ Remove last"):
                st.session_state.cmp.pop()
                st.rerun()

    st.markdown("")
    cols = st.columns(len(st.session_state.cmp), gap="medium")
    for i, col in enumerate(cols):
        with col:
            colors = ["#3b82f6","#a855f7","#f59e0b"]
            st.markdown(f"""<div style='background:{colors[i]}20;border:1px solid {colors[i]}40;
                border-radius:10px;padding:6px 14px;margin-bottom:12px;'>
                <b style='color:{colors[i]};'>Product {i+1}</b>
            </div>""", unsafe_allow_html=True)
            name = st.text_input("Name", value=st.session_state.cmp[i]["name"],
                key=f"cn_{i}", placeholder="e.g. Cetaphil Cream")
            ings = st.text_area("Ingredients",
                value=st.session_state.cmp[i]["ingredients"],
                key=f"cing_{i}", height=160,
                placeholder="Paste full ingredient list…")
            st.session_state.cmp[i]["name"]        = name
            st.session_state.cmp[i]["ingredients"] = ings

    st.markdown("")
    if st.button("⚖️ Compare Now", type="primary", use_container_width=True):
        valid = [p for p in st.session_state.cmp
                 if p["name"].strip() and p["ingredients"].strip()]
        if len(valid) < 2:
            st.error("Enter at least 2 products with ingredients.")
            st.stop()

        pdata = []
        with st.spinner("🔬 Analysing all products…"):
            for p in valid:
                il  = [x.strip() for x in p["ingredients"].replace("\n",",").split(",") if x.strip()]
                res = analyze_ingredients(il, profile)
                sc  = calculate_score(res)
                pdata.append({"name":p["name"],"score":sc,
                    "safe"   :[r["ingredient"] for r in res if r["status"]=="safe"],
                    "caution":[r["ingredient"] for r in res if r["status"]=="caution"],
                    "avoid"  :[r["ingredient"] for r in res if r["status"]=="avoid"]})

        # Score cards
        st.markdown("---")
        sc_cols = st.columns(len(valid), gap="medium")
        for col, pd in zip(sc_cols, pdata):
            with col:
                c  = "#22c55e" if pd["score"]>=7 else "#f59e0b" if pd["score"]>=5 else "#ef4444"
                bg = "#0d2818" if pd["score"]>=7 else "#2a2000" if pd["score"]>=5 else "#2a0d0d"
                st.markdown(f"""<div class='score-box' style='border-color:{c}40;background:{bg};'>
                    <div style='color:#94a3b8;font-size:0.75rem;font-weight:600;
                                letter-spacing:.5px;text-transform:uppercase;'>{pd['name'][:22]}</div>
                    <div style='color:{c};font-size:3rem;font-weight:700;line-height:1.1;margin:6px 0;'>
                        {pd['score']}<span style='font-size:1.2rem;'>/10</span>
                    </div>
                    <div style='color:#475569;font-size:0.78rem;'>
                        ✅ {len(pd['safe'])} &nbsp; ⚠️ {len(pd['caution'])} &nbsp; ❌ {len(pd['avoid'])}
                    </div>
                </div>""", unsafe_allow_html=True)

        # Problem ingredients
        st.markdown("---")
        pr_cols = st.columns(len(valid), gap="medium")
        for col, pd in zip(pr_cols, pdata):
            with col:
                st.markdown(f"**❌ {pd['name'][:22]} — Avoid**")
                if pd["avoid"]:
                    for ing in pd["avoid"][:6]:
                        st.markdown(f"<div class='ing-avoid'><b style='color:#fca5a5;'>"
                                    f"{ing}</b></div>", unsafe_allow_html=True)
                else:
                    st.markdown("✅ No problematic ingredients!")

        # AI verdict
        st.markdown("---")
        with st.spinner("🏆 Generating verdict…"):
            verdict = compare_products_ai(pdata, profile)

        st.markdown(f"""<div style='background:linear-gradient(135deg,#0f172a,#1e293b);
            border:1px solid #334155;border-radius:12px;padding:20px;
            color:#cbd5e1;line-height:1.7;'>
            🏆 <b style='color:#fbbf24;'>AI Verdict</b><br><br>{verdict}
        </div>""", unsafe_allow_html=True)

        best = max(pdata, key=lambda x: x["score"])
        st.markdown("")
        st.success(f"🏆 Best pick: **{best['name']}** with a score of **{best['score']}/10**")
        save_comparison(" vs ".join(p["name"] for p in pdata), verdict)
        st.caption("✅ Comparison saved.")


# ══════════════════════════════════════════════════════════════════
# PAGE 5 – SAVED PRODUCTS
# ══════════════════════════════════════════════════════════════════
elif page == "🔖 Saved Products":
    page_header("🔖", "Saved Products", "Your bookmarked products and past comparisons.")

    saved = load_saved_products()
    if not saved:
        st.markdown("""<div style='text-align:center;padding:60px;color:#475569;'>
            <div style='font-size:3rem;'>🔖</div>
            <h3>No saved products yet</h3>
            <p>Bookmark products from the <b>Find Products</b> page to see them here.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"**{len(saved)} bookmarked products**")
        st.markdown("")
        s_cols = st.columns(3, gap="medium")
        for i, row in enumerate(saved):
            with s_cols[i % 3]:
                st.markdown("<div class='shopcard'>", unsafe_allow_html=True)
                if row[5]:
                    try: st.image(row[5], width=140)
                    except: pass
                title = row[1][:55] + "…" if len(row[1]) > 55 else row[1]
                st.markdown(f"<div style='font-weight:600;color:#e2e8f0;font-size:0.88rem;"
                            f"margin:6px 0;'>{title}</div>", unsafe_allow_html=True)
                if row[2]:
                    st.markdown(f"<span style='color:#22c55e;font-weight:700;'>💰 {row[2]}</span>",
                                unsafe_allow_html=True)
                if row[3]:
                    c = store_color(row[3])
                    st.markdown(f"<span style='color:{c};font-weight:600;font-size:0.82rem;'>"
                                f"🏪 {row[3]}</span>", unsafe_allow_html=True)
                if row[4]:
                    st.markdown(f"<a href='{row[4]}' target='_blank' class='buy-btn'>"
                                f"🛒 View & Buy →</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                if st.button("🗑️ Remove", key=f"del_{row[0]}"):
                    delete_saved_product(row[0])
                    st.rerun()
                st.markdown("---")




# ══════════════════════════════════════════════════════════════════
# PAGE 6 – HISTORY
# ══════════════════════════════════════════════════════════════════
elif page == "📚 My History":
    page_header("📚", "My Analysis History", "All products you've analysed with IngredientIQ.")

    history = load_history()
    if not history:
        st.markdown("""<div style='text-align:center;padding:60px;color:#475569;'>
            <div style='font-size:3rem;'>📚</div>
            <h3>No history yet</h3>
            <p>Go to <b>Analyze Product</b> to get started.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # Stats bar
        avg_score = sum(r[4] for r in history) / len(history)
        top = max(history, key=lambda r: r[4])
        s1, s2, s3 = st.columns(3)
        for col, label, val, c in [
            (s1, "Products Analysed", len(history), "#22c55e"),
            (s2, "Average Score", f"{avg_score:.1f}/10", "#7dd3fc"),
            (s3, "Best Score", f"{top[4]}/10", "#fbbf24"),
        ]:
            with col:
                st.markdown(f"""<div class='metric-card'>
                    <div style='font-size:1.8rem;font-weight:700;color:{c};'>{val}</div>
                    <div style='color:#64748b;font-size:0.78rem;'>{label}</div>
                </div>""", unsafe_allow_html=True)

        if len(history) >= 3:
            st.markdown("")
            all_ings = " ".join(r[2] for r in history).lower()
            flagged  = [x for x in ["fragrance","alcohol denat","sulfate","paraben","mineral oil"]
                        if x in all_ings]
            if flagged:
                st.warning("⚠️ Pattern detected — you frequently use products with: **"
                           + ", ".join(flagged) + "**. Consider switching.")

        st.markdown("---")
        for row in history:
            sc  = row[4]
            c   = "#22c55e" if sc>=7 else "#f59e0b" if sc>=5 else "#ef4444"
            dot = "🟢" if sc>=7 else "🟡" if sc>=5 else "🔴"
            with st.expander(f"{dot} **{row[1]}** &nbsp;·&nbsp; "
                             f"<span style='color:{c};'>{sc}/10</span> &nbsp;·&nbsp; {row[5]}",
                             expanded=False):
                st.markdown(f"""<div style='background:#0f172a;border-radius:8px;
                    padding:14px;color:#94a3b8;font-size:0.88rem;line-height:1.6;'>
                    {row[3]}
                </div>""", unsafe_allow_html=True)
                st.markdown("")
                with st.expander("📋 View ingredients"):
                    ing_text = row[2][:500] + ("…" if len(row[2]) > 500 else "")
                    st.markdown(f"<span style='color:#64748b;font-size:0.82rem;'>{ing_text}</span>",
                                unsafe_allow_html=True)

        comp_hist = load_compare_history()
        if comp_hist:
            st.markdown("---")
            st.markdown("### ⚖️ Past Comparisons")
            for row in comp_hist:
                with st.expander(f"⚖️ **{row[1]}** &nbsp;·&nbsp; {row[3]}"):
                    st.markdown(f"**Verdict:** {row[2]}")
            