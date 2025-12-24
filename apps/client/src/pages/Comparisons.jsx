import React, { useState, useMemo, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';
import { useRFP } from '../context/RFPContext';
import { useSearchParams } from 'react-router-dom';
import { X } from 'lucide-react';

export default function Comparisons() {
    const { proposals, rfps } = useRFP();
    const [searchParams] = useSearchParams();
    const rfpId = searchParams.get('rfp');

    // UI State
    const [selectedDimensions, setSelectedDimensions] = useState([]);
    const [showReport, setShowReport] = useState(false);
    const [selectedProposal, setSelectedProposal] = useState(null);

    // Get the specific RFP and its proposals
    const activeRFP = rfps.find(r => String(r.id) === String(rfpId)) || rfps.find(r => (r.proposals || 0) > 0) || rfps[0];
    const activeProposals = proposals.filter(p => String(p.rfpId) === String(activeRFP?.id) && p.status === 'Accepted');

    // =======================
    // EXTRACT DIMENSIONS
    // =======================
    const [aiDimensions, setAiDimensions] = useState([]);
    const [loadingDimensions, setLoadingDimensions] = useState(false);

    useEffect(() => {
        if (activeRFP?.id) {
            setLoadingDimensions(true);
            fetch(`http://localhost:8000/api/analysis/rfp/${activeRFP.id}/dimensions`, {
                method: 'POST'
            })
                .then(res => res.json())
                .then(data => {
                    setAiDimensions(data.dimensions || []);
                })
                .catch(err => console.error("Failed to fetch dimensions:", err))
                .finally(() => setLoadingDimensions(false));
        }
    }, [activeRFP?.id]);

    const availableDimensions = useMemo(() => {
        return aiDimensions.length > 0 ? aiDimensions : [
            { id: 'cost', name: 'Cost', type: 'general' },
            { id: 'timeline', name: 'Timeline', type: 'general' },
            { id: 'experience', name: 'Experience', type: 'general' }
        ];
    }, [aiDimensions]);


    // =======================
    // CALCULATE SCORES
    // =======================
    const dimensionsData = useMemo(() => {
        if (availableDimensions.length === 0) return [];

        return activeProposals.map(p => {
            // Price/Cost Logic
            const priceRaw = parseFloat(p.price.replace(/[^0-9.]/g, '')) || 0;
            const priceAmount = p.price.toLowerCase().includes('k') ? priceRaw * 1000 : priceRaw;
            const maxPrice = Math.max(...activeProposals.map(prop => {
                const raw = parseFloat(prop.price.replace(/[^0-9.]/g, '')) || 0;
                return prop.price.toLowerCase().includes('k') ? raw * 1000 : raw;
            }));

            // Text to analyze (prefer full extracted text, fall back to summary)
            const analysisText = ((p.extracted_text || "") + " " + (p.summary || "")).toLowerCase();

            const scores = {};

            availableDimensions.forEach(dim => {
                if (dim.id === 'cost') {
                    scores[dim.id] = maxPrice > 0 ? Math.round(((maxPrice - priceAmount) / maxPrice) * 100) : 50;
                } else if (dim.id === 'timeline') {
                    // Check specific timeline keywords or use explicit start date
                    const hasDate = p.start_date || analysisText.includes('start') || analysisText.includes('schedule');
                    scores[dim.id] = hasDate ? 85 : 60;
                } else {
                    // Keyword matching for dynamic dimensions
                    const keywords = dim.keywords || [dim.name.toLowerCase()];
                    const matches = keywords.filter(kw => analysisText.includes(kw.toLowerCase()));
                    // higher score for more matches, max 95, min 40
                    const baseScore = 40;
                    const matchBonus = (matches.length / Math.max(keywords.length, 1)) * 55;
                    scores[dim.id] = Math.round(Math.min(baseScore + matchBonus, 95));
                }
            });

            // Overall score
            const selectedScores = selectedDimensions.map(dimId => scores[dimId] || 50);
            const overallScore = selectedScores.length > 0
                ? Math.round(selectedScores.reduce((a, b) => a + b, 0) / selectedScores.length)
                : Math.round(Object.values(scores).reduce((a, b) => a + b, 0) / Object.values(scores).length);

            return {
                id: p.id,
                vendor: p.vendor,
                price: p.price,
                summary: p.summary || 'No summary',
                scores: scores,
                overallScore
            };
        });
    }, [activeProposals, availableDimensions, selectedDimensions]);

    // =======================
    // DIMENSION SELECTION HANDLERS
    // =======================
    const toggleDimension = (dimId) => {
        if (selectedDimensions.includes(dimId)) {
            setSelectedDimensions(selectedDimensions.filter(d => d !== dimId));
        } else if (selectedDimensions.length < 5) {
            setSelectedDimensions([...selectedDimensions, dimId]);
        }
    };

    const generateReport = () => {
        if (selectedDimensions.length > 0) {
            setShowReport(true);
        }
    };

    // =======================
    // CHARTS (only for selected dimensions)
    // =======================
    const selectedDimensionNames = selectedDimensions.map(dimId =>
        availableDimensions.find(d => d.id === dimId)?.name || dimId
    );

    const radarOptions = {
        chart: { type: 'radar', toolbar: { show: false } },
        xaxis: { categories: selectedDimensionNames },
        colors: ['#3b82f6', '#10b981', '#f59e0b'],
        stroke: { width: 2 },
        fill: { opacity: 0.2 },
        markers: { size: 4 },
        legend: { position: 'top' }
    };

    const radarSeries = dimensionsData.slice(0, 3).map(d => ({
        name: d.vendor,
        data: selectedDimensions.map(dimId => d.scores[dimId] || 50)
    }));

    const barOptions = {
        chart: { type: 'bar', height: 350, stacked: false, toolbar: { show: false } },
        plotOptions: { bar: { horizontal: false, columnWidth: '45%', borderRadius: 4 } },
        dataLabels: { enabled: false },
        xaxis: { categories: dimensionsData.map(d => d.vendor.split(' ')[0]) },
        yaxis: { title: { text: 'Score (0-100)' }, max: 100 },
        colors: ['#3b82f6', '#10b981'],
        legend: { position: 'top' },
        fill: { opacity: 1 }
    };

    const barSeries = [
        { name: 'Overall Score', data: dimensionsData.map(d => d.overallScore) },
        { name: 'Price Score', data: dimensionsData.map(d => d.scores.cost) }
    ];

    // =======================
    // RENDER: DIMENSION SELECTION
    // =======================
    if (!showReport) {
        return (
            <div className="animate-fade-in pb-12">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 mb-2">Compare Proposals</h1>
                        <p className="text-slate-500">For RFP: <span className="font-bold text-slate-800">{activeRFP?.title}</span></p>
                    </div>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
                    <h3 className="font-bold text-slate-700 mb-2">Select Comparison Dimensions (Max 5)</h3>
                    <p className="text-sm text-slate-500 mb-6">Choose the criteria you want to use for comparing proposals</p>

                    {/* General Dimensions */}
                    <div className="mb-6">
                        <div className="text-xs font-bold text-slate-400 uppercase mb-3">General Dimensions</div>
                        <div className="flex flex-wrap gap-3">
                            {availableDimensions.filter(d => d.type === 'general').length > 0 ? (
                                availableDimensions.filter(d => d.type === 'general').map(dim => (
                                    <button
                                        key={dim.id}
                                        onClick={() => toggleDimension(dim.id)}
                                        className={`px-4 py-2 rounded-full font-medium transition-all ${selectedDimensions.includes(dim.id)
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                            }`}
                                        disabled={!selectedDimensions.includes(dim.id) && selectedDimensions.length >= 5}
                                        title={!selectedDimensions.includes(dim.id) && selectedDimensions.length >= 5 ? "Max 5 dimensions selected" : dim.description}
                                    >
                                        {dim.name}
                                    </button>
                                ))
                            ) : (
                                <p className="text-sm text-slate-400 italic">No general dimensions available.</p>
                            )}
                        </div>
                    </div>

                    {/* AI-Extracted Dimensions */}
                    <div className="mb-6">
                        <div className="text-xs font-bold text-slate-400 uppercase mb-3">RFP Requirement Dimensions</div>
                        {loadingDimensions ? (
                            <div className="flex items-center space-x-2 text-slate-400">
                                <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></div>
                                <span className="text-sm italic">AI is extracting dimensions...</span>
                            </div>
                        ) : availableDimensions.filter(d => d.type === 'dynamic').length > 0 ? (
                            <div className="flex flex-wrap gap-3">
                                {availableDimensions.filter(d => d.type === 'dynamic').map(dim => (
                                    <button
                                        key={dim.id}
                                        onClick={() => toggleDimension(dim.id)}
                                        className={`px-4 py-2 rounded-full font-medium transition-all ${selectedDimensions.includes(dim.id)
                                            ? 'bg-teal-600 text-white'
                                            : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                            }`}
                                        disabled={!selectedDimensions.includes(dim.id) && selectedDimensions.length >= 5}
                                        title={!selectedDimensions.includes(dim.id) && selectedDimensions.length >= 5 ? "Max 5 dimensions selected" : dim.description}
                                    >
                                        {dim.name}
                                    </button>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-slate-400 italic">No specific dimensions extracted yet.</p>
                        )}
                    </div>

                    <div className="flex items-center justify-between pt-6 border-t border-slate-200">
                        <div className="text-sm text-slate-600">
                            Selected: <span className="font-bold text-slate-900">{selectedDimensions.length}</span> / 5
                        </div>
                        <button
                            onClick={generateReport}
                            disabled={selectedDimensions.length === 0}
                            className={`px-6 py-3 rounded-lg font-semibold ${selectedDimensions.length > 0
                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                }`}
                        >
                            Generate Report
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // =======================
    // RENDER: COMPARISON REPORT
    // =======================
    return (
        <div className="animate-fade-in pb-12">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">Comparison Report</h1>
                    <p className="text-slate-500">Analysis for RFP: <span className="font-bold text-slate-800">{activeRFP?.title}</span></p>
                </div>
                <button
                    onClick={() => setShowReport(false)}
                    className="text-sm px-4 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded font-medium"
                >
                    ← Change Dimensions
                </button>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="font-bold text-slate-700 mb-4">Attribute Analysis</h3>
                    <ReactApexChart options={radarOptions} series={radarSeries} type="radar" height={300} />
                </div>
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="font-bold text-slate-700 mb-4">Score vs Price</h3>
                    <ReactApexChart options={barOptions} series={barSeries} type="bar" height={300} />
                </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-200">
                            <tr>
                                <th className="p-4 text-xs font-bold text-slate-500 uppercase">Vendor</th>
                                {selectedDimensions.map(dimId => {
                                    const dim = availableDimensions.find(d => d.id === dimId);
                                    return <th key={dimId} className="p-4 text-xs font-bold text-slate-500 uppercase">{dim?.name}</th>;
                                })}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {dimensionsData.map((d) => (
                                <tr key={d.id} className="hover:bg-slate-50">
                                    <td className="p-4 font-semibold text-slate-800">{d.vendor}</td>
                                    {selectedDimensions.map(dimId => (
                                        <td key={dimId} className="p-4">
                                            <span className={`px-2 py-1 rounded text-sm font-medium ${d.scores[dimId] >= 80 ? 'bg-green-100 text-green-700' :
                                                d.scores[dimId] >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>
                                                {dimId === 'cost' && d.scores[dimId] >= 80 ? 'Top Tier' :
                                                    dimId === 'cost' && d.scores[dimId] >= 60 ? 'Standard' :
                                                        dimId === 'cost' ? 'High Cost' :
                                                            dimId === 'timeline' && d.scores[dimId] >= 80 ? 'Top Tier' :
                                                                dimId === 'timeline' && d.scores[dimId] >= 60 ? 'Standard' :
                                                                    dimId === 'timeline' ? 'Slow' :
                                                                        dimId === 'experience' && d.scores[dimId] >= 80 ? 'Top Tier' :
                                                                            dimId === 'experience' && d.scores[dimId] >= 60 ? 'Standard' : 'Low Experience'}
                                            </span>
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal */}
            {selectedProposal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-auto">
                        <div className="p-6 border-b border-slate-200 flex justify-between items-center">
                            <h3 className="font-bold text-lg">{selectedProposal.vendor} - Details</h3>
                            <button onClick={() => setSelectedProposal(null)} className="text-slate-400 hover:text-slate-600">
                                <X size={24} />
                            </button>
                        </div>
                        <div className="p-6 space-y-4">
                            <div><div className="text-xs font-bold text-slate-500 uppercase mb-1">Price</div><div>{selectedProposal.price}</div></div>
                            <div><div className="text-xs font-bold text-slate-500 uppercase mb-1">Summary</div><div>{selectedProposal.summary}</div></div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
