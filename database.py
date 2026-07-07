import sqlite3
import os
import json
from datetime import datetime
from utils import hash_password, verify_password

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db_connection():
    """Establish connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create database tables and insert initial sample data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        eco_points INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carbon_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        transport REAL NOT NULL,
        electricity REAL NOT NULL,
        water REAL NOT NULL,
        food REAL NOT NULL,
        waste REAL NOT NULL,
        total_emissions REAL NOT NULL,
        score_category TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completed_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        challenge_text TEXT NOT NULL,
        challenge_type TEXT NOT NULL,
        points_awarded INTEGER NOT NULL,
        completed_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        badge_name TEXT NOT NULL,
        awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, badge_name)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipt_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        store_name TEXT NOT NULL,
        purchase_date TEXT NOT NULL,
        total_price REAL NOT NULL,
        total_co2 REAL NOT NULL,
        eco_score INTEGER NOT NULL,
        items_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # --- ADVANCED TABLES ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        target_value REAL NOT NULL,
        deadline TEXT NOT NULL,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carbon_offsets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        co2_offset_kg REAL NOT NULL,
        price_usd REAL NOT NULL,
        image_url TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offset_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        offset_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        total_co2_offset REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (offset_id) REFERENCES carbon_offsets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES community_posts (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        type TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    conn.commit()

    # Seed core data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Create Default Users
        admin_pass = hash_password("admin123")
        user_pass = hash_password("password123")
        
        cursor.execute(
            "INSERT INTO users (username, password, name, email, eco_points, role) VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", admin_pass, "Eco Admin", "admin@carbonfootprint.com", 500, "admin")
        )
        cursor.execute(
            "INSERT INTO users (username, password, name, email, eco_points, role) VALUES (?, ?, ?, ?, ?, ?)",
            ("green_hero", user_pass, "Sazwan Syed", "sazwan@carbonfootprint.com", 250, "user")
        )
        
        names = [("alice_green", "Alice Vance", 420), 
                 ("bob_eco", "Bob Ross", 310), 
                 ("charlie_earth", "Charlie Brown", 180), 
                 ("diana_nature", "Diana Prince", 520)]
        for username, name, pts in names:
            dummy_pass = hash_password("password123")
            cursor.execute(
                "INSERT INTO users (username, password, name, email, eco_points, role) VALUES (?, ?, ?, ?, ?, ?)",
                (username, dummy_pass, name, f"{username}@example.com", pts, "user")
            )

        conn.commit()

        # Get User IDs
        cursor.execute("SELECT id FROM users WHERE username = 'green_hero'")
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_id = cursor.fetchone()[0]

        # Seed Carbon History
        history_data = [
            ("2026-01", 300.0, 180.0, 30.0, 250.0, 50.0),
            ("2026-02", 250.0, 160.0, 25.0, 250.0, 45.0),
            ("2026-03", 180.0, 140.0, 20.0, 120.0, 35.0),
            ("2026-04", 120.0, 110.0, 15.0, 120.0, 30.0),
            ("2026-05", 80.0, 90.0, 12.0, 60.0, 20.0)
        ]
        for month, trans, elec, water, food, waste in history_data:
            total = trans + elec + water + food + waste
            score_cat = "Red" if total > 500 else ("Yellow" if total >= 200 else "Green")
            cursor.execute(
                """INSERT INTO carbon_history 
                   (user_id, month, transport, electricity, water, food, waste, total_emissions, score_category)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, month, trans, elec, water, food, waste, total, score_cat)
            )

        # Seed completed challenges
        challenges = [
            ("Walk instead of using a vehicle", "daily", 10, "2026-06-08"),
            ("Save electricity (turn off unused appliances)", "daily", 15, "2026-06-08"),
            ("Carry reusable water bottles", "daily", 5, "2026-06-09"),
            ("Use public transport for all commutes", "weekly", 50, "2026-06-05")
        ]
        for ch_text, ch_type, pts, ch_date in challenges:
            cursor.execute(
                """INSERT INTO completed_challenges (user_id, challenge_text, challenge_type, points_awarded, completed_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, ch_text, ch_type, pts, ch_date)
            )

        # Seed badges
        badges_list = [(user_id, "Eco Rookie"), (user_id, "Carbon Cutter"), (admin_id, "Eco Rookie"), (admin_id, "Green Champion")]
        for u_id, b_name in badges_list:
            cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, ?)", (u_id, b_name))

        # Seed articles
        articles_data = [
            ("What is Carbon Footprint?", "Carbon Footprint", "A carbon footprint is the total amount of greenhouse gases (including carbon dioxide and methane) that are generated by our actions. The average global carbon footprint is close to 4 tons per person annually. To avoid a 2°C rise in global temperatures, the average global carbon footprint needs to drop to under 2 tons by 2050. Reducing carbon footprints is essential for combating climate change.", "Eco Admin"),
            ("Causes and Impacts of Climate Change", "Climate Change", "Climate change is primarily driven by human activities, especially the burning of fossil fuels like coal, oil, and gas. Burning these fuels generates greenhouse gases that wrap around the Earth, trapping the sun's heat and raising temperatures. Impacts include intense droughts, water scarcity, severe fires, rising sea levels, flooding, melting polar ice, catastrophic storms, and declining biodiversity.", "Eco Admin"),
            ("Renewable Energy: Powering a Green Future", "Renewable Energy", "Renewable energy is energy derived from natural sources that are replenished at a higher rate than they are consumed. Solar, wind, geothermal, hydro, and ocean energy are examples of renewable sources. Transitioning from fossil fuels to renewable energy is the most crucial step we can take to reduce greenhouse gas emissions and limit global warming.", "Eco Admin"),
            ("Top 10 Sustainable Living Tips", "Sustainable Living", "1. Shift to LED lightbulbs to save energy.\n2. Walk, bike, or use public transit.\n3. Eat more plant-based meals.\n4. Reduce, reuse, and recycle.\n5. Conserve water by fixing leaks and taking shorter showers.\n6. Use energy-efficient appliances.\n7. Minimize food waste.\n8. Bring reusable bags and bottles.\n9. Go paperless.\n10. Plant native trees.", "Eco Admin")
        ]
        for title, cat, content, author in articles_data:
            cursor.execute("INSERT INTO articles (title, category, content, author) VALUES (?, ?, ?, ?)", (title, cat, content, author))

        # Seed notifications
        cursor.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
            (user_id, "Welcome to the advanced Carbon Footprint Awareness Platform! Log your emissions and track your goals.", "system")
        )

        conn.commit()

    # Seed Carbon Offsets if table is empty
    cursor.execute("SELECT COUNT(*) FROM carbon_offsets")
    if cursor.fetchone()[0] == 0:
        offsets = [
            ("Global Tree Planting Initiative", "Help plant native trees in deforested areas of South America and Africa. Each tree offsets carbon and aids local biomes.", "Forestry", 500.0, 10.0, "tree_planting"),
            ("Wind Farm Clean Grid Project", "Fund large-scale wind turbine farms to displace fossil fuels from regional electricity power grids.", "Renewable Energy", 1200.0, 25.0, "wind_farm"),
            ("Urban Rooftop Solar Panels", "Accelerate the transition to solar energy in community buildings, reducing urban dependence on coal grids.", "Solar", 2000.0, 45.0, "solar_panel"),
            ("Ocean Kelp Carbon Sink", "Support marine kelp reforestation programs that biological sequester carbon deep in ocean beds.", "Oceanic", 800.0, 18.0, "ocean_kelp")
        ]
        for title, desc, cat, co2, price, img in offsets:
            cursor.execute(
                "INSERT INTO carbon_offsets (title, description, category, co2_offset_kg, price_usd, image_url) VALUES (?, ?, ?, ?, ?, ?)",
                (title, desc, cat, co2, price, img)
            )
        
        # Seed some community posts
        cursor.execute("SELECT id FROM users WHERE username = 'alice_green'")
        alice_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM users WHERE username = 'bob_eco'")
        bob_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM users WHERE username = 'green_hero'")
        green_hero_row = cursor.fetchone()
        green_hero_id = green_hero_row[0] if green_hero_row else alice_id

        posts = [
            (alice_id, "Tips for reducing electricity consumption", "I switched all my lights to LEDs and managed to drop my monthly energy carbon by 25 kg! Highly recommend it."),
            (bob_id, "My daily walk commute routine", "I started walking to the office (2km trip) instead of taking the car. Feeling much healthier and saving carbon!")
        ]
        for u_id, title, content in posts:
            cursor.execute("INSERT INTO community_posts (user_id, title, content) VALUES (?, ?, ?)", (u_id, title, content))
            post_id = cursor.lastrowid
            
            # Seed comments
            cursor.execute(
                "INSERT INTO community_comments (post_id, user_id, content) VALUES (?, ?, ?)",
                (post_id, green_hero_id, "That's fantastic! I am trying to do the same this month.")
            )

        conn.commit()

    conn.close()

# DATABASE OPERATIONAL METHODS

def create_user(username, password, name, email, role='user'):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)",
            (username, hashed, name, email, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, 'Eco Rookie')", (user_id,))
        
        # Add welcome notification
        cursor.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, 'Welcome to the platform! Earn eco badges and check the offset marketplace.', 'system')",
            (user_id,)
        )
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(user['password'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_profile(user_id, name, email, password=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if password:
            hashed = hash_password(password)
            cursor.execute(
                "UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?",
                (name, email, hashed, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id)
            )
        
        cursor.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, 'Your profile details have been successfully updated.', 'info')", (user_id,))
        conn.commit()
        return True, "Profile updated successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def add_carbon_entry(user_id, month, transport, electricity, water, food, waste, total_emissions, score_category):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM carbon_history WHERE user_id = ? AND month = ?", (user_id, month))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            """UPDATE carbon_history 
               SET transport = ?, electricity = ?, water = ?, food = ?, waste = ?, total_emissions = ?, score_category = ?
               WHERE id = ?""",
            (transport, electricity, water, food, waste, total_emissions, score_category, existing['id'])
        )
    else:
        cursor.execute(
            """INSERT INTO carbon_history 
               (user_id, month, transport, electricity, water, food, waste, total_emissions, score_category)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, month, transport, electricity, water, food, waste, total_emissions, score_category)
        )
    
    # Award points for logging footprint (20 points)
    cursor.execute("UPDATE users SET eco_points = eco_points + 20 WHERE id = ?", (user_id,))
    
    # Add notification
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"Successfully logged carbon emissions for {month}. Total: {total_emissions} kg CO₂ (+20 pts).", "success")
    )
    
    check_and_award_badges(user_id, cursor)
    check_goals_after_entry(user_id, month, total_emissions, cursor)
    
    conn.commit()
    conn.close()

