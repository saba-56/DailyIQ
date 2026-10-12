
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

    const [degree, setDegree] = useState("B.Tech");
    const [branch, setBranch] = useState("CSE");
    const [studyYear, setStudyYear] = useState("4th year");
    const [skills, setSkills] = useState("");
    const [preferredLocation, setPreferredLocation] = useState("India");

    const { login, register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (isRegister) {
                if (!name.trim()) {
                    throw new Error("Please enter your name.");
                }

                if (!branch.trim() || !skills.trim() || !preferredLocation.trim()) {
                    throw new Error(
                        "Please complete your branch, skills, and preferred location."
                    );
                }

                await register(
                    name.trim(),
                    email.trim(),
                    password,
                    degree,
                    branch.trim(),
                    studyYear,
                    skills.trim(),
                    preferredLocation.trim()
                );
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
                            ? "Create your account to discover opportunities matched to your education and skills."
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
                        <>
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

                            <div className="form-group">
                                <label htmlFor="degree">Degree</label>
                                <select
                                    id="degree"
                                    value={degree}
                                    onChange={(e) => setDegree(e.target.value)}
                                    required
                                >
                                    <option value="B.Tech">B.Tech</option>
                                    <option value="B.E.">B.E.</option>
                                    <option value="BCA">BCA</option>
                                    <option value="MCA">MCA</option>
                                    <option value="M.Tech">M.Tech</option>
                                    <option value="B.Sc">B.Sc</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="branch">Branch / Specialization</label>
                                <input
                                    id="branch"
                                    type="text"
                                    placeholder="e.g. Computer Science Engineering"
                                    value={branch}
                                    onChange={(e) => setBranch(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="studyYear">Current Study Year</label>
                                <select
                                    id="studyYear"
                                    value={studyYear}
                                    onChange={(e) => setStudyYear(e.target.value)}
                                    required
                                >
                                    <option value="1st year">1st year</option>
                                    <option value="2nd year">2nd year</option>
                                    <option value="3rd year">3rd year</option>
                                    <option value="4th year">4th year</option>
                                    <option value="Final year">Final year</option>
                                    <option value="Graduate">Graduate</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="skills">Skills and Interests</label>
                                <input
                                    id="skills"
                                    type="text"
                                    placeholder="e.g. Python, Java, SQL, Web Development"
                                    value={skills}
                                    onChange={(e) => setSkills(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="preferredLocation">
                                    Preferred Job Location
                                </label>
                                <input
                                    id="preferredLocation"
                                    type="text"
                                    placeholder="e.g. Kolkata, Remote, India"
                                    value={preferredLocation}
                                    onChange={(e) =>
                                        setPreferredLocation(e.target.value)
                                    }
                                    required
                                />
                            </div>
                        </>
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