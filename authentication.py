import streamlit as st
import database as db
from datetime import datetime
import base64
import os

def render_profile_tab():
    """Render the premium profile management interface."""
    user = st.session_state.user
    fresh_user = db.get_user_by_id(user['id'])
    if fresh_user:
        st.session_state.user = fresh_user
        user = fresh_user

    pts = user['eco_points']
    if pts >= 500:
        level = "Champion"
        level_icon = "🏆"
        level_color = "#FBBF24"
        xp_pct = min(100, int((pts - 500) / 5))
        next_level = "Max Level"
    elif pts >= 200:
        level = "Warrior"
        level_icon = "🛡️"
        level_color = "#3B82F6"
        xp_pct = int((pts - 200) / 3)
        next_level = f"{500 - pts} pts to Champion"
    else:
        level = "Rookie"
        level_icon = "🌱"
        level_color = "#22C55E"
        xp_pct = int(pts / 2)
        next_level = f"{200 - pts} pts to Warrior"

    xp_pct = min(xp_pct, 100)

    st.markdown("""
        <div style="margin-bottom:24px;">
            <h2 style="color:#111827;margin:0 0 6px;font-size:1.7rem;">👤 Profile Settings</h2>
            <p style="color:#6B7280;font-size:14px;margin:0;">Manage your sustainability profile and track your eco achievements.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#111827;margin:0 0 16px;'>✏️ Update Information</h4>", unsafe_allow_html=True)

        new_name = st.text_input("Full Name", value=user['name'], key="profile_name")
        new_email = st.text_input("Email Address", value=user['email'], key="profile_email")

        st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("<h5 style='color:#111827;margin:0 0 12px;font-size:13px;'>🔒 Change Password (Optional)</h5>", unsafe_allow_html=True)
        new_pass = st.text_input("New Password", type="password", placeholder="Leave blank to keep current", key="profile_password")
        confirm_pass = st.text_input("Confirm New Password", type="password", placeholder="Leave blank to keep current", key="profile_confirm_password")

        if st.button("💾 Save Changes", use_container_width=True):
            if not new_name or not new_email:
                st.error("Name and Email are required.")
            elif new_pass and new_pass != confirm_pass:
                st.error("Passwords do not match.")
            else:
                success, msg = db.update_user_profile(user['id'], new_name, new_email, new_pass if new_pass else None)
                if success:
                    st.success(msg)
                    st.session_state.user = db.get_user_by_id(user['id'])
                    st.rerun()
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # ── Sustainability ID Card ──
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0F9D58,#0B7A43);border-radius:20px;padding:28px;margin-bottom:16px;position:relative;overflow:hidden;">
                <div style="position:absolute;right:-20px;top:-20px;font-size:100px;opacity:0.08;">🌍</div>
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
                    <div style="width:60px;height:60px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;border:2px solid rgba(255,255,255,0.4);">👤</div>
                    <div>
                        <div style="font-size:18px;font-weight:800;color:#FFFFFF;">{user['name']}</div>
                        <div style="font-size:12px;color:rgba(255,255,255,0.75);">@{user['username']} · {user['role'].capitalize()}</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
                    <div style="background:rgba(255,255,255,0.12);border-radius:12px;padding:12px;text-align:center;">
                        <div style="font-size:10px;color:rgba(255,255,255,0.65);text-transform:uppercase;letter-spacing:0.8px;font-weight:600;margin-bottom:4px;">Eco Points</div>
                        <div style="font-size:22px;font-weight:800;color:#FBBF24;">🪙 {pts}</div>
                    </div>
                    <div style="background:rgba(255,255,255,0.12);border-radius:12px;padding:12px;text-align:center;">
                        <div style="font-size:10px;color:rgba(255,255,255,0.65);text-transform:uppercase;letter-spacing:0.8px;font-weight:600;margin-bottom:4px;">Eco Level</div>
                        <div style="font-size:18px;font-weight:800;color:{level_color};">{level_icon} {level}</div>
                    </div>
                </div>
                <div>
                    <div style="display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,0.7);margin-bottom:6px;">
                        <span>XP Progress</span><span>{next_level}</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.2);border-radius:100px;height:8px;">
                        <div style="background:#FBBF24;border-radius:100px;height:8px;width:{xp_pct}%;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── Badges ──
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#111827;margin:0 0 16px;'>🏅 Achievement Badges</h4>", unsafe_allow_html=True)
        badges = db.get_badges(user['id'])
        if badges:
            badge_icons = {
                "Eco Rookie": "🌱", "Carbon Cutter": "✂️", "Eco Warrior": "🛡️",
                "Green Champion": "🏆", "Energy Saver": "💡", "Water Guard": "💧"
            }
            badge_colors = {
                "Eco Rookie": "#DCFCE7", "Carbon Cutter": "#DBEAFE", "Eco Warrior": "#EDE9FE",
                "Green Champion": "#FEF3C7", "Energy Saver": "#FEF3C7", "Water Guard": "#CFFAFE"
            }
            cols = st.columns(min(len(badges), 3))
            for idx, badge in enumerate(badges):
                icon = badge_icons.get(badge['badge_name'], "🏅")
                bg = badge_colors.get(badge['badge_name'], "#F1F5F9")
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div style="background:{bg};border-radius:14px;padding:14px 10px;text-align:center;margin-bottom:8px;">
                            <div style="font-size:28px;margin-bottom:6px;">{icon}</div>
                            <div style="font-size:11px;font-weight:700;color:#111827;line-height:1.2;">{badge['badge_name']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align:center;padding:24px;">
                    <div style="font-size:36px;margin-bottom:8px;">🏅</div>
                    <p style="color:#6B7280;font-size:13px;">No badges yet. Complete challenges to earn badges!</p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def _render_hero_banner():
    """Render earth_banner.png as a full-page background cover with premium animations."""
    img_path = os.path.join(os.path.dirname(__file__), "image", "photo", "earth_banner.png")
    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        data_uri = f"data:image/png;base64,{b64}"
    except FileNotFoundError:
        data_uri = ""

    if data_uri:
        bg_css = f"background: linear-gradient(rgba(10, 25, 15, 0.4), rgba(5, 15, 8, 0.5)), url('{data_uri}') no-repeat center center fixed !important;"
    else:
        bg_css = "background: linear-gradient(135deg, #022c22 0%, #064e3b 50%, #065f46 100%) !important;"

    # Inject page styles
    st.markdown(f"""
        <style>
            /* Make the earth picture cover the entire page background */
            [data-testid="stAppViewContainer"] {{
                {bg_css}
                background-size: cover !important;
                background-attachment: fixed !important;
            }}
            
            [data-testid="stHeader"] {{
                background: transparent !important;
            }}
            
            /* Style the main page block container as the glassmorphic card */
            .main .block-container {{
                background: rgba(17, 24, 39, 0.75) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border-radius: 28px !important;
                padding: 40px 36px !important;
                box-shadow: 0 25px 60px rgba(0,0,0,0.65) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                max-width: 480px !important;
                margin: 4% auto !important;
                animation: fadeInUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
            }}
            
            [data-testid="stAppViewBlockContainer"] {{
                padding-top: 0 !important;
                max-width: 100% !important;
            }}

            /* Animations */
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(40px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @keyframes floatLogo {{
                0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                50% {{ transform: translateY(-10px) rotate(5deg); }}
            }}
            
            @keyframes textGlow {{
                0%, 100% {{ text-shadow: 0 0 10px rgba(34, 197, 94, 0.4), 0 0 20px rgba(34, 197, 94, 0.2); }}
                50% {{ text-shadow: 0 0 20px rgba(34, 197, 94, 0.7), 0 0 40px rgba(34, 197, 94, 0.4); }}
            }}

            /* Header Section Styling */
            .welcome-header {{
                text-align: center;
                margin-bottom: 1.5rem;
                animation: fadeInUp 0.8s ease-out forwards;
            }}
            
            .welcome-logo {{
                font-size: 72px;
                display: inline-block;
                animation: floatLogo 5s ease-in-out infinite;
                filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3));
                margin-bottom: 8px;
            }}
            
            .welcome-title {{
                font-size: 3.2rem;
                font-weight: 900;
                color: #FFFFFF;
                margin: 0;
                letter-spacing: -1.5px;
                animation: textGlow 4s ease-in-out infinite;
            }}
            
            .welcome-subtitle {{
                font-size: 1.25rem;
                color: rgba(255, 255, 255, 0.95);
                margin: 6px 0 0 0;
                font-weight: 500;
                letter-spacing: 0.5px;
            }}

            /* Glassmorphic Tabs TabList styling */
            .stTabs [data-baseweb="tab-list"] {{
                background: rgba(255, 255, 255, 0.08) !important;
                border-radius: 16px !important;
                padding: 6px !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                justify-content: center !important;
                max-width: 320px;
                margin: 0 auto 1.5rem !important;
                backdrop-filter: blur(8px) !important;
                -webkit-backdrop-filter: blur(8px) !important;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background: transparent !important;
                color: rgba(255, 255, 255, 0.7) !important;
                border: none !important;
                font-weight: 700 !important;
                font-size: 14px !important;
                padding: 10px 24px !important;
                border-radius: 12px !important;
                transition: all 0.25s ease !important;
            }}
            
            .stTabs [data-baseweb="tab"]:hover {{
                color: #FFFFFF !important;
            }}
            
            .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                background: #22C55E !important;
                color: #FFFFFF !important;
                box-shadow: 0 4px 14px rgba(34, 197, 94, 0.4) !important;
            }}

            /* Make stTabs and panels transparent */
            .stTabs, [data-testid="stTabPanel"] {{
                background: transparent !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                animation: none !important;
            }}

            /* Form Elements inside block container */
            .main .block-container .stTextInput input,
            .main .block-container .stTextInput > div > div > input {{
                background: rgba(255, 255, 255, 0.07) !important;
                border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 12px !important;
                height: 48px !important;
                color: #FFFFFF !important;
                caret-color: #22C55E !important;
                font-size: 15px !important;
                padding: 0 16px !important;
                box-shadow: none !important;
                outline: none !important;
                transition: all 0.25s ease !important;
            }}
            
            .main .block-container .stTextInput input:focus,
            .main .block-container .stTextInput > div > div > input:focus {{
                border-color: #22C55E !important;
                background: rgba(255, 255, 255, 0.12) !important;
                box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.25) !important;
            }}
            
            .main .block-container .stTextInput label, 
            .main .block-container .stTextInput label p {{
                color: rgba(255, 255, 255, 0.9) !important;
                font-weight: 600 !important;
                font-size: 13px !important;
                margin-bottom: 6px !important;
            }}

            /* Premium styled green button */
            .main .block-container .stButton > button {{
                background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
                font-size: 15px !important;
                height: 48px !important;
                border-radius: 12px !important;
                border: none !important;
                box-shadow: 0 4px 14px rgba(22, 163, 74, 0.3) !important;
                transition: all 0.25s ease !important;
            }}
            
            .main .block-container .stButton > button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(22, 163, 74, 0.45) !important;
                color: #FFFFFF !important;
            }}
            
            .main .block-container .stButton > button:active {{
                transform: translateY(0) !important;
            }}
        </style>
    """, unsafe_allow_html=True)



    # Render animated welcome header floating on background
    st.markdown("""
        <div class="welcome-header">
            <div class="welcome-logo">🌍</div>
            <h1 class="welcome-title">EcoHub</h1>
            <p class="welcome-subtitle">Track. Reduce. Protect the Planet.</p>
        </div>
    """, unsafe_allow_html=True)

def render_login_page():
    """Render the premium login interface."""
    st.markdown("<h3 style='color:#FFFFFF;text-align:center;margin:0 0 24px;font-size:1.6rem;font-weight:800;'>Sign In</h3>", unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="", key="login_username")
    password = st.text_input("Password", type="password", placeholder="", key="login_password")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    login_btn = st.button("🔐 Log In", use_container_width=True)
    if login_btn:
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            user = db.verify_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Welcome back, {user['name']}! 🌱")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown("""
        <p style="text-align:center;color:rgba(255,255,255,0.7);margin-top:16px;font-size:13px;font-weight:500;">
            Don't have an account? Select <b style="color:#22C55E;">Register</b> tab above.
        </p>
    """, unsafe_allow_html=True)

def render_register_page():
    """Render the premium registration interface."""
    st.markdown("<h3 style='color:#FFFFFF;text-align:center;margin:0 0 24px;font-size:1.6rem;font-weight:800;'>Create Account</h3>", unsafe_allow_html=True)

    name = st.text_input("Full Name", placeholder="", key="register_name")
    email = st.text_input("Email Address", placeholder="", key="register_email")
    username = st.text_input("Choose Username", placeholder="", key="register_username")
    password = st.text_input("Password", type="password", placeholder="", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="", key="register_confirm_password")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    register_btn = st.button("🌱 Sign Up", use_container_width=True)
    if register_btn:
        if not name or not email or not username or not password or not confirm_password:
            st.error("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, msg = db.create_user(username, password, name, email)
            if success:
                st.success(msg)
                st.info("You can now log in using the Sign In tab.")
            else:
                st.error(msg)
