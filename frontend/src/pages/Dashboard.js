import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;

    setLoading(true);
    setError("");
    setSearchResults([]);

    try {
        const response = await fetch(
            `${process.env.REACT_APP_API_URL}/stocks/search?name=${query}`,
            {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            }
        );    
        const data = await response.json();

        if (response.ok) {
            setSearchResults(data);
        } else {
            console.error("Server Error:", data);
            setError(data.error || "Failed to fetch stock data.");
        }
    } catch (err) {
        console.error("Fetch Error:", err);
        setError("An error occurred while searching for stocks.");
    } finally {
        setLoading(false);
    }
  };

  const handleStockClick = (symbol) => {
    navigate(`/stocks/${symbol}`);
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen p-8">
      <h2 className="text-3xl font-bold mb-4">Welcome to Your Dashboard</h2>

      <div className="bg-gray-800 p-6 rounded shadow-md mb-6">
        <h3 className="text-2xl font-semibold mb-4">Search Stocks</h3>
        <form onSubmit={handleSearch} className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Enter stock name or symbol"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full p-3 rounded bg-gray-700 text-white focus:outline-none"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500"
          >
            Search
          </button>
        </form>
      </div>

      {loading && <p className="text-blue-500">Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {searchResults.map((stock) => (
          <div
            key={stock.symbol}
            onClick={() => handleStockClick(stock.symbol)}
            className="bg-gray-800 p-4 rounded shadow-md hover:shadow-lg cursor-pointer transition-all duration-300 transform hover:scale-105"
          >
            <h4 className="text-xl font-semibold">{stock.name}</h4>
            <p className="text-gray-400">Symbol: {stock.symbol}</p>
            <p className="text-gray-400">Type: {stock.type}</p>
            <p className="text-gray-400">Region: {stock.region}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;