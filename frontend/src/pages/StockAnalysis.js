import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Building, TrendingUp, TrendingDown, AlertTriangle, Newspaper, BarChart2 } from 'lucide-react';
import RiskAnalysisSection from '../components/RiskAnalysisSection';

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

const SentimentAnalysisCard = ({ sentiment }) => {
  if (!sentiment || !sentiment.overall_prediction) {
    return null;
  }

  const score = sentiment.overall_prediction;

  const getSentimentColor = (score) => {
    if (score <= 40) return 'text-red-500';
    if (score >= 60) return 'text-green-500';
    return 'text-yellow-500';
  };

  const getSentimentText = (score) => {
    if (score <= 40) return 'Bearish';
    if (score >= 60) return 'Bullish';
    return 'Neutral';
  };

  const getSentimentIcon = (score) => {
    if (score <= 40) return <TrendingDown size={24} />;
    if (score >= 60) return <TrendingUp size={24} />;
    return <AlertTriangle size={24} />;
  };

  return (
    <Card className="bg-gray-800">
      <CardHeader>
        <CardTitle className="flex items-center">
          {getSentimentIcon(score)}
          <span className="ml-2">Market Sentiment</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center">
          <div className={`text-3xl font-bold mb-2 ${getSentimentColor(score)}`}>
            {getSentimentText(score)}
          </div>
          <div className="text-gray-400">
            Sentiment Score: {score.toFixed(1)}
          </div>
          <div className="mt-4 w-full bg-gray-700 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full ${getSentimentColor(score)}`}
              style={{ width: `${score}%` }}
            ></div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const NewsSection = ({ title, news, icon }) => {
  const newsToRender = news || [];
  
  if (newsToRender.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        {icon}
        <span className="ml-2">{title}</span>
      </h2>
      <div className="space-y-4">
        {newsToRender.map((article, index) => (
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

const PricePredictionCard = ({ prediction }) => {
  // ... (PricePredictionCard implementation remains the same)
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
    news: [],
    country_news: [],
    sentiment: null,
    risk_analysis: null,
    price_prediction: null
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

        setStockDetails(prevDetails => ({
          ...prevDetails,
          ...data
        }));
        setError("");
      } catch (err) {
        console.error('Fetch error:', err);
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
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error: </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  const isPositiveChange = stockDetails.current_quote.change > 0;

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      {/* Header Section */}
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

      {/* Analysis Cards Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <SentimentAnalysisCard sentiment={stockDetails.sentiment} />
        {stockDetails.price_prediction && (
          <PricePredictionCard prediction={stockDetails.price_prediction} />
        )}
      </div>

      {/* Price History Chart */}
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

      {/* Company Info and Stock News */}
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
            <p>
              <span className="text-gray-400">Website:</span> 
              <a href={stockDetails.profile.website} target="_blank" rel="noopener noreferrer" 
                 className="ml-2 text-blue-400 hover:text-blue-300">
                {stockDetails.profile.website}
              </a>
            </p>
          </div>
        </div>

        <NewsSection 
          title={`${stockDetails.profile.name} News`}
          news={stockDetails.news} 
          icon={<Newspaper className="mr-2" />}
        />
      </div>

      {/* Country Market News */}
      {stockDetails.country_news && stockDetails.country_news.length > 0 && (
        <NewsSection 
          title={`${stockDetails.profile.country} Market News`}
          news={stockDetails.country_news}
          icon={<Newspaper className="mr-2" />}
        />
      )}

      {/* Risk Analysis Section */}
      <RiskAnalysisSection riskAnalysis={stockDetails.risk_analysis} />
    </div>
  );
};

export default StockAnalysis;