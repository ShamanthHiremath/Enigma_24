import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Building } from 'lucide-react';

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
          news: Array.isArray(data.news) ? data.news : [],
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

        <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4">Latest News</h2>
          <div className="space-y-4">
            {stockDetails.news.map((article, index) => (
              <div key={index} className="border-b border-gray-700 last:border-b-0 pb-4">
                <a href={article.link} target="_blank" rel="noopener noreferrer"
                   className="hover:text-blue-400 transition-colors">
                  <h3 className="font-medium mb-1">{article.title}</h3>
                  <p className="text-sm text-gray-400">{article.publisher} - {new Date(article.published_at).toLocaleDateString()}</p>
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysis;