"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import MessageBubble from "./MessageBubble";
import InputBar from "./InputBar";
import LeadBadge from "./LeadBadge";
import { sendMessage } from "@/lib/api";

export type Message = {
  id: string;
  role: "user" | "agent";
  content: string;
  intent?: string;
  confidence?: number;
  citations?: string[];
  isStreaming?: boolean;
};

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showLeadBadge, setShowLeadBadge] = useState(false);
  const [leadName, setLeadName] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const esRef = useRef<EventSource | null>(null);

  const scrollDown = () => {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  };

  const handleSend = useCallback(
    async (text: string) => {
      if (isStreaming || !text.trim()) return;

      // Add user message
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      };
      setMessages((prev) => [...prev, userMsg]);
      scrollDown();

      // Placeholder agent message while streaming
      const agentMsgId = crypto.randomUUID();
      setMessages((prev) => [
        ...prev,
        { id: agentMsgId, role: "agent", content: "", isStreaming: true },
      ]);
      setIsStreaming(true);

      try {
        // 1. POST /chat → get session_id
        const { session_id } = await sendMessage(sessionId, text);
        if (!sessionId) setSessionId(session_id);

        // 2. GET /stream/{session_id} via SSE
        const es = new EventSource(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/stream/${session_id}`
        );
        esRef.current = es;

        let tokenBuffer = "";
        let intent: string | undefined;
        let confidence: number | undefined;
        let citations: string[] | undefined;

        es.onmessage = (e) => {
          const data = JSON.parse(e.data);

          if (data.type === "token") {
            tokenBuffer += data.content;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId ? { ...m, content: tokenBuffer } : m
              )
            );
            scrollDown();
          } else if (data.type === "metadata") {
            intent = data.intent;
            confidence = data.confidence;
            citations = data.citations;

            if (data.lead_captured) {
              const name = tokenBuffer.match(/you're all set,?\s*(\w+)/i)?.[1] || "you";
              setLeadName(name);
              setShowLeadBadge(true);
              setTimeout(() => setShowLeadBadge(false), 5000);
            }
          } else if (data.type === "done") {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === agentMsgId
                  ? { ...m, content: tokenBuffer, isStreaming: false, intent, confidence, citations }
                  : m
              )
            );
            setIsStreaming(false);
            es.close();
          }
        };

        es.onerror = () => {
          es.close();
          setIsStreaming(false);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === agentMsgId
                ? { ...m, content: tokenBuffer || "Sorry, something went wrong.", isStreaming: false }
                : m
            )
          );
        };
      } catch (err) {
        setIsStreaming(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === agentMsgId
              ? { ...m, content: "Connection error. Is the backend running?", isStreaming: false }
              : m
          )
        );
      }
    },
    [isStreaming, sessionId]
  );

  // Auto-scroll whenever messages change
  useEffect(() => { scrollDown(); }, [messages.length]);

  const HINTS = [
    "What's the difference between your plans?",
    "Can I get a refund?",
    "Does it work with OBS?",
    "I want to sign up for Pro 🚀",
  ];

  return (
    <>
      {messages.length === 0 ? (
        <div className="welcome" style={{ flex: 1 }}>
          <div className="welcome-icon">🎬</div>
          <h1>AutoStream AI Agent</h1>
          <p>Ask me about plans, pricing, features, or get started with a free trial.</p>
          <div className="welcome-hints">
            {HINTS.map((h) => (
              <button key={h} className="hint-chip" onClick={() => handleSend(h)}>
                {h}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="chat-window">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>
      )}

      <InputBar onSend={handleSend} disabled={isStreaming} />
    </>
  );
}
