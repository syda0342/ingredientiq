# IngredientIQ

**AI-Powered Personalized Skincare & Haircare Intelligence**

IngredientIQ is an intelligent web application that analyzes cosmetic product ingredients against your unique skin and hair profile, helping you make informed purchasing decisions and avoid harmful ingredients tailored to your specific needs.

---

## Problem Statement

The cosmetics industry presents four major challenges for consumers:

1. **Unreadable Ingredient Labels** - Products contain 15-50 chemical INCI names that are unrecognizable to average consumers
2. **No Personalization** - Generic tools like INCI Decoder or CosDNA ignore individual skin type, hair type, age, concerns, and medical conditions
3. **Medical Conditions Ignored** - People with Keratosis Pilaris, Rosacea, Eczema, or Scalp Psoriasis receive zero condition-specific guidance
4. **Wasted Money** - Indian consumers spend ₹2,000-5,000/year on incompatible products due to misleading marketing

**IngredientIQ addresses all four problems in a single AI-powered platform.**

---

## Features

### 1. Personalized Profile Setup
- Skin type (Oily, Dry, Combination, Sensitive)
- Hair type (Normal, Oily, Dry, Damaged)
- Age range (5 groups: 13-17, 18-25, 26-35, 36-50, 50+)
- Skin concerns (Acne, Sensitivity, Pigmentation, Dryness, Redness, Oiliness)
- Hair concerns (Hairfall, Dandruff, Dryness, Frizz, Scalp Issues)
- Medical conditions (Keratosis Pilaris, Eczema, Rosacea, Scalp Psoriasis)
- Allergen tracking
- Budget preferences

### 2. OCR Label Scanner
- Photograph product labels directly
- OCR.space API Engine 2 extracts ingredients automatically
- Converts complex INCI names into structured ingredient lists
- No manual typing needed

### 3. 5-Layer ML Ingredient Analyzer
Each ingredient is classified as **Safe / Caution / Avoid** through a rule-based ML cascade:

**Layer 1:** Allergen Check - Immediate flagging if ingredient matches user allergens  
**Layer 2:** Age Profile Match - Age-specific good/bad ingredient lists  
**Layer 3:** Skin Concern Filter - Acne, Sensitivity, Pigmentation, Dryness, Redness, Oiliness  
**Layer 4:** Hair Concern Filter - Hairfall, Dandruff, Dryness, Frizz, Scalp Issues  
**Layer 5:** Skin & Hair Type - Oily, Dry, Combination, Sensitive, Damaged profiles

**Scoring Formula:**
```
Compatibility Score = (Safe×1.0 + Caution×0.5) / Total × 10

7-10  Great match for you
5-6   Use with caution  
0-4   Not recommended
```

Every result includes a **personalized reason** specific to your profile - this is explainable AI, not a black box.

### 4. AI Product Recommendations
- Groq LLaMA-3.3-70B-Versatile generates 5 personalized product picks
- Focus-aware prompting separates skincare vs haircare recommendations
- Considers your complete profile: age, skin/hair type, concerns, conditions, budget

### 5. Live Shopping Integration
- SerpAPI fetches real-time products from:
  - Nykaa
  - Amazon
  - Flipkart
  - Myntra
  - Blinkit
- Accurate INR pricing
- Direct "View & Buy" links
- Bookmark products for later

### 6. Product Comparison
- Side-by-side analysis of 2-3 products
- AI verdict with detailed reasoning
- Pattern detection across ingredient lists
- Best pick recommendation for your profile

### 7. Analysis History
- SQLite database stores all analyzed products
- Track compatibility scores over time
- Review past comparisons
- Pattern recognition across your product choices

---

## Technology Stack

### Frontend
- **Streamlit** - Web framework with 6-page navigation
- Custom dark UI with gradient cards and hover effects
- Responsive column layouts

### AI & Logic
- **Groq Cloud API** - LLaMA-3.3-70B-Versatile for NLP and product recommendations
- **OCR.space API Engine 2** - Label reading and ingredient extraction
- **Rule-based ML Classifier** - 100+ ingredient classification rules
- Profile-aware NLP with context injection

### Data & APIs
- **SQLite3** - 4 tables (profiles, history, compare, saved)
- **SerpAPI** - Google Shopping live product results
- **Python-dotenv** - Secure API key management

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- API Keys (instructions below)

