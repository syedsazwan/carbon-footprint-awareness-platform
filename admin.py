import streamlit as st
import database as db
import pandas as pd

def render_admin_panel():
    """Render the admin interface for managing users, articles, and platform stats."""
    user = st.session_state.user
    
    # Security check
    if user['role'] != 'admin':
        st.markdown("<h2 style='color:#e74c3c;'>🚫 Access Denied</h2>", unsafe_allow_html=True)
        st.error("Admin privileges are required to view this panel. If you are an administrator, please sign in with an admin account.")
        return

    st.markdown("<h2>⚙️ Administrator Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6d9773;'>Manage platform content, view global statistics, and monitor user contributions.</p>", unsafe_allow_html=True)

    # Load Stats
    stats = db.get_admin_stats()
    
    tab1, tab2 = st.tabs(["📊 Platform Metrics", "👥 User Directory"])
    
    with tab1:
        st.markdown("<h4>Platform Performance</h4>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="eco-metric">
                    <div class="eco-metric-label">Total Users</div>
                    <div class="eco-metric-val">{stats['total_users']}</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="eco-metric">
                    <div class="eco-metric-label">Calculations</div>
                    <div class="eco-metric-val">{stats['total_calculations']}</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="eco-metric">
                    <div class="eco-metric-label">Avg Carbon</div>
                    <div class="eco-metric-val">{stats['average_emissions']} kg</div>
                    <div style="font-size:11px; color:#6d9773;">Per monthly log</div>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                <div class="eco-metric">
                    <div class="eco-metric-label">Challenges Completed</div>
                    <div class="eco-metric-val">{stats['total_challenges_completed']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        # Global Leaderboard
        st.markdown("<br><h4>🏆 Green Champion Rankings</h4>", unsafe_allow_html=True)
        leaderboard = db.get_leaderboard()
        if leaderboard:
            ld_df = pd.DataFrame(leaderboard)
            ld_df.index = ld_df.index + 1
            ld_df.columns = ["User ID", "Name", "Eco Points"]
            st.dataframe(ld_df, use_container_width=True)
        else:
            st.info("No users found.")

    with tab2:
        st.markdown("<h4>Registered Users Directory</h4>", unsafe_allow_html=True)
        
        # Display list of users from SQLite
        conn = db.get_db_connection()
        users_df = pd.read_sql_query("SELECT id, username, name, email, eco_points, role, created_at FROM users", conn)
        conn.close()
        
        users_df.columns = ["User ID", "Username", "Full Name", "Email Address", "Eco Points", "Role", "Registration Date"]
        st.dataframe(users_df, use_container_width=True)

