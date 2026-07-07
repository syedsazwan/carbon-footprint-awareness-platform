import streamlit as st
import database as db
from datetime import datetime
import textwrap

def clean_html(html_str: str) -> str:
    """Strip leading and trailing whitespace from each line of HTML to prevent Streamlit markdown code-block bugs."""
    return "\n".join(line.strip() for line in html_str.splitlines())

RECOMMENDATIONS = {
    "Transport": [
        {"text": "Walk or bike for short trips under 2km", "points": 15, "icon": "🚶", "difficulty": "Easy"},
        {"text": "Use public transit (bus/train) for your daily commute", "points": 30, "icon": "🚌", "difficulty": "Medium"},
        {"text": "Carpool or share a ride with colleagues/friends", "points": 20, "icon": "🚗", "difficulty": "Easy"},
        {"text": "Maintain optimal tire pressure to save fuel", "points": 10, "icon": "🔧", "difficulty": "Easy"}
    ],
    "Electricity": [
        {"text": "Replace 5 incandescent bulbs with energy-efficient LEDs", "points": 25, "icon": "💡", "difficulty": "Easy"},
        {"text": "Unplug all chargers and standby appliances tonight", "points": 10, "icon": "🔌", "difficulty": "Easy"},
        {"text": "Set your AC temperature to 24°C or above", "points": 15, "icon": "🌡️", "difficulty": "Easy"},
        {"text": "Wash laundry in cold water and air-dry clothes", "points": 15, "icon": "👕", "difficulty": "Easy"}
    ],
    "Water": [
        {"text": "Limit shower time to exactly 5 minutes", "points": 15, "icon": "🚿", "difficulty": "Easy"},
        {"text": "Fix a leaky faucet or pipe in the house", "points": 20, "icon": "💧", "difficulty": "Medium"},
        {"text": "Use a bucket instead of a hose to clean vehicles", "points": 20, "icon": "🪣", "difficulty": "Easy"},
        {"text": "Collect rainwater for watering house plants", "points": 25, "icon": "🌧️", "difficulty": "Medium"}
    ],
    "Food": [
        {"text": "Commit to a completely Meatless Day", "points": 20, "icon": "🥗", "difficulty": "Easy"},
        {"text": "Have a fully Vegan day (no animal products)", "points": 30, "icon": "🍎", "difficulty": "Medium"},
        {"text": "Buy groceries from local farmer's markets", "points": 15, "icon": "🌽", "difficulty": "Easy"},
        {"text": "Plan weekly meals to ensure zero food waste", "points": 15, "icon": "🍱", "difficulty": "Medium"}
    ],
    "Waste": [
        {"text": "Start composting fruit/vegetable scraps and coffee grounds", "points": 30, "icon": "🍂", "difficulty": "Medium"},
        {"text": "Avoid buying any single-use plastic bottles or cups today", "points": 10, "icon": "🥤", "difficulty": "Easy"},
        {"text": "Sort and recycle paper, glass, and aluminum containers", "points": 15, "icon": "♻️", "difficulty": "Easy"},
        {"text": "Carry a reusable canvas bag for shopping", "points": 10, "icon": "🛍️", "difficulty": "Easy"}
    ]
}

DIFFICULTY_COLORS = {"Easy": "#22C55E", "Medium": "#FBBF24", "Hard": "#EF4444"}
DIFFICULTY_BG = {"Easy": "#F0FDF4", "Medium": "#FFFBEB", "Hard": "#FEF2F2"}
CATEGORY_ICONS = {"Transport": "🚗", "Electricity": "⚡", "Water": "💧", "Food": "🥗", "Waste": "♻️"}
CATEGORY_COLORS = {"Transport": "#3B82F6", "Electricity": "#FBBF24", "Water": "#06B6D4", "Food": "#22C55E", "Waste": "#A78BFA"}
CATEGORY_BG = {"Transport": "#DBEAFE", "Electricity": "#FEF3C7", "Water": "#CFFAFE", "Food": "#DCFCE7", "Waste": "#EDE9FE"}

