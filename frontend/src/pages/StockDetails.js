import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Building } from 'lucide-react';

const StockDetails = ({ stockDetails }) => {
  const {
    current_quote,
    profile,
    historical_prices
  } = stockDetails;

  const isPositiveChange = current_quote.change > 0;
  
  // Process historical data for the chart
  const chartData = historical_prices
    .slice()
    .reverse()
    .map(item => ({
      date: new Date(item.date).toLocaleDateString(),
      price: item.close
    }));

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      {/* Header Section */}
      <div className="bg-white rounded-lg p-6 shadow-lg">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold">{profile.name}</h1>
            <p className="text-gray-600">{profile.symbol}</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">${current_quote.price.toFixed(2)}</p>
            <div className={`flex items-center justify-end ${isPositiveChange ? 'text-green-600' : 'text-red-600'}`}>
              {isPositiveChange ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
              <span className="ml-1">
                {Math.abs(current_quote.change).toFixed(2)} ({Math.abs(current_quote.change_percent).toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Company Info */}
      <div className="bg-white rounded-lg p-6 shadow-lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-gray-600">Sector</p>
            <p className="font-medium">{profile.sector}</p>
          </div>
          <div>
            <p className="text-gray-600">Industry</p>
            <p className="font-medium">{profile.industry}</p>
          </div>
          <div>
            <p className="text-gray-600">Country</p>
            <p className="font-medium">{profile.country}</p>
          </div>
        </div>
      </div>

      {/* Price Chart */}
      <div className="bg-white rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-bold mb-4">Price History</h2>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date"
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                domain={['auto', 'auto']}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#4f46e5" 
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

export default StockDetails;