### Step 1: Clone the Repository
```bash
git clone https://github.com/syda0342/ingredientiq.git
cd ingredientiq
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up API Keys

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
OCR_API_KEY=your_ocr_space_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

#### How to Get API Keys:

**Groq API (Free)**
1. Go to https://console.groq.com
2. Sign up and create an API key
3. Copy the key to your `.env` file

**OCR.space API (Free)**
1. Go to https://ocr.space/ocrapi
2. Register for a free API key
3. Use Engine 2 for best results
4. Copy the key to your `.env` file

**SerpAPI (Free Tier Available)**
1. Go to https://serpapi.com
2. Sign up for a free account (100 searches/month)
3. Get your API key from the dashboard
4. Copy the key to your `.env` file

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Usage Guide

### 1. Set Up Your Profile
Navigate to **My Profile** and enter:
- Your skin type and hair type
- Age range
- Concerns (skin and hair)
- Any medical conditions
- Known allergens
- Budget preferences

### 2. Analyze a Product
Go to **Analyze Product** and either:
- **Type/Paste** the ingredient list manually, OR
- **Upload a photo** of the product label (OCR will extract ingredients)

Click **Analyze Ingredients** to get:
- Compatibility score (0-10)
- Breakdown of Safe/Caution/Avoid ingredients
- Personalized explanations for each ingredient

### 3. Find Personalized Products
Visit **Find Products** to:
- Choose search focus (Skincare, Haircare, or Both)
- Get AI-generated product recommendations
- See 5 best ingredients for your profile
- Browse live shopping results with real prices

### 4. Compare Products
Use **Compare Products** to:
- Load products from your analysis history
- Add 2-3 products side-by-side
- Get AI verdict on which is best for you
- See detailed reasoning and trade-offs

### 5. Track Your History
Check **My History** to:
- View all previously analyzed products
- See compatibility scores at a glance
- Review past comparisons
- Spot patterns in your choices

---

## Project Architecture

```
ingredientiq/
│
├── app.py                  # Main Streamlit application (6 pages)
├── ai_helper.py           # Groq, OCR.space, SerpAPI integrations
├── ml_model.py            # Rule-based ingredient classifier
├── database.py            # SQLite operations (profiles, history, compare, saved)
├── requirements.txt       # Python dependencies
├── .env.example          # API key template
├── .gitignore            # Excludes .env and *.db files
└── README.md             # This file
```

---

## Algorithm Deep Dive

### Ingredient Scoring Algorithm

The 5-layer cascade processes each ingredient sequentially:

```python
# Pseudocode
for ingredient in product_ingredients:
    
    # Layer 1: Allergen Check
    if ingredient in user_allergens:
        flag as AVOID
        continue
    
    # Layer 2: Age Profile Match
    if ingredient in age_bad_list[user_age]:
        score -= penalty
    if ingredient in age_good_list[user_age]:
        score += bonus
    
    # Layer 3: Skin Concern Filter
    for concern in user_skin_concerns:
        if ingredient in concern_bad_list[concern]:
            flag as CAUTION or AVOID
        if ingredient in concern_good_list[concern]:
            score += bonus
    
    # Layer 4: Hair Concern Filter
    for concern in user_hair_concerns:
        if ingredient in concern_bad_list[concern]:
            flag as CAUTION or AVOID
        if ingredient in concern_good_list[concern]:
            score += bonus
    
    # Layer 5: Skin & Hair Type
    if ingredient in type_bad_list[user_skin_type]:
        flag as AVOID
    if ingredient in type_good_list[user_hair_type]:
        score += bonus

# Final Compatibility Score
compatibility = (safe_count * 1.0 + caution_count * 0.5) / total_count * 10
```

---

## Deployment (Streamlit Cloud)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Initial commit - IngredientIQ AI Skincare App"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository → `app.py`
5. Click "Advanced settings"
6. Add your API keys in **Secrets**:
   ```toml
   GROQ_API_KEY = "your_key_here"
   OCR_API_KEY = "your_key_here"
   SERPAPI_KEY = "your_key_here"
   ```
7. Click "Deploy"

Your app will be live at: `https://[your-app-name].streamlit.app`

**Note:** SQLite database resets on each redeployment. For persistent storage, consider migrating to Supabase or Firebase.

---

## Results & Validation

### Real-World Testing
- OCR successfully extracted ingredients from Avene, Dot & Key, and Cetaphil products
- Fragrance flagged as **Caution** for sensitivity-prone users
- Coconut oil flagged as **Avoid** for oily skin (comedogenic rating)
- AI correctly separated skincare vs haircare recommendations
- Cetaphil scored **9.8/10** vs Dot & Key for oily+sensitive skin - matched dermatological recommendations
- Live shopping returned real products from Nykaa, Amazon, Blinkit, Myntra with accurate INR pricing

---

## Future Scope

1. **Barcode/QR Scanning** - Auto-fetch ingredient lists from database, removing OCR step entirely
2. **Dermatologist Database** - Partner with dermatologists to validate ingredient classifications for medical conditions
3. **Mobile App** - React Native or Flutter version for on-shelf scanning in beauty stores
4. **Community Reviews** - Social layer where users share experiences filtered by skin type
5. **Cloud Database** - Replace SQLite with Supabase/Firebase for persistent history across deployments
6. **Multilingual Support** - Regional Indian languages for labels and recommendations
7. **Ingredient Deep Dives** - Detailed explanations of what each ingredient does scientifically
8. **Batch Analysis** - Upload multiple products at once for comparison

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Syona Daniel**  
Sophia College for Women, Department of IT  
Final Year Capstone Project

---

## Acknowledgments

- **Groq Inc.** - LLaMA-3.3-70B-Versatile API
- **OCR.space** - Free OCR API Engine 2
- **SerpAPI** - Google Shopping API
- **Streamlit** - Open-source web framework
- **Anthropic Claude** - Development assistance and code optimization

---

## References

1. Groq Inc. (2024). LLaMA-3.3-70B-Versatile API Documentation. https://console.groq.com/docs
2. Streamlit Inc. (2024). Streamlit Open-Source Framework Documentation. https://docs.streamlit.io
3. OCR.space. (2024). Free OCR API Documentation. Engine 2. https://ocr.space/ocrapi
4. SerpAPI. (2024). Google Shopping API Documentation. https://serpapi.com
5. Meta AI. (2024). LLaMA 3: Open Foundation and Fine-Tuned Models. https://ai.meta.com/llama
6. Draelos, Z. D. (2010). *Cosmetic Dermatology: Products and Procedures*. Wiley-Blackwell.
7. Touitou, Y., & Labat, C. (2017). Skin care and cosmetics: a mini-review. *Aging*, 9(4), 1203.

---

## Contact

For questions, suggestions, or collaboration opportunities:
- GitHub: [@syda0342](https://github.com/syda0342)
- Project Link: [https://github.com/syda0342/ingredientiq](https://github.com/syda0342/ingredientiq)

---

<div align="center">

**Made for smarter skincare decisions**

Star this repo if you found it helpful!

</div>