def render_recommendations_page():
    """Render the premium personalized recommendations and challenges interface."""
    user = st.session_state.user

    st.markdown(clean_html("""
        <div style="margin-bottom:24px;">
            <h2 style="color:#111827;margin:0 0 6px;font-size:1.7rem;">⚡ Action & Challenges</h2>
            <p style="color:#6B7280;font-size:14px;margin:0;">Complete eco-actions to reduce your carbon footprint and earn Eco Points!</p>
        </div>
    """), unsafe_allow_html=True)

    # Fetch data
    history = db.get_carbon_history(user['id'])
    latest_calc = history[-1] if history else None
    today = datetime.now().strftime("%Y-%m-%d")
    completed = db.get_completed_challenges(user['id'])
    completed_today_texts = {c['challenge_text'] for c in completed if c['completed_date'] == today}

    if latest_calc:
        sectors = {
            "Transport": latest_calc['transport'],
            "Electricity": latest_calc['electricity'],
            "Water": latest_calc['water'],
            "Food": latest_calc['food'],
            "Waste": latest_calc['waste']
        }
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)
        priority_sector = sorted_sectors[0][0]
        categories_to_show = [priority_sector] + [s for s, _ in sorted_sectors[1:]]

        st.markdown(clean_html(f"""
            <div class="eco-card" style="border-left:4px solid #22C55E;background:linear-gradient(135deg,#F0FDF4,#DCFCE7);margin-bottom:24px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="font-size:36px;">🎯</div>
                    <div>
                        <h4 style="color:#111827;margin:0 0 4px;">Tailored Action Plan</h4>
                        <p style="color:#6B7280;margin:0;font-size:13px;">Based on your <b style="color:#111827;">{latest_calc['month']}</b> report, your highest emission sector is <b style="color:#EF4444;">{sorted_sectors[0][0]}</b> ({sorted_sectors[0][1]} kg CO₂). Focus on these challenges for maximum impact!</p>
                    </div>
                </div>
            </div>
        """), unsafe_allow_html=True)
    else:
        st.info("💡 Log a monthly calculation to get personalized priorities!")
        categories_to_show = list(RECOMMENDATIONS.keys())
        priority_sector = None

    # Render each category
    for category in categories_to_show:
        is_priority = category == priority_sector
        cat_color = CATEGORY_COLORS[category]
        cat_bg = CATEGORY_BG[category]
        cat_icon = CATEGORY_ICONS[category]

        priority_badge = '<span style="background:#FEE2E2;color:#991B1B;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px;">🔥 PRIORITY</span>' if is_priority else ''

        st.markdown(clean_html(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:28px 0 12px;">
                <div style="width:34px;height:34px;background:{cat_bg};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">{cat_icon}</div>
                <h3 style="color:#111827;margin:0;font-size:16px;">{category} Challenges{priority_badge}</h3>
            </div>
        """), unsafe_allow_html=True)

        items = RECOMMENDATIONS[category]
        col1, col2 = st.columns(2)

        for idx, item in enumerate(items):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                is_completed = item['text'] in completed_today_texts
                diff = item.get('difficulty', 'Easy')
                diff_color = DIFFICULTY_COLORS[diff]
                diff_bg = DIFFICULTY_BG[diff]

                card_border = "#22C55E" if is_completed else "#E5E7EB"
                card_bg = "#F0FDF4" if is_completed else "#FFFFFF"
                done_badge = '<span style="background:#DCFCE7;color:#166534;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;">✔ Done</span>' if is_completed else ''

                st.markdown(clean_html(f"""
                    <div style="background:{card_bg};border:1.5px solid {card_border};border-radius:16px;padding:16px;margin-bottom:12px;
                         box-shadow:0 1px 4px rgba(0,0,0,0.05);transition:all 0.2s ease;">
                        <div style="display:flex;align-items:flex-start;gap:12px;">
                            <div style="width:44px;height:44px;background:{cat_bg};border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;">{item['icon']}</div>
                            <div style="flex:1;">
                                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;flex-wrap:wrap;">
                                    <span style="background:{diff_bg};color:{diff_color};font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;">{diff}</span>
                                    {done_badge}
                                </div>
                                <p style="margin:0 0 8px;font-size:13px;color:#111827;font-weight:500;line-height:1.4;">{item['text']}</p>
                                <div style="display:flex;align-items:center;gap:6px;">
                                    <span style="background:#FFFBEB;color:#92400E;font-size:12px;font-weight:700;padding:3px 10px;border-radius:20px;">🪙 +{item['points']} pts</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """), unsafe_allow_html=True)

                if is_completed:
                    st.button("✓ Completed Today", key=f"btn_{category}_{idx}", disabled=True, use_container_width=True)
                else:
                    if st.button(f"Mark Complete (+{item['points']} pts)", key=f"btn_{category}_{idx}", use_container_width=True):
                        success, msg = db.complete_challenge(
                            user_id=user['id'],
                            challenge_text=item['text'],
                            challenge_type="recommendation",
                            points=item['points']
                        )
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # ── Daily & Weekly Challenges ──
    st.markdown("<hr style='margin:32px 0 24px;'>", unsafe_allow_html=True)
    st.markdown(clean_html("""
        <div style="margin-bottom:16px;">
            <h3 style="color:#111827;margin:0 0 4px;">🏆 Daily & Weekly Challenges</h3>
            <p style="color:#6B7280;font-size:13px;margin:0;">Extra challenges to boost your Eco Points</p>
        </div>
    """), unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#111827;margin:0 0 16px;'>⚡ Daily Challenges</h4>", unsafe_allow_html=True)
        daily_challenges = [
            {"text": "Walk instead of using a vehicle", "points": 10, "icon": "🚶"},
            {"text": "Save electricity (turn off unused appliances)", "points": 15, "icon": "💡"},
            {"text": "Carry reusable water bottles", "points": 5, "icon": "💧"}
        ]
        for idx, dc in enumerate(daily_challenges):
            is_done = dc['text'] in completed_today_texts
            done_txt = '<span style="background:#DCFCE7;color:#166534;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:6px;">✔ Done</span>' if is_done else ''
            st.markdown(clean_html(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:12px;background:#F8FAFC;border-radius:12px;margin-bottom:8px;border:1px solid #E5E7EB;">
                    <span style="font-size:22px;">{dc['icon']}</span>
                    <div style="flex:1;">
                        <p style="margin:0;font-size:13px;color:#111827;font-weight:500;">{dc['text']}{done_txt}</p>
                        <span style="font-size:11px;color:#FBBF24;font-weight:700;">🪙 +{dc['points']} pts</span>
                    </div>
                </div>
            """), unsafe_allow_html=True)
            if is_done:
                st.button("✓ Done Today", key=f"dc_{idx}", disabled=True, use_container_width=True)
            else:
                if st.button("Complete", key=f"dc_{idx}", use_container_width=True):
                    success, msg = db.complete_challenge(user['id'], dc['text'], "daily", dc['points'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#111827;margin:0 0 16px;'>🌟 Weekly Challenges</h4>", unsafe_allow_html=True)
        weekly_challenges = [
            {"text": "Use public transport for all commutes", "points": 50, "icon": "🚌"},
            {"text": "Reduce plastic waste (no plastics for a week)", "points": 40, "icon": "♻️"}
        ]
        for idx, wc in enumerate(weekly_challenges):
            is_done = any(c['challenge_text'] == wc['text'] for c in completed if (datetime.now() - datetime.strptime(c['completed_date'], "%Y-%m-%d")).days < 7)
            done_txt = '<span style="background:#DCFCE7;color:#166534;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:6px;">✔ Done</span>' if is_done else ''
            st.markdown(clean_html(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:12px;background:#F8FAFC;border-radius:12px;margin-bottom:8px;border:1px solid #E5E7EB;">
                    <span style="font-size:22px;">{wc['icon']}</span>
                    <div style="flex:1;">
                        <p style="margin:0;font-size:13px;color:#111827;font-weight:500;">{wc['text']}{done_txt}</p>
                        <span style="font-size:11px;color:#FBBF24;font-weight:700;">🪙 +{wc['points']} pts</span>
                    </div>
                </div>
            """), unsafe_allow_html=True)
            if is_done:
                st.button("✓ Done This Week", key=f"wc_{idx}", disabled=True, use_container_width=True)
            else:
                if st.button("Complete Weekly", key=f"wc_{idx}", use_container_width=True):
                    success, msg = db.complete_challenge(user['id'], wc['text'], "weekly", wc['points'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
