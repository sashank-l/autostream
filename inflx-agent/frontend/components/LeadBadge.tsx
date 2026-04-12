"use client";

import { useEffect } from "react";
import confetti from "canvas-confetti";

export default function LeadBadge({ name }: { name: string }) {
  useEffect(() => {
    // Fire confetti
    confetti({
      particleCount: 120,
      spread: 70,
      origin: { y: 0.85 },
      colors: ["#6c63ff", "#00d4aa", "#22c55e", "#86efac"],
    });
  }, []);

  return (
    <div className="lead-toast" role="status" aria-live="polite">
      <span className="toast-icon">🎉</span>
      <div className="toast-body">
        <p className="toast-title">Lead captured!</p>
        <p className="toast-sub">
          {name ? `${name} has been added to your pipeline.` : "Contact added to your pipeline."}
        </p>
      </div>
    </div>
  );
}
