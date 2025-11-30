import React, { useState } from 'react';

function ResumeUpload({ onResumeUploaded }) {
    const [uploading, setUploading] = useState(false);
    const [uploadedCount, setUploadedCount] = useState(0);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = async (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            await handleFile(e.target.files[0]);
        }
    };

    const handleFile = async (file) => {
        if (!file.name.endsWith('.pdf')) {
            alert('Please upload a PDF file');
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/candidates/upload-resume', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            onResumeUploaded(data);
            setUploadedCount(prev => prev + 1);
            alert(`Resume uploaded successfully! Candidate: ${data.name || 'Unknown'}`);
        } catch (error) {
            alert('Error uploading resume: ' + error.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="card">
            <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                <span>📄</span> Upload Resumes
            </h3>

            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${dragActive
                        ? 'border-purple-500 bg-purple-500/10'
                        : 'border-white/20 hover:border-purple-500/50'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="resume-upload"
                    className="hidden"
                    accept=".pdf"
                    onChange={handleChange}
                    disabled={uploading}
                />

                <label htmlFor="resume-upload" className="cursor-pointer">
                    <div className="text-6xl mb-4">📤</div>
                    <p className="text-lg mb-2">
                        {uploading ? 'Uploading...' : 'Drag & drop PDF resumes here'}
                    </p>
                    <p className="text-sm text-slate-400">or click to browse</p>
                </label>
            </div>

            <div className="mt-4 text-center">
                <p className="text-slate-300">
                    Uploaded: <span className="font-bold text-purple-400">{uploadedCount}</span> resumes
                </p>
            </div>
        </div>
    );
}

export default ResumeUpload;
