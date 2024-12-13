import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

const StockAnalysis = () => {
  const { symbol } = useParams();
  const [stockDetails, setStockDetails] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [stockNews, setStockNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStockData = async () => {
      if (!symbol) return;

      try {
        setLoading(true);
        // Fetch stock details
        const detailsResponse = await fetch(`${process.env.REACT_APP_API_URL}/stocks/details/${symbol}`);
        const detailsData = await detailsResponse.json();

        // Fetch historical data
        const historicalResponse = await fetch(`${process.env.REACT_APP_API_URL}/stocks/historical/${symbol}`);
        const historicalData = await historicalResponse.json();

        // Fetch stock news
        const newsResponse = await fetch(`${process.env.REACT_APP_API_URL}/stocks/news/${symbol}`);
        const newsData = await newsResponse.json();

        setStockDetails(detailsData);
        setHistoricalData(historicalData);
        setStockNews(newsData);
      } catch (err) {
        console.error("Error fetching stock data:", err);
        setError("Failed to fetch stock details");
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [symbol]);

  const getChartData = () => {
    if (!historicalData || historicalData.length === 0) return [];

    return historicalData.map(item => ({
      name: format(new Date(item.Date), 'MMM dd'),
      price: item.Close
    }));
  };

  if (loading) return <div className="text-white text-center p-8">Loading stock details...</div>;
  if (error) return <div className="text-red-500 text-center p-8">{error}</div>;
  if (!stockDetails) return <div className="text-white text-center p-8">No stock data available</div>;

  return (
    <div className="bg-gray-900 text-white min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Stock Overview */}
        <div className="grid md:grid-cols-2 gap-4 md:gap-8 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-3xl font-bold mb-4">{stockDetails.name} ({stockDetails.symbol})</h2>
            <div className="space-y-3">
              <p className="text-xl">Current Price: <span className="font-bold text-green-500">${stockDetails.price}</span></p>
              <p>Industry: {stockDetails.industry}</p>
              <p>Sector: {stockDetails.sector}</p>
              <p>Country: {stockDetails.country}</p>
              <p>Market Cap: {stockDetails.marketCap}</p>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-2xl font-semibold mb-4">Financial Metrics</h3>
            <div className="space-y-3">
              <p>Dividend Yield: {stockDetails.dividendYield}%</p>
              <p>P/E Ratio: {stockDetails.priceToEarnings}</p>
              <p>Earnings Growth: {stockDetails.earningsGrowth}%</p>
              <p>Debt to Equity: {stockDetails.debtToEquity}</p>
            </div>
          </div>
        </div>

        {/* Price Chart */}
        <div className="bg-gray-800 p-6 rounded-lg mb-8 h-96">
          <h3 className="text-2xl font-semibold mb-4">Historical Price Trend</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={getChartData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  color: 'white' 
                }} 
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#3B82F6" 
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Stock News */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-2xl font-semibold mb-4">Recent Stock News</h3>
          <div className="space-y-4">
            {stockNews.map((article, index) => (
              <div key={index} className="border-b border-gray-700 pb-4 last:border-b-0">
                <h4 className="text-lg font-semibold mb-2">{article.title}</h4>
                <p className="text-gray-400 mb-2">Published by: {article.publisher}</p>
                <a 
                  href={article.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  Read More
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