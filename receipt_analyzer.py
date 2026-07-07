import streamlit as st
import database as db
import receipt_scanner as scanner
from PIL import Image
import json
import difflib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Carbon database factors (in kg CO2 per unit)
CARBON_FACTORS = {
    # Red (High Carbon: >5 kg CO2)
    "beef": {"co2": 27.0, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Tofu", "Chicken Breast", "Tempeh"]},
    "lamb": {"co2": 39.2, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Pork", "Chicken Breast", "Tofu"]},
    "steak": {"co2": 27.0, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Chicken Breast", "Portobello Mushrooms"]},
    "beef jerky": {"co2": 27.0, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Turkey Jerky", "Mushroom Jerky"]},
    "cheese": {"co2": 13.5, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Vegan Cheese", "Hummus"]},
    "cheddar": {"co2": 13.5, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Vegan Cheddar", "Nutritional Yeast"]},
    "unleaded fuel": {"co2": 2.3, "category": "Transportation", "unit": "L", "intensity": "High 🔴", "alternatives": ["Public Transit", "EV Charging", "Carpooling"]},
    "gasoline": {"co2": 2.3, "category": "Transportation", "unit": "L", "intensity": "High 🔴", "alternatives": ["Biking", "Public Transport"]},
    "fuel": {"co2": 2.3, "category": "Transportation", "unit": "L", "intensity": "High 🔴", "alternatives": ["Biking", "Public Transport", "EV Carpooling"]},
    "chocolate": {"co2": 19.0, "category": "Food", "unit": "kg", "intensity": "High 🔴", "alternatives": ["Dark Chocolate (Ethical)", "Dried Fruits"]},
    
    # Yellow (Moderate Carbon: 1.5 - 5.0 kg CO2)
    "pork": {"co2": 12.1, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Tofu", "Seitan"]},
    "chicken": {"co2": 6.9, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Tofu", "Lentils"]},
    "poultry": {"co2": 6.9, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Chickpeas", "Tofu"]},
    "turkey": {"co2": 6.1, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Seitan", "Tofu"]},
    "fish": {"co2": 5.4, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Seaweed alternatives", "Beans"]},
    "seafood": {"co2": 7.5, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Tofu", "Jackfruit"]},
    "eggs": {"co2": 4.8, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Scrambled Tofu", "Flaxseed egg replacement"]},
    "butter": {"co2": 11.5, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Vegan Butter", "Olive Oil"]},
    "dairy milk": {"co2": 1.9, "category": "Food", "unit": "L", "intensity": "Moderate 🟡", "alternatives": ["Oat Milk", "Almond Milk", "Soy Milk"]},
    "whole milk": {"co2": 1.9, "category": "Food", "unit": "L", "intensity": "Moderate 🟡", "alternatives": ["Oat Milk", "Almond Milk"]},
    "yogurt": {"co2": 2.2, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Coconut Yogurt", "Soy Yogurt"]},
    "greek yogurt": {"co2": 2.2, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Almond Yogurt", "Oat Yogurt"]},
    "rice": {"co2": 2.7, "category": "Food", "unit": "kg", "intensity": "Moderate 🟡", "alternatives": ["Quinoa", "Bulgur", "Cauliflower Rice"]},
    "laundry detergent": {"co2": 2.0, "category": "Household", "unit": "item", "intensity": "Moderate 🟡", "alternatives": ["Eco Laundry Sheets", "Refillable Detergent"]},
    "soda": {"co2": 0.8, "category": "Food", "unit": "item", "intensity": "Moderate 🟡", "alternatives": ["Tap Water", "Home Carbonated Water"]},
    
    # Green (Low Carbon: <1.5 kg CO2)
    "tofu": {"co2": 0.8, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "spinach": {"co2": 0.4, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "avocado": {"co2": 0.9, "category": "Food", "unit": "item", "intensity": "Low 🟢", "alternatives": []},
    "almond milk": {"co2": 0.7, "category": "Food", "unit": "L", "intensity": "Low 🟢", "alternatives": []},
    "oat milk": {"co2": 0.9, "category": "Food", "unit": "L", "intensity": "Low 🟢", "alternatives": []},
    "soy milk": {"co2": 1.0, "category": "Food", "unit": "L", "intensity": "Low 🟢", "alternatives": []},
    "oatmeal": {"co2": 1.2, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "oats": {"co2": 1.2, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "bread": {"co2": 1.4, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "wheat bread": {"co2": 1.4, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "apples": {"co2": 0.4, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "bananas": {"co2": 0.8, "category": "Food", "unit": "kg", "intensity": "Low 🟢", "alternatives": []},
    "croissant": {"co2": 1.2, "category": "Food", "unit": "item", "intensity": "Low 🟢", "alternatives": []},
    "coffee": {"co2": 1.5, "category": "Food", "unit": "item", "intensity": "Low 🟢", "alternatives": []},
    "filter coffee": {"co2": 0.5, "category": "Food", "unit": "item", "intensity": "Low 🟢", "alternatives": []},
    "shampoo": {"co2": 0.5, "category": "Household", "unit": "item", "intensity": "Low 🟢", "alternatives": []},
    "soap": {"co2": 0.3, "category": "Household", "unit": "item", "intensity": "Low 🟢", "alternatives": []},
    "led bulb": {"co2": -5.0, "category": "Household", "unit": "item", "intensity": "Low 🟢 (Energy Saver! 💡)", "alternatives": []},
    "plastic carry bag": {"co2": 0.2, "category": "Household", "unit": "item", "intensity": "Low 🟢", "alternatives": ["Reusable Canvas Bag"]},
    "plastic bag": {"co2": 0.2, "category": "Household", "unit": "item", "intensity": "Low 🟢", "alternatives": ["Cotton Tote Bag"]},
    "potato chips": {"co2": 1.2, "category": "Food", "unit": "item", "intensity": "Low 🟢", "alternatives": ["Air-popped Popcorn"]}
}

def match_carbon_factor(item_name):
    """Fuzzy match item name with carbon factors database."""
    name_lower = item_name.lower()
    
    # 1. Direct keyword match
    for key, data in CARBON_FACTORS.items():
        if key in name_lower:
            return data
            
    # 2. Fuzzy match
    keys = list(CARBON_FACTORS.keys())
    close_matches = difflib.get_close_matches(name_lower, keys, n=1, cutoff=0.4)
    if close_matches:
        match_key = close_matches[0]
        return CARBON_FACTORS[match_key]
        
    # 3. Default fallback
    return {"co2": 1.5, "category": "Other", "unit": "item", "intensity": "Moderate 🟡", "alternatives": ["Eco-certified brands"]}

def render_receipt_analyzer():
    user = st.session_state.user
    
    # Styling variables
    PRIMARY_COLOR = "#0c3b2e"
    SECONDARY_COLOR = "#6d9773"
    ACCENT_COLOR = "#ffba00"
    
    st.markdown("<h2>🧾 AI Receipt Carbon Footprint Analyzer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6d9773;'>Transform paper receipts into actionable ecological insights. Scan using your device camera or upload image/PDF files to analyze itemized carbon footprints.</p>", unsafe_allow_html=True)
    
    # Sub-navigation tabs
    tab_scan, tab_history = st.tabs(["📸 Scanner & Analyzer", "💾 Saved Scan History"])
    
    with tab_scan:
        st.markdown("<div class='eco-card'>", unsafe_allow_html=True)
        st.markdown("<h4>1. Scan or Upload Receipt</h4>", unsafe_allow_html=True)
        
        # User input choice
        input_choice = st.radio("Choose Capture Mode", ["Use Demo Sample (Instantly)", "Upload File (Image/PDF)", "Scan with Device Camera"], horizontal=True)
        
        raw_image = None
        sample_key = None
        uploaded_file = None
        
        if input_choice == "Use Demo Sample (Instantly)":
            sample_key = st.selectbox("Select Sample Receipt", list(scanner.SAMPLE_RECEIPTS.keys()))
            st.info(f"💡 This option simulates an OCR scan of **{sample_key}** to display the visual scanner, image preprocessing steps, and extracted metrics.")
            
        elif input_choice == "Upload File (Image/PDF)":
            uploaded_file = st.file_uploader("Upload receipt image (.png, .jpg, .jpeg) or PDF document", type=["png", "jpg", "jpeg", "pdf"])
            if uploaded_file:
                # If PDF, we can show basic doc info
                if uploaded_file.name.lower().endswith(".pdf"):
                    st.success(f"📄 PDF loaded: {uploaded_file.name}")
                else:
                    raw_image = Image.open(uploaded_file)
                    st.image(raw_image, caption="Uploaded Receipt Source", width=350)
                    
        elif input_choice == "Scan with Device Camera":
            camera_file = st.camera_input("Take a snapshot of your receipt")
            if camera_file:
                raw_image = Image.open(camera_file)
                st.success("📸 Image captured successfully!")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Image scanner preprocessing steps visualization (only for images)
        if raw_image is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🔍 Interactive Preprocessing Steps (Edge & Boundary Detection)"):
                st.markdown("<p style='color: #6d9773; font-size:13px;'>View the digital enhancement pipeline executing in OpenCV to prepare the receipt for OCR.</p>", unsafe_allow_html=True)
                
                # Apply scanner steps
                with st.spinner("Processing image edges..."):
                    steps, contour_found = scanner.preprocess_for_scanner(raw_image)
                
                col_orig, col_gray, col_edges, col_wrap = st.columns(4)
                with col_orig:
                    st.image(steps["original"], caption="1. Original (RGB)", use_container_width=True)
                with col_gray:
                    st.image(steps["grayscale"], caption="2. Enhanced Grayscale", use_container_width=True)
                with col_edges:
                    st.image(steps["edges"], caption="3. Canny Edge Detection", use_container_width=True)
                with col_wrap:
                    st.image(steps["processed"], caption="4. Cropped / Wrapped Output", use_container_width=True)
                    
                if contour_found:
                    st.success("🎯 Receipt borders successfully auto-detected! Applying perspective alignment.")
                else:
                    st.warning("⚠️ Could not confidently auto-detect 4 borders of a receipt. Applying center crop and contrast enhancement.")

        # OCR extraction trigger
        if sample_key or uploaded_file or raw_image:
            st.markdown("<br><div class='eco-card'>", unsafe_allow_html=True)
            st.markdown("<h4>2. OCR Text Extraction & Review</h4>", unsafe_allow_html=True)
            
            # Button to trigger OCR
            trigger_ocr = st.button("Perform OCR Extraction ⚡", use_container_width=True)
            
            # Store extracted info in session state so it's editable
            if trigger_ocr:
                with st.spinner("Extracting purchase details..."):
                    if sample_key:
                        ocr_raw, store, date, items = scanner.run_hybrid_ocr(None, sample_key)
                    elif uploaded_file:
                        ocr_raw, store, date, items = scanner.run_hybrid_ocr(uploaded_file)
                    else:
                        ocr_raw, store, date, items = scanner.run_hybrid_ocr(raw_image)
                        
                    st.session_state.ocr_raw = ocr_raw
                    st.session_state.ocr_store = store
                    st.session_state.ocr_date = date
                    st.session_state.ocr_items = items
                    st.success("✅ Extraction complete! Review and adjust details below.")
            
            # Display editable text areas if OCR has run
            if "ocr_raw" in st.session_state:
                col_meta1, col_meta2 = st.columns(2)
                with col_meta1:
                    store_name_edit = st.text_input("Store Name", value=st.session_state.ocr_store)
                with col_meta2:
                    date_edit = st.text_input("Purchase Date (YYYY-MM-DD)", value=st.session_state.ocr_date)
                
                # Raw text area for custom text editing
                edited_raw_text = st.text_area("✏️ Extracted Receipt Text (Edit items or numbers directly if needed)", value=st.session_state.ocr_raw, height=220)
                
                # Keep values in session state
                st.session_state.ocr_store = store_name_edit
                st.session_state.ocr_date = date_edit
                st.session_state.ocr_raw = edited_raw_text
                
                # Recalculate button
                recalculate = st.button("Analyze Carbon Footprint & Eco Score 🚀", use_container_width=True)
                
                if recalculate or ("analyzed" in st.session_state and st.session_state.analyzed):
                    # Reparse the edited raw text
                    parsed_res = scanner.parse_receipt_text(st.session_state.ocr_raw)
                    items_to_analyze = parsed_res["items"] if parsed_res["items"] else st.session_state.ocr_items
                    
                    if not items_to_analyze:
                        st.error("⚠️ No items detected in the text. Please ensure each item is written on a line in the format: `Product Name   qty @ price   total`")
                    else:
                        # Carbon calculation
                        analyzed_items = []
                        total_price = 0.0
                        total_co2 = 0.0
                        
                        for item in items_to_analyze:
                            factor = match_carbon_factor(item["name"])
                            co2_val = round(factor["co2"] * item["qty"], 2)
                            line_total = round(item["price"] * item["qty"], 2)
                            
                            total_price += line_total
                            total_co2 += co2_val
                            
                            analyzed_items.append({
                                "Product Name": item["name"],
                                "Qty": item["qty"],
                                "Unit Price ($)": item["price"],
                                "Line Total ($)": line_total,
                                "CO2 Footprint (kg)": co2_val,
                                "Carbon Intensity": factor["intensity"],
                                "Alternatives": factor["alternatives"],
                                "Category": factor["category"]
                            })
                            
                        # Calculate Eco Score: higher is better (max 100). 
                        # Ratio of CO2 per Dollar spent. Lower co2/dollar = higher score
                        co2_ratio = total_co2 / total_price if total_price > 0 else 0
                        eco_score = max(5, min(100, int(100 - co2_ratio * 25)))
                        
                        # Store analysis results in session state
                        st.session_state.analyzed_items = analyzed_items
                        st.session_state.total_price = round(total_price, 2)
                        st.session_state.total_co2 = round(total_co2, 2)
                        st.session_state.eco_score = eco_score
                        st.session_state.analyzed = True
                        
                        # DISPLAY ANALYSIS RESULTS
                        st.markdown("<hr style='border-color: rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                        st.markdown("<h4>3. Carbon Footprint Analysis Dashboard</h4>", unsafe_allow_html=True)
                        
                        # Metric Cards
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        with col_m1:
                            st.markdown(f"""
                                <div class="eco-metric">
                                    <div class="eco-metric-label">Items Extracted</div>
                                    <div class="eco-metric-val">{len(analyzed_items)}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        with col_m2:
                            st.markdown(f"""
                                <div class="eco-metric">
                                    <div class="eco-metric-label">Total Bill</div>
                                    <div class="eco-metric-val">${st.session_state.total_price:.2f}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        with col_m3:
                            st.markdown(f"""
                                <div class="eco-metric">
                                    <div class="eco-metric-label">Total CO₂ Impact</div>
                                    <div class="eco-metric-val" style="color: #e74c3c;">{st.session_state.total_co2:.2f} kg</div>
                                </div>
                            """, unsafe_allow_html=True)
                        with col_m4:
                            color_score = "#27ae60" if eco_score >= 80 else ("#f1c40f" if eco_score >= 40 else "#e74c3c")
                            st.markdown(f"""
                                <div class="eco-metric">
                                    <div class="eco-metric-label">Shopping Eco Score</div>
                                    <div class="eco-metric-val" style="color: {color_score};">{eco_score} / 100</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        # Eco Score explanation
                        if eco_score >= 80:
                            st.success("🌟 Excellent! Your purchase lists items with exceptionally low greenhouse gas footprints. Keep supporting local, organic, and plant-based alternatives.")
                        elif eco_score >= 40:
                            st.warning("⚠️ Moderate Eco Score. Your bill contains a mix of sustainable items and high-impact products (e.g. dairy, cheese, or red meat). View alternative suggestions below.")
                        else:
                            st.error("🚨 Low Eco Score. Your cart is heavily dominated by carbon-intensive items. Swapping a few primary items to alternatives can significantly reduce your impact.")

                        # Tabular layout
                        st.markdown("<br><h5>📊 Itemized Carbon Breakdown</h5>", unsafe_allow_html=True)
                        df_items = pd.DataFrame(analyzed_items)
                        
                        # Render table
                        table_df = df_items[["Product Name", "Qty", "Line Total ($)", "CO2 Footprint (kg)", "Carbon Intensity", "Category"]]
                        st.dataframe(table_df, use_container_width=True)
                        
                        # Plotly graph: horizontal bar chart of item footprints
                        st.markdown("<h5>📉 Product Carbon Footprint Ranking</h5>", unsafe_allow_html=True)
                        fig = px.bar(
                            df_items.sort_values(by="CO2 Footprint (kg)", ascending=True),
                            x="CO2 Footprint (kg)",
                            y="Product Name",
                            color="CO2 Footprint (kg)",
                            color_continuous_scale=["#27ae60", "#f1c40f", "#e74c3c"],
                            orientation="h",
                            title="Emissions Contribution per Item (kg CO₂)"
                        )
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#2c3e50"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # AI Recommendations
                        st.markdown("<br><div class='eco-card' style='background-color: #f4fdf8;'>", unsafe_allow_html=True)
                        st.markdown("<h4 style='color: #0c3b2e;'>🌱 AI-Powered Sustainable Alternatives</h4>", unsafe_allow_html=True)
                        
                        high_carbon_items = df_items[df_items["CO2 Footprint (kg)"] > 3.0]
                        
                        if not high_carbon_items.empty:
                            st.write("We detected high-carbon hotspots in your purchase. Consider these eco-friendly swaps next time:")
                            for _, r in high_carbon_items.iterrows():
                                if r["Alternatives"]:
                                    alts_str = ", ".join(r["Alternatives"])
                                    st.markdown(f"- **{r['Product Name']}** ({r['CO2 Footprint (kg)']} kg CO₂): Swap to **{alts_str}** to decrease emissions by up to **80%**.")
                        else:
                            st.markdown("🍀 **Excellent Grocery Selections!** All items in your bill fall under the moderate or low emissions categories. You are doing a fantastic job minimizing your shopping footprint.")
                            
                        # Shopping Habits recommendations
                        st.markdown("<h5 style='color: #0c3b2e; margin-top:10px;'>💡 Recommended Sustainable Shopping Habits</h5>", unsafe_allow_html=True)
                        st.markdown("""
                        1. **Bring Reusable Bags:** Carry a reusable canvas or cotton tote to avoid plastic bags which contribute to plastic pollution and manufacturing carbon.
                        2. **Prioritize Local & Seasonal:** Buying locally sourced fruits and vegetables reduces transit emissions ('food miles') and supports regional farms.
                        3. **Reduce Meat & Dairy Consumption:** Shifting towards plant-based proteins (beans, lentils, tofu, grains) is the single most effective way to lower shopping basket emissions.
                        4. **Bulk Purchases:** Buying frequently used products in bulk reduces overall packaging materials and shipping trips.
                        """)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Save Scan to history
                        st.markdown("<br>", unsafe_allow_html=True)
                        save_btn = st.button("Save Analysis to History 💾", use_container_width=True)
                        if save_btn:
                            # Package items into JSON
                            items_json = json.dumps(analyzed_items)
                            success, msg = db.add_receipt_entry(
                                user['id'],
                                st.session_state.ocr_store,
                                st.session_state.ocr_date,
                                st.session_state.total_price,
                                st.session_state.total_co2,
                                st.session_state.eco_score,
                                items_json
                            )
                            if success:
                                st.success(f"🎉 {msg}")
                                # Clean up state to trigger fresh reload of history tab
                                if 'receipt_history' in st.session_state:
                                    del st.session_state.receipt_history
                            else:
                                st.error(f"Failed to save receipt: {msg}")
            
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_history:
        st.markdown("<div class='eco-card'>", unsafe_allow_html=True)
        st.markdown("<h4>Saved Receipt History & Trends</h4>", unsafe_allow_html=True)
        
        history = db.get_receipt_history(user['id'])
        
        if not history:
            st.warning("⚠️ No receipt history found. Upload or scan a receipt in the first tab to save your footprint history.")
        else:
            df_hist = pd.DataFrame(history)
            
            # Format display df
            df_hist_display = df_hist[["store_name", "purchase_date", "total_price", "total_co2", "eco_score"]].copy()
            df_hist_display.columns = ["Store Name", "Purchase Date", "Total Cost ($)", "Total CO2 (kg)", "Eco Score"]
            
            # Interactive metric summary
            avg_eco_score = int(df_hist["eco_score"].mean())
            total_scans = len(df_hist)
            total_spent = df_hist["total_price"].sum()
            total_carbon = df_hist["total_co2"].sum()
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("Total Scanned Receipts", total_scans)
            with col_s2:
                st.metric("Total Spent", f"${total_spent:.2f}")
            with col_s3:
                st.metric("Total Shopping Carbon", f"{total_carbon:.2f} kg CO₂")
            with col_s4:
                st.metric("Average Eco Score", f"{avg_eco_score} / 100")
                
            st.markdown("<br><h5>📜 All Logged Receipts</h5>", unsafe_allow_html=True)
            st.dataframe(df_hist_display, use_container_width=True)
            
            # Historical charts
            st.markdown("<h5>📈 Monthly Shopping Carbon Trend</h5>", unsafe_allow_html=True)
            
            # Parse dates and group by month
            df_hist["date_parsed"] = pd.to_datetime(df_hist["purchase_date"])
            df_hist_sorted = df_hist.sort_values(by="date_parsed")
            
            fig_trend = px.line(
                df_hist_sorted,
                x="purchase_date",
                y="total_co2",
                markers=True,
                labels={"purchase_date": "Purchase Date", "total_co2": "Carbon Footprint (kg CO₂)"},
                title="Total Shopping Carbon Footprint per Receipt"
            )
            fig_trend.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#2c3e50"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Detail expander for individual receipt item details
            st.markdown("<br><h5>🔍 Deep Dive: View Receipt Details</h5>", unsafe_allow_html=True)
            receipt_options = {f"{r['purchase_date']} - {r['store_name']} (${r['total_price']})": r['id'] for r in history}
            selected_rec_label = st.selectbox("Select Receipt to Inspect", list(receipt_options.keys()))
            
            if selected_rec_label:
                rec_id = receipt_options[selected_rec_label]
                rec_detail = next(r for r in history if r['id'] == rec_id)
                items_detail = json.loads(rec_detail['items_json'])
                
                st.markdown(f"**Store:** {rec_detail['store_name']} | **Date:** {rec_detail['purchase_date']}")
                st.markdown(f"**Total Carbon:** {rec_detail['total_co2']} kg CO₂ | **Eco Score:** {rec_detail['eco_score']} / 100")
                
                df_det = pd.DataFrame(items_detail)
                st.dataframe(df_det[["Product Name", "Qty", "Line Total ($)", "CO2 Footprint (kg)", "Carbon Intensity", "Category"]], use_container_width=True)
                
        st.markdown("</div>", unsafe_allow_html=True)
