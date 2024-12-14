import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { Menu, X } from 'lucide-react';
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import StockAnalysis from "./pages/StockAnalysis";
import { Toaster } from 'react-hot-toast';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Check login status on component mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    window.location.href = "/";
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    
    <Router>
      <Toaster 
        position="top-right"
        toastOptions={{
          success: { duration: 3000 },
          error: { duration: 5000 }
        }} 
      />
      <div className="bg-gray-900 text-white min-h-screen flex flex-col">
        {/* Navbar */}
        <nav className="p-4 text-white w-full bg-blue-600 sticky top-0 z-50">
          <div className="container mx-auto flex justify-between items-center">
            {/* Logo */}
            <div className="text-xl font-bold">
              <Link 
                to="/" 
                className="text-white hover:text-opacity-80"
                onClick={closeMobileMenu}
              >
                Stock Analyzer
              </Link>
            </div>

            {/* Mobile Menu Toggle */}
            <button 
              className="lg:hidden text-white"
              onClick={toggleMobileMenu}
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Desktop Navigation */}
            <ul className="hidden lg:flex items-center space-x-6">
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
                  <li>
                    <Link
                      to="/dashboard"
                      className="px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-80"
                    >
                      Dashboard
                    </Link>
                  </li>
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

            {/* Mobile Navigation */}
            {isMobileMenuOpen && (
              <div className="absolute top-full left-0 w-full bg-blue-600 lg:hidden">
                <ul className="flex flex-col items-center space-y-4 p-4">
                  {!isLoggedIn && (
                    <>
                      <li>
                        <Link
                          to="/login"
                          className="block px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-90"
                          onClick={closeMobileMenu}
                        >
                          Login
                        </Link>
                      </li>
                      <li>
                        <Link
                          to="/signup"
                          className="block px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-90"
                          onClick={closeMobileMenu}
                        >
                          Signup
                        </Link>
                      </li>
                    </>
                  )}
                  {isLoggedIn && (
                    <>
                      <li>
                        <Link
                          to="/dashboard"
                          className="block px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-80"
                          onClick={closeMobileMenu}
                        >
                          Dashboard
                        </Link>
                      </li>
                      <li>
                        <button
                          onClick={() => {
                            handleLogout();
                            closeMobileMenu();
                          }}
                          className="block px-4 py-2 rounded bg-white text-gray-900 hover:bg-opacity-90"
                        >
                          Logout
                        </button>
                      </li>
                    </>
                  )}
                </ul>
              </div>
            )}
          </div>
        </nav>
        {/* Main Content - Flex grow to push footer down */}
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route
              path="/login"
              element={<Login onLogin={() => setIsLoggedIn(true)} />}
            />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/stocks" element={<StockAnalysis />} />
            <Route path="/stocks/:symbol" element={<StockAnalysis />} />
          </Routes>

          {/* Floating Action Button */}
            <button
              onClick={() => window.open("https://llm-rag1.streamlit.app/", "_blank")}
              className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white w-14 h-14 flex items-center justify-center rounded-full shadow-lg transition duration-300"
              title="Chat with us"
            >
              💬
            </button>
          
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-gray-400 p-4 text-center">
          <div className="container mx-auto">
            <p className="text-sm">© 2024 Stock Analyzer. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
        