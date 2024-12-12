import React from "react";

const Dashboard = () => {
  return (
    <div className="bg-gray-900 text-white min-h-screen p-8">
      <h2 className="text-3xl font-bold mb-4">Welcome to Your Dashboard</h2>
      <div className="bg-gray-800 p-6 rounded shadow-md">
        <h3 className="text-2xl font-semibold mb-4">Your Stock Portfolio</h3>
        {/* Display user's stock data here */}
        <div className="text-gray-400">
          <p>Here you can track your portfolio, view stock analysis, and more!</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
