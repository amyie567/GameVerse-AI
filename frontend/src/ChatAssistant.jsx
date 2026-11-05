import { useState, useEffect } from "react";
import "./ChatAssistant.css";

function ChatAssistant() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load saved conversations when the component opens
  useEffect(() => {
    async function loadChatHistory() {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/chat-history");

        if (!response.ok) {
          throw new Error("Failed to load chat history");
        }

        const data = await response.json();

        const savedMessages = [];

        data.reverse().forEach((chat) => {
          savedMessages.push({
            sender: "user",
            text: chat.user_message,
          });

          savedMessages.push({
            sender: "bot",
            text: chat.assistant_response,
          });
        });

        setChatHistory(savedMessages);
      } catch (error) {
        console.error("Chat history loading error:", error);

        setChatHistory([
          {
            sender: "bot",
            text: "Hello, gamer! 🎮 I'm your GameVerse AI assistant. Ask me for game recommendations!",
          },
        ]);
      }
    }

    loadChatHistory();
  }, []);

  async function sendMessage(event) {
    event.preventDefault();

    if (!message.trim() || loading) return;

    const userMessage = message.trim();

    setChatHistory((previous) => [
      ...previous,
      { sender: "user", text: userMessage },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();

      setChatHistory((previous) => [
        ...previous,
        { sender: "bot", text: data.reply },
      ]);
    } catch (error) {
      setChatHistory((previous) => [
        ...previous,
        {
          sender: "bot",
          text: "Sorry! I couldn't connect to the server. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="chat-section">
      <div className="chat-heading">
        <p className="eyebrow">POWERED BY GAMEVERSE AI</p>
        <h2>🤖 AI Gaming Assistant</h2>
        <p>Your personal gaming companion.</p>
      </div>

      <div className="chat-container">
        <div className="chat-header">
          <span>🟢</span>
          <div>
            <h3>GameVerse Assistant</h3>
            <small>Ready to help you game smarter</small>
          </div>
        </div>

        <div className="chat-messages">
          {chatHistory.map((chat, index) => (
            <div key={index} className={`chat-message ${chat.sender}`}>
              <span>{chat.sender === "bot" ? "🤖" : "👤"}</span>
              <p>{chat.text}</p>
            </div>
          ))}

          {loading && (
            <div className="chat-message bot">
              <span>🤖</span>
              <p>Thinking...</p>
            </div>
          )}
        </div>

        <form className="chat-input-area" onSubmit={sendMessage}>
          <input
            type="text"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask me about games..."
            disabled={loading}
          />

          <button type="submit" disabled={loading || !message.trim()}>
            SEND
          </button>
        </form>
      </div>
    </section>
  );
}

export default ChatAssistant;
