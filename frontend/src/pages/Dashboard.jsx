import React, { useState } from 'react';
import ResumeUpload from '../components/ResumeUpload';
import JobDescriptionInput from '../components/JobDescriptionInput';
import CandidateList from '../components/CandidateList';

function Dashboard() {
    const [candidates, setCandidates] = useState([]);
    const [rankedCandidates, setRankedCandidates] = useState([]);

    const handleResumeUploaded = (resumeData) => {
        setCandidates(prev => [...prev, resumeData]);
    };

    const handleJobMatch = (results) => {
        setRankedCandidates(results);
    };

    return (
        <div className="space-y-8">
            <div className="text-center">
                <h2 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Recruitment Dashboard
                </h2>
                <p className="text-slate-400">Upload resumes and match candidates to job descriptions</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <ResumeUpload onResumeUploaded={handleResumeUploaded} />
                <JobDescriptionInput
                    onJobMatch={handleJobMatch}
                    candidatesCount={candidates.length}
                />
            </div>

            {rankedCandidates.length > 0 && (
                <CandidateList candidates={rankedCandidates} />
            )}
        </div>
    );
}

export default Dashboard;
