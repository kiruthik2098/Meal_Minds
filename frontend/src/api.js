// Use relative /api URL so requests go through the Vite proxy seamlessly, avoiding CORS or localhost vs 127.0.0.1 discrepancies
const API_BASE = '/api';

export const api = {
  // 1. Dashboard statistics
  async getDashboardStats() {
    const res = await fetch(`${API_BASE}/dashboard/statistics`);
    if (!res.ok) throw new Error('Failed to fetch dashboard statistics');
    return res.json();
  },

  // 2. Weekday pattern distributions
  async getWeekdayPatterns() {
    const res = await fetch(`${API_BASE}/analytics/weekday-patterns`);
    if (!res.ok) throw new Error('Failed to fetch weekday analytics');
    return res.json();
  },

  // 3. Model comparison metrics
  async getModelPerformance() {
    const res = await fetch(`${API_BASE}/model/performance`);
    if (!res.ok) throw new Error('Failed to fetch model metrics');
    return res.json();
  },

  // 4. Meal records list
  async getRecords(limit = 100) {
    const res = await fetch(`${API_BASE}/records?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch operational records');
    return res.json();
  },

  // 5. Create new meal record
  async createRecord(recordData) {
    const res = await fetch(`${API_BASE}/records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(recordData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to create record' }));
      throw new Error(err.detail || 'Validation error');
    }
    return res.json();
  },

  // 6. Predict demand & generate recommendations
  async predictDemand(predictionPayload) {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(predictionPayload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Prediction failed' }));
      throw new Error(err.detail || 'Failed to generate forecast');
    }
    return res.json();
  },

  // 7. Get historical predictions list
  async getPredictions(limit = 20) {
    const res = await fetch(`${API_BASE}/predictions?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch predictions');
    return res.json();
  }
};
