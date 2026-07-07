import streamlit as st
import database as db
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

def train_and_predict(history):
    """Train a scikit-learn Linear Regression model to forecast emissions."""
    df = pd.DataFrame(history)
    df = df.sort_values(by="month")
    
    # Pre-process dates
    df['date'] = pd.to_datetime(df['month'] + "-01")
    # Convert dates to ordinal numbers for regression training
    df['ordinal'] = df['date'].map(datetime.toordinal)
    
    X = df[['ordinal']].values
    y = df['total_emissions'].values
    
    # Train the model
    model = LinearRegression()
    model.fit(X, y)
    
    # Get model parameters
    slope = model.coef_[0]
    intercept = model.intercept_
    r2_score = model.score(X, y) if len(X) > 1 else 1.0
    
    # Predict next 3 months
    last_date = df['date'].max()
    future_dates = []
    future_ordinals = []
    
    for i in range(1, 4):
        # Add roughly 30 days per month
        next_date = last_date + timedelta(days=30 * i)
        future_dates.append(next_date.strftime("%Y-%m"))
        future_ordinals.append([next_date.toordinal()])
        
    predictions = model.predict(future_ordinals)
    # Ensure no negative predictions
    predictions = np.clip(predictions, 0, None)
    
    return {
        "dates": df['month'].tolist(),
        "actual": y.tolist(),
        "future_dates": future_dates,
        "predicted": predictions.tolist(),
        "slope": slope,
        "intercept": intercept,
        "r2_score": r2_score
    }

