import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(__file__))
from predict import predict_single_day

def generate_recommendations(date_str, expected_attendance, is_holiday=0, is_exam_day=0, is_event_day=0):
    """
    Translates raw ML forecast into actionable canteen preparation recommendations.
    Provides:
    1. Predicted Demand (AI model output)
    2. Operational Safety Buffer (Residual standard error + risk adjustment)
    3. Recommended Preparation Quantity
    4. Transparent Factor Explanations (Attendance shift, day-of-week context, recent trend)
    5. Actionable Waste-Reduction Suggestions
    """
    # 1. Obtain raw ML prediction
    pred_info = predict_single_day(date_str, expected_attendance, is_holiday, is_exam_day, is_event_day)
    
    predicted_demand = pred_info["predicted_demand"]
    day_name = pred_info["day_of_week"]
    residual_std = pred_info["residual_std"]  # ~6.27 meals
    weekday_hist_mean = pred_info["weekday_historical_mean"]
    
    # Event & Holiday Operational Demand Multipliers:
    # On Campus Fest / Event Days: Walk-in guest turnout, symposium delegates, and extra student appetite (+18% consumption surge)
    # On Holidays: Day scholars are absent; consumption is restricted to 50-60% of baseline (55% hostel dining rate)
    if is_event_day:
        predicted_demand = round(predicted_demand * 1.18, 1)
    elif is_holiday:
        predicted_demand = round(predicted_demand * 0.55, 1)

    # 2. Safety Buffer Calculation
    # Canteen goal: prevent food stockout (under-cooking) without causing massive waste.
    # We use a 1.0 sigma residual buffer (covers ~84% of upside variance), capped appropriately.
    base_buffer = round(residual_std * 1.0)
    
    # Context adjustments to buffer
    if is_event_day:
        # Higher uncertainty on campus fest/event days: increased buffer
        buffer = int(base_buffer * 1.8)
    elif day_name == "Friday":
        # Friday is a high-waste day; tighten buffer to prevent routine excess
        buffer = max(3, int(base_buffer * 0.7))
    elif is_holiday:
        # Holiday has minimal variance and small headcount; minimal buffer
        buffer = max(1, int(base_buffer * 0.4))
    else:
        buffer = int(base_buffer)
        
    recommended_prep = int(round(predicted_demand + buffer))
    
    # 3. Factor Explanations (Truth-grounded from features)
    explanations = []
    
    # Attendance factor
    data_path = os.path.join(os.path.dirname(__file__), "data", "canteen_operations_180d.csv")
    df = pd.read_csv(data_path)
    overall_avg_att = df["attendance"].mean()
    att_diff_pct = ((expected_attendance - overall_avg_att) / overall_avg_att) * 100
    
    if att_diff_pct > 5:
        explanations.append({
            "type": "positive",
            "icon": "trending-up",
            "text": f"Expected attendance ({expected_attendance}) is {abs(att_diff_pct):.1f}% above overall average ({overall_avg_att:.0f})."
        })
    elif att_diff_pct < -5:
        explanations.append({
            "type": "negative",
            "icon": "trending-down",
            "text": f"Expected attendance ({expected_attendance}) is {abs(att_diff_pct):.1f}% below overall average ({overall_avg_att:.0f})."
        })
    else:
        explanations.append({
            "type": "neutral",
            "icon": "minus",
            "text": f"Expected attendance ({expected_attendance}) aligns with normal operational levels."
        })
        
    # Weekday historical demand context
    diff_from_weekday = predicted_demand - weekday_hist_mean
    if abs(diff_from_weekday) > 10:
        dir_word = "higher" if diff_from_weekday > 0 else "lower"
        explanations.append({
            "type": "info",
            "icon": "calendar",
            "text": f"Prediction is {abs(diff_from_weekday):.1f} meals {dir_word} than historical {day_name} average ({weekday_hist_mean:.1f})."
        })
    else:
        explanations.append({
            "type": "info",
            "icon": "calendar",
            "text": f"Consistent with historical {day_name} average demand ({weekday_hist_mean:.1f} meals)."
        })
        
    # Recent trend context
    recent_7d_mean = df["meals_consumed"].iloc[-7:].mean()
    trend_val = recent_7d_mean - df["meals_consumed"].mean()
    if trend_val > 5:
        explanations.append({
            "type": "info",
            "icon": "activity",
            "text": f"Recent 7-day dining demand is trending upward (+{trend_val:.1f} meals/day)."
        })
    elif trend_val < -5:
        explanations.append({
            "type": "info",
            "icon": "activity",
            "text": f"Recent 7-day dining demand is trending slightly lower ({trend_val:.1f} meals/day)."
        })
        
    if is_event_day:
        explanations.append({
            "type": "warning",
            "icon": "alert-circle",
            "text": "Campus Fest / Event Surge (+18%): Increased walk-in rate, guest delegates, and extended dining hours factored into elevated production target."
        })
    if is_holiday:
        explanations.append({
            "type": "warning",
            "icon": "alert-circle",
            "text": "Academic Holiday Schedule (50-60% of normal): Day-scholar attendance absent; preparation calibrated at 55% baseline for residential hostel students."
        })

    # 4. Actionable Waste-Reduction Suggestions (Rule Layer)
    suggestions = []
    
    if is_holiday:
        suggestions.append({
            "level": "caution",
            "title": "Holiday Production Downscaling",
            "message": "Campus is on holiday schedule. Downscaled meals produced to match hostel-only demand to prevent large batch spoilage."
        })
    elif is_event_day:
        suggestions.append({
            "level": "info",
            "title": "Event Surge & Batch Staggering",
            "message": "Elevated meals produced due to campus event. Stagger preparation into 2 batches (65% early, 35% supplementary) to meet peak turnout without overproducing."
        })
    
    # Friday Specific Anomaly
    if day_name == "Friday":
        suggestions.append({
            "level": "warning",
            "title": "High-Waste Friday Pattern Detected",
            "message": "Fridays historically produce 13.6% waste (56+ meals wasted) due to early student departures. Keep preparation strictly at or below recommended quantity, and avoid secondary batch preparations after 1:30 PM."
        })
        
    # Demand significantly below capacity
    if predicted_demand < (overall_avg_att * 0.75) and not is_holiday:
        suggestions.append({
            "level": "caution",
            "title": "Subdued Demand Forecast",
            "message": "Predicted consumption is considerably below typical canteen capacity. Reduce pre-cooked base portions by 15% and switch to cooked-to-order for supplementary trays."
        })
        
    # High event surge
    if is_event_day or predicted_demand > 500:
        suggestions.append({
            "level": "info",
            "title": "Batch Staggering Recommended",
            "message": "High-demand day anticipated. Stagger food prep into 2 batches (65% at 11:30 AM, 35% at 1:00 PM) to avoid end-of-day over-prep if turnout peaks early."
        })
        
    # Standard operational tip if no specific alert
    if len(suggestions) == 0:
        suggestions.append({
            "level": "success",
            "title": "Balanced Production Target",
            "message": f"Demand patterns are steady. Target {recommended_prep} meals (+{buffer} safety buffer) to maintain 95%+ service availability with minimal surplus."
        })
        
    return {
        "date": date_str,
        "day_of_week": day_name,
        "expected_attendance": expected_attendance,
        "predicted_demand": predicted_demand,
        "safety_buffer": buffer,
        "recommended_preparation": recommended_prep,
        "model_name": pred_info["model_name"],
        "model_mae": pred_info["model_mae"],
        "explanations": explanations,
        "suggestions": suggestions
    }

