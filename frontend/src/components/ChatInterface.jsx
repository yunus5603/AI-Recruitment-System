import React, { useState, useRef, useEffect } from 'react';

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [code, setCode] = useState('');
    const [executing, setExecuting] = useState(false);
    const [executionResult, setExecutionResult] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setSending(true);

        try {
            const response = await fetch('http://localhost:8000/interview/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userMessage),
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const data = await response.json();
            setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
        } catch (error) {
            alert('Error sending message: ' + error.message);
        } finally {
            setSending(false);
        }
    };

    const executeCode = async () => {
        if (!code.trim()) return;

        setExecuting(true);
        setExecutionResult(null);

        try {
            const response = await fetch('http://localhost:8000/interview/execute-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, language: 'python' }),
            });

            if (!response.ok) {
                throw new Error('Failed to execute code');
            }

            const result = await response.json();
            setExecutionResult(result);
        } catch (error) {
            alert('Error executing code: ' + error.message);
        } finally {
            setExecuting(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Chat Section */}
            <div className="card flex flex-col h-[600px]">
                <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                    <span>💬</span> AI Interview Chat
                </h3>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                    {messages.length === 0 ? (
                        <div className="text-center text-slate-400 py-8">
                            <p className="text-lg mb-2">👋 Start the interview!</p>
                            <p className="text-sm">Ask technical questions or request coding challenges</p>
                        </div>
                    ) : (
                        messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`p-4 rounded-lg ${msg.role === 'user'
                                        ? 'bg-purple-600/20 ml-8'
                                        : 'bg-slate-700/30 mr-8'
                                    }`}
                            >
                                <p className="text-sm font-semibold mb-1 text-purple-400">
                                    {msg.role === 'user' ? '👤 You' : '🤖 AI Interviewer'}
                                </p>
                                <p className="text-slate-100 whitespace-pre-wrap">{msg.content}</p>
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="input-field flex-1"
                        placeholder="Type your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={sending}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={sending || !input.trim()}
                        className="btn-primary disabled:opacity-50"
                    >
                        {sending ? '...' : 'Send'}
                    </button>
                </div>
            </div>

            {/* Code Execution Section */}
            <div className="card flex flex-col h-[600px]">
                <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                    <span>⚡</span> Code Executor
                </h3>

                <div className="flex-1 flex flex-col gap-4">
                    {/* Code Editor */}
                    <div className="flex-1">
                        <label className="block text-sm font-medium mb-2">Python Code:</label>
                        <textarea
                            className="input-field resize-none h-full font-mono text-sm"
                            placeholder="# Write your Python code here&#10;print('Hello, World!')"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                        />
                    </div>

                    {/* Execute Button */}
                    <button
                        onClick={executeCode}
                        disabled={executing || !code.trim()}
                        className="btn-primary disabled:opacity-50"
                    >
                        {executing ? 'Executing...' : '▶ Run Code'}
                    </button>

                    {/* Output */}
                    {executionResult && (
                        <div className="glass-dark rounded-lg p-4">
                            <p className="text-sm font-semibold mb-2 flex items-center gap-2">
                                {executionResult.success ? (
                                    <span className="text-green-400">✓ Success</span>
                                ) : (
                                    <span className="text-red-400">✗ Error</span>
                                )}
                            </p>
                            <pre className="text-sm font-mono text-slate-200 whitespace-pre-wrap">
                                {executionResult.success ? executionResult.output : executionResult.error}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ChatInterface;
