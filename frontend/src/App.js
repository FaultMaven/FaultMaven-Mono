import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
    const [query, setQuery] = useState("");
    const [logs, setLogs] = useState("");
    const [response, setResponse] = useState("Response will appear here...");
    const [isSidebar, setIsSidebar] = useState(false);

    // ✅ Detect if the app is running inside the sidebar
    useEffect(() => {
        const isInSidebar = window.location.pathname === "/sidebar-mode";
        setIsSidebar(isInSidebar);
    }, []);

    const handleSubmit = async () => {
        const payload = { query, logs };

        try {
            const res = await fetch(`${config.apiUrl}/query`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                throw new Error(`HTTP error! Status: ${res.status}`);
            }

            const data = await res.json();
            console.log("API Response:", data);

            if (data.response) {
                if (typeof data.response === "object") {
                    setResponse(
                        <div>
                            <strong>Next Steps:</strong> {data.response.next_steps?.join(", ") || "N/A"}
                            <br />
                            <strong>Likely Cause:</strong> {data.response.likely_cause || "N/A"}
                        </div>
                    );
                } else {
                    setResponse(data.response);
                }
            } else {
                setResponse("No valid response received.");
            }
        } catch (error) {
            console.error("Error fetching API:", error);
            setResponse("Error submitting query. Please try again.");
        }
    };

    return (
        <div className={`container ${isSidebar ? "sidebar-mode" : ""}`}>
            {isSidebar && (
                <div className="sidebar-header">
                    <span>FaultMaven Copilot</span>
                    <button className="close-sidebar" onClick={() => window.parent.postMessage({ type: "CLOSE_SIDEBAR" }, "*")}>×</button>
                </div>
            )}

            {!isSidebar && <h2>FaultMaven - Submit Your Query</h2>}

            <div className="input-container">
                <label>Your Question:</label>
                <textarea
                    rows="2"
                    placeholder="E.g., Why is my server slow?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
            </div>

            <div className="input-container">
                <label>Log/Metric Data (Optional):</label>
                <textarea
                    rows="6"
                    placeholder="Paste logs or metrics here..."
                    value={logs}
                    onChange={(e) => setLogs(e.target.value)}
                />
            </div>

            <button onClick={handleSubmit}>Submit</button>

            <div className="response-container">
                <h3>Response:</h3>
                <div>{response}</div>
            </div>
        </div>
    );
}

export default App;
