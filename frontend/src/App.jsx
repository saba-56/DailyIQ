import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import "./App.css";

import { AuthProvider, useAuth } from "./context/AuthContext";
import Home from "./Home";
import Affairs from "./Affairs";
import Opportunities from "./Opportunities";
import Quiz from "./Quiz";
import AskAI from "./AskAIPage";
import Login from "./Login";
import Account from "./Account";

function Navigation() {
  const { user, isAuthenticated } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="logo-link">
        <h1 className="logo">🧠 DailyIQ</h1>
      </Link>

      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/affairs">Affairs</Link>
        <Link to="/opportunities" className="nav-opportunities-link">
          Opportunities
          <span className="nav-badge-upcoming">Soon</span>
        </Link>
        <Link to="/quiz">Quiz</Link>
        <Link to="/ask-ai">Ask AI</Link>

        {isAuthenticated ? (
          <Link to="/account" className="nav-user-chip">
            <span className="user-status-dot"></span>
            {user?.name?.split(" ")[0] || "Account"}
          </Link>
        ) : (
          <Link to="/login" className="nav-signin-btn">
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="app">
          <Navigation />

          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/affairs" element={<Affairs />} />
            <Route path="/opportunities" element={<Opportunities />} />
            <Route path="/quiz" element={<Quiz />} />
            <Route path="/ask-ai" element={<AskAI />} />
            <Route path="/login" element={<Login />} />
            <Route path="/account" element={<Account />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;