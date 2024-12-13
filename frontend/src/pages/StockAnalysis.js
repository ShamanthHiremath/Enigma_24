import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Building, TrendingUp, TrendingDown, AlertTriangle, Newspaper, ShieldCheck, ShieldAlert, ShieldOff } from 'lucide-react';const RiskBadge = ({ riskLevel }) => {
  const getRiskColor = () => {
    switch (riskLevel) {
      case 'Low': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskIcon = () => {
    switch (riskLevel) {
      case 'Low': return <ShieldCheck className="mr-1" />;
      case 'Medium': return <ShieldAlert className="mr-1" />;
      case 'High': return <ShieldOff className="mr-1" />;
      default: return <AlertTriangle className="mr-1" />;
    }
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getRiskColor()}`}>
      {getRiskIcon()}
      {riskLevel} Risk
    </div>
  );
};

const RiskAnalysisSection = ({ riskAnalysis }) => {
  if (!riskAnalysis) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        <AlertTriangle className="mr-2" /> Risk Analysis
      </h2>
      
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-lg font-semibold mb-2">Risk Metrics</h3>
          <div className="space-y-2">
            <p>
              <span className="text-gray-400">Risk Level:</span>{' '}
              <RiskBadge riskLevel={riskAnalysis.risk_level} />
            </p>
            <p>
              <span className="text-gray-400">Volatility:</span>{' '}
              <span className={`font-medium ${
                parseFloat(riskAnalysis.volatility) > 5 
                  ? 'text-red-500' 
                  : parseFloat(riskAnalysis.volatility) > 2 
                  ? 'text-yellow-500' 
                  : 'text-green-500'
              }`}>
                {riskAnalysis.volatility}
              </span>
            </p>
            <p>
              <span className="text-gray-400">Daily Return:</span>{' '}
              <span className={`font-medium ${
                parseFloat(riskAnalysis.daily_return) > 0 
                  ? 'text-green-500' 
                  : 'text-red-500'
              }`}>
                {riskAnalysis.daily_return}
              </span>
            </p>
            <p>
              <span className="text-gray-400">Market Trend:</span>{' '}
              <span className={`font-medium ${
                riskAnalysis.trend === 'Bullish' 
                  ? 'text-green-500' 
                  : 'text-red-500'
              }`}>
                {riskAnalysis.trend}
              </span>
            </p>
          </div>
        </div>
        
        {riskAnalysis.latest_close && (
          <div>
            <h3 className="text-lg font-semibold mb-2">Price Insights</h3>
            <div className="bg-gray-700 rounded-lg p-4">
              <p>
                <span className="text-gray-400">Latest Close Price:</span>{' '}
                <span className="font-bold">${riskAnalysis.latest_close.toFixed(2)}</span>
              </p>
              {/* You could add more price-related insights here */}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
const SentimentBadge = ({ prediction }) => {
  if (prediction === null || prediction === undefined) {
    return null;
  }

  const getSentimentClass = (score) => {
    if (score <= 40) return 'bg-red-100 text-red-800';
    if (score >= 60) return 'bg-green-100 text-green-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getSentimentText = (score) => {
    if (score <= 40) return 'Bearish';
    if (score >= 60) return 'Bullish';
    return 'Neutral';
  };

  const getSentimentIcon = (score) => {
    if (score <= 40) return <TrendingDown className="mr-1" />;
    if (score >= 60) return <TrendingUp className="mr-1" />;
    return <AlertTriangle className="mr-1" />;
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getSentimentClass(prediction)}`}>
      {getSentimentIcon(prediction)}
      {getSentimentText(prediction)} ({prediction.toFixed(1)})
    </div>
  );
};

