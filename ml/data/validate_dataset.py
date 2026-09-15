import os
import pandas as pd

def validate_dataset(filepath=None):
    if filepath is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, 'canteen_operations_180d.csv')
        
    print(f'=== Validating Dataset: {filepath} ===')
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'File not found: {filepath}')
        
    df = pd.read_csv(filepath)
    errors = []
    
    # Check 1: Record count
    if len(df) < 90:
        errors.append(f'Dataset has insufficient records: {len(df)} (Expected >= 90)')
    else:
        print(f'[PASS] Record count: {len(df)} records')
        
    # Check 2: Required columns
    required_cols = ['date', 'day_of_week', 'attendance', 'meals_prepared', 'meals_consumed', 'waste']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f'Missing required columns: {missing_cols}')
    else:
        print(f'[PASS] Required columns present: {required_cols}')
        
    # Check 3: Null or missing values
    null_counts = df[required_cols].isnull().sum()
    if null_counts.sum() > 0:
        errors.append(f'Null values detected: {null_counts[null_counts > 0].to_dict()}')
    else:
        print('[PASS] Zero missing/null values')
        
    # Check 4: Duplicate dates
    dupes = df[df.duplicated(subset=['date'])]
    if len(dupes) > 0:
        errors.append(f'Duplicate dates found: {dupes["date"].tolist()}')
    else:
        print('[PASS] All dates are strictly unique')
        
    # Check 5: Non-negative values
    for col in ['attendance', 'meals_prepared', 'meals_consumed', 'waste']:
        if (df[col] < 0).any():
            errors.append(f'Negative values found in column: {col}')
    print('[PASS] All numerical attributes strictly >= 0')
    
    # Check 6: Physical constraint (consumed <= prepared)
    violating_consumption = df[df['meals_consumed'] > df['meals_prepared']]
    if len(violating_consumption) > 0:
        errors.append(f'{len(violating_consumption)} rows violate meals_consumed <= meals_prepared')
    else:
        print('[PASS] Physical constraint satisfied: meals_consumed <= meals_prepared for 100% of rows')
        
    # Check 7: Exact waste calculation (waste == prepared - consumed)
    calculated_waste = df['meals_prepared'] - df['meals_consumed']
    discrepancy = (df['waste'] != calculated_waste).sum()
    if discrepancy > 0:
        errors.append(f'{discrepancy} rows have inconsistent waste values')
    else:
        print('[PASS] Calculated waste matches meals_prepared - meals_consumed exactly')
        
    # Summary of stats
    print('\n=== Dataset Operational Summary ===')
    print(f'Date Range: {df["date"].min()} to {df["date"].max()}')
    print(f'Avg Daily Attendance: {df["attendance"].mean():.1f}')
    print(f'Avg Meals Consumed:   {df["meals_consumed"].mean():.1f}')
    print(f'Avg Meals Prepared:   {df["meals_prepared"].mean():.1f}')
    print(f'Avg Daily Waste:      {df["waste"].mean():.1f} meals')
    print(f'Overall Waste Rate:   {(df["waste"].sum() / df["meals_prepared"].sum() * 100):.2f}%')
    
    # Weekday waste check
    print('\n=== Waste by Day of Week ===')
    weekday_waste = df.groupby('day_of_week')[['meals_prepared', 'meals_consumed', 'waste']].mean().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    weekday_waste['waste_pct'] = (weekday_waste['waste'] / weekday_waste['meals_prepared']) * 100
    print(weekday_waste)
    
    if errors:
        print('\n[FAIL] Validation Errors:')
        for e in errors:
            print(f' - {e}')
        return False
    else:
        print('\n[SUCCESS] Dataset passed all integrity and business rule validations!')
        return True

if __name__ == '__main__':
    validate_dataset()
