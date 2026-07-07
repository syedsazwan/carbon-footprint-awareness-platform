import streamlit as st
import database as db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_dashboard_page():
    """Render the premium bright dashboard analytics screen."""
    user = st.session_state.user

    # ── Welcome Banner ──
    _pts = db.get_eco_points(user['id'])
    st.markdown(f"""
        <div class="welcome-banner fade-in">
            <div style="position:relative;z-index:1;">
                <div style="font-size:12px;color:rgba(255,255,255,0.75);font-weight:600;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">Welcome back 👋</div>
                <div style="font-size:26px;font-weight:800;color:#FFFFFF;margin-bottom:6px;">{user['name']}</div>
                <div style="font-size:14px;color:rgba(255,255,255,0.8);max-width:380px;">Track your carbon footprint, earn eco points, and help build a sustainable future.</div>
                <div style="margin-top:14px;display:flex;gap:12px;align-items:center;">
                    <div style="background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);border-radius:20px;padding:6px 14px;font-size:13px;color:#FFFFFF;font-weight:600;">🪙 {_pts} Eco Points</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Fetch Data ──
    history = db.get_carbon_history(user['id'])

    if not history:
        st.markdown("""
            <div class="eco-card" style="text-align:center;padding:48px 32px;">
                <div style="font-size:56px;margin-bottom:16px;">📊</div>
                <h3 style="color:#111827;margin:0 0 8px;">No Data Yet</h3>
                <p style="color:#6B7280;">Navigate to the <b>Carbon Calculator</b> to log your first monthly footprint!</p>
            </div>
        """, unsafe_allow_html=True)
        demo_df = pd.DataFrame([
            {"Month": "Jan", "Emissions": 810.0},
            {"Month": "Feb", "Emissions": 730.0},
            {"Month": "Mar", "Emissions": 495.0},
            {"Month": "Apr", "Emissions": 395.0},
            {"Month": "May", "Emissions": 262.0}
        ])
        fig = px.area(demo_df, x="Month", y="Emissions", title="Sample Monthly Trend (Demo)", markers=True)
        fig.update_traces(line_color='#22C55E', line_width=3, fillcolor='rgba(34,197,94,0.08)')
        fig.update_layout(paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
                          font=dict(color='#111827', family='Inter'),
                          title_font=dict(color='#111827', size=15, family='Inter'),
                          xaxis=dict(showgrid=False, color='#111827', tickfont=dict(color='#374151')),
                          yaxis=dict(showgrid=True, gridcolor='#E5E7EB', color='#111827', tickfont=dict(color='#374151')))
        st.plotly_chart(fig, use_container_width=True)
        return

    df = pd.DataFrame(history)
    df = df.sort_values(by="month")
    available_months = df['month'].tolist()

    # Month selector row
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_month = st.selectbox("📅 Select Month to Inspect", available_months, index=len(available_months)-1)
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("📥 Download Report", use_container_width=True):
            st.info("Navigate to **Export PDF Report** in the sidebar to download!")

    row = df[df['month'] == selected_month].iloc[0]

    # MoM comparison
    pct_reduction = None
    selected_idx = available_months.index(selected_month)
    if selected_idx > 0:
        prev_row = df[df['month'] == available_months[selected_idx - 1]].iloc[0]
        prev_total = prev_row['total_emissions']
        curr_total = row['total_emissions']
        if prev_total > 0:
            pct_reduction = ((prev_total - curr_total) / prev_total) * 100

    # ── KPI Cards ──
    score = row['score_category']
    score_colors = {"Green": "#22C55E", "Yellow": "#FBBF24", "Red": "#EF4444"}
    score_bg = {"Green": "#F0FDF4", "Yellow": "#FFFBEB", "Red": "#FEF2F2"}
    score_icon = {"Green": "🟢", "Yellow": "🟡", "Red": "🔴"}

    if pct_reduction is not None:
        mom_val = f"{abs(pct_reduction):.1f}%"
        mom_label = "Reduced" if pct_reduction >= 0 else "Increased"
        mom_color = "#22C55E" if pct_reduction >= 0 else "#EF4444"
        mom_icon = "📉" if pct_reduction >= 0 else "📈"
        mom_bg = "#F0FDF4" if pct_reduction >= 0 else "#FEF2F2"
    else:
        mom_val = "First"
        mom_label = "Log"
        mom_color = "#3B82F6"
        mom_icon = "✨"
        mom_bg = "#EFF6FF"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">Total Carbon</div>
                    <div style="width:36px;height:36px;background:#F0FDF4;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🌍</div>
                </div>
                <div class="eco-metric-val">{row['total_emissions']}<span style="font-size:14px;font-weight:500;color:#6B7280;"> kg</span></div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">CO₂ for {selected_month}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">Carbon Score</div>
                    <div style="width:36px;height:36px;background:{score_bg[score]};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">{score_icon[score]}</div>
                </div>
                <div class="eco-metric-val" style="color:{score_colors[score]};">{score}</div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">Based on emissions level</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">MoM Progress</div>
                    <div style="width:36px;height:36px;background:{mom_bg};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">{mom_icon}</div>
                </div>
                <div class="eco-metric-val" style="color:{mom_color};font-size:1.6rem;">{mom_val}</div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">{mom_label} vs last month</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">Eco Points</div>
                    <div style="width:36px;height:36px;background:#FFFBEB;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🪙</div>
                </div>
                <div class="eco-metric-val" style="color:#FBBF24;">{_pts}</div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">Earned from actions</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Charts Row ──
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#111827;margin:0 0 16px;'>📌 Emission Sources — {selected_month}</h4>", unsafe_allow_html=True)
        labels = ['Transport', 'Electricity', 'Water', 'Food', 'Waste']
        values = [row['transport'], row['electricity'], row['water'], row['food'], row['waste']]
        fig_pie = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=.5,
            marker_colors=['#22C55E', '#3B82F6', '#FBBF24', '#F472B6', '#A78BFA'],
            textinfo='percent', hoverinfo='label+value+percent'
        )])
        fig_pie.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5,
                        font=dict(color='#111827', size=11, family='Inter')),
            paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
            font=dict(family='Inter', color='#111827')
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart2:
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#111827;margin:0 0 16px;'>🎯 Carbon Score Gauge</h4>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row['total_emissions'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Total CO₂ (kg)", 'font': {'color': '#6B7280', 'size': 13, 'family': 'Inter'}},
            number={'font': {'color': '#111827', 'size': 36, 'family': 'Inter'}, 'suffix': ' kg'},
            gauge={
                'axis': {'range': [None, 1000], 'tickcolor': '#9CA3AF', 'tickfont': {'color': '#9CA3AF'}},
                'bar': {'color': score_colors[score], 'thickness': 0.25},
                'bgcolor': '#F8FAFC',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 200], 'color': '#DCFCE7'},
                    {'range': [200, 500], 'color': '#FEF3C7'},
                    {'range': [500, 1000], 'color': '#FEE2E2'}
                ],
                'threshold': {'line': {'color': score_colors[score], 'width': 3}, 'thickness': 0.75, 'value': row['total_emissions']}
            }
        ))
        fig_gauge.update_layout(
            margin=dict(t=30, b=10, l=20, r=20),
            paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
            font=dict(color='#111827', family='Inter')
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Trend Chart ──
    st.markdown('<div class="eco-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#111827;margin:0 0 4px;'>📈 Monthly Carbon Footprint Trend</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;font-size:13px;margin:0 0 16px;'>Track your emissions reduction journey over time</p>", unsafe_allow_html=True)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df['month'], y=df['total_emissions'],
        mode='lines+markers+text',
        name='Emissions',
        line=dict(color='#22C55E', width=3),
        marker=dict(size=8, color='#22C55E', line=dict(width=2, color='#FFFFFF')),
        fill='tozeroy', fillcolor='rgba(34,197,94,0.08)',
        text=[f"{v:.0f}" for v in df['total_emissions']],
        textposition='top center',
        textfont=dict(size=11, color='#6B7280', family='Inter')
    ))
    fig_trend.update_layout(
        xaxis_title="Month", yaxis_title="Emissions (kg CO₂)",
        paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
        font=dict(color='#111827', family='Inter'),
        xaxis=dict(showgrid=False, color='#111827', tickfont=dict(color='#374151')),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB', color='#111827', tickfont=dict(color='#374151')),
        hovermode='x unified', showlegend=False, margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Category Comparison ──
    st.markdown('<div class="eco-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#111827;margin:0 0 4px;'>📊 Category Breakdown vs. History Average</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;font-size:13px;margin:0 0 16px;'>Compare your selected month against your historical average</p>", unsafe_allow_html=True)
    compare_df = pd.DataFrame({
        "Category": ['Transport', 'Electricity', 'Water', 'Food', 'Waste'],
        f"Selected ({selected_month})": [row['transport'], row['electricity'], row['water'], row['food'], row['waste']],
        "Avg History": [df['transport'].mean(), df['electricity'].mean(), df['water'].mean(), df['food'].mean(), df['waste'].mean()]
    })
    compare_melted = pd.melt(compare_df, id_vars="Category", var_name="Timeframe", value_name="Emissions (kg)")
    fig_compare = px.bar(
        compare_melted, x="Category", y="Emissions (kg)", color="Timeframe", barmode="group",
        color_discrete_map={f"Selected ({selected_month})": "#22C55E", "Avg History": "#CBD5E1"}
    )
    fig_compare.update_layout(
        paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
        font=dict(color='#111827', family='Inter'),
        xaxis=dict(showgrid=False, color='#111827', tickfont=dict(color='#374151')),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB', color='#111827', tickfont=dict(color='#374151')),
        legend=dict(font=dict(color='#111827')),
        margin=dict(t=10, b=10), bargap=0.3
    )
    fig_compare.update_traces(marker_line_width=0)
    st.plotly_chart(fig_compare, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
