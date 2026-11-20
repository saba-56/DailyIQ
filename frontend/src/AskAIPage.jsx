import axios from "axios";
import { useEffect, useRef, useState } from "react";
import { API_BASE } from "./config";

const SUGGESTIONS = [
    "📰 What are today's top headlines in DailyIQ?",
    "💉 Tell me about the Bharat Biotech malaria vaccine deal",
    "🚀 What is the Idefix rover mission to Mars' moon?",
    "📈 Why are global oil prices fluctuating?",
    "💡 Explain inflation and how RBI controls it in simple terms",
];

function formatInline(text) {
    const parts = text.split(/(\*\*.*?\*\*|\*.*?\*)/g);
    return parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
            return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith("*") && part.endsWith("*") && part.length >= 2) {
            return <em key={i}>{part.slice(1, -1)}</em>;
        }
        return part;
    });
}

function FormattedMessage({ content }) {
    const blocks = content.split(/\n{2,}/);

    return (
        <div className="message-body">
            {blocks.map((block, idx) => {
                const lines = block.split("\n");
                const isBulletList = lines.every((line) =>
                    /^[\*\-•]\s+/.test(line.trim())
                );

                if (isBulletList) {
                    return (
                        <ul key={idx} className="ai-bullet-list">
                            {lines.map((line, lIdx) => {
                                const clean = line.replace(/^[\*\-•]\s*/, "");
                                return <li key={lIdx}>{formatInline(clean)}</li>;
                            })}
                        </ul>
                    );
                }

                return (
                    <p key={idx} className="ai-paragraph">
                        {lines.map((line, lIdx) => (
                            <span key={lIdx}>
                                {formatInline(line)}
                                {lIdx < lines.length - 1 && <br />}
                            </span>
                        ))}
                    </p>
                );
            })}
        </div>
    );
}

function AskAIPage() {
    const [messages, setMessages] = useState([
        {
            role: "model",
            content:
                "Hello! 👋 I'm your **DailyIQ AI Knowledge Companion**.\n\nAsk me anything about today's current affairs, breaking news, history, science, geopolitics, or concepts you're studying. How can I help you today?",
            time: new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
            }),
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    const sendMessage = async (textToSend) => {
        const query = (textToSend || input).trim();
        if (!query || loading) return;

        setError("");
        const userTime = new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });

        const newMessages = [
            ...messages,
            { role: "user", content: query, time: userTime },
        ];
        setMessages(newMessages);
        setInput("");

        // Build history payload for Gemini multi-turn conversation
        // Filter out the initial welcome message from the model history to keep prompt clean
        const historyPayload = newMessages.slice(1, -1).map((m) => ({
            role: m.role,
            content: m.content,
        }));

        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE}/ask-ai`, {
                message: query,
                history: historyPayload,
            });

            const reply = response.data?.reply || "No response received.";
            const botTime = new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
            });

            setMessages((prev) => [
                ...prev,
                { role: "model", content: reply, time: botTime },
            ]);
        } catch (err) {
            console.error("Ask AI error:", err);
            setError(
                "Could not reach DailyIQ AI. Please check that the backend is running."
            );
            setMessages((prev) => [
                ...prev,
                {
                    role: "model",
                    content:
                        "⚠️ Sorry, I ran into an issue connecting to the AI service. Please make sure the backend is running and try again.",
                    time: new Date().toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                    }),
                },
            ]);
        } finally {
            setLoading(false);
            if (textareaRef.current) {
                textareaRef.current.focus();
            }
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const clearChat = () => {
        setMessages([
            {
                role: "model",
                content:
                    "Conversation reset! ✨ What topic or news story would you like to explore next?",
                time: new Date().toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                }),
            },
        ]);
        setError("");
    };

    return (
        <div className="page ask-ai-page">
            <header className="ask-ai-header">
                <div className="ask-ai-title-wrap">
                    <h2>🤖 Ask AI Tutor</h2>
                    <p className="ask-ai-tagline">
                        Your intelligent news, current affairs, and general
                        knowledge companion.
                    </p>
                </div>

                {messages.length > 1 && (
                    <button
                        type="button"
                        className="clear-chat-btn"
                        onClick={clearChat}
                        title="Clear conversation"
                    >
                        🗑️ Reset Chat
                    </button>
                )}
            </header>

            {/* Starter Suggestion Chips */}
            {messages.length <= 2 && (
                <div className="suggestions-section">
                    <span className="suggestions-label">💡 Suggested Questions:</span>
                    <div className="suggestions-list">
                        {SUGGESTIONS.map((suggestion, index) => (
                            <button
                                key={index}
                                type="button"
                                className="suggestion-chip"
                                onClick={() => sendMessage(suggestion)}
                                disabled={loading}
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Chat Messages Container */}
            <div className="chat-container">
                <div className="messages-stream">
                    {messages.map((msg, index) => {
                        const isUser = msg.role === "user";
                        return (
                            <div
                                key={index}
                                className={`chat-message-row ${
                                    isUser ? "user-row" : "model-row"
                                }`}
                            >
                                <div className="message-avatar">
                                    {isUser ? "👤" : "🧠"}
                                </div>

                                <div className="message-bubble-wrap">
                                    <div className="message-sender-name">
                                        {isUser ? "You" : "DailyIQ AI"}
                                        <span className="message-time">
                                            {msg.time}
                                        </span>
                                    </div>

                                    <div className="message-bubble">
                                        <FormattedMessage content={msg.content} />
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {loading && (
                        <div className="chat-message-row model-row thinking-row">
                            <div className="message-avatar">🧠</div>
                            <div className="message-bubble-wrap">
                                <div className="message-sender-name">
                                    DailyIQ AI
                                </div>
                                <div className="message-bubble thinking-bubble">
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                    <span className="thinking-text">
                                        Analyzing news & formulating answer...
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {error && <div className="chat-error-banner">{error}</div>}

                {/* Input Controls */}
                <form
                    className="chat-input-bar"
                    onSubmit={(e) => {
                        e.preventDefault();
                        sendMessage();
                    }}
                >
                    <textarea
                        ref={textareaRef}
                        className="chat-textarea"
                        placeholder="Ask anything about current affairs, news, science, or concepts..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        rows={1}
                        disabled={loading}
                    />

                    <button
                        type="submit"
                        className="chat-send-btn"
                        disabled={!input.trim() || loading}
                    >
                        {loading ? "..." : "Send ➤"}
                    </button>
                </form>

                <div className="chat-footer-hint">
                    Press <strong>Enter</strong> to send &bull; <strong>Shift + Enter</strong> for a new line
                </div>
            </div>
        </div>
    );
}

export default AskAIPage;