def check_goals_after_entry(user_id, month, emissions, cursor):
    """Update user goals depending on emissions entry."""
    # Fetch active goals with deadlines >= current log month
    cursor.execute("SELECT * FROM goals WHERE user_id = ? AND status = 'Active'", (user_id,))
    goals = cursor.fetchall()
    
    for goal in goals:
        # If logged month matches target deadline or category
        if goal['deadline'] == month:
            if emissions <= goal['target_value']:
                cursor.execute("UPDATE goals SET status = 'Achieved' WHERE id = ?", (goal['id'],))
                # Award 100 eco points for achieving goal
                cursor.execute("UPDATE users SET eco_points = eco_points + 100 WHERE id = ?", (user_id,))
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                    (user_id, f"🏆 Goal Achieved! Kept emissions under {goal['target_value']} kg CO₂ for {month} (+100 Eco Points!).", "success")
                )
            else:
                cursor.execute("UPDATE goals SET status = 'Failed' WHERE id = ?", (goal['id'],))
                cursor.execute(
                    "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                    (user_id, f"⚠️ Goal Unfulfilled: Emissions for {month} ({emissions} kg) exceeded target limit ({goal['target_value']} kg).", "warning")
                )

def check_and_award_badges(user_id, cursor):
    """Check and award badges based on conditions."""
    cursor.execute("SELECT COUNT(*) FROM carbon_history WHERE user_id = ?", (user_id,))
    calc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT eco_points FROM users WHERE id = ?", (user_id,))
    points = cursor.fetchone()[0]
    
    # Check if Carbon Cutter is deserved
    cursor.execute("SELECT total_emissions FROM carbon_history WHERE user_id = ? ORDER BY month DESC LIMIT 2", (user_id,))
    rows = cursor.fetchall()
    if len(rows) >= 2:
        latest = rows[0][0]
        prev = rows[1][0]
        if latest <= prev * 0.9:
            cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, 'Carbon Cutter')", (user_id,))
            cursor.execute("INSERT OR IGNORE INTO notifications (user_id, message, type) VALUES (?, 'Earned Badge: Carbon Cutter for reducing emissions by 10% MoM!', 'badge')", (user_id,))
            
    # Check Points
    if points >= 500:
        cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, 'Green Champion')", (user_id,))
        cursor.execute("INSERT OR IGNORE INTO notifications (user_id, message, type) VALUES (?, 'Earned Badge: Green Champion for crossing 500 Eco Points!', 'badge')", (user_id,))
    elif points >= 200:
        cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, 'Eco Warrior')", (user_id,))
        cursor.execute("INSERT OR IGNORE INTO notifications (user_id, message, type) VALUES (?, 'Earned Badge: Eco Warrior for crossing 200 Eco Points!', 'badge')", (user_id,))
        
    # Check Energy/Water efficiency
    cursor.execute("SELECT electricity, water FROM carbon_history WHERE user_id = ? ORDER BY month DESC LIMIT 1", (user_id,))
    latest_calc = cursor.fetchone()
    if latest_calc:
        if latest_calc['electricity'] < 100:
            cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, 'Energy Saver')", (user_id,))
            cursor.execute("INSERT OR IGNORE INTO notifications (user_id, message, type) VALUES (?, 'Earned Badge: Energy Saver for electric footprint < 100 kg CO₂!', 'badge')", (user_id,))
        if latest_calc['water'] < 15:
            cursor.execute("INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, 'Water Guard')", (user_id,))
            cursor.execute("INSERT OR IGNORE INTO notifications (user_id, message, type) VALUES (?, 'Earned Badge: Water Guard for water footprint < 15 kg CO₂!', 'badge')", (user_id,))

