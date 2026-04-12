import Link from "next/link";
import LeadDashboard from "@/components/LeadDashboard";

export default function LeadsPage() {
  return (
    <div className="page-leads">
      <header className="header" style={{ marginBottom: 32 }}>
        <Link href="/" className="header-logo">
          <div className="header-logo-icon">🎬</div>
          <span className="header-logo-name">Auto<span>Stream</span></span>
        </Link>
        <nav className="header-nav">
          <Link href="/" className="nav-link">Chat</Link>
          <Link href="/leads" className="nav-link active">Leads</Link>
        </nav>
      </header>
      <LeadDashboard />
    </div>
  );
}
