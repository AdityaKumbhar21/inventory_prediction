import { useState, useEffect } from 'react';
import axios from 'axios';
import API_URL from '../config';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { CheckCircle2, Database, Brain, Loader2 } from 'lucide-react';

function Dashboard() {
  const [health, setHealth] = useState(null);
  const [model, setModel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [healthRes, modelRes] = await Promise.all([
        axios.get(`${API_URL}/health`),
        axios.get(`${API_URL}/model`)
      ]);
      setHealth(healthRes.data);
      setModel(modelRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data. Make sure the backend is running on ' + API_URL);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-6">
        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Status:</span>
                <span className="text-sm font-medium bg-green-100 text-green-700 px-2 py-1 rounded">
                  {health?.status || 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Model Loaded:</span>
                <span className="text-sm">{health?.model_loaded ? '✓' : '✗'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Data Loaded:</span>
                <span className="text-sm">{health?.data_loaded ? '✓' : '✗'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Model Info */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              ML Model Information
            </CardTitle>
            <CardDescription>XGBoost Regressor Performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-2xl font-bold text-primary">{model?.r2}</p>
                <p className="text-sm text-muted-foreground">R² Score ({(model?.r2 * 100).toFixed(1)}%)</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{model?.rmse}</p>
                <p className="text-sm text-muted-foreground">RMSE</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{model?.mae}</p>
                <p className="text-sm text-muted-foreground">MAE</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{model?.mape}%</p>
                <p className="text-sm text-muted-foreground">MAPE</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            Available Data
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-primary">10</p>
              <p className="text-sm text-muted-foreground mt-2">Stores</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-primary">50</p>
              <p className="text-sm text-muted-foreground mt-2">Items</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-primary">500</p>
              <p className="text-sm text-muted-foreground mt-2">Combinations</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-primary">88.4%</p>
              <p className="text-sm text-muted-foreground mt-2">Accuracy</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Getting Started */}
      <Alert>
        <AlertDescription>
          <p className="font-semibold mb-2">Getting Started:</p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>Navigate to <strong>Predict</strong> to make inventory predictions</li>
            <li>Use <strong>Analytics</strong> to view historical data and trends</li>
            <li>Model uses XGBoost algorithm with 88.4% accuracy</li>
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  );
}

export default Dashboard;