def get_carbon_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carbon_history WHERE user_id = ? ORDER BY month ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_carbon_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carbon_history WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_eco_points(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT eco_points FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_badges(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT badge_name, awarded_at FROM badges WHERE user_id = ? ORDER BY awarded_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, eco_points FROM users ORDER BY eco_points DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Chatbot History
def get_chatbot_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message, timestamp FROM chatbot_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_chatbot_message(user_id, sender, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chatbot_history (user_id, sender, message) VALUES (?, ?, ?)", (user_id, sender, message))
    conn.commit()
    conn.close()

def clear_chatbot_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chatbot_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Challenges
def get_completed_challenges(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM completed_challenges WHERE user_id = ? ORDER BY completed_date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def complete_challenge(user_id, challenge_text, challenge_type, points):
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute(
        "SELECT id FROM completed_challenges WHERE user_id = ? AND challenge_text = ? AND completed_date = ?",
        (user_id, challenge_text, today)
    )
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return False, "You have already completed this challenge today!"
        
    cursor.execute(
        "INSERT INTO completed_challenges (user_id, challenge_text, challenge_type, points_awarded, completed_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, challenge_text, challenge_type, points, today)
    )
    cursor.execute("UPDATE users SET eco_points = eco_points + ? WHERE id = ?", (points, user_id))
    
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"Eco action completed: '{challenge_text}'! Earned {points} Eco Points.", "success")
    )
    
    check_and_award_badges(user_id, cursor)
    conn.commit()
    conn.close()
    return True, f"Challenge completed! Earned {points} Eco Points!"

# Articles
def get_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_article(title, category, content, author):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO articles (title, category, content, author) VALUES (?, ?, ?, ?)", (title, category, content, author))
    conn.commit()
    conn.close()

# Admin Stats
def get_admin_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM carbon_history")
    total_calc = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(total_emissions) FROM carbon_history")
    avg_emissions = cursor.fetchone()[0]
    avg_emissions = round(avg_emissions, 2) if avg_emissions else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM completed_challenges")
    total_challenges = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_users": total_users,
        "total_calculations": total_calc,
        "average_emissions": avg_emissions,
        "total_challenges_completed": total_challenges
    }

# Receipt Scans History
def add_receipt_entry(user_id, store_name, purchase_date, total_price, total_co2, eco_score, items_json):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO receipt_history 
               (user_id, store_name, purchase_date, total_price, total_co2, eco_score, items_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, store_name, purchase_date, total_price, total_co2, eco_score, items_json)
        )
        cursor.execute("UPDATE users SET eco_points = eco_points + 30 WHERE id = ?", (user_id,))
        
        cursor.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
            (user_id, f"Scanned purchase receipt from {store_name} and mapped {total_co2} kg CO₂ (+30 Eco Points).", "success")
        )
        
        check_and_award_badges(user_id, cursor)
        conn.commit()
        return True, "Receipt saved successfully! Earned 30 Eco Points!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_receipt_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipt_history WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- GOALS OPERATIONS ---

