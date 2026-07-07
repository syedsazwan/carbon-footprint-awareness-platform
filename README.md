# 🌱 Carbon Footprint Awareness Platform

An AI-powered, hackathon-level platform built with **Streamlit** that empowers users to measure, analyze, forecast, and reduce their carbon footprint. The platform combines interactive data visualization, machine learning predictions, gamification, and a smart ecological assistant to motivate sustainable lifestyle choices.

---

## 🏆 Key Features

1. **User Authentication & Profiles:** 
   - Secure registrations and logins.
   - Hashed password security using PBKDF2-SHA256.
   - Profile management with dynamic badge updates.
2. **Carbon Footprint Calculator:**
   - Real-time calculations across 5 primary categories: **Transportation**, **Electricity**, **Water**, **Food habits**, and **Waste generation**.
   - Validated against standard carbon emissions factor datasets.
3. **Interactive Dashboard (Plotly):**
   - High-fidelity analytics containing monthly carbon score categories (**Green/Low**, **Yellow/Moderate**, **Red/High**).
   - Interactive gauge indicator of total emissions.
   - Breakdown pie charts and historical month-over-month (MoM) progress charts.
4. **AI-Powered EcoBot:**
   - Rule-based & context-aware chatbot that gives custom insights based on the user's latest calculation.
   - Analyzes carbon hotspots and provides tailored reduction strategies.
   - Quick prompt triggers for quick interaction.
5. **Gamification System:**
   - Earn **Eco Points** by completing daily challenges, weekly challenges, and personalized recommendation goals.
   - Unlock achievement badges (e.g., *Eco Rookie*, *Carbon Cutter*, *Energy Saver*, *Green Champion*).
   - Global Leaderboard to promote community competition.
6. **AI Emission Forecasting (Scikit-Learn):**
   - Trains a `LinearRegression` model on the user's history to forecast emissions for the next 3 months.
   - Displays slope coefficients (emissions growth rate) and model confidence values (R² score).
   - Proposes targets to reduce carbon footprint.
7. **Educational Learning Center & Quiz:**
   - Built-in articles about climate change, renewable energy, waste, and conservation.
   - Interactive **Climate Quiz** rewarding users with Eco Points for correct answers.
8. **Exportable PDF Reports (ReportLab):**
   - Generates professional, download-ready PDF reports with formatted data tables and targeted tips.
9. **Admin Panel:**
   - High-level platform statistics (total users, average emissions, completed challenges).
   - Full user directory.
   - Publish/remove learning center articles.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **Visualizations:** Plotly, Matplotlib
- **Machine Learning:** Scikit-Learn
- **PDF Engine:** ReportLab

---

## 📂 Project Structure

```
carbon_footprint_platform/
│
├── app.py                  # Main Entrypoint
├── database.db             # SQLite Database (Auto-created)
├── database.py             # SQLite Schema & Operations
├── authentication.py       # Login, Sign Up, & Profile UI
├── carbon_calculator.py    # Calculator Form & Emission Logic
├── chatbot.py              # EcoBot Interface & AI Response
├── recommendations.py     # Tailored Recommendations & Challenges
├── dashboard.py            # Plotly Analytics & Visualizations
├── reports.py              # ReportLab PDF Generation
├── ml_model.py             # Scikit-learn Linear Regression Forecasting
├── admin.py                # Admin Panel Tabs & Platform Stats
├── articles.py             # Learning Center & Climate Quiz
├── utils.py                # Security Hashing & Shared Styling
├── assets/                 # Shared Media Resources
├── data/                   # Data Stores
└── models/                 # Model Checkpoints
```

---

## 🔧 Database Schema

### `users`
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `password` (TEXT PBKDF2-SHA256 hashed)
- `name` (TEXT)
- `email` (TEXT)
- `eco_points` (INTEGER)
- `role` (TEXT: 'user' or 'admin')
- `created_at` (TIMESTAMP)

### `carbon_history`
- `user_id` (INTEGER FOREIGN KEY)
- `month` (TEXT: 'YYYY-MM')
- `transport`, `electricity`, `water`, `food`, `waste` (REAL emissions in kg CO₂)
- `total_emissions` (REAL)
- `score_category` (TEXT: 'Green' | 'Yellow' | 'Red')

### `completed_challenges`
- `user_id` (INTEGER FOREIGN KEY)
- `challenge_text` (TEXT)
- `challenge_type` (TEXT: 'daily' | 'weekly' | 'recommendation' | 'quiz')
- `points_awarded` (INTEGER)
- `completed_date` (TEXT: 'YYYY-MM-DD')

### `badges`
- `user_id` (INTEGER FOREIGN KEY)
- `badge_name` (TEXT)
- `awarded_at` (TIMESTAMP)

### `chatbot_history`
- `user_id` (INTEGER FOREIGN KEY)
- `sender` (TEXT: 'user' | 'bot')
- `message` (TEXT)
- `timestamp` (TIMESTAMP)

---

## 🚀 Installation & Running Guide

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.

### 2. Setup Workspace
Clone or navigate to the project directory:
```bash
cd carbon_footprint_platform
```

### 3. Install Dependencies
Run the pip installer:
```bash
pip install -r requirements.txt
```

### 4. Run the Platform
Start the Streamlit application:
```bash
streamlit run app.py
```

---

## 👤 Sample Accounts (Preloaded)

To make presentation and testing instant, the database is preloaded with accounts and dummy data:

* **Administrator Account:**
  * **Username:** `admin`
  * **Password:** `admin123`
* **Eco Hero User (with 5 months of carbon logs):**
  * **Username:** `green_hero`
  * **Password:** `password123`
