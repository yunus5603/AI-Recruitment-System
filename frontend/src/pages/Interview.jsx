import React from 'react';
import ChatInterface from '../components/ChatInterface';

function Interview() {
    return (
        <div className="space-y-8">
            <div className="text-center">
                <h2 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Technical Interview
                </h2>
                <p className="text-slate-400">AI-powered interview with code execution capabilities</p>
            </div>

            <ChatInterface />
        </div>
    );
}

export default Interview;
