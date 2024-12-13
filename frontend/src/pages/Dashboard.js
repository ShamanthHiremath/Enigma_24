import React from "react";

const Dashboard = () => {
  return (
    <div className="bg-gray-900 text-white min-h-screen p-8">
      <h2 className="text-3xl font-bold mb-4">Welcome to Your Dashboard</h2>
      <div className="bg-gray-800 p-6 rounded shadow-md mb-6">
        <h3 className="text-2xl font-semibold mb-4">Your Personal Details</h3>
        <p className="text-gray-400">Here you can view your personal stock data and preferences.</p>
        {/* Add user-specific details or components here */}
      </div>
    </div>
  );
};

export default Dashboard;
