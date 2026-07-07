import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

def get_emission_forecast(history: list):
    """
    Train a scikit-learn Linear Regression model on user carbon logs
    and forecast emissions for the next 3 months.
    """
    if len(history) < 2:
        return None
        
    df = pd.DataFrame(history)
    df = df.sort_values(by="month")
    
    # Preprocess dates to ordinals
    df['date'] = pd.to_datetime(df['month'] + "-01")
    df['ordinal'] = df['date'].map(datetime.toordinal)
    
    X = df[['ordinal']].values
    y = df['total_emissions'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    slope = float(model.coef_[0])
    intercept = float(model.intercept_)
    r2_score = float(model.score(X, y))
    
    last_date = df['date'].max()
    future_dates = []
    future_ordinals = []
    
    for i in range(1, 4):
        # 30.5 days on average
        next_date = last_date + timedelta(days=int(30.5 * i))
        future_dates.append(next_date.strftime("%Y-%m"))
        future_ordinals.append([next_date.toordinal()])
        
    predictions = model.predict(future_ordinals)
    predictions = np.clip(predictions, 0, None).tolist() # prevent negative emissions
    
    # Generate ideal target reduction paths (-5% per month from last actual)
    last_actual = float(y[-1])
    target_path = [last_actual]
    for i in range(1, 4):
        target_path.append(target_path[-1] * 0.95)
        
    # Standard short, medium and long term goals recommendations
    rec_short = last_actual * 0.95
    rec_medium = last_actual * 0.85
    rec_long = last_actual * 0.50
    
    return {
        "months": df['month'].tolist(),
        "actual_emissions": y.tolist(),
        "future_months": future_dates,
        "predicted_emissions": predictions,
        "slope": slope,
        "intercept": intercept,
        "r2_score": r2_score,
        "ideal_targets": target_path[1:], # matching future months
        "recommendations": {
            "short_term_target": round(rec_short, 2),
            "medium_term_target": round(rec_medium, 2),
            "long_term_target": round(rec_long, 2)
        }
    }
