import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="bg-gray-900 text-white min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-5xl font-bold mb-6">Welcome to Stock Analyzer</h1>
      <p className="text-xl text-gray-400">Analyze and predict stock trends effortlessly.</p>
      <Link to="/stocks" className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500">
        Start Analyzing Stocks
      </Link>
    </div>
  );
};

export default Home;
