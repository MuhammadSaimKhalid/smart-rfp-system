import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
    LayoutDashboard,
    FilePlus,
    FolderOpen,
    Files,
    BarChart2,
    Settings,
    ShieldCheck,
    Menu
} from 'lucide-react';

export default function Layout() {
    const navItems = [
        { to: "/", icon: <LayoutDashboard size={20} />, label: "Dashboard" },
        { to: "/create-rfp", icon: <FilePlus size={20} />, label: "Create RFP" },
        { to: "/open-rfps", icon: <FolderOpen size={20} />, label: "Open RFPs" },
        { to: "/comparisons", icon: <BarChart2 size={20} />, label: "Comparisons" },
        { to: "/documents", icon: <Files size={20} />, label: "Documents" },
        { to: "/settings", icon: <Settings size={20} />, label: "Settings" },
    ];

    return (
        <div className="app-container">
            {/* Sidebar */}
            <aside style={{
                width: 'var(--sidebar-width)',
                height: '100vh',
                position: 'fixed',
                left: 0,
                top: 0,
                backgroundColor: 'white',
                borderRight: '1px solid var(--border-light)',
                display: 'flex',
                flexDirection: 'column',
                zIndex: 50
            }}>
                <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--primary)', fontWeight: '700', fontSize: '1.125rem' }}>
                        <div style={{
                            width: 32, height: 32,
                            background: 'var(--primary)',
                            borderRadius: 6,
                            display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white'
                        }}>S</div>
                        Smart RFP
                    </div>
                </div>

                <nav style={{ flex: 1, padding: '1.5rem' }}>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {navItems.map((item) => (
                            <li key={item.to}>
                                <NavLink
                                    to={item.to}
                                    className={({ isActive }) => `
                    flex items-center gap-3 px-3 py-2 rounded-md transition-colors
                    ${isActive ? 'bg-blue-50 text-blue-800 font-medium' : 'text-slate-600 hover:bg-slate-50'}
                  `}
                                    style={({ isActive }) => ({
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem',
                                        padding: '0.75rem 1rem',
                                        borderRadius: '8px',
                                        textDecoration: 'none',
                                        color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                                        backgroundColor: isActive ? '#eff6ff' : 'transparent',
                                        fontWeight: isActive ? 600 : 500
                                    })}
                                >
                                    {item.icon}
                                    {item.label}
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <span style={{ width: 8, height: 8, background: '#10b981', borderRadius: '50%', display: 'inline-block' }}></span>
                        AI Engine: Active
                    </div>
                    <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Version 2.0 (React)
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="main-content" style={{ flex: 1, marginLeft: 'var(--sidebar-width)', minHeight: '100vh', background: 'var(--bg-body)' }}>
                <header style={{
                    marginBottom: '2rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    {/* Breadcrumbs or Page Title determined by Route could go here */}
                    <div></div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <button className="btn btn-secondary">
                            <ShieldCheck size={16} /> Secure Mode
                        </button>
                        <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            👤
                        </div>
                    </div>
                </header>

                <Outlet />
            </main>
        </div>
    );
}
