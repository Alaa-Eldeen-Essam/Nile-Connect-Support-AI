import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  ArrowUpRight,
  ChevronRight,
  CircleHelp,
  KeyRound,
  LoaderCircle,
  MoreHorizontal,
  RotateCcw,
  Send,
  Settings2,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";

const suggestions = [
  "My home internet is down",
  "Help me configure my router",
  "I have a billing question",
  "I need to open a support ticket",
];

const openingMessage = {
  role: "assistant",
  text: "Hello — I’m Nile, an independent support-demo assistant. What can I help you with today?",
};

function basicAuth(password) {
  return `Basic ${window.btoa(`admin:${password}`)}`;
}

function App() {
  const [messages, setMessages] = useState([openingMessage]);
  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [adminToken, setAdminToken] = useState("");
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [settings, setSettings] = useState({});
  const [draft, setDraft] = useState({});
  const [settingsError, setSettingsError] = useState("");
  const [settingsBusy, setSettingsBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isSending]);

  async function sendMessage(text = message) {
    const content = text.trim();
    if (!content || isSending) return;
    setMessages((current) => [...current, { role: "user", text: content }]);
    setMessage("");
    setIsSending(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content }),
      });
      const body = await response.json();
      setMessages((current) => [
        ...current,
        { role: "assistant", text: response.ok ? body.reply : body.detail || "The service is unavailable." },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        { role: "assistant", text: "I couldn’t reach the support service. Please try again." },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  async function resetChat() {
    await fetch("/api/chat/reset", { method: "POST" });
    setMessages([openingMessage]);
  }

  async function unlockSettings(event) {
    event.preventDefault();
    setSettingsBusy(true);
    setSettingsError("");
    try {
      const response = await fetch("/api/admin/settings", {
        headers: { Authorization: basicAuth(adminToken) },
      });
      if (!response.ok) throw new Error("Invalid admin token.");
      const body = await response.json();
      setSettings(body.settings);
      setIsUnlocked(true);
    } catch (error) {
      setSettingsError(error.message || "Could not open settings.");
    } finally {
      setSettingsBusy(false);
    }
  }

  async function saveSettings(event) {
    event.preventDefault();
    setSettingsBusy(true);
    setSettingsError("");
    try {
      const response = await fetch("/api/admin/settings", {
        method: "PUT",
        headers: {
          Authorization: basicAuth(adminToken),
          "Content-Type": "application/json",
        },
        body: JSON.stringify(draft),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Could not save settings.");
      setSettings(body.settings);
      setDraft({});
    } catch (error) {
      setSettingsError(error.message || "Could not save settings.");
    } finally {
      setSettingsBusy(false);
    }
  }

  function closeDrawer() {
    setDrawerOpen(false);
    setIsUnlocked(false);
    setAdminToken("");
    setDraft({});
    setSettingsError("");
  }

  const hasConversation = messages.length > 1;

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <section className="support-window">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark"><Sparkles size={18} /></div>
            <div>
              <p>Nile Connect</p>
              <span><i /> Support AI · Demo</span>
            </div>
          </div>
          <div className="header-actions">
            <button className="icon-button" onClick={resetChat} aria-label="Start a new chat" title="New chat">
              <RotateCcw size={17} />
            </button>
            <div className="menu-wrap">
              <button className="icon-button" onClick={() => setMenuOpen(!menuOpen)} aria-label="More options">
                <MoreHorizontal size={20} />
              </button>
              {menuOpen && (
                <div className="popover">
                  <button onClick={() => { setMenuOpen(false); setDrawerOpen(true); }}>
                    <Settings2 size={16} /> Admin settings <ChevronRight size={14} />
                  </button>
                  <a href="#disclaimer" onClick={() => setMenuOpen(false)}>
                    <CircleHelp size={16} /> About this demo <ChevronRight size={14} />
                  </a>
                </div>
              )}
            </div>
          </div>
        </header>

        <div ref={scrollRef} className={`conversation ${hasConversation ? "has-conversation" : ""}`}>
          {!hasConversation && (
            <section className="welcome">
              <div className="welcome-badge"><Sparkles size={15} /> Independent support demo</div>
              <h1>Clear answers.<br /><em>Calm support.</em></h1>
              <p>Ask a question, describe an issue, or choose a starting point below.</p>
              <div className="suggestions">
                {suggestions.map((item) => (
                  <button key={item} onClick={() => sendMessage(item)}>{item}<ArrowUpRight size={14} /></button>
                ))}
              </div>
            </section>
          )}

          {hasConversation && (
            <div className="message-list">
              {messages.map((item, index) => (
                <article key={`${item.role}-${index}`} className={`message ${item.role}`}>
                  {item.role === "assistant" && <span className="message-mark">N</span>}
                  {item.role === "assistant" ? <div className="markdown"><ReactMarkdown>{item.text}</ReactMarkdown></div> : <p>{item.text}</p>}
                </article>
              ))}
              {isSending && <article className="message assistant loading"><span className="message-mark">N</span><LoaderCircle size={17} /> Thinking</article>}
            </div>
          )}
        </div>

        <form className="composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); } }}
            placeholder="Type your message…"
            maxLength="4000"
            rows="1"
            aria-label="Your message"
          />
          <button className="send-button" type="submit" disabled={!message.trim() || isSending} aria-label="Send message">
            <Send size={17} />
          </button>
        </form>
      </section>

      <footer id="disclaimer" className="disclaimer">
        <ShieldCheck size={15} />
        <p><strong>Independent portfolio demonstration.</strong> Nile Connect Support AI is not affiliated with, endorsed by, or operated by Telecom Egypt, WE, or any telecom provider. Demonstration knowledge content is adapted from the public Kaggle dataset <a href="https://www.kaggle.com/datasets/mahmoudramadan025/we-telecom-scraped-data" target="_blank" rel="noreferrer">WE Telecom Scraped Data <ArrowUpRight size={12} /></a> and may be incomplete or inaccurate. Do not provide real personal, billing, or account data.</p>
      </footer>

      {drawerOpen && (
        <div className="drawer-layer" role="dialog" aria-modal="true" aria-label="Admin settings">
          <button className="scrim" onClick={closeDrawer} aria-label="Close settings" />
          <aside className="settings-drawer">
            <button className="close-button" onClick={closeDrawer} aria-label="Close settings"><X size={19} /></button>
            <div className="drawer-title"><span><KeyRound size={17} /></span><div><p>Admin area</p><h2>Runtime settings</h2></div></div>
            {!isUnlocked ? (
              <form className="unlock-form" onSubmit={unlockSettings}>
                <p>Enter the server-side admin token to configure integrations. This token stays only in this browser tab.</p>
                <label>Admin token<input type="password" value={adminToken} onChange={(event) => setAdminToken(event.target.value)} autoFocus required /></label>
                {settingsError && <p className="form-error">{settingsError}</p>}
                <button className="primary" disabled={settingsBusy}>{settingsBusy ? "Checking…" : "Continue securely"}<ChevronRight size={16} /></button>
              </form>
            ) : (
              <form className="settings-form" onSubmit={saveSettings}>
                <p>Configured values are masked. Leave a field empty to keep its current value.</p>
                {Object.entries(settings).map(([key, status]) => (
                  <label key={key}>{key}<small>{status}</small><input type="password" value={draft[key] || ""} onChange={(event) => setDraft({ ...draft, [key]: event.target.value })} autoComplete="off" /></label>
                ))}
                {settingsError && <p className="form-error">{settingsError}</p>}
                <button className="primary" disabled={settingsBusy}>{settingsBusy ? "Saving…" : "Save settings"}<ShieldCheck size={16} /></button>
              </form>
            )}
          </aside>
        </div>
      )}
    </main>
  );
}

export default App;
