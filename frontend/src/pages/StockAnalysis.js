import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';  // Added date formatting

const StockAnalysis = () => {
  const { symbol } = useParams();
  const [quote, setQuote] = useState(null);
  const [dailyData, setDailyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setLoading(true);
        // Fetch quote
        const quoteResponse = await fetch(`${process.env.REACT_APP_API_URL}/stocks/quote/${symbol}`);
        const quoteData = await quoteResponse.json();

        // Fetch daily data
        const dailyResponse = await fetch(`${process.env.REACT_APP_API_URL}/stocks/details/daily/${symbol}`);
        const dailyData = await dailyResponse.json();

        setQuote(quoteData);
        setDailyData(dailyData);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching stock data:", err);
        setError("Failed to fetch stock details");
        setLoading(false);
      }
    };

    if (symbol) {
      fetchStockData();
    }
  }, [symbol]);

  const getChartData = () => {
    if (!dailyData || dailyData.length === 0) return [];

    // Return full daily data, formatted for chart
    return dailyData.map(item => ({
      name: format(parseISO(item.date), 'MMM dd'),  // Format date more readably
      price: item.close
    }));
  };

  if (loading) return <div className="text-white text-center p-8">Loading...</div>;
  if (error) return <div className="text-red-500 text-center p-8">{error}</div>;
  if (!quote) return <div className="text-white text-center p-8">No stock data available</div>;

  return (
    <div className="bg-gray-900 text-white min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">  {/* Increased max width */}
        <div className="grid md:grid-cols-2 gap-4 md:gap-8">
          {/* Stock Summary */}
          <div className="bg-gray-800 p-4 md:p-6 rounded-lg">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">{quote.symbol}</h2>
            <div className="space-y-2">
              <p className="text-lg md:text-xl">Current Price: <span className="font-bold text-green-500">${quote.price}</span></p>
              <p>Price Change: 
                <span className={`ml-2 ${quote.change.startsWith('-') ? 'text-red-500' : 'text-green-500'}`}>
                  {quote.change} ({quote.change_percent})
                </span>
              </p>
            </div>
          </div>

          {/* Timeframe Description */}
          <div className="bg-gray-800 p-4 md:p-6 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Daily Price Trend</h3>
              <p className="text-gray-400">
                Showing daily closing prices for the past year, 
                providing a comprehensive view of the stock's performance.
              </p>
            </div>
          </div>
        </div>

        {/* Price Chart */}
        <div className="mt-4 md:mt-8 bg-gray-800 p-4 md:p-6 rounded-lg h-96 md:h-[500px]">  {/* Increased height */}
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={getChartData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="name" 
                stroke="#9CA3AF" 
                fontSize={10} 
                angle={-45} 
                textAnchor="end"
                interval="preserveStart"  // Shows more x-axis labels
              />
              <YAxis 
                stroke="#9CA3AF" 
                domain={['dataMin', 'dataMax']}  // Dynamic y-axis range
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  color: 'white',
                  fontSize: '12px'
                }}
                itemStyle={{ color: '#9CA3AF' }}
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysis;