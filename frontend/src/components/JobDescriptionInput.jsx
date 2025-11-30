import React, { useState } from 'react';

function JobDescriptionInput({ onJobMatch, candidatesCount }) {
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [requiredSkills, setRequiredSkills] = useState('');
    const [preferredSkills, setPreferredSkills] = useState('');
    const [matching, setMatching] = useState(false);

    const handleMatch = async () => {
        if (!jobTitle || !jobDescription || !requiredSkills) {
            alert('Please fill in job title, description, and required skills');
            return;
        }

        if (candidatesCount === 0) {
            alert('Please upload at least one resume first');
            return;
        }

        setMatching(true);

        const jobData = {
            title: jobTitle,
            description: jobDescription,
            required_skills: requiredSkills.split(',').map(s => s.trim()).filter(s => s),
            preferred_skills: preferredSkills.split(',').map(s => s.trim()).filter(s => s),
        };

        try {
            const response = await fetch('http://localhost:8000/candidates/match', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jobData),
            });

            if (!response.ok) {
                throw new Error('Matching failed');
            }

            const results = await response.json();
            onJobMatch(results);

            if (results.length === 0) {
                alert('No candidates matched the 80% threshold');
            }
        } catch (error) {
            alert('Error matching candidates: ' + error.message);
        } finally {
            setMatching(false);
        }
    };

    return (
        <div className="card">
            <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                <span>💼</span> Job Description
            </h3>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-2">Job Title</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="e.g., Senior Full Stack Developer"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Job Description</label>
                    <textarea
                        className="input-field resize-none"
                        rows="4"
                        placeholder="Describe the role, responsibilities, and requirements..."
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Required Skills (comma-separated)</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="e.g., React, Node.js, Python, AWS"
                        value={requiredSkills}
                        onChange={(e) => setRequiredSkills(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Preferred Skills (comma-separated)</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="e.g., Docker, Kubernetes, GraphQL"
                        value={preferredSkills}
                        onChange={(e) => setPreferredSkills(e.target.value)}
                    />
                </div>

                <button
                    onClick={handleMatch}
                    disabled={matching || candidatesCount === 0}
                    className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {matching ? 'Matching...' : `Match Candidates (${candidatesCount} uploaded)`}
                </button>
            </div>
        </div>
    );
}

export default JobDescriptionInput;
