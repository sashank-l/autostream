import ChatWindow from "@/components/ChatWindow";
import Link from "next/link";

export default function Home() {
  return (
    <div className="page-chat">
      <header className="header">
        <Link href="/" className="header-logo">
          <div className="header-logo-icon">🎬</div>
          <span className="header-logo-name">Auto<span>Stream</span></span>
        </Link>
        <nav className="header-nav">
          <Link href="/" className="nav-link active">Chat</Link>
          <Link href="/leads" className="nav-link">Leads</Link>
        </nav>
      </header>
      <ChatWindow />
    </div>
  );
}
