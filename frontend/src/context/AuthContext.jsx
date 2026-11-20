import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import { API_BASE } from "../config";

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(() => localStorage.getItem("dailyiq_token"));
    const [bookmarkedIds, setBookmarkedIds] = useState([]);
    const [bookmarks, setBookmarks] = useState([]);
    const [loading, setLoading] = useState(true);

    // Set default headers whenever token changes
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
            localStorage.setItem("dailyiq_token", token);
        } else {
            delete axios.defaults.headers.common["Authorization"];
            localStorage.removeItem("dailyiq_token");
        }
    }, [token]);

    // Check token and fetch user on initial mount
    useEffect(() => {
        const initAuth = async () => {
            const savedToken = localStorage.getItem("dailyiq_token");
            if (!savedToken) {
                setLoading(false);
                return;
            }

            try {
                const res = await axios.get(`${API_BASE}/auth/me`, {
                    headers: { Authorization: `Bearer ${savedToken}` }
                });
                setUser(res.data);
                setBookmarkedIds(res.data.bookmarked_ids || []);
            } catch (err) {
                console.warn("Session expired or invalid token:", err);
                setUser(null);
                setToken(null);
                setBookmarkedIds([]);
                localStorage.removeItem("dailyiq_token");
            } finally {
                setLoading(false);
            }
        };

        initAuth();
    }, []);

    const login = async (email, password) => {
        const res = await axios.post(`${API_BASE}/auth/login`, { email, password });
        const { token: newToken, user: userData } = res.data;
        setToken(newToken);
        setUser(userData);
        setBookmarkedIds(userData.bookmarked_ids || []);
        return userData;
    };


    const register = async (
        name,
        email,
        password,
        degree = "Student",
        branch = "General",
        studyYear = "Current",
        skills = "General Knowledge",
        preferredLocation = "India"
    ) => {
        const res = await axios.post(`${API_BASE}/auth/register`, {
            name,
            email,
            password,
            degree,
            branch,
            study_year: studyYear,
            skills,
            preferred_location: preferredLocation
        });

        const { token: newToken, user: userData } = res.data;

        setToken(newToken);
        setUser(userData);
        setBookmarkedIds(userData.bookmarked_ids || []);

        return userData;
    };

    const logout = async () => {
        try {
            if (token) {
                await axios.post(`${API_BASE}/auth/logout`);
            }
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            setUser(null);
            setToken(null);
            setBookmarkedIds([]);
            setBookmarks([]);
            localStorage.removeItem("dailyiq_token");
        }
    };

    const toggleBookmark = async (affairId) => {
        if (!user || !token) {
            return { requiresLogin: true };
        }

        try {
            const res = await axios.post(`${API_BASE}/auth/bookmarks/${affairId}`);
            const isBookmarked = res.data.bookmarked;

            if (isBookmarked) {
                setBookmarkedIds((prev) => [...prev, affairId]);
            } else {
                setBookmarkedIds((prev) => prev.filter((id) => id !== affairId));
                setBookmarks((prev) => prev.filter((item) => item.id !== affairId));
            }

            return { success: true, isBookmarked };
        } catch (err) {
            console.error("Failed to toggle bookmark:", err);
            return { error: true };
        }
    };

    const fetchBookmarks = async () => {
        if (!token) return [];
        try {
            const res = await axios.get(`${API_BASE}/auth/bookmarks`);
            setBookmarks(res.data);
            return res.data;
        } catch (err) {
            console.error("Failed to fetch bookmarks:", err);
            return [];
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                loading,
                isAuthenticated: !!user,
                bookmarkedIds,
                bookmarks,
                login,
                register,
                logout,
                toggleBookmark,
                fetchBookmarks
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
