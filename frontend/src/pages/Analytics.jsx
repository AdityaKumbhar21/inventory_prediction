import { useState } from 'react';
import axios from 'axios';
import API_URL from '../config';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { BarChart3, Loader2, TrendingUp, TrendingDown, Minus } from 'lucide-react';

function Analytics() {
  const [formData, setFormData] = useState({
    store: '1',
    item: '1',
    days: '90'
  });
  const [analytics, setAnalytics] = useState(null);
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
      const res = await axios.get(
        `${API_URL}/analytics/${formData.store}/${formData.item}?days=${formData.days}`
      );
      setAnalytics(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return <TrendingUp className="h-5 w-5 text-green-600" />;
    if (trend === 'decreasing') return <TrendingDown className="h-5 w-5 text-red-600" />;
    return <Minus className="h-5 w-5 text-gray-600" />;
  };

  const getTrendColor = (trend) => {
    if (trend === 'increasing') return 'text-green-600';
    if (trend === 'decreasing') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Analytics</h1>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Analytics Parameters</CardTitle>
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
                <Label htmlFor="days">Days of History</Label>
                <Input
                  id="days"
                  name="days"
                  type="number"
                  value={formData.days}
                  onChange={handleChange}
                  min="1"
                  max="365"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <BarChart3 className="mr-2 h-4 w-4" />
                    Get Analytics
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

          {analytics && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Statistics (Last {formData.days} days)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Mean Sales</p>
                      <p className="text-2xl font-bold">{analytics.statistics.mean_sales.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Median Sales</p>
                      <p className="text-2xl font-bold">{analytics.statistics.median_sales.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Std Dev</p>
                      <p className="text-2xl font-bold">{analytics.statistics.std_sales.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Min Sales</p>
                      <p className="text-2xl font-bold">{analytics.statistics.min_sales.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Max Sales</p>
                      <p className="text-2xl font-bold">{analytics.statistics.max_sales.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Trend</p>
                      <div className="flex items-center gap-2">
                        {getTrendIcon(analytics.trend)}
                        <p className={`text-xl font-bold capitalize ${getTrendColor(analytics.trend)}`}>
                          {analytics.trend}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Historical Sales</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={analytics.historical_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="sales"
                        stroke="#8884d8"
                        strokeWidth={2}
                        dot={false}
                        name="Sales"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </>
          )}

          {!analytics && !error && (
            <div className="flex items-center justify-center h-[400px] border-2 border-dashed rounded-lg">
              <p className="text-muted-foreground">Enter parameters and click Get Analytics to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Analytics;
