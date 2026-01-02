import React from 'react';
import { FileText, Download, Filter, Search } from 'lucide-react';

export default function Documents() {
    return (
        <div className="animate-fade-in pb-12">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">Documents Repository</h1>
                    <p className="text-slate-500">Manage your generated RFPs and uploaded proposals.</p>
                </div>
                <div className="flex gap-3">
                    <button className="btn bg-white border border-slate-200 text-slate-600 hover:bg-slate-50">
                        <Filter size={18} /> Filter
                    </button>
                    <button className="btn btn-primary">
                        <Download size={18} /> Export All
                    </button>
                </div>
            </div>

            {/* Search Bar */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-8 flex items-center gap-3">
                <Search size={20} className="text-slate-400" />
                <input
                    type="text"
                    placeholder="Search content within documents..."
                    className="flex-1 outline-none text-slate-700"
                />
            </div>

            {/* Empty State / Construction */}
            <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl p-16 flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-6">
                    <FileText size={32} />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">Document Filing System Coming Soon</h3>
                <p className="text-slate-500 max-w-md mx-auto">
                    We are building a centralized hub for all your generated contracts and vendor submissions.
                    Check back in the next update.
                </p>
            </div>
        </div>
    );
}
