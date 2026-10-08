import { useState } from "react";

import ChatPage from "./pages/ChatPage";
import SOCPage from "./pages/SOCPage";

import "./App.css";

function App() {

  const [page, setPage] = useState("chat");

  // Keep chat history at App level so it survives
  // switching between LLM Interface and SOC Dashboard.
  const [messages, setMessages] = useState([]);

  // Create one unique session for this browser conversation.
  const [sessionId] = useState(() => crypto.randomUUID());

  return (
    <div className="app">

      <header className="header">

        <div>

          <h1>DEEP-DECEIVER</h1>

          <p>
            Agentic Active-Defense Framework
          </p>

        </div>


        <div className="navigation">

          <button
            className={
              page === "chat"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => setPage("chat")}
          >
            LLM Interface
          </button>


          <button
            className={
              page === "soc"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => setPage("soc")}
          >
            SOC Dashboard
          </button>


          <div className="status">

            <span className="status-dot"></span>

            System Online

          </div>

        </div>

      </header>


      {page === "chat" ? (

        <ChatPage
          messages={messages}
          setMessages={setMessages}
          sessionId={sessionId}
        />

      ) : (

        <SOCPage />

      )}

    </div>
  );
}

export default App;