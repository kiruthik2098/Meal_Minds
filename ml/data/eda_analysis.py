import os
import pandas as pd
import numpy as np

def run_eda(filepath):
    print('=====================================================')
    print('       PHASE 3: EXPLORATORY DATA ANALYSIS (EDA)       ')
    print('=====================================================\n')
    
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # 1. Basic Distributions
    print('--- 1. Operational Distributions ---')
    print(df[['attendance', 'meals_prepared', 'meals_consumed', 'waste']].describe().round(2))
    
    # 2. Correlation Matrix
    print('\n--- 2. Correlation Matrix (What drives demand & waste?) ---')
    num_cols = ['attendance', 'meals_prepared', 'meals_consumed', 'waste', 'is_holiday', 'is_exam_day', 'is_event_day']
    corr = df[num_cols].corr()
    print(corr[['meals_consumed', 'waste']].round(3))
    
    # 3. Day of Week Analysis
    print('\n--- 3. Day of Week Profiles ---')
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_profile = df.groupby('day_of_week')[['attendance', 'meals_consumed', 'meals_prepared', 'waste']].mean().reindex(dow_order)
    dow_profile['waste_ratio_%'] = ((dow_profile['waste'] / dow_profile['meals_prepared']) * 100).round(2)
    print(dow_profile.round(2))
    
    # 4. Outlier Analysis using IQR
    print('\n--- 4. Outlier Detection (Interquartile Range) ---')
    for col in ['attendance', 'meals_consumed', 'waste']:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        print(f'{col}: IQR={iqr:.1f} | Bounds=[{lower_bound:.1f}, {upper_bound:.1f}] | Count of Outliers={len(outliers)}')
        if len(outliers) > 0:
            print(f'   -> Reason: Identified on Event Days ({len(outliers[outliers["is_event_day"]==1])}) or Holidays ({len(outliers[outliers["is_holiday"]==1])})')
            
    print('\n=====================================================')
    print(' [SUCCESS] EDA Complete. Data behavior is understood. ')
    print('=====================================================')

if __name__ == '__main__':
    data_path = os.path.join(os.path.dirname(__file__), 'canteen_operations_180d.csv')
    run_eda(data_path)
