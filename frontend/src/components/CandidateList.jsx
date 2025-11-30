import React from 'react';

function CandidateList({ candidates }) {
    return (
        <div className="card">
            <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                <span>🏆</span> Qualified Candidates (≥80% Match)
            </h3>

            {candidates.length === 0 ? (
                <p className="text-center text-slate-400 py-8">
                    No candidates match the criteria yet
                </p>
            ) : (
                <div className="space-y-4">
                    {candidates.map((candidate, index) => (
                        <div
                            key={index}
                            className="glass-dark rounded-lg p-6 hover:bg-white/10 transition-all"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h4 className="text-xl font-semibold text-white">
                                        {candidate.candidate_name || 'Unknown Candidate'}
                                    </h4>
                                    <div className="flex items-center gap-2 mt-2">
                                        <span className="text-sm text-slate-400">Match Score:</span>
                                        <div className="flex items-center gap-2">
                                            <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all"
                                                    style={{ width: `${candidate.match_score}%` }}
                                                />
                                            </div>
                                            <span className="text-lg font-bold text-purple-400">
                                                {candidate.match_score.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <span className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg font-semibold">
                                    ✓ Qualified
                                </span>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <p className="text-sm text-slate-400 mb-2">Matched Skills:</p>
                                    <div className="flex flex-wrap gap-2">
                                        {candidate.matched_skills.map((skill, i) => (
                                            <span
                                                key={i}
                                                className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm"
                                            >
                                                ✓ {skill}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {candidate.missing_skills.length > 0 && (
                                    <div>
                                        <p className="text-sm text-slate-400 mb-2">Missing Skills:</p>
                                        <div className="flex flex-wrap gap-2">
                                            {candidate.missing_skills.map((skill, i) => (
                                                <span
                                                    key={i}
                                                    className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm"
                                                >
                                                    ✗ {skill}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="pt-4 border-t border-white/10">
                                <p className="text-sm text-slate-400 mb-1">AI Justification:</p>
                                <p className="text-slate-200">{candidate.justification}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default CandidateList;
