import sqlite3
import json
from datetime import datetime

DB = "ingredientiq.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Create profiles with IF NOT EXISTS (never crashes on restart)
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
        id               INTEGER PRIMARY KEY,
        skin_type        TEXT,
        hair_type        TEXT,
        age_range        TEXT,
        skin_concerns    TEXT,
        hair_concerns    TEXT,
        allergies        TEXT,
        skin_condition   TEXT,
        hair_condition   TEXT,
        budget           INTEGER
    )''')

    # Safe migration: add any missing columns to old DBs
    existing = [row[1] for row in c.execute("PRAGMA table_info(profiles)")]
    for col, ctype in [
        ("skin_concerns",  "TEXT"),
        ("hair_concerns",  "TEXT"),
        ("skin_condition", "TEXT"),
        ("hair_condition", "TEXT"),
        ("budget",         "INTEGER"),
    ]:
        if col not in existing:
            c.execute(f"ALTER TABLE profiles ADD COLUMN {col} {ctype}")

    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id           INTEGER PRIMARY KEY,
        product_name TEXT,
        ingredients  TEXT,
        analysis     TEXT,
        score        REAL,
        timestamp    TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS compare_history (
        id        INTEGER PRIMARY KEY,
        products  TEXT,
        verdict   TEXT,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS saved_products (
        id        INTEGER PRIMARY KEY,
        title     TEXT,
        price     TEXT,
        source    TEXT,
        link      TEXT,
        thumbnail TEXT,
        timestamp TEXT
    )''')

    conn.commit()
    conn.close()


def save_profile(skin_type, hair_type, age_range,
                 skin_concerns, hair_concerns,
                 allergies, skin_condition="", hair_condition="", budget=1000):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM profiles")
    c.execute(
        """INSERT INTO profiles
           (skin_type, hair_type, age_range, skin_concerns, hair_concerns,
            allergies, skin_condition, hair_condition, budget)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            skin_type,
            hair_type,
            age_range,
            json.dumps(skin_concerns),
            json.dumps(hair_concerns),
            allergies or "",
            skin_condition or "",
            hair_condition or "",
            int(budget),
        )
    )
    conn.commit()
    conn.close()


def load_profile():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Explicit column list → positional index access, never breaks
    c.execute("""SELECT skin_type, hair_type, age_range,
                        skin_concerns, hair_concerns, allergies,
                        skin_condition, hair_condition, budget
                 FROM profiles LIMIT 1""")
    row = c.fetchone()
    conn.close()

    if not row:
        return None

    valid_skin = ["Acne", "Sensitivity", "Pigmentation", "Dryness", "Redness", "Oiliness"]
    valid_hair = ["Hairfall", "Dandruff", "Dryness", "Frizz", "Scalp Issues", "Breakage"]

    try:
        sc = [x for x in json.loads(row[3] or "[]") if x in valid_skin]
    except Exception:
        sc = []
    try:
        hc = [x for x in json.loads(row[4] or "[]") if x in valid_hair]
    except Exception:
        hc = []

    s_cond = str(row[6]) if row[6] else ""
    h_cond = str(row[7]) if row[7] else ""

    return {
        "skin_type"         : str(row[0]) if row[0] else "Oily",
        "hair_type"         : str(row[1]) if row[1] else "Normal",
        "age_range"         : str(row[2]) if row[2] else "20s",
        "skin_concerns"     : sc,
        "hair_concerns"     : hc,
        "concerns"          : sc + hc,
        "allergies"         : str(row[5]) if row[5] else "",
        "skin_condition"    : s_cond,
        "hair_condition"    : h_cond,
        "specific_condition": " | ".join(filter(None, [s_cond, h_cond])),
        "budget"            : int(row[8]) if row[8] else 1000,
    }


def save_analysis(product_name, ingredients, analysis, score):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO history VALUES (NULL,?,?,?,?,?)",
              (product_name, ingredients, analysis, score,
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def load_history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def save_comparison(products_summary, verdict):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO compare_history VALUES (NULL,?,?,?)",
              (products_summary, verdict,
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def load_compare_history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM compare_history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def save_product_bookmark(title, price, source, link, thumbnail):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM saved_products WHERE title=?", (title,))
    if not c.fetchone():
        c.execute("INSERT INTO saved_products VALUES (NULL,?,?,?,?,?,?)",
                  (title, price, source, link, thumbnail,
                   datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
    conn.close()


def load_saved_products():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM saved_products ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def delete_saved_product(product_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM saved_products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()