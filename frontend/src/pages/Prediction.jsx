import { useState } from 'react';
import axios from 'axios';
import API_URL from '../config';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, Loader2 } from 'lucide-react';

function Prediction() {
  const [formData, setFormData] = useState({
    store: '1',
    item: '1',
    date: new Date().toISOString().split('T')[0]
  });
  const [result, setResult] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const predRes = await axios.post(`${API_URL}/predict`, {
        store: parseInt(formData.store),
        item: parseInt(formData.item),
        date: formData.date
      });
      setResult(predRes.data);

      const forecastRes = await axios.get(
        `${API_URL}/forecast/${formData.store}/${formData.item}?days=7`
      );
      setForecast(forecastRes.data.predictions);
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Inventory Prediction</h1>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Prediction Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="store">Store ID (1-10)</Label>
                <Input
                  id="store"
                  name="store"
                  type="number"
                  value={formData.store}
                  onChange={handleChange}
                  min="1"
                  max="10"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="item">Item ID (1-50)</Label>
                <Input
                  id="item"
                  name="item"
                  type="number"
                  value={formData.item}
                  onChange={handleChange}
                  min="1"
                  max="50"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  name="date"
                  type="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Predicting...
                  </>
                ) : (
                  <>
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Predict
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Prediction Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Predicted Sales</p>
                      <p className="text-3xl font-bold text-primary">{result.predicted_sales}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Recommended Inventory</p>
                      <p className="text-3xl font-bold text-green-600">{result.recommended_inventory}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Lower Bound</p>
                      <p className="text-2xl font-semibold">{result.confidence_lower}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Upper Bound</p>
                      <p className="text-2xl font-semibold">{result.confidence_upper}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {forecast && forecast.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>7-Day Forecast</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={forecast}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area
                          type="monotone"
                          dataKey="confidence_upper"
                          stackId="1"
                          stroke="#8884d8"
                          fill="#8884d8"
                          fillOpacity={0.2}
                          name="Upper Bound"
                        />
                        <Area
                          type="monotone"
                          dataKey="predicted_sales"
                          stackId="2"
                          stroke="#82ca9d"
                          fill="#82ca9d"
                          name="Predicted Sales"
                        />
                        <Area
                          type="monotone"
                          dataKey="confidence_lower"
                          stackId="3"
                          stroke="#ffc658"
                          fill="#ffc658"
                          fillOpacity={0.2}
                          name="Lower Bound"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {!result && !error && (
            <div className="flex items-center justify-center h-[400px] border-2 border-dashed rounded-lg">
              <p className="text-muted-foreground">Enter parameters and click Predict to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Prediction;
