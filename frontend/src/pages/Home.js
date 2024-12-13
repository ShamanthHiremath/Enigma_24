import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, TrendingUp, ArrowUp, ArrowDown, Loader2 } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

// Dummy data for market indices and stocks
const DUMMY_NIFTY_DATA = [
  { Date: '2023-01-01', Close: 17000 },
  { Date: '2023-02-01', Close: 17500 },
  { Date: '2023-03-01', Close: 17200 },
  { Date: '2023-04-01', Close: 17800 },
  { Date: '2023-05-01', Close: 18000 },
  { Date: '2023-06-01', Close: 18500 },
  { Date: '2023-07-01', Close: 19000 },
];

const DUMMY_SENSEX_DATA = [
  { Date: '2023-01-01', Close: 57000 },
  { Date: '2023-02-01', Close: 58000 },
  { Date: '2023-03-01', Close: 57500 },
  { Date: '2023-04-01', Close: 59000 },
  { Date: '2023-05-01', Close: 60000 },
  { Date: '2023-06-01', Close: 61000 },
  { Date: '2023-07-01', Close: 62000 },
];

const DUMMY_TOP_STOCKS = [
  { symbol: 'INFY', price: 1450, change: 2.5 },
  { symbol: 'TCS', price: 3200, change: 1.8 },
  { symbol: 'RELIANCE', price: 2300, change: 3.2 },
  { symbol: 'HDFC', price: 1700, change: -1.5 },
  { symbol: 'ICICI', price: 950, change: 2.1 },
];