const NewsSection = ({ title, news, icon }) => {
  if (!news || news.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        {icon}
        <span className="ml-2">{title}</span>
      </h2>
      <div className="space-y-4">
        {news.map((article, index) => (
          <div key={index} className="border-b border-gray-700 last:border-b-0 pb-4">
            <a 
              href={article.link || article.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-400 transition-colors block"
            >
              <h3 className="font-medium mb-1">{article.title || article.headline}</h3>
              <div className="flex justify-between items-center">
                <p className="text-sm text-gray-400">
                  {article.publisher || 'Unknown Source'} 
                  {article.published_at && ` - ${new Date(article.published_at).toLocaleDateString()}`}
                </p>
                {article.relevant_prediction && (
                  <SentimentBadge prediction={article.relevant_prediction} />
                )}
              </div>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

const StockAnalysis = () => {
  const { symbol } = useParams();
  const [stockDetails, setStockDetails] = useState({
    current_quote: {
      price: 0,
      change: 0,
      change_percent: 0,
    },
    profile: {
      name: '',
      symbol: '',
      industry: '',
      sector: '',
      country: '',
      website: '',
    },
    historical_prices: [],
    stock_news: [],
    country_news: [],
    sentiment: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStockData = async () => {
      if (!symbol) {
        setError("No stock symbol provided");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_API_URL}/stocks/details/${symbol}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch stock data: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }

        // Ensure all required properties exist with defaults
        const processedData = {
          current_quote: {
            price: data.current_quote?.price ?? 0,
            change: data.current_quote?.change ?? 0,
            change_percent: data.current_quote?.change_percent ?? 0,
          },
          profile: {
            name: data.profile?.name ?? 'Unknown',
            symbol: data.profile?.symbol ?? symbol,
            industry: data.profile?.industry ?? 'Unknown',
            sector: data.profile?.sector ?? 'Unknown',
            country: data.profile?.country ?? 'Unknown',
            website: data.profile?.website ?? '#',
          },
          historical_prices: Array.isArray(data.historical_prices) ? data.historical_prices : [],
          stock_news: Array.isArray(data.news) ? data.news : [],
          country_news: Array.isArray(data.country_news) ? data.country_news : [],
          sentiment: data.sentiment ?? null,
        };        

        setStockDetails(processedData);
        setError("");
      } catch (err) {
        setError(err.message || "Failed to load stock data");
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [symbol]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center p-8 bg-red-100 rounded-lg m-4">
        {error}
      </div>
    );
  }

  const isPositiveChange = stockDetails.current_quote.change > 0;

  // Render Sentiment Section
  const renderSentimentSection = () => {
    if (!stockDetails.sentiment) return null;
    return (
      <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
        <h2 className="text-xl font-bold mb-4">Market Sentiment</h2>
        
        {/* Overall Sentiment */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Overall Sentiment</h3>
          <SentimentBadge prediction={stockDetails.sentiment.overall_prediction} />
        </div>

        {/* Sentiment News */}
        <div>
          <h3 className="text-lg font-semibold mb-2">Sentiment News</h3>
          {stockDetails.sentiment.news.map((item, index) => (
            <div 
              key={index} 
              className="mb-2 p-3 bg-gray-700 rounded-lg flex items-center justify-between"
            >
              <div>
                <p className="text-sm font-medium">{item.headline}</p>
                <SentimentBadge prediction={item.relevant_prediction} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{stockDetails.profile.name}</h1>
            <p className="text-gray-400">{symbol}</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">${stockDetails.current_quote.price.toFixed(2)}</div>
            <div className={`flex items-center justify-end ${isPositiveChange ? 'text-green-500' : 'text-red-500'}`}>
              {isPositiveChange ? <ArrowUp size={20} /> : <ArrowDown size={20} />}
              <span className="ml-1">{Math.abs(stockDetails.current_quote.change_percent).toFixed(2)}%</span>
            </div>
          </div>
        </div>
      </div>

      {stockDetails.historical_prices.length > 0 && (
        <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4">Price History</h2>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stockDetails.historical_prices}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  stroke="#9CA3AF"
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '12px'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke={isPositiveChange ? "#10B981" : "#EF4444"}
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Building className="mr-2" />
            Company Information
          </h2>
          <div className="space-y-3">
            <p><span className="text-gray-400">Industry:</span> {stockDetails.profile.industry}</p>
            <p><span className="text-gray-400">Sector:</span> {stockDetails.profile.sector}</p>
            <p><span className="text-gray-400">Country:</span> {stockDetails.profile.country}</p>
            <p><span className="text-gray-400">Website:</span> 
              <a href={stockDetails.profile.website} target="_blank" rel="noopener noreferrer" 
                 className="ml-2 text-blue-400 hover:text-blue-300">{stockDetails.profile.website}</a>
            </p>
          </div>
        </div>

        {/* Stock-specific News */}
        <NewsSection 
          title={`${stockDetails.profile.name} News`}
          news={stockDetails.stock_news}
          icon={<Newspaper className="mr-2" />}
        />
      </div>

      {/* Country-specific News */}
      <NewsSection 
        title={`${stockDetails.profile.country} Market News`}
        news={stockDetails.country_news}
        icon={<Newspaper className="mr-2" />}
      />
      <RiskAnalysisSection riskAnalysis={stockDetails.risk_analysis} />
      {/* Sentiment Section */}
      {renderSentimentSection()}
    </div>
  );
};

export default StockAnalysis;