import React, { useState, useEffect } from 'react';
import ResumeUpload from '../components/ResumeUpload';
import JobDescriptionInput from '../components/JobDescriptionInput';
import CandidateList from '../components/CandidateList';
import { SkillsChart } from '../components/DashboardCharts';

function Dashboard() {
    const [candidates, setCandidates] = useState([]);
    const [rankedCandidates, setRankedCandidates] = useState([]);

    // Analytics State
    const [stats, setStats] = useState({
        total_candidates: 0,
        total_matches: 0,
        avg_match_score: 0,
        pass_rate: 0
    });
    const [skillsData, setSkillsData] = useState([]);

    useEffect(() => {
        fetchAnalytics();
    }, [candidates, rankedCandidates]); // Refresh when data changes

    const fetchAnalytics = async () => {
        try {
            const [statsRes, skillsRes] = await Promise.all([
                fetch('http://localhost:8000/analytics/dashboard'),
                fetch('http://localhost:8000/analytics/skills')
            ]);
            if (statsRes.ok && skillsRes.ok) {
                setStats(await statsRes.json());
                const skills = await skillsRes.json();
                setSkillsData(skills.skills);
            }
        } catch (error) {
            console.error("Error fetching analytics:", error);
        }
    };

    const handleResumeUploaded = (resumeData) => {
        setCandidates(prev => [...prev, resumeData]);
    };

    const handleJobMatch = (results) => {
        setRankedCandidates(results);
    };

    const handleExport = async () => {
        try {
            const response = await fetch('http://localhost:8000/analytics/export');
            if (!response.ok) throw new Error("Export failed");

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "recruitment_report.pdf";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error("Export error:", error);
            alert("Failed to export report");
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Recruitment Dashboard
                    </h2>
                    <p className="text-slate-400">Real-time metrics and candidate matching</p>
                </div>
                <button
                    onClick={handleExport}
                    className="btn-secondary flex items-center gap-2"
                >
                    <span className="text-lg">📥</span>
                    Export Report
                </button>
            </div>

            {/* Analytics Section */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard title="Total Candidates" value={stats.total_candidates} />
                <StatCard title="Total Matches" value={stats.total_matches} />
                <StatCard title="Avg Score" value={`${stats.avg_match_score}%`} />
                <StatCard title="Pass Rate" value={`${stats.pass_rate}%`} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Charts */}
                <div className="lg:col-span-1">
                    <SkillsChart data={skillsData} />
                </div>

                {/* Actions */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <ResumeUpload onResumeUploaded={handleResumeUploaded} />
                        <JobDescriptionInput
                            onJobMatch={handleJobMatch}
                            candidatesCount={stats.total_candidates} // Use DB count
                        />
                    </div>

                    {rankedCandidates.length > 0 && (
                        <CandidateList candidates={rankedCandidates} />
                    )}
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value }) {
    return (
        <div className="card p-4">
            <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
            <p className="text-2xl font-bold text-slate-100">{value}</p>
        </div>
    );
}

export default Dashboard;
