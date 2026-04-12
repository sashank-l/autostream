"use client";

import { useRef, useEffect, KeyboardEvent } from "react";

interface InputBarProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function InputBar({ onSend, disabled }: InputBarProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const val = textareaRef.current?.value.trim();
    if (!val || disabled) return;
    onSend(val);
    if (textareaRef.current) {
      textareaRef.current.value = "";
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  };

  return (
    <div className="input-bar">
      <div className="input-bar-inner">
        <textarea
          ref={textareaRef}
          className="input-textarea"
          placeholder={disabled ? "AutoStream is typing…" : "Ask me anything about AutoStream…"}
          rows={1}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          disabled={disabled}
          id="chat-input"
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={disabled}
          aria-label="Send message"
          id="send-btn"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
      <p style={{ fontSize: 11, color: "var(--text3)", textAlign: "center", marginTop: 8 }}>
        Press <kbd style={{ background: "var(--bg3)", border: "1px solid var(--border)", borderRadius: 4, padding: "1px 4px", fontSize: 10 }}>Enter</kbd> to send · <kbd style={{ background: "var(--bg3)", border: "1px solid var(--border)", borderRadius: 4, padding: "1px 4px", fontSize: 10 }}>Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
