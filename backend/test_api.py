import sys
import os
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

client = TestClient(app)

def test_api_suite():
    print("=====================================================")
    print("         PHASE 8: REST API INTEGRATION SUITE         ")
    print("=====================================================\n")

    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] GET / -> 200 OK (Service healthy)")

    # 2. Dashboard KPIs
    res = client.get("/api/dashboard/statistics")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_records"] == 180
    assert stats["overall_waste_percentage"] > 0
    print(f"[PASS] GET /api/dashboard/statistics -> 200 OK (Records: {stats['total_records']}, Waste %: {stats['overall_waste_percentage']}%, Active Model MAE: {stats['active_model_mae']})")

    # 3. Weekday patterns
    res = client.get("/api/analytics/weekday-patterns")
    assert res.status_code == 200
    patterns = res.json()
    assert len(patterns) == 7
    friday = [p for p in patterns if p["day_of_week"] == "Friday"][0]
    print(f"[PASS] GET /api/analytics/weekday-patterns -> 200 OK (7 weekdays returned; Friday waste rate: {friday['waste_percentage']}%)")

    # 4. Model comparison metrics
    res = client.get("/api/model/performance")
    assert res.status_code == 200
    models = res.json()
    assert len(models) >= 4
    print(f"[PASS] GET /api/model/performance -> 200 OK ({len(models)} models benchmarked; Winner: {models[0]['model_name']} with MAE: {models[0]['mae']})")

    # 5. Prediction endpoint with recommendations
    pred_payload = {
        "date": "2026-08-28",
        "expected_attendance": 410,
        "is_holiday": 0,
        "is_exam_day": 0,
        "is_event_day": 0
    }
    res = client.post("/api/predict", json=pred_payload)
    assert res.status_code == 200
    pred = res.json()
    assert "predicted_demand" in pred
    assert "recommended_preparation" in pred
    assert len(pred["explanations"]) > 0
    assert len(pred["suggestions"]) > 0
    print(f"[PASS] POST /api/predict -> 200 OK (Predicted: {pred['predicted_demand']} | Recommended: {pred['recommended_preparation']} | Buffer: +{pred['safety_buffer']})")

    # 6. Physical validation guardrail (Negative test: consumed > prepared)
    invalid_record = {
        "date": "2026-09-01",
        "attendance": 300,
        "meals_prepared": 200,
        "meals_consumed": 250  # VIOLATION
    }
    res = client.post("/api/records", json=invalid_record)
    assert res.status_code == 422 or res.status_code == 400
    print(f"[PASS] POST /api/records [Invalid: consumed > prepared] -> {res.status_code} Blocked properly by Pydantic validator.")

    # 7. Valid record creation
    valid_record = {
        "date": "2026-09-01",
        "attendance": 350,
        "meals_prepared": 340,
        "meals_consumed": 315,
        "is_holiday": 0,
        "is_exam_day": 0,
        "is_event_day": 0
    }
    res = client.post("/api/records", json=valid_record)
    assert res.status_code == 201
    created = res.json()
    assert created["waste"] == 25
    assert created["day_of_week"] == "Tuesday"
    print(f"[PASS] POST /api/records -> 201 Created (ID: {created['id']}, Date: {created['date']}, Waste auto-calculated: {created['waste']})")

    # Clean up test record
    del_res = client.delete(f"/api/records/{created['id']}")
    assert del_res.status_code == 204
    print(f"[PASS] DELETE /api/records/{created['id']} -> 204 Cleaned up test record.")

    print("\n=====================================================")
    print("   [SUCCESS] ALL REST API ENDPOINTS WORKING PROPERLY  ")
    print("=====================================================")

if __name__ == "__main__":
    test_api_suite()
