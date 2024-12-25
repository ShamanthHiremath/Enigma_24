import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './card';
import { TrendingUp, TrendingDown, BarChart2, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PricePredictionCard = ({ prediction }) => {
  if (!prediction || prediction.error) {
    return (
      <Card className="bg-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center text-xl">
            <BarChart2 className="mr-2" />
            Price Prediction
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center p-4">
            <AlertTriangle className="mx-auto mb-2 text-yellow-500" size={24} />
            <div className="text-gray-400">
              Unable to generate price prediction at this time.
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const isBullish = prediction.prediction_direction === 'Bullish';
  const trendColor = isBullish ? 'text-green-500' : 'text-red-500';
  const TrendIcon = isBullish ? TrendingUp : TrendingDown;

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-500';
    if (confidence >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  // Prepare training metrics data for the chart
  const trainingData = prediction.training_metrics?.loss.map((loss, index) => ({
    epoch: index + 1,
    loss: loss,
    val_loss: prediction.training_metrics.val_loss[index]
  }));

  return (
    <Card className="bg-gray-800">
      <CardHeader>
        <CardTitle className="flex items-center text-xl">
          <BarChart2 className="mr-2" />
          Price Prediction
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Price Prediction Section */}
          <div className="text-center">
            <div className="text-sm text-gray-400 mb-1">Predicted Price</div>
            <div className={`text-3xl font-bold ${trendColor} flex items-center justify-center`}>
              <TrendIcon className="mr-2" size={24} />
              {formatPrice(prediction.predicted_price)}
            </div>
          </div>

          {/* Price Change Section */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">Price Change</div>
              <div className={`font-bold ${trendColor}`}>
                {formatPrice(prediction.price_change)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-1">Current Price</div>
              <div className="font-bold text-white">
                {formatPrice(prediction.last_close_price)}
              </div>
            </div>
          </div>

          {/* Training Metrics Chart */}
          {prediction.training_metrics && (
            <div className="mt-6">
              <div className="text-sm text-gray-400 mb-2">Model Training Progress</div>
              <div className="h-64 w-full">
                <ResponsiveContainer>
                  <LineChart data={trainingData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="epoch" 
                      stroke="#9CA3AF"
                      label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      label={{ value: 'Loss', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                      labelStyle={{ color: '#9CA3AF' }}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="loss" 
                      stroke="#10B981" 
                      name="Training Loss" 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="val_loss" 
                      stroke="#F59E0B" 
                      name="Validation Loss" 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-gray-400">Final Training Loss</div>
                  <div className="font-medium text-green-500">
                    {prediction.training_metrics.final_loss.toFixed(2)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400">Final Validation Loss</div>
                  <div className="font-medium text-yellow-500">
                    {prediction.training_metrics.final_val_loss.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Confidence Meter */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Prediction Confidence</span>
              <span className={getConfidenceColor(prediction.prediction_confidence)}>
                {prediction.prediction_confidence}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getConfidenceColor(prediction.prediction_confidence)}`}
                style={{ width: `${prediction.prediction_confidence}%` }}
              />
            </div>
          </div>

          {/* Prediction Direction Badge */}
          <div className="flex justify-center">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              isBullish ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              <TrendIcon className="mr-1" size={16} />
              {prediction.prediction_direction}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PricePredictionCard;