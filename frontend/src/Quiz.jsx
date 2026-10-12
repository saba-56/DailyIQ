
import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

function Quiz() {
    const [mode, setMode] = useState("today");
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [current, setCurrent] = useState(0);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function loadQuiz(selectedMode = mode) {
        setLoading(true);
        setError("");
        setQuestions([]);
        setAnswers({});
        setCurrent(0);
        setResult(null);

        try {
            const endpoint =
                selectedMode === "today"
                    ? "/quiz/today"
                    : "/quiz/practice?limit=10";

            const response = await fetch(`${API}${endpoint}`);

            if (!response.ok) {
                throw new Error("Unable to load quiz questions.");
            }

            const data = await response.json();
            setQuestions(data.questions || []);

            if (!data.questions?.length) {
                setError(
                    selectedMode === "today"
                        ? "No questions are available for today's quiz yet."
                        : "No practice questions are available yet."
                );
            }
        } catch (err) {
            setError(
                "Could not connect to DailyIQ. Check that your backend is running."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadQuiz("today");
    }, []);

    function changeMode(newMode) {
        setMode(newMode);
        loadQuiz(newMode);
    }

    function chooseAnswer(questionId, option) {
        if (result) return;

        setAnswers((previous) => ({
            ...previous,
            [questionId]: option,
        }));
    }

    async function submitQuiz() {
        if (Object.keys(answers).length !== questions.length) {
            setError("Please answer every question before submitting.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const response = await fetch(`${API}/quiz/submit`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    answers: questions.map((question) => ({
                        question_id: question.id,
                        selected_option: answers[question.id],
                    })),
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Quiz submission failed."
                );
            }

            setResult(data);
        } catch (err) {
            setError(err.message || "Unable to submit your quiz.");
        } finally {
            setLoading(false);
        }
    }

    const question = questions[current];

    return (
        <div className="page" style={{ maxWidth: 850, margin: "0 auto", padding: 24 }}>
            <h2>🎯 DailyIQ Quiz</h2>
            <p>Test your knowledge with current-affairs questions.</p>

            <div style={{ display: "flex", gap: 10, margin: "20px 0" }}>
                <button
                    onClick={() => changeMode("today")}
                    disabled={loading}
                    style={{
                        padding: "10px 16px",
                        fontWeight: mode === "today" ? "bold" : "normal",
                    }}
                >
                    Today's Quiz
                </button>

                <button
                    onClick={() => changeMode("practice")}
                    disabled={loading}
                    style={{
                        padding: "10px 16px",
                        fontWeight: mode === "practice" ? "bold" : "normal",
                    }}
                >
                    Practice Quiz
                </button>
            </div>

            {loading && <p>Loading...</p>}
            {error && (
                <p role="alert" style={{ color: "crimson" }}>
                    {error}
                </p>
            )}

            {!loading && !error && questions.length > 0 && (
                <>
                    {!result && (
                        <>
                            <p>
                                Question {current + 1} of {questions.length}
                            </p>

                            <div style={{
                                height: 6,
                                background: "#e5e7eb",
                                borderRadius: 8,
                                marginBottom: 20,
                            }}>
                                <div style={{
                                    height: "100%",
                                    width: `${((current + 1) / questions.length) * 100}%`,
                                    background: "#2563eb",
                                    borderRadius: 8,
                                }} />
                            </div>

                            <div style={{
                                border: "1px solid #ddd",
                                borderRadius: 12,
                                padding: 22,
                            }}>
                                <h3>{question.question}</h3>

                                {["A", "B", "C", "D"].map((option) => (
                                    <button
                                        key={option}
                                        onClick={() =>
                                            chooseAnswer(question.id, option)
                                        }
                                        style={{
                                            display: "block",
                                            width: "100%",
                                            textAlign: "left",
                                            padding: 14,
                                            margin: "10px 0",
                                            borderRadius: 8,
                                            border: answers[question.id] === option
                                                ? "2px solid #2563eb"
                                                : "1px solid #ccc",
                                            background: answers[question.id] === option
                                                ? "#eff6ff"
                                                : "white",
                                            color: "#111827",
                                            cursor: "pointer",
                                        }}
                                    >
                                        <strong>{option}.</strong>{" "}
                                        {question.options[option]}
                                    </button>
                                ))}
                            </div>

                            <p>
                                Answered: {Object.keys(answers).length} /{" "}
                                {questions.length}
                            </p>

                            <div style={{
                                display: "flex",
                                justifyContent: "space-between",
                                gap: 10,
                                marginTop: 20,
                            }}>
                                <button
                                    onClick={() => setCurrent((n) => n - 1)}
                                    disabled={current === 0}
                                >
                                    Previous
                                </button>

                                {current < questions.length - 1 ? (
                                    <button
                                        onClick={() => setCurrent((n) => n + 1)}
                                    >
                                        Next
                                    </button>
                                ) : (
                                    <button
                                        onClick={submitQuiz}
                                        disabled={loading}
                                    >
                                        Submit Quiz
                                    </button>
                                )}
                            </div>
                        </>
                    )}

                    {result && (
                        <div style={{
                            border: "1px solid #ddd",
                            borderRadius: 12,
                            padding: 22,
                        }}>
                            <h2>Quiz Results</h2>
                            <h3>
                                Score: {result.correct_answers} /{" "}
                                {result.total_questions}
                            </h3>
                            <p>
                                Percentage: {result.score_percentage}%
                            </p>
                            <p>Correct: {result.correct_answers}</p>
                            <p>Incorrect: {result.incorrect_answers}</p>

                            <hr />

                            {questions.map((q, index) => {
                                const answerResult = result.results.find(
                                    (item) => item.question_id === q.id
                                );

                                return (
                                    <div key={q.id} style={{ marginBottom: 22 }}>
                                        <h4>
                                            {index + 1}. {q.question}
                                        </h4>
                                        <p>
                                            Your answer:{" "}
                                            {answerResult?.selected_option || "—"}
                                        </p>
                                        <p>
                                            Correct answer:{" "}
                                            {answerResult?.correct_option}
                                        </p>
                                        <p>
                                            {answerResult?.explanation}
                                        </p>

                                        {q.source_url && (
                                            <a
                                                href={q.source_url}
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                Read source article
                                            </a>
                                        )}
                                    </div>
                                );
                            })}

                            <button onClick={() => loadQuiz(mode)}>
                                Try Again
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Quiz;