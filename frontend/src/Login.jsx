import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

function Login() {
    const [isRegister, setIsRegister] = useState(false);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const { login, register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (isRegister) {
                if (!name.trim()) {
                    throw new Error("Please enter your full name.");
                }

                await register(name.trim(), email.trim(), password);
            } else {
                await login(email.trim(), password);
            }

            navigate("/account");
        } catch (err) {
            console.error("Auth error:", err);

            setError(
                err.response?.data?.detail ||
                err.message ||
                "Authentication failed. Please check your details and try again."
            );
        } finally {
            setLoading(false);
        }
    };

    const switchMode = (registerMode) => {
        setIsRegister(registerMode);
        setError("");
    };

    return (
        <div className="page auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <span className="auth-badge">Account Access</span>

                    <h2>{isRegister ? "Join DailyIQ" : "Welcome Back"}</h2>

                    <p>
                        {isRegister
                            ? "Create your account to track daily learning streaks, save key affairs, and take quizzes."
                            : "Sign in to access your saved affairs, learning streak, and profile."}
                    </p>
                </div>

                <div className="auth-tabs">
                    <button
                        type="button"
                        className={`auth-tab ${!isRegister ? "active" : ""}`}
                        onClick={() => switchMode(false)}
                    >
                        Sign In
                    </button>

                    <button
                        type="button"
                        className={`auth-tab ${isRegister ? "active" : ""}`}
                        onClick={() => switchMode(true)}
                    >
                        Create Account
                    </button>
                </div>

                {error && (
                    <div className="auth-error-box" role="alert">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    {isRegister && (
                        <div className="form-group">
                            <label htmlFor="name">Full Name</label>
                            <input
                                id="name"
                                type="text"
                                placeholder="Enter your full name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="email">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            placeholder="At least 6 characters"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            minLength={6}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="auth-submit-btn"
                        disabled={loading}
                    >
                        {loading
                            ? "Please wait..."
                            : isRegister
                                ? "Create Free Account"
                                : "Sign In to Account"}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>
                        {isRegister ? (
                            <>
                                Already have an account?{" "}
                                <button
                                    type="button"
                                    className="auth-link-btn"
                                    onClick={() => switchMode(false)}
                                >
                                    Sign in here
                                </button>
                            </>
                        ) : (
                            <>
                                New to DailyIQ?{" "}
                                <button
                                    type="button"
                                    className="auth-link-btn"
                                    onClick={() => switchMode(true)}
                                >
                                    Create an account
                                </button>
                            </>
                        )}
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Login;
