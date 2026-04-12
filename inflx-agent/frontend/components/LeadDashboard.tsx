"use client";

import { useEffect, useState } from "react";
import { getLeads } from "@/lib/api";

type Lead = {
  id: number;
  name: string;
  email: string;
  platform: string;
  captured_at: string;
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function LeadDashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLeads = async () => {
    try {
      const data = await getLeads();
      setLeads(data.leads);
    } catch (e) {
      console.error("Failed to fetch leads", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
    // Poll every 10s so new leads appear live
    const interval = setInterval(fetchLeads, 10000);
    return () => clearInterval(interval);
  }, []);

  const today = leads.filter(
    (l) => new Date(l.captured_at).toDateString() === new Date().toDateString()
  ).length;

  const platforms = [...new Set(leads.map((l) => l.platform))].length;

  return (
    <>
      <div className="leads-header">
        <h1>Lead Dashboard</h1>
        <p>All contacts captured by the AutoStream AI Agent</p>
      </div>

      <div className="leads-stat-row">
        <div className="stat-card">
          <p className="stat-label">Total Leads</p>
          <p className="stat-value">{leads.length}</p>
          <p className="stat-sub">↑ All time</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Captured Today</p>
          <p className="stat-value">{today}</p>
          <p className="stat-sub">↑ Since midnight</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Platforms</p>
          <p className="stat-value">{platforms}</p>
          <p className="stat-sub">Unique platforms</p>
        </div>
      </div>

      <div className="leads-table-wrap">
        {loading ? (
          <div className="loading-dots">
            <span /><span /><span />
          </div>
        ) : leads.length === 0 ? (
          <div className="empty-state">
            <p>No leads yet. Go chat with the agent! 🚀</p>
          </div>
        ) : (
          <table className="leads-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Email</th>
                <th>Platform</th>
                <th>Captured At</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead, i) => (
                <tr key={lead.id}>
                  <td style={{ color: "var(--text3)" }}>{i + 1}</td>
                  <td style={{ fontWeight: 500 }}>{lead.name}</td>
                  <td style={{ color: "var(--text2)" }}>{lead.email}</td>
                  <td>
                    <span className="platform-badge">{lead.platform}</span>
                  </td>
                  <td style={{ color: "var(--text3)", fontSize: 12 }}>
                    {formatDate(lead.captured_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