const Home = () => {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showContent, setShowContent] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Simulate search functionality
    setLoading(true);
    setSearchPerformed(true);
    
    setTimeout(() => {
      // Filter dummy stocks based on query
      const filteredStocks = DUMMY_TOP_STOCKS.filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase())
      );
      
      setSearchResults(filteredStocks);
      setLoading(false);
    }, 1000);
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gray-800/80 backdrop-blur-lg p-4 rounded-xl shadow-2xl border border-gray-700"
        >
          <p className="text-gray-300 mb-1">{label}</p>
          <p className="text-green-500 font-bold text-lg">₹{payload[0].value.toFixed(2)}</p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white min-h-screen overflow-hidden">
      <AnimatePresence>
        {!showContent && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 1.2, opacity: 0 }}
            transition={{ duration: 1.5 }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <motion.div
              animate={{ rotate: 360, scale: [1, 1.2, 1] }}
              transition={{ 
                duration: 2, 
                ease: "easeInOut",
                repeat: Infinity
              }}
            >
              <TrendingUp size={80} className="text-amber-500" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showContent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="container mx-auto px-4 py-8"
          >
            <motion.div 
              initial={{ y: -50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="max-w-2xl mx-auto bg-gray-800/40 backdrop-blur-lg rounded-3xl p-8 shadow-2xl mb-8"
            >
              <h1 className="text-5xl font-bold mb-8 text-center bg-gradient-to-r from-amber-500 to-amber-300 bg-clip-text text-transparent">
                Stock Insights
              </h1>
              
              <form onSubmit={handleSearch} className="mb-8">
                <div className="relative">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      setSearchPerformed(false);
                      setSearchResults([]);
                    }}
                    placeholder="Search stocks by name or symbol..."
                    className="w-full p-4 pl-12 bg-gray-700/50 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all"
                  />
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-amber-500 transition-colors disabled:opacity-50"
                  >
                    {loading ? <Loader2 className="animate-spin" /> : <Search />}
                  </motion.button>
                </div>
              </form>
            </motion.div>

            {/* Conditional Rendering for Market Data and Search Results */}
            <AnimatePresence>
              {!searchPerformed && (
                <>
                  <div className="grid md:grid-cols-2 gap-8 mb-8">
                    {/* Nifty 50 Chart */}
                    <motion.div
                      initial={{ opacity: 0, x: -50 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 }}
                      className="bg-gray-800/40 backdrop-blur-lg rounded-3xl p-6 shadow-2xl"
                    >
                      <div className="flex justify-between items-center mb-4">
                        <h2 className="text-2xl font-bold">Nifty 50</h2>
                        <div className="flex items-center text-green-500">
                          <ArrowUp className="mr-2" />
                          <span>+3.2%</span>
                        </div>
                      </div>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={DUMMY_NIFTY_DATA}>
                            <defs>
                              <linearGradient id="niftyGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.5} />
                                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.1} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                            <XAxis dataKey="Date" />
                            <YAxis />
                            <Tooltip content={<CustomTooltip />} />
                            <Area 
                              type="monotone" 
                              dataKey="Close" 
                              stroke="#22c55e" 
                              fillOpacity={1} 
                              fill="url(#niftyGradient)"
                              strokeWidth={3}
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </motion.div>

                    {/* Sensex Chart */}
                    <motion.div
                      initial={{ opacity: 0, x: 50 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.9 }}
                      className="bg-gray-800/40 backdrop-blur-lg rounded-3xl p-6 shadow-2xl"
                    >
                      <div className="flex justify-between items-center mb-4">
                        <h2 className="text-2xl font-bold">Sensex</h2>
                        <div className="flex items-center text-green-500">
                          <ArrowUp className="mr-2" />
                          <span>+2.7%</span>
                        </div>
                      </div>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={DUMMY_SENSEX_DATA}>
                            <defs>
                              <linearGradient id="sensexGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.5} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                            <XAxis dataKey="Date" />
                            <YAxis />
                            <Tooltip content={<CustomTooltip />} />
                            <Area 
                              type="monotone" 
                              dataKey="Close" 
                              stroke="#3b82f6" 
                              fillOpacity={1} 
                              fill="url(#sensexGradient)"
                              strokeWidth={3}
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </motion.div>
                  </div>

                  {/* Top Stocks Section */}
                  <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.1 }}
                    className="bg-gray-800/40 backdrop-blur-lg rounded-3xl p-6 shadow-2xl"
                  >
                    <h2 className="text-2xl font-bold mb-6">Top Performing Stocks</h2>
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                      {DUMMY_TOP_STOCKS.map((stock, index) => (
                        <motion.div
                          key={stock.symbol}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 1.2 + index * 0.1 }}
                          className="bg-gray-700/50 rounded-xl p-4 text-center"
                        >
                          <div className="font-bold text-lg mb-2">{stock.symbol}</div>
                          <div className="text-xl mb-2">₹{stock.price}</div>
                          <div className={`flex items-center justify-center ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {stock.change >= 0 ? <ArrowUp className="mr-1" /> : <ArrowDown className="mr-1" />}
                            {Math.abs(stock.change)}%
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>

            {/* Search Results Section */}
            {searchPerformed && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-800/40 backdrop-blur-lg rounded-3xl p-6 shadow-2xl"
              >
                <h2 className="text-2xl font-bold mb-6">Search Results</h2>
                {loading ? (
                  <div className="flex justify-center items-center h-40">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ 
                        repeat: Infinity, 
                        duration: 1, 
                        ease: "linear" 
                      }}
                    >
                      <Loader2 size={48} className="text-amber-500 animate-spin" />
                    </motion.div>
                  </div>
                ) : searchResults.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    {searchResults.map((stock, index) => (
                      <motion.div
                        key={stock.symbol}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * index }}
                        className="bg-gray-700/50 rounded-xl p-4 text-center"
                      >
                        <div className="font-bold text-lg mb-2">{stock.symbol}</div>
                        <div className="text-xl mb-2">₹{stock.price}</div>
                        <div className={`flex items-center justify-center ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {stock.change >= 0 ? <ArrowUp className="mr-1" /> : <ArrowDown className="mr-1" />}
                          {Math.abs(stock.change)}%
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-400 py-10">
                    No stocks found matching your search.
                  </div>
                )}
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Home;