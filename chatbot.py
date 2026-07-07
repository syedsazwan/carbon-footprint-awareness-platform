import streamlit as st
import database as db
from datetime import datetime
import requests
import json
import g4f

ECO_RESPONSES = {
    "hello": "Hello! I'm **EcoBot**, your personal sustainability assistant. How can I help you on your green journey today? 🌍",
    "hi": "Hi there! EcoBot here, ready to share some daily green wisdom. How are you doing today? 🌱",
    "help": "I can help you with:\n- Reducing your carbon footprint (by category like Transport, Energy, Water, Food, Waste)\n- Explaining your carbon score & dashboard results\n- Answering questions about your own logs, points, badges, goals, and challenges\n- Retrieving information on general science & sustainability topics (e.g. global warming, solar panels, recycling) via dynamic lookup!\n\nTry clicking any of the Quick Buttons below or typing your question!",
    "climate change": "Climate change refers to long-term shifts in temperatures and weather patterns, mainly caused by human activities like burning fossil fuels (coal, oil, gas) which release greenhouse gases that trap heat in the atmosphere. This raises global temperatures, leading to extreme weather, melting glaciers, and rising sea levels. 🌡️🌀",
    "renewable energy": "Renewable energy comes from natural sources that replenish themselves faster than they are consumed. Examples include solar (sun), wind, geothermal (heat from the earth), hydro (water flow), and bioenergy. Transitioning to renewables is the single most effective way to cut global carbon emissions! ☀️💨💧",
    "solar": "Solar panels convert sunlight into electricity using photovoltaic (PV) cells. By installing solar panels, a household can reduce its reliance on fossil-fuel grids and cut carbon emissions by up to 3 to 4 tons of CO₂ per year! ☀️🔋",
    "recycling": "Recycling involves converting waste materials into new materials and objects. It prevents resource depletion, reduces energy consumption, and cuts down on landfill methane emissions. Always try to separate paper, glass, metals, and plastics! ♻️🗑️",
    "composting": "Composting is the natural process of recycling organic matter, such as leaves and food scraps, into a valuable fertilizer that enriches soil. By composting, you reduce the organic waste sent to landfills, which prevents the production of methane, a potent greenhouse gas. 🍂🍎",
    "water conservation": "Conserving water is crucial because treating and pumping water requires energy (and thus fossil fuels). Simple tips: fix leaks, take shorter showers (under 5 minutes), use rainwater harvesting for plants, and install low-flow faucets. 💧🚿",
    "plastic": "Plastic pollution damages ecosystems and marine life, and plastic production is heavily reliant on petroleum (fossil fuels). Switch to reusable water bottles, shopping bags, and containers, and try to avoid single-use plastics entirely! 🥤🛍️",
    "top 10 sustainable living tips": "Here are the Top 10 Sustainable Living Tips:\n1. Shift to LED lightbulbs to save energy.\n2. Walk, bike, or use public transit.\n3. Eat more plant-based meals.\n4. Reduce, reuse, and recycle.\n5. Conserve water by fixing leaks and taking shorter showers.\n6. Use energy-efficient appliances.\n7. Minimize food waste.\n8. Bring reusable bags and bottles.\n9. Go paperless.\n10. Plant native trees.",
}

def get_eco_challenge_tip():
    import random
    challenges = [
        "🚶 **Daily Eco Challenge:** Try walking, biking, or taking public transit for any trip under 3 kilometers today!",
        "💡 **Daily Eco Challenge:** Unplug all electronics and chargers that you aren't actively using. Idle energy (phantom load) accounts for 5-10% of household electricity!",
        "🥤 **Daily Eco Challenge:** Go the entire day without using a single piece of single-use plastic (bottles, bags, straws, utensils).",
        "🥗 **Daily Eco Challenge:** Eat completely plant-based meals today (Vegan). This simple shift can cut your food carbon footprint by over 60%!",
        "🚿 **Daily Eco Challenge:** Limit your shower time to exactly 4 minutes. A standard showerhead releases about 9.5 liters of water per minute!"
    ]
    return random.choice(challenges)