def create_goal(user_id, category, target_value, deadline):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO goals (user_id, category, target_value, deadline) VALUES (?, ?, ?, ?)",
        (user_id, category, target_value, deadline)
    )
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"New goal active: Keep {category} emissions under {target_value} kg by {deadline}.", "info")
    )
    conn.commit()
    conn.close()
    return True

def get_goals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals WHERE user_id = ? ORDER BY deadline ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_goal(goal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()


# --- CARBON OFFSET MARKETPLACE ---

def get_offsets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carbon_offsets")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def buy_offset(user_id, offset_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM carbon_offsets WHERE id = ?", (offset_id,))
    offset = cursor.fetchone()
    if not offset:
        conn.close()
        return False, "Carbon offset project not found."
        
    total_price = offset['price_usd'] * quantity
    total_co2_offset = offset['co2_offset_kg'] * quantity
    
    # In a real SaaS this drafts stripe, here we check user has points or just purchase
    cursor.execute(
        """INSERT INTO offset_transactions (user_id, offset_id, quantity, total_price, total_co2_offset)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, offset_id, quantity, total_price, total_co2_offset)
    )
    
    # Award massive eco points for offset funding (50 points per quantity unit)
    awarded_points = quantity * 50
    cursor.execute("UPDATE users SET eco_points = eco_points + ? WHERE id = ?", (awarded_points, user_id))
    
    # Log notification
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"Purchased {quantity} units of '{offset['title']}', offsetting {total_co2_offset} kg CO₂ (+{awarded_points} Eco Points!). Thank you!", "success")
    )
    
    check_and_award_badges(user_id, cursor)
    conn.commit()
    conn.close()
    return True, f"Successfully contributed! Offset {total_co2_offset} kg CO₂ and earned {awarded_points} Eco Points."

def get_offset_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT ot.*, co.title, co.category 
           FROM offset_transactions ot
           JOIN carbon_offsets co ON co.id = ot.offset_id
           WHERE ot.user_id = ?
           ORDER BY ot.created_at DESC""",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- COMMUNITY FORUM ---

def get_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT cp.*, u.name as author_name, u.username as author_username,
           (SELECT COUNT(*) FROM community_comments cc WHERE cc.post_id = cp.id) as comment_count
           FROM community_posts cp
           JOIN users u ON u.id = cp.user_id
           ORDER BY cp.created_at DESC"""
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_post_by_id(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT cp.*, u.name as author_name, u.username as author_username
           FROM community_posts cp
           JOIN users u ON u.id = cp.user_id
           WHERE cp.id = ?""",
        (post_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_post(user_id, title, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO community_posts (user_id, title, content) VALUES (?, ?, ?)",
        (user_id, title, content)
    )
    # Award 15 eco points for contributing to forum
    cursor.execute("UPDATE users SET eco_points = eco_points + 15 WHERE id = ?", (user_id,))
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, 'Published forum post: +15 Eco Points.', 'success')",
        (user_id,)
    )
    conn.commit()
    conn.close()
    return True

