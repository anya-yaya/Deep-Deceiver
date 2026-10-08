import { useState } from "react";
import "../App.css";

function ChatPage({ messages, setMessages, sessionId }) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMessage = message.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          responseSource: data.response_source,
          detection: data.detection,
          decoy: data.decoy,
          session: data.session,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Unable to connect to the DEEP-DECEIVER backend.",
        },
      ]);

      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">

      

      <main className="chat-container">

        <div className="chat-header">
          <h2>LLM Interface</h2>

          <p>
            Interact with the protected language model environment.
          </p>
        </div>

        <div className="messages">

          {messages.length === 0 && (
            <div className="welcome">
              <h3>Welcome to DEEP-DECEIVER</h3>

              <p>
                Your messages will be processed through the
                active-defense pipeline.
              </p>
            </div>
          )}

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`message ${
                msg.role === "user"
                  ? "user-message"
                  : "assistant-message"
              }`}
            >

              <div className="message-role">
                {msg.role === "user"
                  ? "You"
                  : "DEEP-DECEIVER"}
              </div>

              <div className="message-content">
                {msg.content}
              </div>

              {msg.role === "assistant" && msg.detection && (

                <div className="detection-panel">

                  {/* RESPONSE SOURCE */}

                  <div className="response-source-section">

                    <div className="detection-title">
                      Response Source
                    </div>

                    <div
                      className={
                        msg.responseSource === "decoy"
                          ? "source-shadow"
                          : "source-production"
                      }
                    >
                      {msg.responseSource === "decoy"
                        ? "SHADOW / HONEYPOT"
                        : "PRODUCTION LLM"}
                    </div>

                  </div>

                  {/* SESSION STATUS */}

                  {msg.session && (

                    <div
                      className={
                        msg.session.environment === "shadow"
                          ? "session-status session-contained"
                          : "session-status session-active"
                      }
                    >

                      <div className="detection-title">
                        Session Status
                      </div>

                      <div className="detection-row">

                        <span>Status</span>

                        <span
                          className={
                            msg.session.status === "contained"
                              ? "detection-danger"
                              : "detection-safe"
                          }
                        >
                          {msg.session.status === "contained"
                            ? "CONTAINED"
                            : "ACTIVE"}
                        </span>

                      </div>

                      <div className="detection-row">

                        <span>Environment</span>

                        <span>
                          {msg.session.environment.toUpperCase()}
                        </span>

                      </div>

                      <div className="detection-row">

                        <span>Production Access</span>

                        <span
                          className={
                            msg.session.production_access
                              ? "detection-safe"
                              : "detection-danger"
                          }
                        >
                          {msg.session.production_access
                            ? "TRUE"
                            : "FALSE"}
                        </span>

                      </div>

                    </div>

                  )}


                  {/* FAST FILTER */}

                  <div className="detection-section">

                    <div className="detection-subtitle">
                      Fast Filter
                    </div>

                    <div className="detection-row">
                      <span>Status</span>

                      <span
                        className={
                          msg.detection.fast_filter.flagged
                            ? "detection-danger"
                            : "detection-safe"
                        }
                      >
                        {msg.detection.fast_filter.flagged
                          ? "Suspicious"
                          : "Benign"}
                      </span>
                    </div>

                    <div className="detection-row">
                      <span>Score</span>

                      <span>
                        {msg.detection.fast_filter.score.toFixed(2)}
                      </span>
                    </div>

                  </div>


                  {/* SENTRY */}

                  <div className="detection-section">

                    <div className="detection-subtitle">
                      Sentry
                    </div>

                    <div className="detection-row">

                      <span>Status</span>

                      <span
                        className={
                          msg.detection.sentry.flagged
                            ? "detection-danger"
                            : "detection-safe"
                        }
                      >
                        {msg.detection.sentry.flagged
                          ? "Threat Detected"
                          : "No Threat"}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Semantic Score</span>

                      <span>
                        {msg.detection.sentry.score.toFixed(4)}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Threshold</span>

                      <span>
                        {msg.detection.sentry.threshold.toFixed(2)}
                      </span>

                    </div>

                  </div>


                  {/* ANALYST */}

                  <div className="detection-section">

                    <div className="detection-subtitle">
                      Analyst
                    </div>

                    <div className="detection-row">

                      <span>Intent</span>

                      <span>
                        {msg.detection.analyst.intent}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Attack Category</span>

                      <span>
                        {msg.detection.analyst.attack_category}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Attacker Goal</span>

                      <span>
                        {msg.detection.analyst.attacker_goal}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Risk Score</span>

                      <span>
                        {msg.detection.analyst.risk_score.toFixed(4)}
                      </span>

                    </div>

                  </div>


                  {/* ORCHESTRATOR */}

                  <div className="detection-section">

                    <div className="detection-subtitle">
                      Orchestrator
                    </div>

                    <div className="detection-row">

                      <span>Route</span>

                      <span
                        className={
                          msg.detection.orchestrator.route === "shadow"
                            ? "detection-danger"
                            : "detection-safe"
                        }
                      >
                        {msg.detection.orchestrator.route.toUpperCase()}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Action</span>

                      <span>
                        {msg.detection.orchestrator.action}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Final Risk</span>

                      <span>
                        {msg.detection.orchestrator.final_risk_score.toFixed(
                          4
                        )}
                      </span>

                    </div>

                    <div className="detection-row">

                      <span>Threshold</span>

                      <span>
                        {msg.detection.orchestrator.threshold.toFixed(
                          2
                        )}
                      </span>

                    </div>

                     {/* DECISION REASON */}

                    <div className="detection-row">

                      <span>Decision Reason</span>

                      <span
                        className={
                          msg.detection.orchestrator.decision_reason === "sentry_threat"
                            ? "detection-danger"
                            : "detection-safe"
                        }
                      >
                        {msg.detection.orchestrator.decision_reason
                          ?.replace(/_/g, " ")
                          .toUpperCase()}
                      </span>

                    </div>                    

                  </div>


                  {/* DECOY */}

                  {msg.decoy && (

                    <div className="decoy-panel">

                      <div className="detection-title">
                        Decoy Agent
                      </div>

                      <div className="detection-row">

                        <span>Environment</span>

                        <span>
                          {msg.decoy.environment}
                        </span>

                      </div>

                      <div className="detection-row">

                        <span>Response Type</span>

                        <span>
                          {msg.decoy.response_type}
                        </span>

                      </div>

                      <div className="detection-row">

                        <span>Production Access</span>

                        <span className="detection-safe">
                          {msg.decoy.production_access
                            ? "TRUE"
                            : "FALSE"}
                        </span>

                      </div>

                    </div>

                  )}

                </div>
              )}

            </div>
          ))}


          {loading && (

            <div className="message assistant-message">

              <div className="message-role">
                DEEP-DECEIVER
              </div>

              <div className="message-content">
                Processing...
              </div>

            </div>

          )}

        </div>


        <div className="input-area">

          <textarea
            value={message}
            onChange={(event) =>
              setMessage(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Enter your message..."
            rows="3"
            disabled={loading}
          />

          <button
            onClick={sendMessage}
            disabled={loading || !message.trim()}
          >
            {loading ? "Processing..." : "Send"}
          </button>

        </div>


        <div className="footer-status">

          <span>
            Protected Environment
          </span>

          <span>
            Detection Pipeline: Fast Filter + Sentry + Analyst + Orchestrator
          </span>

        </div>

      </main>

    </div>
  );
}

export default ChatPage;