def get_wikipedia_summary(query: str):
    """Fetch summary of a topic from Wikipedia dynamically."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "utf8": 1,
        "srlimit": 1
    }
    headers = {
        "User-Agent": "EcoHubChatbot/1.0 (contact@ecohub-platform.org)"
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=5).json()
        search_results = res.get("query", {}).get("search", [])
        if not search_results:
            return None, None
            
        best_title = search_results[0]["title"]
        
        summary_params = {
            "action": "query",
            "format": "json",
            "titles": best_title,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "exsentences": 3,
            "redirects": True
        }
        summary_res = requests.get(url, params=summary_params, headers=headers, timeout=5).json()
        pages = summary_res.get("query", {}).get("pages", {})
        page_id = list(pages.keys())[0]
        
        if page_id == "-1":
            return None, None
            
        extract = pages[page_id].get("extract", "")
        return best_title, extract
    except Exception:
        return None, None

def extract_wiki_query(prompt: str) -> str:
    """Clean the user prompt to find the core query for Wikipedia search."""
    clean = prompt.lower().strip().rstrip("?").rstrip("!").rstrip(".")
    # Remove common conversational prefixes
    prefixes = [
        "what is a ", "what is an ", "what is ", "what are ",
        "tell me about a ", "tell me about an ", "tell me about ",
        "explain to me ", "explain what is ", "explain ",
        "who is ", "who was ", "definition of ", "define ",
        "search for ", "information on ", "info about "
    ]
    for prefix in prefixes:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break
    return clean.strip()

def call_gpt_generative(user_id, prompt):
    """Call GPT-4o model with user statistics context using keyless g4f."""
    try:
        # Fetch user's data from DB
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, username, eco_points FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        name = user_row['name'] if user_row else "User"
        pts = user_row['eco_points'] if user_row else 0
        
        if pts >= 500:
            level = "Champion 🏆"
        elif pts >= 200:
            level = "Warrior 🛡️"
        else:
            level = "Rookie 🌱"
            
        history = db.get_carbon_history(user_id)
        goals = db.get_goals(user_id)
        completed = db.get_completed_challenges(user_id)
        badges = db.get_badges(user_id)
        
        system_prompt = (
            "You are EcoBot, a highly advanced, friendly, and professional AI sustainability assistant on the EcoHub carbon footprint tracking platform.\n"
            "Your purpose is to answer user questions about climate change, sustainability, and their personal carbon footprints.\n\n"
            "Here is the context of the user you are chatting with:\n"
            f"- User Name: {name}\n"
            f"- Eco Points: {pts}\n"
            f"- Eco Level: {level}\n"
        )
        
        if badges:
            badge_names = ", ".join([b['badge_name'] for b in badges])
            system_prompt += f"- Unlocked Badges: {badge_names}\n"
            
        if history:
            latest = history[-1]
            system_prompt += (
                f"- Carbon History (last {min(5, len(history))} months):\n"
            )
            for h in history[-5:]:
                system_prompt += f"  * {h['month']}: {h['total_emissions']} kg CO2 ({h['score_category']} score)\n"
            
            system_prompt += (
                f"- Breakdown of user's latest calculation ({latest['month']}):\n"
                f"  * Transport: {latest['transport']} kg CO2\n"
                f"  * Electricity: {latest['electricity']} kg CO2\n"
                f"  * Water: {latest['water']} kg CO2\n"
                f"  * Food: {latest['food']} kg CO2\n"
                f"  * Waste: {latest['waste']} kg CO2\n"
            )
        else:
            system_prompt += "- Carbon History: No calculations logged yet.\n"
            
        if goals:
            active_goals = [g for g in goals if g.get('status', 'Active') == 'Active']
            if active_goals:
                system_prompt += "- Active Goals:\n"
                for g in active_goals:
                    system_prompt += f"  * Keep {g['category']} under {g['target_value']} kg CO2 by {g['deadline']}\n"
                    
        if completed:
            system_prompt += "- Recently Completed Challenges:\n"
            for c in completed[:5]:
                system_prompt += f"  * {c['challenge_text']} (+{c['points_awarded']} pts on {c['completed_date']})\n"
                
        system_prompt += (
            "\nFormatting Instructions:\n"
            "1. Answer in friendly, professional, clear English. Use markdown elements (bold, bullet points) for readability.\n"
            "2. When users ask about their stats (points, level, badges, score, history, goals), refer directly to the user context provided above.\n"
            "3. Keep answers concise, helpful, and action-oriented."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Retrieve history from session state if available, otherwise database
        chat_history = []
        if "chat_messages" in st.session_state:
            chat_history = st.session_state.chat_messages
        else:
            db_history = db.get_chatbot_history(user_id)
            chat_history = [
                {"role": "user" if c['sender'] == "user" else "assistant", "content": c['message']}
                for c in db_history
            ]
            
        for msg in chat_history[-10:]:
            role = msg["role"]
            if role == "bot":
                role = "assistant"
            messages.append({"role": role, "content": msg["content"]})
            
        if not messages or messages[-1]["content"] != prompt:
            messages.append({"role": "user", "content": prompt})
            
        response = g4f.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            timeout=15
        )
        if response and isinstance(response, str) and response.strip():
            return response.strip()
    except Exception as e:
        # Fallback to local rule-based system silently on exception
        pass
    return None

def generate_bot_response(user_id, prompt):
    # Try generative GPT-4o first
    gpt_response = call_gpt_generative(user_id, prompt)
    if gpt_response:
        return gpt_response
    prompt_lower = prompt.lower().strip()
    history = db.get_carbon_history(user_id)
    latest_calc = history[-1] if history else None

    # 1. Greetings
    if any(prompt_lower.startswith(w) for w in ["hi", "hello", "hey", "greetings", "yo"]):
        greeting_msg = ECO_RESPONSES.get(prompt_lower, "Hello! I am **EcoBot**, your sustainability assistant. How can I help you today? 🌱")
        return greeting_msg

    # 2. Live Data / User Profile Query integration
    if any(k in prompt_lower for k in [
        "my points", "my level", "how many points", "how many eco points", "my score", 
        "my emissions", "my footprint", "my history", "my logs", "my records", "my badges", 
        "my achievements", "my goals", "my targets", "my completed challenges", 
        "my challenges", "what challenge did i do", "what challenges have i done", "completed challenges"
    ]):
        if any(k in prompt_lower for k in ["points", "level", "xp", "how many"]):
            pts = db.get_eco_points(user_id)
            if pts >= 500:
                level = "Champion"
                icon = "🏆"
                next_lvl = "Max Level reached!"
            elif pts >= 200:
                level = "Warrior"
                icon = "🛡️"
                next_lvl = f"Only {500 - pts} more Eco Points to reach **Champion 🏆**!"
            else:
                level = "Rookie"
                icon = "🌱"
                next_lvl = f"Only {200 - pts} more Eco Points to reach **Warrior 🛡️**!"
            return f"🪙 **Your Eco Status:**\nYou currently have **{pts} Eco Points**.\nYour current level is **{icon} {level}**.\n\n*{next_lvl}*\n\nKeep completing daily challenges, logging calculations, and scanning receipts to earn more points!"

        elif any(k in prompt_lower for k in ["badges", "achievements", "rewards"]):
            badges = db.get_badges(user_id)
            if not badges:
                return "🏅 **Your Badges:**\nYou haven't unlocked any badges yet! Badges are awarded automatically for completing milestones (like logging calculations, scanning carbon receipts, or purchasing carbon offsets). Keep up the green work to unlock your first badge!"
            else:
                badge_list = "\n".join([f"- 🏅 **{b['badge_name']}** (Unlocked: {b['awarded_at'][:10]})" for b in badges])
                return f"🏅 **Your Badges ({len(badges)}):**\nHere are the badges you've unlocked on EcoHub:\n{badge_list}\n\nGreat job on making a sustainable impact!"

        elif any(k in prompt_lower for k in ["goals", "targets"]):
            goals = db.get_goals(user_id)
            if not goals:
                return "🎯 **Your Eco Goals:**\nYou do not have any active carbon goals right now. Setting goals is a great way to stay accountable! Head over to the **Action & Challenges** tab to create a new goal."
            else:
                active_goals = [g for g in goals if g.get('status', 'Active') == 'Active']
                if not active_goals:
                    return "🎯 **Your Eco Goals:**\nYou have no active goals. Any goals you set will show up here. You can set them in the **Action & Challenges** tab."
                
                goal_list = "\n".join([
                    f"- **{g['category'].capitalize()}**: Keep under **{g['target_value']} kg CO₂** by {g['deadline']}"
                    for g in active_goals
                ])
                return f"🎯 **Your Active Goals ({len(active_goals)}):**\nHere are your current carbon reduction targets:\n{goal_list}\n\nTrack your progress on the Dashboard to see if you're keeping under these thresholds!"

        elif any(k in prompt_lower for k in ["challenges", "what challenge", "completed"]):
            completed = db.get_completed_challenges(user_id)
            if not completed:
                return "⚡ **Your Challenges:**\nYou haven't completed any daily eco challenges yet. Take a look at the **Action & Challenges** tab to find today's challenges and start earning Eco Points!"
            else:
                completed_list = "\n".join([f"- ✅ **{c['challenge_text']}** (+{c['points_awarded']} pts on {c['completed_date']})" for c in completed[:5]])
                return f"⚡ **Recently Completed Challenges:**\nHere are your last {min(5, len(completed))} completed challenges:\n{completed_list}\n\nKeep going! Every small action counts!"

        elif any(k in prompt_lower for k in ["emissions", "footprint", "history", "logs", "records", "calculation"]):
            if not history:
                return "📊 **Your Emissions:**\nYou haven't logged any emissions calculations yet. Navigate to the **Carbon Calculator** page to enter your monthly utilities and commuting logs!"
            else:
                latest = history[-1]
                history_list = "\n".join([f"- 📅 **{e['month']}**: {e['total_emissions']} kg CO₂ ({e['score_category']})" for e in reversed(history[:5])])
                
                breakdown = (
                    f"🚙 Transport: {latest['transport']} kg\n"
                    f"💡 Electricity: {latest['electricity']} kg\n"
                    f"💧 Water: {latest['water']} kg\n"
                    f"🥗 Food: {latest['food']} kg\n"
                    f"🗑️ Waste: {latest['waste']} kg"
                )
                
                return (
                    f"📊 **Your Carbon Emissions History:**\n"
                    f"Here are your last {min(5, len(history))} logs:\n{history_list}\n\n"
                    f"🌱 **Breakdown of your latest month ({latest['month']}):**\n"
                    f"Total: **{latest['total_emissions']} kg CO₂** ({latest['score_category']})\n"
                    f"```\n{breakdown}\n```"
                )

    # 3. Category-Specific Footprint Reduction Tips
    if any(k in prompt_lower for k in ["reduce", "decrease", "cut", "lower", "lessen", "mitigate"]):
        if any(k in prompt_lower for k in ["transport", "car", "commute", "travel", "fly", "flight", "vehicle", "driving"]):
            return (
                "🚙 **How to Reduce Transportation Emissions:**\n"
                "- **Walk or Cycle:** For trips under 3 km, walking or cycling produces zero emissions and is great for health.\n"
                "- **Use Public Transit:** Trains and buses emit 50-80% less CO₂ per passenger-kilometer compared to private cars.\n"
                "- **Carpool or Rideshare:** Share rides with colleagues or friends to split emissions.\n"
                "- **Vehicle Maintenance:** Keep tires inflated properly (improves fuel economy by 3%) and service your engine regularly.\n"
                "- **Fly Less:** Aviation has an enormous carbon density. Consider trains for regional trips or offset your flights."
            )
        elif any(k in prompt_lower for k in ["electricity", "energy", "power", "utility", "appliance", "solar", "heating", "cooling", "ac"]):
            return (
                "💡 **How to Reduce Home Energy & Electricity Emissions:**\n"
                "- **Unplug Phantom Loads:** Standby energy (electronics plugged in but idle) accounts for 5-10% of home electricity. Use smart power strips.\n"
                "- **Switch to LEDs:** LED bulbs use 75-80% less energy than incandescent bulbs and last up to 25 times longer.\n"
                "- **Optimize Thermostat:** Set your AC or heater 1-2 degrees closer to outside temperature. Every degree saves ~3% energy.\n"
                "- **Wash Cold:** Washing clothes in cold water saves 90% of the energy used by washing machines (which is spent heating the water).\n"
                "- **Install Solar Panels:** Generate your own clean, renewable power and feed excess back to the grid."
            )
        elif any(k in prompt_lower for k in ["water", "shower", "tap", "leak", "bath"]):
            return (
                "💧 **How to Reduce Water Emissions:**\n"
                "- **Shorten Showers:** Cutting shower time to 5 minutes saves up to 40 liters of water (and the energy required to treat/heat it).\n"
                "- **Fix Leaks Immediately:** A single dripping faucet can waste over 11,000 liters of water per year.\n"
                "- **Low-Flow Fixtures:** Install aerators on faucets and low-flow showerheads to reduce consumption by up to 50%.\n"
                "- **Rainwater Harvesting:** Collect rainwater for watering plants and gardens instead of using treated tap water."
            )
        elif any(k in prompt_lower for k in ["food", "diet", "meat", "vegan", "vegetarian", "beef", "eating", "meal"]):
            return (
                "🥗 **How to Reduce Food & Diet Emissions:**\n"
                "- **Eat More Plant-Based:** A vegan diet has 75% lower emissions than a high-meat diet. Try going meatless for 2-3 days a week.\n"
                "- **Choose Poultry/Fish over Beef:** Beef produces 27 kg of CO₂ per kg of meat, compared to 6 kg for chicken and 0.8 kg for tofu.\n"
                "- **Zero Food Waste:** Plan meals in advance, freeze leftovers, and store food properly. Landfilled food waste decays into methane.\n"
                "- **Eat Local & Seasonal:** Buying local cuts down on 'food miles' (emissions from transporting food across the globe)."
            )
        elif any(k in prompt_lower for k in ["waste", "recycle", "compost", "plastic", "trash", "landfill"]):
            return (
                "🗑️ **How to Reduce Waste Emissions:**\n"
                "- **Compost Organic Scraps:** Food and yard waste in landfills produces methane. Composting converts it into nutrient-rich soil.\n"
                "- **Avoid Single-Use Plastics:** Switch to reusable shopping bags, water bottles, coffee mugs, and food containers.\n"
                "- **Recycle Correctly:** Know your local recycling rules. Clean containers before recycling to avoid contaminating the batch.\n"
                "- **Buy Less & Repair:** Extend the lifespan of electronics, clothes, and furniture. Manufacturing new goods is highly carbon-intensive."
            )
        else:
            # General fallback to highest sector
            if not latest_calc:
                return (
                    "To give you personalized reduction tips, please complete your first calculation in the **Carbon Calculator** tab! In the meantime, here are 3 quick actions:\n"
                    "1. 🚶 **Swap 2-3 car trips/week** for walking, cycling, or public transport.\n"
                    "2. 💡 **Unplug idle chargers and electronics** to stop phantom electricity draws.\n"
                    "3. 🥗 **Have a meat-free day** once or twice a week to cut your dietary carbon footprint."
                )
            sectors = {"Transport": latest_calc['transport'], "Electricity": latest_calc['electricity'],
                       "Water": latest_calc['water'], "Food": latest_calc['food'], "Waste": latest_calc['waste']}
            highest_sector = max(sectors, key=sectors.get)
            highest_val = sectors[highest_sector]
            tips = f"I analyzed your latest calculation for **{latest_calc['month']}**. Your highest emission source is **{highest_sector}** ({highest_val} kg CO₂).\n\nTailored strategies:\n"
            if highest_sector == "Transport":
                tips += "- **Commute Greener:** Swap 2-3 car trips/week with public transit, bicycling, or walking.\n- **Carpooling:** Share rides to split emissions.\n- **Maintain Vehicle:** Proper tire inflation improves fuel efficiency by up to 3%."
            elif highest_sector == "Electricity":
                tips += "- **Unplug Phantom Loads:** Standby power costs up to 10% of your bill.\n- **Upgrade to LEDs:** LED bulbs use 75% less energy and last 25× longer.\n- **Solar Transition:** Consider solar panels or green power from your utility provider."
            elif highest_sector == "Water":
                tips += "- **Shorten Showers:** Keep showers under 5 minutes.\n- **Fix Leaks:** A dripping faucet wastes over 11,000 liters/year.\n- **Cold Wash:** Heating water accounts for 90% of washing machine energy."
            elif highest_sector == "Food":
                tips += "- **Meatless Days:** Swap meat for legumes and tofu. Livestock farming generates ~15% of global emissions.\n- **Buy Local & Seasonal:** Reduces transport emissions.\n- **Zero Food Waste:** Plan meals, freeze leftovers, and compost scraps."
            else:
                tips += "- **Compost Organic Waste:** Composting prevents landfill methane.\n- **Say No to Plastics:** Use reusable bags/cups.\n- **Recycle Correctly:** Sort paper, metal, and glass."
            return tips

    # 4. Carbon Footprint General
    if "carbon footprint" in prompt_lower or "footprint" in prompt_lower:
        return "A **Carbon Footprint** is the total greenhouse gases generated by our actions. The global average is ~4 tons/person annually. On EcoHub, we track it across 5 categories: Transportation, Electricity, Water, Food, and Waste. To avoid a 2°C rise, we must reduce the average under 2 tons by 2050! 🌱"

    # 5. Carbon Score Explainers
    elif "carbon score" in prompt_lower or "explain my carbon score" in prompt_lower:
        if not latest_calc:
            return "Your **Carbon Score** is computed monthly:\n- 🟢 **Green (Low):** Under 200 kg CO₂/month\n- 🟡 **Yellow (Moderate):** 200–500 kg CO₂/month\n- 🔴 **Red (High):** Over 500 kg CO₂/month\n\nGo to the **Calculator** tab to log your first calculation!"
        score = latest_calc['score_category']
        total = latest_calc['total_emissions']
        month = latest_calc['month']
        if score == "Green":
            return f"🌟 **Fantastic!** Your score for **{month}** is **Green** ({total} kg CO₂). You're well below the global average. Keep walking/biking, eating plant-based, and minimising electricity waste!"
        elif score == "Yellow":
            return f"⚠️ **Good Effort!** Your score for **{month}** is **Yellow** ({total} kg CO₂). Small changes — fewer car trips, 2–3 meatless meals/week, unplugging idle appliances — can move you into the Green zone!"
        else:
            return f"🚨 **High Footprint!** Your score for **{month}** is **Red** ({total} kg CO₂). Focus on your highest emission category from the Dashboard and take on one eco challenge daily to start reducing."

    # 6. Dashboard
    elif "dashboard" in prompt_lower or "explain my dashboard" in prompt_lower:
        return "Your **Dashboard** shows:\n1. **Emissions Overview:** Monthly carbon footprint summary\n2. **Carbon Score:** Green/Yellow/Red status\n3. **Emission Sources:** Pie chart of your top emission habits\n4. **Emissions Trend:** Line graph of your progress over time\n5. **ML Predictions:** Scikit-learn forecasts for future months"

    # 7. Sustainability / General Tips
    elif any(k in prompt_lower for k in ["sustainability", "sustainable", "sustainable lifestyle tips", "tips"]):
        return ECO_RESPONSES["top 10 sustainable living tips"]

    # 8. Food/Diet (non-reduction)
    elif any(k in prompt_lower for k in ["food", "diet", "meat", "vegan", "vegetarian"]) and not any(k in prompt_lower for k in ["points", "history", "logs", "records", "calculation"]):
        return "🥗 **Food & Diet Emissions:**\n- **Vegan:** ~60 kg CO₂/month (lowest impact)\n- **Vegetarian:** ~120 kg CO₂/month\n- **Non-Vegetarian:** ~250 kg CO₂/month\n\n*Tip:* Swap beef (27 kg CO₂/kg) for tofu (0.8 kg CO₂/kg) to instantly cut food emissions!"

    # 9. Transport (non-reduction)
    elif any(k in prompt_lower for k in ["transport", "car", "commute", "flight", "bike", "bus", "train"]) and not any(k in prompt_lower for k in ["points", "history", "logs", "records", "calculation"]):
        return "🚗 **Transportation Emissions:**\n- Car: **0.18 kg CO₂/km**\n- Motorcycle: **0.10 kg CO₂/km**\n- Bus: **0.08 kg CO₂/km**\n- Train: **0.04 kg CO₂/km**\n- Flight: **90 kg CO₂/hour**\n\n*Tip:* Bus/train reduces emissions by 50%+ vs driving!"

    # 10. Electricity / Energy (non-reduction)
    elif any(k in prompt_lower for k in ["electricity", "energy", "power"]) and not any(k in prompt_lower for k in ["points", "history", "logs", "records", "calculation"]):
        return "💡 **Electricity Impact:**\nGrid electricity carries **0.85 kg CO₂/kWh**. Unplugging phantom loads, upgrading to LEDs (75% less energy), and installing solar panels can dramatically cut your domestic footprint."

    # 11. Water (non-reduction)
    elif any(k in prompt_lower for k in ["water", "shower"]) and not any(k in prompt_lower for k in ["points", "history", "logs", "records", "calculation"]):
        return "💧 **Water Footprint:**\nWater usage: **0.0003 kg CO₂/liter** (energy for treatment & distribution). To reduce: showers under 5 min, fix leaky faucets (saves 11,000+ liters/year), and use cold wash cycles."

    # 12. Receipt Analyzer
    elif any(k in prompt_lower for k in ["receipt", "scanner", "ocr", "analyzer"]):
        return "🧾 **Receipt Carbon Analyzer:**\nUpload a shopping receipt image or PDF. Our OpenCV module preprocesses it, hybrid OCR extracts the items, and they're fuzzy-matched against our carbon factor database to compute a **Shopping Eco Score** (out of 100) with green alternatives suggested!"

    # 13. AI Forecast
    elif any(k in prompt_lower for k in ["forecast", "prediction", "ml", "machine learning", "ai forecast"]):
        return "🧠 **AI Emission Forecast:**\nEcoHub uses `scikit-learn` **Linear Regression** trained on your historical data. It calculates the emission trend slope and projects the next 3 months with an R² confidence score. Navigate to **AI Emission Forecast** in the sidebar to see your personalized projection!"

    # 14. Eco Challenge
    elif any(k in prompt_lower for k in ["challenge", "eco challenge"]):
        return get_eco_challenge_tip()

    # 15. Climate change / global warming
    elif any(k in prompt_lower for k in ["climate change", "global warming"]):
        return ECO_RESPONSES["climate change"]

    # 16. General predefined lookup
    for key, val in ECO_RESPONSES.items():
        if key in prompt_lower:
            return val

    # 17. Wikipedia dynamic search integration (General Knowledge Backup)
    words = prompt_lower.split()
    question_starters = ["what", "who", "how", "explain", "tell", "define", "where", "why", "meaning", "is", "are", "can", "about"]
    is_question = any(q in prompt_lower for q in question_starters) or len(words) >= 2
    
    if is_question:
        query = extract_wiki_query(prompt)
        title, summary = get_wikipedia_summary(query)
        if title and summary:
            return (
                f"📚 **According to Wikipedia ({title}):**\n\n"
                f"{summary}\n\n"
                f"*Source: [Wikipedia page for {title}](https://en.wikipedia.org/wiki/{title.replace(' ', '_')})*"
            )

    # 18. Smart Fallback with suggestions
    return (
        "I'm not sure about that specific question, but here are **3 practical eco tips** to get started:\n\n"
        "1. 🚶 **Walk or cycle** for trips under 3 km — saves ~0.18 kg CO₂ per km vs driving.\n"
        "2. 🥗 **Replace one meat meal per day** with plant-based food — cuts food emissions by up to 40%.\n"
        "3. 💡 **Unplug idle electronics** — phantom loads account for 5–10% of home electricity use.\n\n"
        "As an AI sustainability assistant, you can ask me about:\n"
        "- **Your Data:** `my score`, `my points`, `my history`, `my badges`, `my goals`, `my challenges`\n"
        "- **Carbon Reduction:** `how to reduce transport`, `how to reduce waste`, `how to reduce food emissions`\n"
        "- **General Science:** Ask any general question (e.g. `what is geothermal energy`, `who is Greta Thunberg`) to search Wikipedia!"
    )

def render_chatbot_page():
    user = st.session_state.user

    st.markdown("<h2 style='color:#111827;'>💬 EcoBot - AI Sustainability Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#374151;font-size:15px;margin-bottom:20px;'>Ask EcoBot anything about climate change, your carbon score, or sustainability tips.</p>", unsafe_allow_html=True)

    # Initialize session_state chat messages from DB on first load
    if "chat_messages" not in st.session_state:
        history = db.get_chatbot_history(user['id'])
        st.session_state.chat_messages = [
            {"role": "user" if c['sender'] == "user" else "assistant", "content": c['message']}
            for c in history
        ]

    # Display all messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # Quick question buttons
    st.markdown("##### 💡 Quick Questions:")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    clicked_prompt = None
    with col1:
        if st.button("How can I reduce my carbon footprint?", key="q1", use_container_width=True):
            clicked_prompt = "How can I reduce my carbon footprint?"
    with col2:
        if st.button("Explain my carbon score.", key="q2", use_container_width=True):
            clicked_prompt = "Explain my carbon score."
    with col3:
        if st.button("Give me an eco challenge.", key="q3", use_container_width=True):
            clicked_prompt = "Give me an eco challenge."
    with col4:
        if st.button("Sustainable lifestyle tips.", key="q4", use_container_width=True):
            clicked_prompt = "Sustainable lifestyle tips."
    with col5:
        if st.button("Explain my dashboard.", key="q5", use_container_width=True):
            clicked_prompt = "Explain my dashboard."
    with col6:
        if st.button("Clear Chat History", key="q6", use_container_width=True):
            db.clear_chatbot_history(user['id'])
            st.session_state.chat_messages = []
            st.rerun()

    # Chat input
    user_input = st.chat_input("Ask EcoBot a question...")
    final_prompt = clicked_prompt or user_input

    if final_prompt:
        # Append and display user message
        st.session_state.chat_messages.append({"role": "user", "content": final_prompt})
        db.add_chatbot_message(user['id'], "user", final_prompt)

        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(final_prompt)

        # Generate bot response
        bot_response = generate_bot_response(user['id'], final_prompt)

        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(bot_response)

        # Append bot message to session state and DB
        st.session_state.chat_messages.append({"role": "assistant", "content": bot_response})
        db.add_chatbot_message(user['id'], "bot", bot_response)

        st.rerun()
