import type { Message } from "./ChatWindow";

const INTENT_CONFIG: Record<string, { label: string; className: string; icon: string }> = {
  high_intent: { label: "HIGH INTENT", className: "badge-intent-high", icon: "🔥" },
  inquiry:     { label: "INQUIRY",     className: "badge-intent-inquiry", icon: "💬" },
  objection:   { label: "OBJECTION",  className: "badge-intent-objection", icon: "⚠️" },
  off_topic:   { label: "OFF TOPIC",  className: "badge-intent-inquiry", icon: "💭" },
};

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const intentCfg = message.intent ? INTENT_CONFIG[message.intent] : null;

  return (
    <div className={`msg-row ${isUser ? "user" : ""}`}>
      <div className={`msg-avatar ${isUser ? "user" : "agent"}`}>
        {isUser ? "👤" : "🤖"}
      </div>
      <div className="msg-content">
        <div className={`msg-bubble ${isUser ? "user" : "agent"} ${message.isStreaming ? "streaming" : ""}`}>
          {message.content || (message.isStreaming ? "" : "...")}
        </div>
      </div>
    </div>
  );
}
