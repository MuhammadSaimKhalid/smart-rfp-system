import React from 'react';
import { FileText, Files, BarChart2, Plus, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useRFP } from '../context/RFPContext';

export default function Dashboard() {
    const { rfps } = useRFP();

    // Computed KPIs
    const openCount = rfps.filter(r => r.status === 'open').length;
    const draftCount = rfps.filter(r => r.status === 'draft').length;

    const kpis = [
        { label: 'Open RFPs', value: openCount, icon: <FileText className="text-blue-600" size={24} />, color: 'bg-blue-100' },
        { label: 'Drafts', value: draftCount, icon: <Files className="text-amber-600" size={24} />, color: 'bg-amber-100' },
        { label: 'Saved Comparisons', value: 3, icon: <BarChart2 className="text-teal-600" size={24} />, color: 'bg-teal-100' },
    ];

    const activity = [
        { id: 1, text: 'Proposal uploaded for HVAC Upgrade', time: '2 hours ago', type: 'proposal' },
        { id: 2, text: 'RFP finalized: Security Services', time: '5 hours ago', type: 'rfp' },
    ];

    return (
        <div className="animate-fade-in">
            <h1 style={{ fontSize: '1.875rem', fontWeight: '700', marginBottom: '1.5rem', color: 'var(--text-main)' }}>Dashboard</h1>

            {/* KPIs */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                {kpis.map((kpi, idx) => (
                    <div key={idx} className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ padding: '1rem', borderRadius: '12px', background: kpi.color.replace('bg-', 'var(--').replace('-100', '-light)') }}>
                            <div style={{
                                width: 48, height: 48, borderRadius: 12,
                                backgroundColor: idx === 0 ? '#dbeafe' : idx === 1 ? '#fef3c7' : '#ccfbf1',
                                display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                {kpi.icon}
                            </div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', fontWeight: '500' }}>{kpi.label}</div>
                            <div style={{ fontSize: '1.875rem', fontWeight: '700', color: 'var(--text-main)' }}>{kpi.value}</div>
                        </div>
                    </div>
                ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>

                {/* Recent Activity */}
                <section className="card">
                    <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>Recent Activity</h3>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {/* Dynamic Activity would go here */}
                        {rfps.slice(0, 3).map(rfp => (
                            <li key={rfp.id} style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'flex-start' }}>
                                <div style={{ marginTop: '0.25rem', width: 10, height: 10, borderRadius: '50%', backgroundColor: '#10b981', flexShrink: 0 }}></div>
                                <div>
                                    <div style={{ fontWeight: '500' }}>RFP Created/Updated: {rfp.title}</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Just now</div>
                                </div>
                            </li>
                        ))}
                    </ul>
                </section>

                {/* Quick Actions */}
                <section className="card">
                    <h3 style={{ marginBottom: '1rem' }}>Quick Actions</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <Link to="/create-rfp" className="btn btn-primary" style={{ justifyContent: 'center', textDecoration: 'none' }}>
                            <Plus size={18} /> Create New RFP
                        </Link>
                        <Link to="/open-rfps" className="btn btn-secondary" style={{ justifyContent: 'center', textDecoration: 'none' }}>
                            View Open RFPs <ArrowRight size={16} />
                        </Link>
                    </div>
                </section>
            </div>
        </div>
    );
}
