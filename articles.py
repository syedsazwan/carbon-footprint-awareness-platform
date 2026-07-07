import streamlit as st
import database as db

def render_learning_center():
    """Render the Learning Center UI (articles and quizzes)."""
    user = st.session_state.user
    
    tab1, tab2 = st.tabs(["📚 Sustainability Library", "🧠 Eco Awareness Quiz"])
    
    with tab1:
        st.markdown("<h2>📚 Sustainability Learning Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6d9773;'>Read expert articles on climate change, renewable energy, and eco-friendly lifestyles.</p>", unsafe_allow_html=True)
        
        # Load articles from database
        articles = db.get_articles()
        
        # Filter and Search
        categories = ["All"] + list({art['category'] for art in articles})
        
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            sel_cat = st.selectbox("Filter by Category", categories)
        with col_f2:
            search_query = st.text_input("Search Articles", placeholder="Type keywords...")
            
        # Filter logic
        filtered_articles = articles
        if sel_cat != "All":
            filtered_articles = [art for art in filtered_articles if art['category'] == sel_cat]
        if search_query:
            filtered_articles = [
                art for art in filtered_articles 
                if search_query.lower() in art['title'].lower() or search_query.lower() in art['content'].lower()
            ]
            
        if not filtered_articles:
            st.info("No articles found matching your criteria.")
        else:
            for art in filtered_articles:
                with st.expander(f"📖 {art['title']} — Category: {art['category']}"):
                    st.markdown(f"""
                        <div style="padding: 10px; border-radius: 8px; background-color: #f8faf9; border-left: 4px solid #6d9773;">
                            <p style="font-size: 13px; color: #6d9773; margin-bottom: 10px;">
                                <b>Author:</b> {art['author']} • <b>Published:</b> {art['created_at'][:10]}
                            </p>
                            <p style="font-size: 15px; color: #2c3e50; line-height: 1.6; white-space: pre-line;">
                                {art['content']}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
    with tab2:
        st.markdown("<h2>🧠 Eco Awareness Quiz</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6d9773;'>Test your environmental knowledge and earn Eco Points! (10 points per correct answer)</p>", unsafe_allow_html=True)
        
        # Check if quiz has been completed in this session or db challenges
        completed_ch = db.get_completed_challenges(user['id'])
        quiz_completed = any(c['challenge_text'] == "Completed Climate Awareness Quiz" for c in completed_ch)
        
        if quiz_completed:
            st.success("🎉 You have already completed the Climate Awareness Quiz and claimed your Eco Points!")
            # Display score or let them retake it for fun (without points)
            st.info("You can still review the quiz questions and check your answers below.")
            
        # Quiz definition
        questions = [
            {
                "id": 1,
                "question": "Which sector contributes the most greenhouse gas emissions globally?",
                "options": ["Transportation", "Energy (Electricity & Heat)", "Agriculture & Forestry", "Industrial Processes"],
                "answer": "Energy (Electricity & Heat)",
                "explanation": "The energy sector (electricity, heat, and energy use in industry/buildings) contributes about 73% of global greenhouse gas emissions."
            },
            {
                "id": 2,
                "question": "What is the primary greenhouse gas emitted by burning fossil fuels?",
                "options": ["Methane", "Carbon Dioxide", "Nitrous Oxide", "Water Vapor"],
                "answer": "Carbon Dioxide",
                "explanation": "Carbon dioxide (CO₂) is the primary greenhouse gas emitted by burning fossil fuels, accounting for over 75% of global emissions."
            },
            {
                "id": 3,
                "question": "How much water is wasted per day by a leaky faucet dripping once per second?",
                "options": ["~5 Liters", "~15 Liters", "~30 Liters", "~60 Liters"],
                "answer": "~30 Liters",
                "explanation": "A faucet dripping once per second wastes roughly 30 liters of water a day, or over 11,000 liters per year."
            },
            {
                "id": 4,
                "question": "Which food source has the highest carbon footprint per kilogram of product?",
                "options": ["Beef", "Chicken", "Rice", "Tofu"],
                "answer": "Beef",
                "explanation": "Beef produces 60 kg of greenhouse gases per kg of meat, which is over 10 times higher than chicken or fish, and 30 times higher than tofu."
            }
        ]
        
        score = 0
        answers = {}
        
        for q in questions:
            st.markdown(f"**Q{q['id']}. {q['question']}**")
            answers[q['id']] = st.radio("Select your answer:", q['options'], key=f"q_{q['id']}", index=None)
            st.markdown("<br>", unsafe_allow_html=True)
            
        submit_quiz = st.button("Submit Quiz Answers", disabled=quiz_completed)
        
        if submit_quiz or quiz_completed:
            # Calculate score
            unanswered = False
            for q in questions:
                ans = answers[q['id']] if not quiz_completed else q['options'][0] # mock value if already done to avoid error
                if ans is None and not quiz_completed:
                    unanswered = True
                    break
                    
            if unanswered:
                st.error("Please answer all questions before submitting.")
            else:
                score = 0
                for q in questions:
                    user_ans = answers[q['id']]
                    if user_ans == q['answer']:
                        score += 1
                        st.markdown(f"✅ **Q{q['id']}: Correct!**")
                    else:
                        st.markdown(f"❌ **Q{q['id']}: Incorrect.** (Your answer: {user_ans})")
                        st.markdown(f"*Correct answer: {q['answer']}*")
                    st.markdown(f"<p style='color: #6d9773; font-size:13px; margin-top: -8px;'>{q['explanation']}</p>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                
                points_earned = score * 10
                st.markdown(f"### Score: {score}/{len(questions)} ({points_earned} Eco Points)")
                
                if not quiz_completed and score > 0:
                    # Log points and award badge
                    db.complete_challenge(
                        user_id=user['id'],
                        challenge_text="Completed Climate Awareness Quiz",
                        challenge_type="quiz",
                        points=points_earned
                    )
                    st.success(f"🎉 Quiz submitted! Earned {points_earned} Eco Points.")
                    st.rerun()
