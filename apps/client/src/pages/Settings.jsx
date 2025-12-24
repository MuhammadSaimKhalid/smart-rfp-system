import React from 'react';
import { Settings as SettingsIcon, Shield, User, Bell, Database } from 'lucide-react';

export default function Settings() {
    const tabs = [
        { icon: User, label: 'Profile & Org', active: true },
        { icon: Shield, label: 'Security', active: false },
        { icon: Bell, label: 'Notifications', active: false },
        { icon: Database, label: 'Integrations', active: false },
    ];

    return (
        <div className="animate-fade-in pb-12">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">Settings</h1>
                    <p className="text-slate-500">Manage your organization preferences and AI configuration.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[250px_1fr] gap-8">
                {/* Sidebar */}
                <div className="space-y-1">
                    {tabs.map((tab, i) => (
                        <button key={i} className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${tab.active ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'
                            }`}>
                            <tab.icon size={18} /> {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content Area */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
                    <div className="flex flex-col items-center justify-center text-center h-64">
                        <div className="w-12 h-12 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mb-4">
                            <SettingsIcon size={24} />
                        </div>
                        <h3 className="font-bold text-slate-800">Configuration Panel</h3>
                        <p className="text-slate-500 text-sm mt-2">Global settings will be available here.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
