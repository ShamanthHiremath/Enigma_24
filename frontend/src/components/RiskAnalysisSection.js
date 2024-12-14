import React from 'react';
import { Shield, TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react';

// Inline Card and CardHeader components
const Card = ({ children, className }) => (
  <div className={`rounded-xl shadow-lg ${className}`}>{children}</div>
);

const CardHeader = ({ children, className }) => (
  <div className={`p-4 border-b border-gray-700 ${className}`}>{children}</div>
);

const CardTitle = ({ children, className }) => (
  <h2 className={`text-xl font-bold text-white ${className}`}>{children}</h2>
);

const CardContent = ({ children, className }) => (
  <div className={`p-4 ${className}`}>{children}</div>
);

const RiskMetricCard = ({ title, value, icon: Icon, colorClass }) => (
  <div className="bg-gray-700 rounded-lg p-4 flex items-center justify-between">
    <div>
      <p className="text-gray-400 text-sm">{title}</p>
      <p className={`text-lg font-bold ${colorClass}`}>{value}</p>
    </div>
    <Icon className={`h-8 w-8 ${colorClass}`} />
  </div>
);

const RiskAnalysisSection = ({ riskAnalysis }) => {
  if (!riskAnalysis) return null;

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getTrendIcon = (trend) => 
    trend?.toLowerCase() === 'bullish' ? TrendingUp : TrendingDown;

  // Transform the flat riskAnalysis structure into the expected metrics structure
  const transformedMetrics = {
    risk_level: riskAnalysis.risk_level,
    metrics: {
      volatility: riskAnalysis.volatility,
      daily_return: riskAnalysis.daily_return,
      trend: riskAnalysis.trend
    },
    latest_data: {
      close: parseFloat(riskAnalysis.latest_close)
    }
  };

  const metrics = [
    {
      title: 'Risk Level',
      value: transformedMetrics.risk_level || 'N/A',
      icon: Shield,
      colorClass: getRiskColor(transformedMetrics.risk_level)
    },
    {
      title: 'Volatility',
      value: transformedMetrics.metrics.volatility || 'N/A',
      icon: Activity,
      colorClass: 'text-blue-400'
    },
    {
      title: 'Daily Return',
      value: transformedMetrics.metrics.daily_return || 'N/A',
      icon: DollarSign,
      colorClass: parseFloat(transformedMetrics.metrics.daily_return) >= 0 ? 'text-green-400' : 'text-red-400'
    },
    {
      title: 'Market Trend',
      value: transformedMetrics.metrics.trend || 'N/A',
      icon: getTrendIcon(transformedMetrics.metrics.trend),
      colorClass: transformedMetrics.metrics.trend?.toLowerCase() === 'bullish' ? 'text-green-400' : 'text-red-400'
    }
  ];

  return (
    <Card className="bg-gray-800">
      <CardHeader>
        <CardTitle>Risk Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric, index) => (
            <RiskMetricCard key={index} {...metric} />
          ))}
        </div>

        {transformedMetrics.latest_data?.close && (
          <div className="mt-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-2">Latest Trading Data</h3>
              <p className="text-gray-400">
                Closing Price: <span className="text-white font-bold">
                  ${transformedMetrics.latest_data.close.toFixed(2)}
                </span>
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RiskAnalysisSection;