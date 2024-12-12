import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import StockAnalysis from "./pages/StockAnalysis";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check login status on component mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token); // Update state if token exists
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    window.location.href = "/"; // Redirect to Home after logout
  };

  return (
    <Router>
      <div className="bg-gray-900 text-white min-h-screen">
        {/* Navbar */}
        <nav className="p-4 text-white w-full bg-blue-600">
          <div className="container mx-auto flex justify-between items-center">
            <div className="text-xl font-bold">
              <Link to="/" className="text-white hover:text-opacity-80">
                Stock Analyzer
              </Link>
            </div>
            <ul className="hidden lg:flex items-center space-x-6">
              {/* Links */}
              {!isLoggedIn && (
                <>
                  <li>
                    <Link
                      to="/login"
                      className="px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-90"
                    >
                      Login
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/signup"
                      className="px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-90"
                    >
                      Signup
                    </Link>
                  </li>
                </>
              )}
              {isLoggedIn && (
                <>
                  {/* Dashboard Link */}
                  <li>
                    <Link
                      to="/dashboard"
                      className="px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-80"
                    >
                      Dashboard
                    </Link>
                  </li>
                  {/* Logout Button */}
                  <li>
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-90"
                    >
                      Logout
                    </button>
                  </li>
                </>
              )}
            </ul>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={<Login onLogin={() => setIsLoggedIn(true)} />}
          />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/stocks" element={<StockAnalysis />} />
        </Routes>

        {/* Footer */}
        <footer className="bg-gray-800 text-gray-400 p-4 text-center mt-8">
          <p>© 2024 Stock Analyzer. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
