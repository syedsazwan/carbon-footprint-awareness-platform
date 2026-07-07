import hashlib
import os
import streamlit as st

def hash_password(password: str) -> str:
    """Hash a password for storing in the database."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt_hex, key_hex = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return key == new_key
    except Exception:
        return False

def init_page_style():
    """Inject premium bright SaaS CSS into the Streamlit app."""
    st.markdown("""
        <style>
            /* ═══════════════════════════════════════════════════════════
               ECOHUB PREMIUM BRIGHT SAAS THEME
               Background : #F8FAFC  (soft white)
               Sidebar    : #0F9D58 → #0B7A43 (green gradient)
               Cards      : #FFFFFF  (pure white)
               Primary    : #22C55E  (green)
               Emerald    : #10B981
               Gold       : #FBBF24
               Blue       : #3B82F6
               Danger     : #EF4444
               Text       : #111827
               Muted      : #6B7280
               Border     : #E5E7EB
            ═══════════════════════════════════════════════════════════ */

            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif !important;
            }

            /* ── Global Background — kill every dark surface Streamlit injects ── */
            .stApp,
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewBlockContainer"] {
                background: #F8FAFC !important;
                background-color: #F8FAFC !important;
            }
            /* Header / toolbar strip */
            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stDecoration"],
            header[data-testid="stHeader"] {
                background: transparent !important;
                background-color: transparent !important;
                box-shadow: none !important;
                border: none !important;
            }
            /* Top decoration coloured bar */
            [data-testid="stDecoration"] {
                display: none !important;
            }
            .main .block-container {
                background: transparent !important;
                padding-top: 0 !important;
                padding-bottom: 4rem !important;
                max-width: 1200px !important;
            }

            /* ── Sidebar ── */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0F9D58 0%, #0B7A43 60%, #076637 100%) !important;
                border-right: none !important;
                box-shadow: 6px 0 32px rgba(15,157,88,0.2) !important;
                min-width: 270px !important;
                max-width: 280px !important;
            }
            section[data-testid="stSidebar"] > div:first-child {
                min-width: 270px !important;
                max-width: 280px !important;
            }
            /* Keep all sidebar text white */
            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3,
            section[data-testid="stSidebar"] h4,
            section[data-testid="stSidebar"] h5,
            section[data-testid="stSidebar"] h6,
            section[data-testid="stSidebar"] label,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] p {
                color: #FFFFFF !important;
            }
            /* Hide radio circle indicator */
            section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {
                display: none !important;
            }
            /* Nav items: rounded pill style */
            section[data-testid="stSidebar"] .stRadio label {
                padding: 11px 16px !important;
                border-radius: 50px !important;
                transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
                margin: 3px 6px !important;
                display: flex !important;
                align-items: center !important;
                cursor: pointer !important;
                background: transparent !important;
            }
            section[data-testid="stSidebar"] .stRadio label:hover {
                background: rgba(255,255,255,0.14) !important;
                transform: translateX(3px) !important;
            }
            /* Active nav item: bright green pill */
            section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
                background: rgba(34,197,94,0.35) !important;
                border: 1px solid rgba(34,197,94,0.5) !important;
                box-shadow: 0 4px 16px rgba(34,197,94,0.25), inset 0 1px 0 rgba(255,255,255,0.15) !important;
                transform: none !important;
            }
            section[data-testid="stSidebar"] .stRadio label [data-testid="stMarkdownContainer"] p {
                color: rgba(255,255,255,0.72) !important;
                font-weight: 500 !important;
                font-size: 13.5px !important;
                letter-spacing: 0.1px !important;
            }
            section[data-testid="stSidebar"] .stRadio label:has(input:checked) [data-testid="stMarkdownContainer"] p {
                color: #FFFFFF !important;
                font-weight: 800 !important;
            }
            /* Nav container padding */
            section[data-testid="stSidebar"] .stRadio > div {
                gap: 2px !important;
            }
            /* Logout button */
            section[data-testid="stSidebar"] .stButton > button {
                background: rgba(255,255,255,0.12) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(255,255,255,0.25) !important;
                border-radius: 14px !important;
                font-weight: 600 !important;
                font-size: 13px !important;
                transition: all 0.2s ease !important;
                width: 100% !important;
                margin: 0 12px !important;
            }
            section[data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(239,68,68,0.25) !important;
                border-color: rgba(239,68,68,0.4) !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 14px rgba(239,68,68,0.2) !important;
            }
            section[data-testid="stSidebar"] hr {
                border-color: rgba(255,255,255,0.12) !important;
            }
            /* Scrollbar inside sidebar */
            section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
                background: rgba(255,255,255,0.2) !important;
            }
            section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
                background: transparent !important;
            }

            /* ── Typography ── */
            h1, h2, h3, h4, h5, h6 {
                color: #111827 !important;
                font-weight: 700 !important;
                letter-spacing: -0.3px !important;
            }
            h1 { font-size: 2rem !important; }
            h2 { font-size: 1.6rem !important; color: #111827 !important; }
            h3 { font-size: 1.25rem !important; }
            h4 { font-size: 1.05rem !important; }
            
            /* ── Global readable text — main content areas ── */
            p, label, span, div {
                color: #111827 !important;
            }
            /* Scoped overrides for markdown body text */
            .stMarkdown, .stMarkdown p, .stMarkdown li {
                color: #374151 !important;
            }
            .stMarkdown strong {
                color: #111827 !important;
            }
            /* Keep sidebar text white (overrides global p/span/div above) */
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] div,
            section[data-testid="stSidebar"] label {
                color: #FFFFFF !important;
            }

            /* ── Premium White Cards ── */
            .eco-card {
                background: #FFFFFF !important;
                border-radius: 20px !important;
                padding: 24px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04) !important;
                border: 1px solid #E5E7EB !important;
                margin-bottom: 20px !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }
            .eco-card:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
            }

            /* ── KPI Metric Cards ── */
            .eco-metric {
                background: #FFFFFF !important;
                border: 1px solid #E5E7EB !important;
                border-radius: 20px !important;
                padding: 20px 18px !important;
                text-align: left !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.04) !important;
                transition: all 0.2s ease !important;
                position: relative !important;
                overflow: hidden !important;
            }
            .eco-metric:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 8px 24px rgba(0,0,0,0.1) !important;
                border-color: #22C55E !important;
            }
            .eco-metric-val {
                font-size: 2rem !important;
                font-weight: 800 !important;
                color: #111827 !important;
                line-height: 1.1 !important;
                margin: 4px 0 !important;
            }
            .eco-metric-label {
                font-size: 11px !important;
                color: #6B7280 !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                font-weight: 600 !important;
                margin-bottom: 4px !important;
            }

            /* ── Score Borders ── */
            .score-green { border-left: 4px solid #22C55E !important; }
            .score-yellow { border-left: 4px solid #FBBF24 !important; }
            .score-red { border-left: 4px solid #EF4444 !important; }

            /* ── Buttons ── */
            div.stButton > button {
                background: linear-gradient(90deg, #22C55E 0%, #10B981 100%) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                padding: 11px 28px !important;
                border-radius: 50px !important;
                border: none !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 4px 14px rgba(34,197,94,0.3) !important;
                letter-spacing: 0.2px !important;
            }
            div.stButton > button:hover {
                transform: translateY(-2px) scale(1.02) !important;
                box-shadow: 0 8px 20px rgba(34,197,94,0.4) !important;
            }
            div.stButton > button:active {
                transform: translateY(0px) scale(1) !important;
            }
            div.stButton > button:disabled {
                background: #E5E7EB !important;
                color: #9CA3AF !important;
                box-shadow: none !important;
            }

            /* ── Download Buttons ── */
            [data-testid="stDownloadButton"] > button {
                background: linear-gradient(90deg, #22C55E 0%, #10B981 100%) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                border-radius: 50px !important;
                border: none !important;
                box-shadow: 0 4px 14px rgba(34,197,94,0.3) !important;
                transition: all 0.2s ease !important;
            }
            [data-testid="stDownloadButton"] > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 20px rgba(34,197,94,0.4) !important;
            }
            /* Override text color of children inside buttons (e.g. spans) to be white */
            div.stButton > button * {
                color: #FFFFFF !important;
            }
            [data-testid="stDownloadButton"] > button * {
                color: #FFFFFF !important;
            }

            /* ── Input Fields ── */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stNumberInput > div > div > input,
            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input {
                background: #FFFFFF !important;
                border: 1.5px solid #E5E7EB !important;
                border-radius: 12px !important;
                color: #111827 !important;
                font-size: 14px !important;
                font-family: 'Inter', sans-serif !important;
                transition: all 0.2s ease !important;
                padding: 10px 14px !important;
            }
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: #22C55E !important;
                box-shadow: 0 0 0 3px rgba(34,197,94,0.12) !important;
                outline: none !important;
            }
            .stTextInput > label,
            .stTextArea > label,
            .stSelectbox > label,
            .stNumberInput > label,
            .stSlider > label {
                color: #111827 !important;
                font-weight: 600 !important;
                font-size: 13px !important;
            }

            /* ── Selectbox & Dropdowns ── */
            .stSelectbox [data-baseweb="select"] > div,
            .stSelectbox div[role="combobox"],
            .stSelectbox div {
                background-color: #FFFFFF !important;
                color: #111827 !important;
            }
            .stSelectbox [data-baseweb="select"] {
                border: 1.5px solid #E5E7EB !important;
                border-radius: 12px !important;
            }
            .stSelectbox [data-baseweb="select"] > div:focus-within {
                border-color: #22C55E !important;
                box-shadow: 0 0 0 3px rgba(34,197,94,0.12) !important;
            }
            /* Popover and select dropdown menu text color */
            [data-baseweb="popover"] *,
            ul[role="listbox"] *,
            li[role="option"] *,
            [data-baseweb="menu"] * {
                color: #111827 !important;
                background-color: #FFFFFF !important;
            }

            /* ── Number Input ── */
            .stNumberInput [data-baseweb="base-input"] {
                background: #FFFFFF !important;
                border: 1.5px solid #E5E7EB !important;
                border-radius: 12px !important;
            }
            .stNumberInput input {
                color: #111827 !important;
            }

            /* ── Slider ── */
            .stSlider [data-testid="stSlider"] > div > div > div {
                background: #22C55E !important;
            }

            /* ── Progress Bar ── */
            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #22C55E, #10B981) !important;
            }
            .stProgress > div > div > div {
                background: #F1F5F9 !important;
                border-radius: 100px !important;
            }

            /* ── Tabs ── */
            .stTabs [data-baseweb="tab-list"] {
                background: #F1F5F9 !important;
                border-radius: 14px !important;
                padding: 4px !important;
                gap: 4px !important;
                border: none !important;
            }
            .stTabs [data-baseweb="tab"] {
                background: transparent !important;
                color: #6B7280 !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                border: none !important;
                font-size: 14px !important;
            }
            .stTabs [data-baseweb="tab"] p,
            .stTabs [data-baseweb="tab"] span {
                color: #6B7280 !important;
            }
            .stTabs [aria-selected="true"] {
                background: #FFFFFF !important;
                color: #111827 !important;
                box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
            }
            .stTabs [aria-selected="true"] p,
            .stTabs [aria-selected="true"] span {
                color: #111827 !important;
                font-weight: 700 !important;
            }
            .stTabs [data-baseweb="tab-panel"] {
                background: transparent !important;
                padding-top: 20px !important;
            }

            /* ── Alerts ── */
            .stAlert, [data-testid="stAlert"] {
                border-radius: 14px !important;
                border: none !important;
            }
            [data-testid="stAlert"][kind="success"] {
                background: #F0FDF4 !important;
                border-left: 4px solid #22C55E !important;
                color: #166534 !important;
            }
            [data-testid="stAlert"][kind="warning"] {
                background: #FFFBEB !important;
                border-left: 4px solid #FBBF24 !important;
                color: #92400E !important;
            }
            [data-testid="stAlert"][kind="error"] {
                background: #FEF2F2 !important;
                border-left: 4px solid #EF4444 !important;
                color: #991B1B !important;
            }
            [data-testid="stAlert"][kind="info"] {
                background: #EFF6FF !important;
                border-left: 4px solid #3B82F6 !important;
                color: #1E40AF !important;
            }

            /* ── Dividers ── */
            hr {
                border: none !important;
                border-top: 1px solid #E5E7EB !important;
                margin: 20px 0 !important;
            }

            /* ── Chat Messages ── */
            div[data-testid="stChatMessageContainer"] {
                background: #FFFFFF !important;
                border-radius: 20px !important;
                padding: 24px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04) !important;
                border: 1px solid #E5E7EB !important;
                margin-bottom: 24px !important;
            }
            [data-testid="stChatMessage"] {
                background: #F8FAFC !important;
                border: 1px solid #E5E7EB !important;
                border-radius: 16px !important;
                margin-bottom: 12px !important;
                padding: 16px !important;
                box-shadow: none !important;
            }
            [data-testid="stChatMessage"] p,
            [data-testid="stChatMessage"] li,
            [data-testid="stChatMessage"] span,
            [data-testid="stChatMessage"] strong {
                color: #111827 !important;
            }
            
            /* ── Bottom block / chat input — kill all dark surfaces Streamlit injects ── */
            [data-testid="stBottomBlockContainer"],
            [data-testid="stBottomBlockContainer"] > *,
            [data-testid="stChatInputContainer"],
            [data-testid="stChatInputContainer"] > *,
            section[data-testid="stBottom"],
            section[data-testid="stBottom"] > *,
            div[class*="stBottom"],
            div[class*="stBottom"] > *,
            div[class*="BottomBlock"],
            div[class*="bottom-block"],
            div[class*="bottom"] {
                background: #F8FAFC !important;
                background-color: #F8FAFC !important;
                box-shadow: none !important;
                border-top: 1px solid #E5E7EB !important;
            }
            /* White rounded chat input pill — no black strip */
            div[data-testid="stChatInput"],
            div[data-testid="stChatInput"] > div,
            div[data-testid="stChatInput"] form,
            div[data-testid="stChatInput"] form > div {
                background: #FFFFFF !important;
                background-color: #FFFFFF !important;
                border-radius: 28px !important;
                box-shadow: 0 8px 24px rgba(15,23,42,0.08) !important;
                border: 1.5px solid #E5E7EB !important;
            }
            div[data-testid="stChatInput"] {
                padding: 4px 8px !important;
                margin: 8px 0 !important;
            }
            [data-testid="stChatInput"] textarea,
            [data-testid="stChatInput"] textarea:focus {
                background: #FFFFFF !important;
                background-color: #FFFFFF !important;
                border: none !important;
                outline: none !important;
                box-shadow: none !important;
                color: #111827 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
            }
            [data-testid="stChatInput"] textarea::placeholder {
                color: #6B7280 !important;
                opacity: 1 !important;
            }
            [data-testid="stChatInput"] button {
                background: linear-gradient(135deg, #22C55E, #10B981) !important;
                color: #FFFFFF !important;
                border-radius: 50% !important;
                width: 36px !important;
                height: 36px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 2px 8px rgba(34,197,94,0.4) !important;
                border: none !important;
                flex-shrink: 0 !important;
            }
            [data-testid="stChatInput"] button svg {
                fill: #FFFFFF !important;
            }
            [data-testid="stChatInput"] button:hover {
                background: linear-gradient(135deg, #16A34A, #059669) !important;
                box-shadow: 0 4px 12px rgba(34,197,94,0.5) !important;
            }

            /* ── All inputs: white bg, dark text, visible placeholder ── */
            input, input[type="text"], input[type="search"],
            input[type="email"], input[type="password"], textarea, select {
                background-color: #FFFFFF !important;
                color: #111827 !important;
            }
            input::placeholder, textarea::placeholder {
                color: #6B7280 !important;
                opacity: 1 !important;
            }

            /* ── Dataframes ── */
            .stDataFrame {
                border: 1px solid #E5E7EB !important;
                border-radius: 16px !important;
                overflow: hidden !important;
                background: #FFFFFF !important;
            }
            .stDataFrame table {
                background: #FFFFFF !important;
            }
            .stDataFrame thead tr th,
            .stDataFrame thead tr th * {
                background: #F8FAFC !important;
                color: #111827 !important;
                font-weight: 700 !important;
                border-bottom: 1px solid #E5E7EB !important;
            }
            .stDataFrame tbody tr td,
            .stDataFrame tbody tr td * {
                color: #111827 !important;
            }
            .stDataFrame tbody tr:nth-child(even) {
                background: #F9FAFB !important;
            }
            .stDataFrame tbody tr:hover {
                background: #F0FDF4 !important;
            }

            /* ── Expander ── */
            .streamlit-expanderHeader {
                background: #FFFFFF !important;
                border-radius: 12px !important;
                color: #111827 !important;
                border: 1px solid #E5E7EB !important;
                font-weight: 600 !important;
            }
            .streamlit-expanderContent {
                background: #FFFFFF !important;
                border: 1px solid #E5E7EB !important;
                border-top: none !important;
                border-radius: 0 0 12px 12px !important;
            }

            /* ── Scrollbar ── */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #F1F5F9; }
            ::-webkit-scrollbar-thumb {
                background: #CBD5E1;
                border-radius: 3px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #22C55E;
            }

            /* ── Native st.metric ── */
            [data-testid="stMetric"] {
                background: #FFFFFF !important;
                border: 1px solid #E5E7EB !important;
                border-radius: 16px !important;
                padding: 16px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            }
            [data-testid="stMetricValue"] {
                color: #111827 !important;
                font-size: 1.8rem !important;
                font-weight: 800 !important;
            }
            [data-testid="stMetricLabel"] {
                color: #6B7280 !important;
                font-weight: 600 !important;
                font-size: 12px !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            [data-testid="stMetricDelta"] {
                font-weight: 600 !important;
                font-size: 13px !important;
            }

            /* ── File uploader ── */
            [data-testid="stFileUploader"] {
                background: #FFFFFF !important;
                border: 2px dashed #E5E7EB !important;
                border-radius: 16px !important;
                transition: border-color 0.2s ease !important;
            }
            [data-testid="stFileUploader"]:hover {
                border-color: #22C55E !important;
            }

            /* ── Checkbox ── */
            .stCheckbox label,
            .stCheckbox label *,
            .stCheckbox p,
            .stCheckbox span {
                color: #111827 !important;
                font-weight: 500 !important;
            }

            /* ── Spinner ── */
            .stSpinner > div {
                border-top-color: #22C55E !important;
            }

            /* ── Radio buttons ── */
            .stRadio label,
            .stRadio label *,
            .stRadio p,
            .stRadio span {
                color: #111827 !important;
                font-weight: 500 !important;
            }
            /* Highlight selected option in radio buttons */
            .stRadio label:has(input:checked) {
                color: #22C55E !important;
                font-weight: 700 !important;
            }
            /* Highlight checked option span text specifically */
            .stRadio label:has(input:checked) span,
            .stRadio label:has(input:checked) p {
                color: #22C55E !important;
                font-weight: 700 !important;
            }

            /* ── Tooltip ── */
            [data-testid="stTooltipIcon"] {
                color: #9CA3AF !important;
            }

            /* ── Section header divider style ── */
            .section-divider {
                height: 1px;
                background: linear-gradient(90deg, #22C55E, transparent);
                margin: 8px 0 20px 0;
                border: none;
            }

            /* ── Badge chips ── */
            .badge-green {
                display: inline-block;
                background: #DCFCE7;
                color: #166534;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 20px;
                letter-spacing: 0.3px;
            }
            .badge-red {
                display: inline-block;
                background: #FEE2E2;
                color: #991B1B;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 20px;
            }
            .badge-yellow {
                display: inline-block;
                background: #FEF3C7;
                color: #92400E;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 20px;
            }
            .badge-blue {
                display: inline-block;
                background: #DBEAFE;
                color: #1E40AF;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 20px;
            }

            /* ── Fade-in animation ── */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(16px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .fade-in {
                animation: fadeInUp 0.4s ease forwards;
            }

            /* ── Welcome banner ── */
            .welcome-banner {
                background: linear-gradient(135deg, #0F9D58 0%, #0B7A43 60%, #065F46 100%);
                border-radius: 20px;
                padding: 28px 32px;
                margin-bottom: 24px;
                position: relative;
                overflow: hidden;
            }
            .welcome-banner::after {
                content: '🌍';
                position: absolute;
                right: 32px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 72px;
                opacity: 0.25;
            }

            /* ── XP Progress ── */
            .xp-bar-track {
                background: rgba(255,255,255,0.2);
                border-radius: 100px;
                height: 6px;
                width: 100%;
                margin-top: 6px;
            }
            .xp-bar-fill {
                background: #FBBF24;
                border-radius: 100px;
                height: 6px;
                transition: width 0.5s ease;
            }

        </style>
    """, unsafe_allow_html=True)
