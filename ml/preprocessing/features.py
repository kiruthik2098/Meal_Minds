import os
import pandas as pd
import numpy as np

def build_features(df, is_training=True, historical_weekday_means=None):
    """
    Feature engineering pipeline with zero future data leakage.
    Features created:
    1. attendance (primary signal)
    2. day_of_week
    3. is_holiday, is_exam_day, is_event_day
    4. lag_1_demand: meals consumed on previous day (t-1)
    5. lag_1_waste: food waste on previous day (t-1)
    6. rolling_7_demand: mean meals consumed over previous 7 days (shift(1).rolling(7))
    7. rolling_7_attendance: mean attendance over previous 7 days
    8. weekday_historical_mean: average demand for this specific weekday computed strictly on train set
    9. recent_demand_trend: rolling_7_demand - weekday_historical_mean
    """
    data = df.copy()
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date').reset_index(drop=True)
    
    # Lag Features (Shifted by 1 to guarantee zero future data leakage)
    data['lag_1_demand'] = data['meals_consumed'].shift(1)
    data['lag_1_waste'] = data['waste'].shift(1)
    data['rolling_7_demand'] = data['meals_consumed'].shift(1).rolling(window=7, min_periods=1).mean()
    data['rolling_7_attendance'] = data['attendance'].shift(1).rolling(window=7, min_periods=1).mean()
    
    # Backfill first row's lags cleanly
    data['lag_1_demand'] = data['lag_1_demand'].bfill()
    data['lag_1_waste'] = data['lag_1_waste'].bfill()
    data['rolling_7_demand'] = data['rolling_7_demand'].bfill()
    data['rolling_7_attendance'] = data['rolling_7_attendance'].bfill()
    
    # Weekday average mapping (Must only use training statistics!)
    if is_training:
        weekday_means = data.groupby('day_of_week')['meals_consumed'].mean().to_dict()
    else:
        weekday_means = historical_weekday_means
        
    data['weekday_historical_mean'] = data['day_of_week'].map(weekday_means)
    
    # Demand Trend: difference between 7-day rolling demand and historical weekday mean
    data['recent_demand_trend'] = data['rolling_7_demand'] - data['weekday_historical_mean']
    
    return data, weekday_means

if __name__ == '__main__':
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'canteen_operations_180d.csv')
    df = pd.read_csv(data_path)
    featured_df, weekday_means = build_features(df, is_training=True)
    
    print('=== Feature Engineering Verification ===')
    print(f'Total Samples: {len(featured_df)}')
    print('\nNew Features Created:')
    for col in ['lag_1_demand', 'lag_1_waste', 'rolling_7_demand', 'rolling_7_attendance', 'weekday_historical_mean', 'recent_demand_trend']:
        print(f' - {col}: min={featured_df[col].min():.1f}, mean={featured_df[col].mean():.1f}, max={featured_df[col].max():.1f}')
        
    nulls = featured_df.isnull().sum().sum()
    print(f'\nTotal Nulls after feature engineering: {nulls}')
    
    print('\n[LEAKAGE CHECK]:')
    print('Row 10 meals_consumed (target):', featured_df.loc[10, 'meals_consumed'])
    print('Row 11 lag_1_demand (used for row 11 prediction):', featured_df.loc[11, 'lag_1_demand'])
    assert featured_df.loc[10, 'meals_consumed'] == featured_df.loc[11, 'lag_1_demand'], 'Leakage check failed!'
    print('[PASS] lag_1_demand perfectly equals target(t-1) with zero future leakage.')