def get_comments(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT cc.*, u.name as author_name, u.username as author_username
           FROM community_comments cc
           JOIN users u ON u.id = cc.user_id
           WHERE cc.post_id = ?
           ORDER BY cc.created_at ASC""",
        (post_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_comment(post_id, user_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO community_comments (post_id, user_id, content) VALUES (?, ?, ?)",
        (post_id, user_id, content)
    )
    # Award 5 eco points for commenting
    cursor.execute("UPDATE users SET eco_points = eco_points + 5 WHERE id = ?", (user_id,))
    
    # Notify post owner if comment is by another user
    cursor.execute("SELECT user_id, title FROM community_posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if post and post['user_id'] != user_id:
        cursor.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
            (post['user_id'], f"Someone commented on your post '{post['title']}': '{content[:30]}...'", "info")
        )
    
    conn.commit()
    conn.close()
    return True


# --- NOTIFICATIONS CENTER ---

def get_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 30", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notification_read(notification_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()

def clear_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# --- SUSTAINABILITY SCORING ---

def get_sustainability_score(user_id):
    """
    Calculate a real-time sustainability index score (0-100) dynamically.
    - Base: 100
    - Monthly carbon logs average emissions: higher average deducts up to 50 pts
    - Active daily/weekly actions/challenges completed: adds up to 25 pts
    - Offset investments: adds up to 25 pts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Carbon Avg Deduction
    cursor.execute("SELECT AVG(total_emissions) FROM carbon_history WHERE user_id = ?", (user_id,))
    avg_em = cursor.fetchone()[0]
    deduction = 0
    if avg_em:
        # Standardize: 400kg is moderate. Over 700kg is red
        if avg_em > 700:
            deduction = 50
        elif avg_em > 400:
            deduction = 35
        elif avg_em > 200:
            deduction = 15
        else:
            deduction = 5
    else:
        # If no logs, assume baseline deduction
        deduction = 20
        
    # 2. Challenge Completion Bonuses
    cursor.execute("SELECT COUNT(*) FROM completed_challenges WHERE user_id = ?", (user_id,))
    ch_count = cursor.fetchone()[0]
    challenge_bonus = min(25, ch_count * 2) # 2 pts per challenge
    
    # 3. Offsets Purchased Bonuses
    cursor.execute("SELECT SUM(quantity) FROM offset_transactions WHERE user_id = ?", (user_id,))
    off_qty = cursor.fetchone()[0]
    off_qty = off_qty if off_qty else 0
    offset_bonus = min(25, off_qty * 5) # 5 pts per offset unit purchased
    
    score = 100 - deduction + challenge_bonus + offset_bonus
    score = max(5, min(100, int(score))) # clamp between 5 and 100
    
    conn.close()
    return score
