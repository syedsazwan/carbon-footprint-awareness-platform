import streamlit as st
import database as db
from datetime import datetime

EF_CAR = 0.18
EF_BIKE = 0.10
EF_BUS = 0.08
EF_TRAIN = 0.04
EF_FLIGHT = 90.0
EF_ELEC = 0.85
EF_WATER = 0.0003
EF_WASTE = 0.5

DIET_FACTORS = {
    "Vegan": 60.0,
    "Vegetarian": 120.0,
    "Non-Vegetarian": 250.0
}

def calculate_monthly_emissions(car_km, bike_km, bus_km, train_km, flight_hrs, electricity_kwh, water_liters, diet_type, waste_kg):
    """Calculate emissions across all categories in kg CO2/month."""
    trans_car = car_km * EF_CAR * 30.0
    trans_bike = bike_km * EF_BIKE * 30.0
    trans_bus = bus_km * EF_BUS * 30.0
    trans_train = train_km * EF_TRAIN * 30.0
    trans_flight = flight_hrs * EF_FLIGHT
    total_transport = trans_car + trans_bike + trans_bus + trans_train + trans_flight
    total_electricity = electricity_kwh * EF_ELEC
    total_water = water_liters * EF_WATER
    total_food = DIET_FACTORS.get(diet_type, 120.0)
    total_waste = waste_kg * EF_WASTE
    total_footprint = total_transport + total_electricity + total_water + total_food + total_waste
    return {
        "transport": round(total_transport, 2),
        "electricity": round(total_electricity, 2),
        "water": round(total_water, 2),
        "food": round(total_food, 2),
        "waste": round(total_waste, 2),
        "total": round(total_footprint, 2)
    }

