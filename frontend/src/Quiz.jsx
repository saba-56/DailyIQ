import { useEffect, useState } from "react";
import { API_BASE as API } from "./config";

function Quiz() {
    const [mode, setMode] = useState("today");
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [current, setCurrent] = useState(0);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
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
                        ? "No questions are available for today's quiz yet. Click 'Generate Questions' below."
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

    async function generateNewQuiz() {
        setGenerating(true);
        setError("");

        try {
            const endpoint =
                mode === "today"
                    ? "/quiz/generate-today"
                    : "/quiz/generate-practice?limit=5";

            const response = await fetch(`${API}${endpoint}`, {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error("Failed to generate questions with AI.");
            }

            await loadQuiz(mode);
        } catch (err) {
            setError("Could not generate questions right now. Please try again.");
        } finally {
            setGenerating(false);
        }
    }

    async function submitQuiz() {
        if (Object.keys(answers).length !== questions.length) {
            setError("Please answer all questions before submitting.");
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
                    answers: questions.map((q) => ({
                        question_id: q.id,
                        selected_option: answers[q.id],
                    })),
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Quiz submission failed.");
            }

            setResult(data);
        } catch (err) {
            setError(err.message || "Unable to submit your quiz.");
        } finally {
            setLoading(false);
        }
    }

    const question = questions[current];
    const answeredCount = Object.keys(answers).length;
    const progressPercent =
        questions.length > 0 ? ((current + 1) / questions.length) * 100 : 0;

    return (
        <div className="page quiz-page">
            <header className="quiz-header">
                <div>
                    <h2>🎯 DailyIQ Quiz</h2>
                    <p className="quiz-tagline">
                        Test your retention and prepare for exams with questions
                        crafted from today's news.
                    </p>
                </div>

                <button
                    type="button"
                    className="generate-quiz-btn"
                    onClick={generateNewQuiz}
                    disabled={loading || generating}
                    title="Generate new questions with Gemini AI"
                >
                    <span className="quiz-btn-icon">⚡</span>
                    <span>
                        {generating ? "Crafting MCQs..." : "Generate Fresh Quiz"}
                    </span>
                </button>
            </header>

            {/* Mode Selector */}
            <div className="quiz-mode-toolbar">
                <div className="day-selector">
                    <button
                        type="button"
                        className={mode === "today" ? "day-btn active" : "day-btn"}
                        onClick={() => changeMode("today")}
                        disabled={loading || generating}
                    >
                        📅 Today's Quiz
                    </button>

                    <button
                        type="button"
                        className={mode === "practice" ? "day-btn active" : "day-btn"}
                        onClick={() => changeMode("practice")}
                        disabled={loading || generating}
                    >
                        📚 Practice Quiz
                    </button>
                </div>
            </div>

            {/* Loading / Generating State */}
            {(loading || generating) && (
                <div className="quiz-loading-card">
                    <div className="quiz-spinner"></div>
                    <p>
                        {generating
                            ? "🧠 Gemini AI is analyzing the news and drafting MCQs..."
                            : "Loading quiz questions..."}
                    </p>
                </div>
            )}

            {/* Error Message */}
            {error && !loading && !generating && (
                <div className="quiz-error-card" role="alert">
                    <p>{error}</p>
                    <button
                        type="button"
                        className="page button"
                        onClick={generateNewQuiz}
                        style={{ marginTop: 12 }}
                    >
                        ⚡ Generate Questions Now
                    </button>
                </div>
            )}

            {/* Active Quiz Question Runner */}
            {!loading && !generating && !error && questions.length > 0 && !result && question && (
                <div className="quiz-card">
                    {/* Top Meta Row */}
                    <div className="quiz-meta-row">
                        <div className="quiz-meta-left">
                            <span className="quiz-progress-label">
                                Question {current + 1} of {questions.length}
                            </span>
                            {question.topic && (
                                <span className="category quiz-topic-badge">
                                    {question.topic}
                                </span>
                            )}
                        </div>

                        <span className="quiz-difficulty-tag">
                            {question.difficulty || "medium"}
                        </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="quiz-progress-bar-track">
                        <div
                            className="quiz-progress-bar-fill"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>

                    {/* Question Headline */}
                    <h3 className="quiz-question-title">{question.question}</h3>

                    {/* Options Grid */}
                    <div className="quiz-options-list">
                        {["A", "B", "C", "D"].map((key) => {
                            const optionText = question.options[key];
                            if (!optionText) return null;
                            const isSelected = answers[question.id] === key;

                            return (
                                <button
                                    key={key}
                                    type="button"
                                    className={`quiz-option-btn ${
                                        isSelected ? "selected" : ""
                                    }`}
                                    onClick={() => chooseAnswer(question.id, key)}
                                >
                                    <span className="quiz-option-key">
                                        {key}
                                    </span>
                                    <span className="quiz-option-text">
                                        {optionText}
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Footer Row */}
                    <div className="quiz-footer-row">
                        <div className="quiz-footer-status">
                            Answered:{" "}
                            <strong>
                                {answeredCount} / {questions.length}
                            </strong>
                        </div>

                        <div className="quiz-nav-btns">
                            <button
                                type="button"
                                className="quiz-nav-btn secondary"
                                onClick={() => setCurrent((n) => n - 1)}
                                disabled={current === 0}
                            >
                                ◄ Previous
                            </button>

                            {current < questions.length - 1 ? (
                                <button
                                    type="button"
                                    className="quiz-nav-btn primary"
                                    onClick={() => setCurrent((n) => n + 1)}
                                >
                                    Next ►
                                </button>
                            ) : (
                                <button
                                    type="button"
                                    className="quiz-nav-btn submit"
                                    onClick={submitQuiz}
                                    disabled={answeredCount < questions.length}
                                    title={
                                        answeredCount < questions.length
                                            ? "Answer all questions to submit"
                                            : "Submit your quiz"
                                    }
                                >
                                    Submit Quiz ✓
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Quiz Results Screen */}
            {result && (
                <div className="quiz-results-container">
                    <div className="quiz-score-hero">
                        <div className="score-circle">
                            <span className="score-fraction">
                                {result.correct_answers}/{result.total_questions}
                            </span>
                            <span className="score-pct">
                                {result.score_percentage}%
                            </span>
                        </div>

                        <div className="score-details">
                            <h3>
                                {result.score_percentage >= 80
                                    ? "🎉 Excellent Work!"
                                    : result.score_percentage >= 50
                                    ? "👏 Good Effort!"
                                    : "Keep Learning & Retrying!"}
                            </h3>
                            <p>
                                You answered {result.correct_answers} correctly out of{" "}
                                {result.total_questions} questions. Review the key
                                explanations below to master the facts.
                            </p>

                            <div className="score-actions">
                                <button
                                    type="button"
                                    className="quiz-nav-btn primary"
                                    onClick={() => loadQuiz(mode)}
                                >
                                    🔄 Try Again
                                </button>

                                <button
                                    type="button"
                                    className="generate-quiz-btn"
                                    onClick={generateNewQuiz}
                                    disabled={generating}
                                >
                                    ⚡ Generate New Questions
                                </button>
                            </div>
                        </div>
                    </div>

                    <h3 className="quiz-review-heading">📝 Detailed Question Review</h3>

                    <div className="quiz-review-list">
                        {questions.map((q, idx) => {
                            const resItem = result.results?.find(
                                (r) => r.question_id === q.id
                            );
                            const isCorrect = resItem?.is_correct;

                            return (
                                <div
                                    key={q.id}
                                    className={`quiz-review-card ${
                                        isCorrect ? "correct-card" : "wrong-card"
                                    }`}
                                >
                                    <div className="review-card-top">
                                        <span className="review-num">
                                            Q{idx + 1}. {q.question}
                                        </span>
                                        <span
                                            className={`review-status-pill ${
                                                isCorrect
                                                    ? "pill-correct"
                                                    : "pill-wrong"
                                            }`}
                                        >
                                            {isCorrect ? "✓ Correct" : "✗ Incorrect"}
                                        </span>
                                    </div>

                                    <div className="review-choices-comparison">
                                        <div className="choice-row">
                                            <span className="choice-label">
                                                Your Answer:
                                            </span>
                                            <span
                                                className={`choice-val ${
                                                    isCorrect ? "val-correct" : "val-wrong"
                                                }`}
                                            >
                                                Option {resItem?.selected_option}:{" "}
                                                {q.options[resItem?.selected_option] ||
                                                    "Not answered"}
                                            </span>
                                        </div>

                                        {!isCorrect && (
                                            <div className="choice-row">
                                                <span className="choice-label">
                                                    Correct Answer:
                                                </span>
                                                <span className="choice-val val-correct">
                                                    Option {resItem?.correct_option}:{" "}
                                                    {q.options[resItem?.correct_option]}
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    {resItem?.explanation && (
                                        <div className="review-explanation">
                                            <strong>⭐ Explanation:</strong>
                                            <p>{resItem.explanation}</p>
                                        </div>
                                    )}

                                    {q.source_url && (
                                        <div className="review-source">
                                            Source:{" "}
                                            <a
                                                href={q.source_url}
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                {q.source_title || "Read Original Article"}
                                            </a>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Quiz;