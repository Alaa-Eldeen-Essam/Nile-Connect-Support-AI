const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const messages = document.querySelector("#messages");
const send = document.querySelector("#send");

function addMessage(text, role) {
  const item = document.createElement("article");
  item.className = `message ${role}`;
  item.textContent = text;
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addMessage(message, "user");
  input.value = "";
  send.disabled = true;
  const pending = addMessage("Thinking…", "assistant pending");
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const body = await response.json();
    pending.textContent = response.ok ? body.reply : body.detail || "The service is unavailable.";
  } catch {
    pending.textContent = "Unable to reach the service. Please try again.";
  } finally {
    send.disabled = false;
    input.focus();
  }
});

document.querySelector("#reset").addEventListener("click", async () => {
  await fetch("/api/chat/reset", { method: "POST" });
  messages.replaceChildren();
  addMessage("Hello! I am a portfolio demonstration. How can I help today?", "assistant");
  input.focus();
});