def render_calculator_page():
    """Render the premium Carbon Footprint Calculator interface."""
    # Page Header
    st.markdown("""
        <div style="margin-bottom:24px;">
            <h2 style="color:#111827;margin:0 0 6px;font-size:1.7rem;">🌱 Carbon Footprint Calculator</h2>
            <p style="color:#6B7280;font-size:14px;margin:0;">Enter your monthly activities to calculate your carbon emissions in kg CO₂.</p>
        </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.user['id']
    current_month = datetime.now().strftime("%Y-%m")
    history = db.get_carbon_history(user_id)
    current_entry = next((e for e in history if e['month'] == current_month), None)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Transport Card
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <div style="width:36px;height:36px;background:#DCFCE7;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🚗</div>
                <div>
                    <h4 style="color:#111827;margin:0;font-size:15px;">Transportation</h4>
                    <p style="color:#6B7280;margin:0;font-size:12px;">Daily commuting distances</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        car_km = st.number_input("🚗 Car travel (km/day)", min_value=0.0, max_value=500.0, value=15.0 if not current_entry else 0.0, step=1.0)
        bike_km = st.number_input("🏍️ Motorcycle/Bike (km/day)", min_value=0.0, max_value=500.0, value=5.0 if not current_entry else 0.0, step=1.0)
        bus_km = st.number_input("🚌 Bus travel (km/day)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
        train_km = st.number_input("🚆 Train travel (km/day)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
        flight_hrs = st.number_input("✈️ Flight hours (hrs/month)", min_value=0.0, max_value=200.0, value=0.0, step=0.5)
        st.markdown('</div>', unsafe_allow_html=True)

        # Energy Card
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <div style="width:36px;height:36px;background:#DBEAFE;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">⚡</div>
                <div>
                    <h4 style="color:#111827;margin:0;font-size:15px;">Home Energy & Utilities</h4>
                    <p style="color:#6B7280;margin:0;font-size:12px;">Monthly electricity and water usage</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        electricity_kwh = st.number_input("💡 Electricity (kWh/month)", min_value=0.0, max_value=5000.0, value=150.0 if not current_entry else 100.0, step=10.0)
        water_liters = st.number_input("💧 Water usage (liters/month)", min_value=0.0, max_value=100000.0, value=5000.0 if not current_entry else 3000.0, step=100.0)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Lifestyle Card
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <div style="width:36px;height:36px;background:#FEF3C7;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">🥗</div>
                <div>
                    <h4 style="color:#111827;margin:0;font-size:15px;">Lifestyle & Consumption</h4>
                    <p style="color:#6B7280;margin:0;font-size:12px;">Food habits and waste generation</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        diet_type = st.selectbox("🍽️ Food Habits", ["Vegan", "Vegetarian", "Non-Vegetarian"], index=1)
        waste_kg = st.number_input("🗑️ Waste generated (kg/month)", min_value=0.0, max_value=1000.0, value=30.0 if not current_entry else 15.0, step=1.0)
        st.markdown('</div>', unsafe_allow_html=True)

        # Month Selector Card
        st.markdown('<div class="eco-card">', unsafe_allow_html=True)
        st.markdown("""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <div style="width:36px;height:36px;background:#F3E8FF;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">📅</div>
                <div>
                    <h4 style="color:#111827;margin:0;font-size:15px;">Calculation Month</h4>
                    <p style="color:#6B7280;margin:0;font-size:12px;">Select the month for this entry</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        selected_month = st.text_input("Month (YYYY-MM)", value=current_month, max_chars=7)
        st.markdown('</div>', unsafe_allow_html=True)

        # Calculate Button
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        calculate_btn = st.button("🌱 Calculate My Emissions", use_container_width=True)

        if calculate_btn:
            try:
                datetime.strptime(selected_month, "%Y-%m")
            except ValueError:
                st.error("Invalid month format. Please use YYYY-MM (e.g. 2026-06).")
                return

            res = calculate_monthly_emissions(
                car_km, bike_km, bus_km, train_km, flight_hrs,
                electricity_kwh, water_liters, diet_type, waste_kg
            )
            total = res['total']
            score_category = "Red" if total > 500 else ("Yellow" if total >= 200 else "Green")

            db.add_carbon_entry(
                user_id=user_id,
                month=selected_month,
                transport=res['transport'],
                electricity=res['electricity'],
                water=res['water'],
                food=res['food'],
                waste=res['waste'],
                total_emissions=total,
                score_category=score_category
            )

            st.success(f"✅ Logged! Total Carbon Footprint: **{total} kg CO₂/month**")

            color_map = {"Green": "#22C55E", "Yellow": "#FBBF24", "Red": "#EF4444"}
            bg_map = {"Green": "#F0FDF4", "Yellow": "#FFFBEB", "Red": "#FEF2F2"}
            _c = color_map[score_category]
            _bg = bg_map[score_category]

            # Results summary
            st.markdown(f"""
                <div class="eco-card" style="border-left:4px solid {_c};background:{_bg};margin-top:8px;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                        <h4 style="color:#111827;margin:0;">Result Saved!</h4>
                        <span style="background:{_c};color:#FFFFFF;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">{score_category.upper()}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">
                        <div style="background:#FFFFFF;border-radius:12px;padding:12px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                            <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">🚗 Transport</div>
                            <div style="font-size:18px;font-weight:800;color:#111827;">{res['transport']}</div>
                            <div style="font-size:10px;color:#9CA3AF;">kg CO₂</div>
                        </div>
                        <div style="background:#FFFFFF;border-radius:12px;padding:12px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                            <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">⚡ Electricity</div>
                            <div style="font-size:18px;font-weight:800;color:#111827;">{res['electricity']}</div>
                            <div style="font-size:10px;color:#9CA3AF;">kg CO₂</div>
                        </div>
                        <div style="background:#FFFFFF;border-radius:12px;padding:12px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                            <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">💧 Water</div>
                            <div style="font-size:18px;font-weight:800;color:#111827;">{res['water']}</div>
                            <div style="font-size:10px;color:#9CA3AF;">kg CO₂</div>
                        </div>
                        <div style="background:#FFFFFF;border-radius:12px;padding:12px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                            <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">🥗 Food</div>
                            <div style="font-size:18px;font-weight:800;color:#111827;">{res['food']}</div>
                            <div style="font-size:10px;color:#9CA3AF;">kg CO₂</div>
                        </div>
                        <div style="background:#FFFFFF;border-radius:12px;padding:12px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                            <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">🗑️ Waste</div>
                            <div style="font-size:18px;font-weight:800;color:#111827;">{res['waste']}</div>
                            <div style="font-size:10px;color:#9CA3AF;">kg CO₂</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.info("💡 Visit the **Dashboard** to see your charts and historical trends!")
            st.session_state.calc_done = True

    # ── Calculation History Table ──
    st.markdown("""
        <div style="margin-top:32px;margin-bottom:12px;">
            <h3 style="color:#111827;margin:0 0 4px;">🕒 Calculation History</h3>
            <p style="color:#6B7280;font-size:13px;margin:0;">Your complete carbon footprint records</p>
        </div>
    """, unsafe_allow_html=True)

    if history:
        import pandas as pd
        hist_table = []
        for e in reversed(history):
            hist_table.append({
                "Month": e['month'],
                "Transport": float(e['transport']),
                "Electricity": float(e['electricity']),
                "Water": float(e['water']),
                "Food": float(e['food']),
                "Waste": float(e['waste']),
                "Total CO₂": float(e['total_emissions']),
                "Score": e['score_category']
            })
        df = pd.DataFrame(hist_table)

        # Filters and Controls
        st.markdown("<div style='background:#FFFFFF; padding:16px; border-radius:12px; margin-bottom:16px; border:1px solid #E5E7EB;'>", unsafe_allow_html=True)
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1], gap="medium")
        with ctrl_col1:
            search_query = st.text_input("🔍 Search History (Month or Score)", placeholder="Search by month or score (e.g., 2026, Green)", label_visibility="visible")
        with ctrl_col2:
            sort_by = st.selectbox("Sort By", ["Month", "Total CO₂", "Transport", "Electricity", "Water", "Food", "Waste"], index=0)
        with ctrl_col3:
            sort_order = st.selectbox("Order", ["Descending", "Ascending"], index=0)
        st.markdown("</div>", unsafe_allow_html=True)

        # Apply search query
        if search_query:
            df = df[
                df['Month'].str.contains(search_query, case=False, na=False) |
                df['Score'].str.contains(search_query, case=False, na=False)
            ]

        if df.empty:
            st.info("🔍 No records match your search. Try a different month or score filter.")
        else:
            # Apply sorting
            ascending = (sort_order == "Ascending")
            df = df.sort_values(by=sort_by, ascending=ascending)

            # Pagination
            import math
            page_size = 5
            total_records = len(df)
            total_pages = max(1, math.ceil(total_records / page_size))

            # Only call st.slider when min < max to avoid RangeError
            if total_pages > 1:
                page = st.slider("Page", min_value=1, max_value=total_pages, value=1)
            else:
                page = 1

            start = (page - 1) * page_size
            end = start + page_size
            paginated_df = df.iloc[start:end].copy()

            # Format numbers for clean rendering
            paginated_df["Transport"] = paginated_df["Transport"].apply(lambda x: f"{x:.2f} kg")
            paginated_df["Electricity"] = paginated_df["Electricity"].apply(lambda x: f"{x:.2f} kg")
            paginated_df["Water"] = paginated_df["Water"].apply(lambda x: f"{x:.2f} kg")
            paginated_df["Food"] = paginated_df["Food"].apply(lambda x: f"{x:.2f} kg")
            paginated_df["Waste"] = paginated_df["Waste"].apply(lambda x: f"{x:.2f} kg")
            paginated_df["Total CO₂"] = paginated_df["Total CO₂"].apply(lambda x: f"{x:.2f} kg")

            def color_score(val):
                if val == "Green":
                    return "background-color:#F0FDF4;color:#166534;font-weight:700"
                elif val == "Yellow":
                    return "background-color:#FFFBEB;color:#92400E;font-weight:700"
                else:
                    return "background-color:#FEF2F2;color:#991B1B;font-weight:700"

            st.markdown('<div class="eco-card" style="padding:0;overflow:hidden;background:#FFFFFF;border-radius:20px;border:1px solid #E5E7EB;">', unsafe_allow_html=True)
            styled_df = paginated_df.style.map(color_score, subset=["Score"])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            if total_pages > 1:
                st.markdown(
                    f"<p style='color:#6B7280;font-size:12px;text-align:center;margin-top:8px;'>"
                    f"Showing {start+1}–{min(end, total_records)} of {total_records} records</p>",
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="eco-card" style="text-align:center;padding:40px;">
                <div style="font-size:40px;margin-bottom:12px;">📋</div>
                <p style="color:#6B7280;">No calculations yet. Use the form above to log your first entry!</p>
            </div>
        """, unsafe_allow_html=True)
