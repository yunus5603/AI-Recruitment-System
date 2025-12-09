import React, { useState, useRef, useEffect } from 'react';
import useAudioRecorder from '../hooks/useAudioRecorder';
import { Mic, Square, Volume2 } from 'lucide-react';

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [code, setCode] = useState('');
    const [executing, setExecuting] = useState(false);
    const [executionResult, setExecutionResult] = useState(null);
    const messagesEndRef = useRef(null);

    // Voice State
    const { isRecording, startRecording, stopRecording, volume } = useAudioRecorder();
    const [isVoiceMode, setIsVoiceMode] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const audioRef = useRef(new Audio());

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleVoiceRecord = async () => {
        if (isRecording) {
            // Manual Stop
            const audioBlob = await stopRecording();
            if (audioBlob) await transcribeAndSend(audioBlob);
        } else {
            // Start Recording with Silence Callback
            await startRecording(async () => {
                // On Silence Detected
                // Note: We need to call stopRecording inside the component context
                // But the hook manages state. Wait, stopRecording returns a promise with blob.
                // We need to trigger the stop manually from here?
                // Actually, the hook's onSilence describes WHEN to stop.
                // Let's modify the usage:
                // We call stopRecording() from here when silence is detected. (circular dependency?)
                // No, the callback is executed by the hook.
                // Inside the hook, we probably shouldn't stop implicitly if we want to return the blob here.
                // Let's refactor: The `startRecording` receives a callback. When that callback fires (silence),
                // we call `stopRecording` HERE in the component.

                console.log("Silence detected, stopping...");
                triggerAutoStop();
            });
        }
    };

    // Wrapper to handle stopping from callback (closure issue if using state directly, but useRef ok)
    // Actually, stopRecording is stable from hook.

    const triggerAutoStop = async () => {
        const audioBlob = await stopRecording();
        if (audioBlob) await transcribeAndSend(audioBlob);
    };

    const transcribeAndSend = async (audioBlob) => {
        setSending(true);
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');

            const transRes = await fetch('http://localhost:8000/interview/transcribe', {
                method: 'POST',
                body: formData
            });

            if (!transRes.ok) throw new Error("Transcription failed");

            const { text } = await transRes.json();
            if (!text.trim()) return;

            // Send as message
            await sendMessage(text); // Modified sendMessage to accept text arg
        } catch (error) {
            console.error("Voice error:", error);
            alert("Voice interaction failed");
        } finally {
            setSending(false);
        }
    };

    const speakResponse = async (text) => {
        if (!isVoiceMode) return;

        try {
            const res = await fetch(`http://localhost:8000/interview/speak?text=${encodeURIComponent(text)}`, {
                method: 'POST'
            }); // Note: POST usually sends body, but let's check backend endpoint definition. 
            // Oh, backend defined 'text' as query param implicitly if not Body().
            // Wait, backend defined `async def text_to_speech(text: str):`. Queries are default for scalars in FastAPI.

            if (!res.ok) throw new Error("TTS failed");

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);

            audioRef.current.src = url;
            audioRef.current.play();
            setIsPlaying(true);

            audioRef.current.onended = () => {
                setIsPlaying(false);
                window.URL.revokeObjectURL(url);
            };
        } catch (error) {
            console.error("TTS Error:", error);
        }
    };

    const sendMessage = async (textOverride = null) => {
        const textToSend = textOverride || input;
        if (!textToSend?.trim()) return;

        const userMessage = {
            role: 'user',
            content: textToSend,
            code_context: code.trim() || undefined
        };

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

            // Speak response if in voice mode
            if (isVoiceMode) {
                speakResponse(data.message);
            }
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
                <h3 className="text-2xl font-semibold mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span>💬</span> AI Interview Chat
                    </div>
                    <button
                        onClick={() => setIsVoiceMode(!isVoiceMode)}
                        className={`text-sm px-3 py-1 rounded-full border transition-all ${isVoiceMode
                            ? 'bg-green-500/20 border-green-500 text-green-400'
                            : 'bg-slate-800 border-slate-700 text-slate-400'
                            }`}
                    >
                        {isVoiceMode ? 'Voice Mode ON' : 'Voice Mode OFF'}
                    </button>
                </h3>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                    {messages.length === 0 ? (
                        <div className="text-center text-slate-400 py-8">
                            <p className="text-lg mb-2">👋 Start the interview!</p>
                            <p className="text-sm">Ask technical questions or request coding challenges</p>
                            {isVoiceMode && (
                                <p className="text-xs text-green-400 mt-2">🎤 Voice Mode Active: Press the mic to speak</p>
                            )}
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
                <div className="flex gap-2 items-center">
                    <input
                        type="text"
                        className="input-field flex-1"
                        placeholder={isRecording ? "Listening..." : "Type your message..."}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={sending || isRecording}
                    />

                    {/* Voice Button */}
                    <button
                        onClick={handleVoiceRecord}
                        className={`p-3 rounded-lg transition-all ${isRecording
                            ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                            : 'bg-slate-700 hover:bg-slate-600'
                            }`}
                        title={isRecording ? "Stop Recording" : "Start Recording"}
                    >
                        {isRecording ? <Square size={20} /> : <Mic size={20} />}
                    </button>

                    <button
                        onClick={() => sendMessage()}
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
                    {/* Code Editor Toolbar */}
                    <div className="flex justify-between items-center mb-1">
                        <label className="text-sm font-medium text-slate-400">Python Code:</label>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setCode('')}
                                className="text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400"
                                disabled={!code}
                            >
                                Clear
                            </button>
                            <button
                                onClick={() => navigator.clipboard.writeText(code)}
                                className="text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400"
                                disabled={!code}
                            >
                                Copy
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 relative">
                        <textarea
                            className="input-field resize-none h-full font-mono text-sm leading-relaxed p-4"
                            placeholder="# Write your Python code here&#10;def solution():&#10;    print('Hello')"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            spellCheck="false"
                        />
                    </div>

                    {/* Execute Button */}
                    <button
                        onClick={executeCode}
                        disabled={executing || !code.trim()}
                        className="btn-primary w-full flex justify-center items-center gap-2 py-3"
                    >
                        {executing ? (
                            <>Running...</>
                        ) : (
                            <>
                                <span>▶</span> Run Code
                            </>
                        )}
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