def render_ml_page():
    """Render the Machine Learning forecasting interface."""
    user = st.session_state.user

    st.markdown("""
        <div style="margin-bottom:24px;">
            <h2 style="color:#111827;margin:0 0 6px;font-size:1.7rem;">🧠 AI Emission Forecast</h2>
            <p style="color:#6B7280;font-size:14px;margin:0;">Scikit-Learn Linear Regression trained on your carbon history to forecast the next 3 months.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Fetch history
    history = db.get_carbon_history(user['id'])
    
    if len(history) < 2:
        st.info("💡 **Note:** Machine Learning models require at least **2 months** of carbon history to forecast trends. We are demonstrating the forecasting model below using your current data bootstrapped with representative green consumer trends.")
        
        # Bootstrap with dummy history representing a typical user
        today = datetime.now()
        history = [
            {"month": (today - timedelta(days=120)).strftime("%Y-%m"), "total_emissions": 850.0},
            {"month": (today - timedelta(days=90)).strftime("%Y-%m"), "total_emissions": 710.0},
            {"month": (today - timedelta(days=60)).strftime("%Y-%m"), "total_emissions": 530.0},
            {"month": (today - timedelta(days=30)).strftime("%Y-%m"), "total_emissions": 420.0}
        ]
        # Include current entry if exists
        curr_hist = db.get_carbon_history(user['id'])
        if curr_hist:
            history.append(curr_hist[0])

    res = train_and_predict(history)
    
    # Display forecast metric cards
    trend_direction = "Decreasing ↓" if res['slope'] < 0 else "Increasing ↑"
    trend_color = "#22C55E" if res['slope'] < 0 else "#EF4444"
    trend_bg = "#F0FDF4" if res['slope'] < 0 else "#FEF2F2"
    next_pred = res['predicted'][0]
    fit_quality = "High" if res['r2_score'] > 0.8 else ("Moderate" if res['r2_score'] > 0.5 else "Low")
    fit_color = "#22C55E" if fit_quality == "High" else ("#FBBF24" if fit_quality == "Moderate" else "#EF4444")
    fit_bg = "#F0FDF4" if fit_quality == "High" else ("#FFFBEB" if fit_quality == "Moderate" else "#FEF2F2")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">Emission Trend</div>
                    <div style="width:36px;height:36px;background:{trend_bg};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">{'📉' if res['slope'] < 0 else '📈'}</div>
                </div>
                <div class="eco-metric-val" style="color:{trend_color};font-size:1.4rem;">{trend_direction}</div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">Slope: {res['slope']:.4f} kg/day</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">Next Month Forecast</div>
                    <div style="width:36px;height:36px;background:#EFF6FF;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🔮</div>
                </div>
                <div class="eco-metric-val" style="color:#3B82F6;">{next_pred:.1f}<span style="font-size:14px;font-weight:500;color:#6B7280;"> kg</span></div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">For {res['future_dates'][0]}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="eco-metric">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div class="eco-metric-label">Model Confidence (R²)</div>
                    <div style="width:36px;height:36px;background:{fit_bg};border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🎯</div>
                </div>
                <div class="eco-metric-val" style="color:{fit_color};">{res['r2_score']:.2f}</div>
                <div style="font-size:12px;color:#6B7280;margin-top:4px;">Fit Quality: {fit_quality}</div>
            </div>
        """, unsafe_allow_html=True)

    # Forecast Plot
    st.markdown('<div class="eco-card" style="margin-top:20px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#111827;margin:0 0 4px;'>📈 3-Month AI Carbon Forecast</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;font-size:13px;margin:0 0 16px;'>Linear regression trained on your historical data with 3-month projection</p>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=res['dates'], y=res['actual'],
        mode='lines+markers', name='Actual Emissions',
        line=dict(color='#22C55E', width=3),
        marker=dict(size=8, color='#22C55E', line=dict(width=2, color='#FFFFFF')),
        fill='tozeroy', fillcolor='rgba(34,197,94,0.06)'
    ))
    forecast_x = [res['dates'][-1]] + res['future_dates']
    forecast_y = [res['actual'][-1]] + res['predicted']
    fig.add_trace(go.Scatter(
        x=forecast_x, y=forecast_y,
        mode='lines+markers', name='ML Forecast',
        line=dict(color='#FBBF24', width=3, dash='dash'),
        marker=dict(size=8, color='#FBBF24', line=dict(width=2, color='#FFFFFF'))
    ))
    target_y = [res['actual'][-1]]
    for i in range(1, 4):
        target_y.append(target_y[-1] * 0.95)
    fig.add_trace(go.Scatter(
        x=forecast_x, y=target_y,
        mode='lines+markers', name='COP26 Target (-5%/mo)',
        line=dict(color='#3B82F6', width=2, dash='dot'),
        marker=dict(size=6, color='#3B82F6')
    ))
    fig.update_layout(
        xaxis_title="Month", yaxis_title="Emissions (kg CO₂)",
        paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
        font=dict(color='#111827', family='Inter'),
        xaxis=dict(showgrid=False, color='#111827', tickfont=dict(color='#374151')),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB', color='#111827', tickfont=dict(color='#374151')),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(color='#111827', family='Inter')),
        hovermode='x unified', margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Insight panel
    st.markdown('<div class="eco-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#111827;margin:0 0 16px;'>🎯 Reduction Targets & Insights</h4>", unsafe_allow_html=True)

    latest_actual = res['actual'][-1]
    predicted_next = res['predicted'][0]

    if predicted_next < latest_actual:
        st.balloons()
        st.success(f"🎉 **Great Progress!** Model predicts a **decrease** of {latest_actual - predicted_next:.1f} kg CO₂ next month — you're on track!")
    else:
        st.warning(f"⚠️ **Action Required:** Model predicts an **increase** of {predicted_next - latest_actual:.1f} kg CO₂ next month. Take more eco challenges!")

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(f"""
            <div style="background:#F0FDF4;border-radius:16px;padding:16px;text-align:center;border:1px solid #DCFCE7;">
                <div style="font-size:20px;margin-bottom:6px;">📅</div>
                <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Next Month</div>
                <div style="font-size:20px;font-weight:800;color:#22C55E;margin:4px 0;">{latest_actual * 0.95:.1f} kg</div>
                <div style="font-size:11px;color:#6B7280;">Target (5% reduction)</div>
            </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown(f"""
            <div style="background:#FFFBEB;border-radius:16px;padding:16px;text-align:center;border:1px solid #FEF3C7;">
                <div style="font-size:20px;margin-bottom:6px;">📆</div>
                <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">3 Months</div>
                <div style="font-size:20px;font-weight:800;color:#FBBF24;margin:4px 0;">{latest_actual * 0.85:.1f} kg</div>
                <div style="font-size:11px;color:#6B7280;">Target (15% reduction)</div>
            </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown(f"""
            <div style="background:#EFF6FF;border-radius:16px;padding:16px;text-align:center;border:1px solid #DBEAFE;">
                <div style="font-size:20px;margin-bottom:6px;">🗓️</div>
                <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">12 Months</div>
                <div style="font-size:20px;font-weight:800;color:#3B82F6;margin:4px 0;">{latest_actual * 0.50:.1f} kg</div>
                <div style="font-size:11px;color:#6B7280;">Target (50% reduction)</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
