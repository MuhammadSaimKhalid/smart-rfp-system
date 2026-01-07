import React, { useState, useMemo, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';
import { useRFP } from '../context/RFPContext';
import { useSearchParams } from 'react-router-dom';
import { X } from 'lucide-react';

export default function Comparisons() {
    const { proposals, rfps } = useRFP();
    const [searchParams, setSearchParams] = useSearchParams(); // Fixed: Destructuring setter
    const rfpId = searchParams.get('rfp');

    // UI State
    const [selectedDimensions, setSelectedDimensions] = useState([]);

    const [showReport, setShowReport] = useState(false);
    const [selectedProposal, setSelectedProposal] = useState(null);

    // Get the specific RFP and its proposals
    // State for filtering
    const [showAcceptedOnly, setShowAcceptedOnly] = useState(false);

    // Get the specific RFP and its proposals
    const activeRFP = rfps.find(r => String(r.id) === String(rfpId)) || rfps.find(r => (r.proposals || 0) > 0) || rfps[0];
    const activeProposals = proposals.filter(p => {
        const matchRFP = String(p.rfpId) === String(activeRFP?.id);
        const matchStatus = showAcceptedOnly ? p.status === 'Accepted' : (p.status === 'Submitted' || p.status === 'Processing' || p.status === 'Accepted');
        // Note: Usually we want to exclude 'Rejected' unless specifically asked. 
        // But for 'Compare All', we usually compare active candidates. 
        // If showAcceptedOnly is true -> Accepted.
        // If false -> All non-rejected (Submitted + Accepted + Processing). 
        // User said "Pending/Rejected will be hidden from this final decision view".
        // I'll stick to: True -> Accepted. False -> Submitted + Accepted + Processing. (Exclude Rejected).

        if (!matchRFP) return false;
        if (showAcceptedOnly) return p.status === 'Accepted';
        return p.status !== 'Rejected';
    });

    console.log('DEBUG: Comparisons render cycle', {
        rfpId,
        rfpsCount: rfps.length,
        activeRFP: activeRFP?.id,
        activeProposalsCount: activeProposals.length
    });

    // State for Saved Comparisons List
    const [savedComparisons, setSavedComparisons] = useState([]);
    const [loadingSaved, setLoadingSaved] = useState(true);

    useEffect(() => {
        if (!rfpId) {
            setLoadingSaved(true);
            fetch('http://localhost:8000/api/comparisons')
                .then(res => res.json())
                .then(data => setSavedComparisons(data))
                .catch(err => console.error("Failed to fetch saved comparisons:", err))
                .finally(() => setLoadingSaved(false));
        }
    }, [rfpId]);

    // Load saved dimensions on mount - Moved to top level
    useEffect(() => {
        if (rfpId) {
            // Check for saved comparison on backend
            fetch(`http://localhost:8000/api/comparisons/${rfpId}`)
                .then(res => {
                    if (res.ok) return res.json();
                    throw new Error('No saved comparison');
                })
                .then(data => {
                    console.log("Loaded saved comparison:", data);
                    if (data.dimensions && data.dimensions.length > 0) {
                        setSelectedDimensions(data.dimensions);
                        setShowReport(true);

                        // Load Cached Results if available
                        if (data.analysis_results && data.analysis_results.length > 0) {
                            console.log("Loaded cached analysis results");
                            setAiResults(data.analysis_results);
                        }
                    }
                })
                .catch(() => {
                    // Fallback to local storage if needed, or just nothing
                    console.log("No saved comparison found for this RFP.");
                });
        }
    }, [rfpId]);

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
            { id: 'experience', name: 'Experience', type: 'general' },
            { id: 'cost', name: 'Cost', type: 'general' },
            { id: 'materials_warranty', name: 'Materials/Warranty', type: 'general' },
            { id: 'schedule', name: 'Schedule', type: 'general' },
            { id: 'safety', name: 'Safety', type: 'general' },
            { id: 'responsiveness', name: 'Responsiveness', type: 'general' }
        ];
    }, [aiDimensions]);


    // =======================
    // AI COMPARISON ANALYSIS
    // =======================
    const [aiResults, setAiResults] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisError, setAnalysisError] = useState(null);

    const generateReport = async () => {
        if (selectedDimensions.length === 0) return;

        setAnalyzing(true);
        setAnalysisError(null);
        setShowReport(true); // Switch to report view immediately to show loading state

        try {
            const proposalIds = activeProposals.map(p => p.id);
            const res = await fetch('http://localhost:8000/api/analysis/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rfp_id: activeRFP.id,
                    proposal_ids: proposalIds,
                    dimensions: selectedDimensions
                })
            });

            if (!res.ok) throw new Error("Analysis failed");

            const data = await res.json();
            setAiResults(data.analyses);

            // AUTO-SAVE Results
            try {
                await fetch('http://localhost:8000/api/comparisons', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        rfp_id: activeRFP.id,
                        dimensions: selectedDimensions,
                        proposal_ids: proposalIds,
                        analysis_results: data.analyses
                    })
                });
                console.log("DEBUG: Comparison auto-saved successfully");
            } catch (saveErr) {
                console.error("Failed to auto-save comparison:", saveErr);
            }

        } catch (err) {
            console.error(err);
            setAnalysisError("Failed to generate AI comparison. Please try again.");
        } finally {
            setAnalyzing(false);
        }
    };

    const saveComparison = async () => {
        if (!activeRFP) return;
        try {
            const proposalIds = activeProposals.map(p => p.id);
            await fetch('http://localhost:8000/api/comparisons', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rfp_id: activeRFP.id,
                    dimensions: selectedDimensions,
                    proposal_ids: proposalIds,
                    analysis_results: aiResults || []
                })
            });
            alert("Comparison saved successfully!");
        } catch (err) {
            console.error(err);
            alert("Failed to save comparison.");
        }
    };

    // Merge AI results with Proposal Basic Data for Charts/Table
    const dimensionsData = useMemo(() => {
        if (!aiResults || activeProposals.length === 0) return [];

        return activeProposals.map(p => {
            const analysis = aiResults.find(a => a.proposal_id === p.id);
            const scores = {};
            let overallScore = 0;

            if (analysis) {
                analysis.scores.forEach(s => {
                    scores[s.dimension] = s.score;
                });
                // Calculate average
                const scoreValues = analysis.scores.map(s => s.score);
                if (scoreValues.length > 0) {
                    overallScore = Math.round(scoreValues.reduce((a, b) => a + b, 0) / scoreValues.length);
                }
            }

            return {
                id: p.id,
                vendor: p.vendor,
                price: p.price,
                summary: p.summary || 'No summary',
                scores: scores,
                overallScore,
                rationale: analysis ? analysis.scores : [] // Pass rationale for tooltip
            };
        });
    }, [aiResults, activeProposals]);

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

    // Async generateReport is defined above.

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
        data: selectedDimensions.map(dimId => (d.scores && d.scores[dimId]) || 0)
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
        { name: 'Overall Score', data: dimensionsData.map(d => d.overallScore || 0) },
        { name: 'Price Score', data: dimensionsData.map(d => (d.scores && d.scores.cost) || 0) }
    ];

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
                <div className="flex gap-3 print:hidden">
                    <button
                        onClick={() => window.print()}
                        className="text-sm px-4 py-2 bg-slate-800 text-white hover:bg-slate-900 rounded font-medium shadow-sm flex items-center gap-2"
                    >
                        <span>Download PDF</span>
                    </button>
                    <button
                        onClick={saveComparison}
                        className="text-sm px-4 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded font-medium border border-blue-200"
                    >
                        Save Comparison
                    </button>
                    <button
                        onClick={() => setShowReport(false)}
                        className="text-sm px-4 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded font-medium"
                    >
                        ← Change Dimensions
                    </button>
                </div>
            </div>

            <style>
                {`
                @media print {
                    .print\\:hidden { display: none !important; }
                    body { background: white; }
                    .sidebar, header, nav { display: none !important; } /* Try to hide layout elements if accessible via common classes, otherwise layout specific override needed */
                    #root > div > div.flex > aside { display: none; } /* Specific Layout targeting */
                    main { padding: 0; margin: 0; }
                }
                `}
            </style>

            {/* Loading / Error States */}
            {analyzing && (
                <div className="bg-blue-50 border border-blue-200 p-12 rounded-xl text-center mb-8 animate-pulse">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700 mb-4"></div>
                    <h3 className="text-lg font-bold text-blue-800">AI is Analyzing Proposals...</h3>
                    <p className="text-blue-600">Checking DB for details, comparing against RFP Budget & Deadline, and generating scores.</p>
                </div>
            )}

            {analysisError && (
                <div className="bg-red-50 border border-red-200 p-8 rounded-xl text-center mb-8">
                    <p className="text-red-800 font-semibold">{analysisError}</p>
                    <button onClick={() => setShowReport(false)} className="mt-4 text-red-600 underline">Go back</button>
                </div>
            )}

            {/* Charts */}
            {!analyzing && !analysisError && dimensionsData.length > 0 && (
                <>
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
                </>
            )}

            {!analyzing && !analysisError && dimensionsData.length === 0 && (
                <div className="bg-amber-50 border border-amber-200 p-8 rounded-xl text-center mb-8">
                    <p className="text-amber-800 font-semibold mb-2">No comparison data available.</p>
                    <p className="text-amber-600 text-sm">Either no proposals are accepted or data is missing. Please accept proposals in the RFP first.</p>
                </div>
            )}

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
                                                {dimId === 'cost' ? (d.scores[dimId] >= 80 ? 'Best Price' : d.scores[dimId] >= 60 ? 'Standard' : 'High Cost') :
                                                    dimId === 'schedule' ? (d.scores[dimId] >= 80 ? 'Fast' : d.scores[dimId] >= 60 ? 'Standard' : 'Slow') :
                                                        d.scores[dimId] >= 80 ? 'Excellent' : d.scores[dimId] >= 60 ? 'Good' : 'Fair'}
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
