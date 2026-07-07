import streamlit as st
import database as db
import utils
from authentication import render_login_page, render_register_page, render_profile_tab
from carbon_calculator import render_calculator_page
from dashboard import render_dashboard_page
from recommendations import render_recommendations_page
from chatbot import render_chatbot_page
from ml_model import render_ml_page
from receipt_analyzer import render_receipt_analyzer
from admin import render_admin_panel
from reports import render_reports_page

def main():
    st.set_page_config(
        page_title="EcoHub | Carbon Footprint Platform",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    db.init_db()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

    if not st.session_state.logged_in:
        from authentication import _render_hero_banner
        _render_hero_banner()
        auth_tab1, auth_tab2 = st.tabs(["🔐 Sign In", "📝 Register"])
        with auth_tab1:
            render_login_page()
        with auth_tab2:
            render_register_page()
        return

    # Call init_page_style ONLY when logged in
    utils.init_page_style()

    user = st.session_state.user
    _pts = db.get_eco_points(user['id'])

    # ── Eco Level calculation ──
    if _pts >= 500:
        _level = "Champion"
        _level_icon = "🏆"
        _level_color = "#FBBF24"
        _xp_pct = min(100, int((_pts - 500) / 5))
    elif _pts >= 200:
        _level = "Warrior"
        _level_icon = "🛡️"
        _level_color = "#3B82F6"
        _xp_pct = int((_pts - 200) / 3)
    else:
        _level = "Rookie"
        _level_icon = "🌱"
        _level_color = "#22C55E"
        _xp_pct = int(_pts / 2)

    _xp_pct = min(_xp_pct, 100)

    # ── Sidebar ──
    st.sidebar.markdown(f"""
        <style>
            @keyframes floatEarth {{
                0%,100% {{ transform: translateY(0px) rotate(0deg); }}
                50% {{ transform: translateY(-6px) rotate(3deg); }}
            }}
            @keyframes glowPulse {{
                0%,100% {{ box-shadow: 0 0 20px rgba(34,197,94,0.3), 0 0 40px rgba(15,157,88,0.15); }}
                50% {{ box-shadow: 0 0 30px rgba(34,197,94,0.5), 0 0 60px rgba(15,157,88,0.25); }}
            }}
            @keyframes xpFill {{
                from {{ width: 0%; }}
                to {{ width: {_xp_pct}%; }}
            }}
            @keyframes leafFloat1 {{
                0%,100% {{ transform: translate(0,0) rotate(0deg); opacity:0.06; }}
                33% {{ transform: translate(8px,-12px) rotate(15deg); opacity:0.10; }}
                66% {{ transform: translate(-5px,-8px) rotate(-10deg); opacity:0.07; }}
            }}
            @keyframes leafFloat2 {{
                0%,100% {{ transform: translate(0,0) rotate(0deg); opacity:0.05; }}
                50% {{ transform: translate(-10px,-15px) rotate(-20deg); opacity:0.09; }}
            }}
            @keyframes particleDrift {{
                0% {{ transform: translateY(0) scale(1); opacity:0.4; }}
                100% {{ transform: translateY(-40px) scale(0.3); opacity:0; }}
            }}
            @keyframes cardHoverLift {{
                to {{ transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.2); }}
            }}
            .sb-user-card:hover {{ animation: cardHoverLift 0.25s ease forwards; }}
        </style>

        <!-- Background leaf illustrations -->
        <div style="position:fixed;top:0;left:0;width:270px;height:100vh;pointer-events:none;overflow:hidden;z-index:0;">
            <div style="position:absolute;top:10%;left:5%;font-size:80px;animation:leafFloat1 8s ease-in-out infinite;">🍃</div>
            <div style="position:absolute;top:55%;left:70%;font-size:60px;animation:leafFloat2 11s ease-in-out infinite 2s;">🌿</div>
            <div style="position:absolute;top:78%;left:10%;font-size:50px;animation:leafFloat1 9s ease-in-out infinite 4s;">🍀</div>
            <!-- Glowing particles -->
            <div style="position:absolute;top:30%;left:30%;width:4px;height:4px;background:#FBBF24;border-radius:50%;animation:particleDrift 4s ease-out infinite;"></div>
            <div style="position:absolute;top:60%;left:60%;width:3px;height:3px;background:#22C55E;border-radius:50%;animation:particleDrift 5s ease-out infinite 1.5s;"></div>
            <div style="position:absolute;top:20%;left:80%;width:3px;height:3px;background:#fff;border-radius:50%;animation:particleDrift 6s ease-out infinite 3s;"></div>
        </div>

        <!-- Logo Section -->
        <div style="position:relative;z-index:1;padding:28px 16px 18px;text-align:center;">
            <div style="display:inline-block;animation:floatEarth 4s ease-in-out infinite;filter:drop-shadow(0 6px 18px rgba(0,0,0,0.3));font-size:56px;line-height:1;">🌍</div>
            <div style="font-size:24px;font-weight:900;color:#FFFFFF;letter-spacing:-0.5px;margin-top:10px;text-shadow:0 2px 8px rgba(0,0,0,0.2);">EcoHub</div>
            <div style="font-size:10px;color:rgba(255,255,255,0.7);letter-spacing:2.5px;text-transform:uppercase;margin-top:3px;font-weight:500;">Carbon Footprint Platform</div>
            <div style="width:40px;height:2px;background:rgba(255,255,255,0.3);border-radius:2px;margin:12px auto 0;"></div>
        </div>

        <!-- User Card -->
        <div class="sb-user-card" style="position:relative;z-index:1;margin:0 12px 14px;background:rgba(255,255,255,0.13);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.25);border-radius:20px;padding:16px;transition:all 0.25s ease;cursor:default;">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:44px;height:44px;background:linear-gradient(135deg,rgba(255,255,255,0.35),rgba(255,255,255,0.15));border:2px solid rgba(255,255,255,0.4);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;animation:glowPulse 3s ease-in-out infinite;">👤</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:13px;font-weight:800;color:#FFFFFF;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:0 1px 4px rgba(0,0,0,0.15);">{user['name']}</div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-top:1px;">@{user['username']}</div>
                </div>
                <div style="font-size:9px;background:rgba(34,197,94,0.35);border:1px solid rgba(34,197,94,0.5);color:#FFFFFF;padding:3px 9px;border-radius:20px;font-weight:700;letter-spacing:0.5px;flex-shrink:0;">{user['role'].upper()}</div>
            </div>
        </div>

        <!-- Eco Points Card -->
        <div style="position:relative;z-index:1;margin:0 12px 18px;background:rgba(255,255,255,0.11);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.2);border-radius:20px;padding:14px 16px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-size:9px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:4px;">🪙 Eco Points</div>
                    <div style="font-size:26px;font-weight:900;color:#FBBF24;line-height:1;text-shadow:0 2px 8px rgba(251,191,36,0.4);">{_pts}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:9px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:4px;">🏅 Level</div>
                    <div style="font-size:15px;font-weight:800;color:{_level_color};text-shadow:0 2px 6px rgba(0,0,0,0.2);">{_level_icon} {_level}</div>
                </div>
            </div>
            <div style="margin-top:12px;">
                <div style="display:flex;justify-content:space-between;font-size:10px;color:rgba(255,255,255,0.55);margin-bottom:5px;">
                    <span>XP Progress</span><span style="color:#FBBF24;font-weight:700;">{_xp_pct} / 100 XP</span>
                </div>
                <div style="background:rgba(255,255,255,0.15);border-radius:100px;height:7px;overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#FBBF24,#F59E0B);border-radius:100px;height:7px;width:{_xp_pct}%;animation:xpFill 1.2s ease-out forwards;box-shadow:0 0 8px rgba(251,191,36,0.5);"></div>
                </div>
            </div>
        </div>

        <!-- Navigation Label -->
        <div style="position:relative;z-index:1;padding:0 16px 8px;font-size:9px;color:rgba(255,255,255,0.45);text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">Navigation</div>
    """, unsafe_allow_html=True)

    nav_options = [
        "📊 Dashboard",
        "🌱 Carbon Calculator",
        "⚡ Action & Challenges",
        "💬 EcoBot AI Chat",
        "🧠 AI Emission Forecast",
        "🧾 Receipt Carbon Analyzer",
        "👤 Profile Settings",
        "📄 Export PDF Report"
    ]

    if user['role'] == 'admin':
        nav_options.append("⚙️ Admin Panel")

    choice = st.sidebar.radio("", nav_options, label_visibility="collapsed")

    # ── Bottom Motivation Card ──
    st.sidebar.markdown(f"""
        <div style="position:relative;z-index:1;margin:10px 12px 16px;background:rgba(255,255,255,0.11);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.2);border-radius:20px;padding:16px;overflow:hidden;">
            <div style="position:absolute;top:-8px;right:-8px;font-size:42px;opacity:0.12;">🌿</div>
            <div style="position:absolute;bottom:-6px;left:-4px;font-size:36px;opacity:0.10;">🍃</div>
            <div style="position:relative;z-index:1;">
                <div style="font-size:13px;font-weight:800;color:#FBBF24;margin-bottom:5px;">🏆 Keep Going!</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.75);line-height:1.5;margin-bottom:10px;font-style:italic;">&ldquo;You&rsquo;re making a real difference for our planet.&rdquo;</div>
                <div style="font-size:9px;color:rgba(255,255,255,0.5);margin-bottom:4px;display:flex;justify-content:space-between;">
                    <span>{_level_icon} {_level}</span><span style="color:#FBBF24;font-weight:700;">{_pts} pts</span>
                </div>
                <div style="background:rgba(255,255,255,0.15);border-radius:100px;height:5px;overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#22C55E,#FBBF24);border-radius:100px;height:5px;width:{_xp_pct}%;box-shadow:0 0 6px rgba(34,197,94,0.4);"></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.12);margin:0 12px 12px;'>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Successfully logged out.")
        st.rerun()

    # ── Route pages ──
    if choice == "📊 Dashboard":
        render_dashboard_page()
    elif choice == "🌱 Carbon Calculator":
        render_calculator_page()
    elif choice == "⚡ Action & Challenges":
        render_recommendations_page()
    elif choice == "💬 EcoBot AI Chat":
        render_chatbot_page()
    elif choice == "🧠 AI Emission Forecast":
        render_ml_page()
    elif choice == "🧾 Receipt Carbon Analyzer":
        render_receipt_analyzer()
    elif choice == "👤 Profile Settings":
        render_profile_tab()
    elif choice == "⚙️ Admin Panel":
        render_admin_panel()
    elif choice == "📄 Export PDF Report":
        render_reports_page()

if __name__ == "__main__":
    main()