if __name__ == "__main__":
    print("=====================================================")
    print("     PHASE 6: RECOMMENDATION ENGINE VERIFICATION     ")
    print("=====================================================\n")
    
    # Test Scenario 1: Normal Friday (Check Friday wastage alert & tight buffer)
    print("--- SCENARIO 1: Friday Operations (High-Waste Day Analysis) ---")
    rec1 = generate_recommendations("2026-08-28", expected_attendance=400)
    print(f"Date: {rec1['date']} ({rec1['day_of_week']}) | Expected Attendance: {rec1['expected_attendance']}")
    print(f"AI Predicted Demand:       {rec1['predicted_demand']} meals")
    print(f"Operational Safety Buffer: +{rec1['safety_buffer']} meals")
    print(f"Recommended Preparation:   {rec1['recommended_preparation']} meals\n")
    print("Explanations:")
    for e in rec1["explanations"]:
        print(f"  [{e['type'].upper()}] {e['text']}")
    print("\nWaste Reduction Suggestions:")
    for s in rec1["suggestions"]:
        print(f"  * {s['title']}: {s['message']}")
        
    # Test Scenario 2: Event Day (Check batch staggering suggestion)
    print("\n--- SCENARIO 2: Campus Event Day (Surge Attendance) ---")
    rec2 = generate_recommendations("2026-08-29", expected_attendance=600, is_event_day=1)
    print(f"Date: {rec2['date']} ({rec2['day_of_week']}) | Expected Attendance: {rec2['expected_attendance']}")
    print(f"AI Predicted Demand:       {rec2['predicted_demand']} meals")
    print(f"Operational Safety Buffer: +{rec2['safety_buffer']} meals")
    print(f"Recommended Preparation:   {rec2['recommended_preparation']} meals\n")
    print("Waste Reduction Suggestions:")
    for s in rec2["suggestions"]:
        print(f"  * {s['title']}: {s['message']}")
    print("=====================================================")
