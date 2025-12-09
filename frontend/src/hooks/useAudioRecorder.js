import { useState, useRef } from 'react';

const useAudioRecorder = () => {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]); // Stores recorded audio blobs
    const audioContext = useRef(null);
    const analyser = useRef(null);
    const source = useRef(null);
    const silenceStart = useRef(null); // Timestamp when silence started
    const silenceTimeout = useRef(null); // Timeout ID (not strictly needed with rAF check but good for safety)
    const animationFrame = useRef(null); // ID for requestAnimationFrame

    // Silence detection configuration
    const SILENCE_THRESHOLD = 10; // Volume threshold (0-255) to consider as silence
    const SILENCE_DURATION = 2000; // Duration in ms to trigger auto-stop

    const startRecording = async (onSilence = null) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // --- Audio Analysis Setup (Silence Detection) ---
            audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
            analyser.current = audioContext.current.createAnalyser();
            analyser.current.fftSize = 256; // Smaller FFT size for simple volume check
            analyser.current.minDecibels = -90;
            analyser.current.maxDecibels = -10;
            analyser.current.smoothingTimeConstant = 0.85;

            source.current = audioContext.current.createMediaStreamSource(stream);
            source.current.connect(analyser.current);
            // ------------------------------------------------

            // --- Media Recorder Setup ---
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : 'audio/webm';

            mediaRecorder.current = new MediaRecorder(stream, { mimeType });
            audioChunks.current = [];

            mediaRecorder.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.current.push(event.data);
                }
            };

            mediaRecorder.current.start();
            setIsRecording(true);

            // Avoid immediate stop by unsetting silence start for a grace period
            silenceStart.current = Date.now() + 1000; // 1 second grace period

            // Start analyzing for silence
            detectSilence(onSilence);

        } catch (err) {
            console.error("Error accessing microphone:", err);
            alert("Microphone access denied or not available.");
        }
    };

    const detectSilence = (onSilence) => {
        if (!analyser.current) return;

        const bufferLength = analyser.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const checkSilence = () => {
            if (!analyser.current) return;

            analyser.current.getByteFrequencyData(dataArray);

            // Calculate average volume
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;

            // Simple Threshold check
            if (average < SILENCE_THRESHOLD) {
                if (!silenceStart.current) {
                    silenceStart.current = Date.now();
                } else if (Date.now() - silenceStart.current > SILENCE_DURATION) {
                    // Silence detected for duration -> Auto Stop
                    if (onSilence) {
                        onSilence(); // Callback to parent to trigger stop sequence
                    }
                    return; // Stop the loop
                }
            } else {
                silenceStart.current = null; // Reset silence timer if noise detected
            }

            if (isRecording || (mediaRecorder.current && mediaRecorder.current.state === 'recording')) {
                animationFrame.current = requestAnimationFrame(checkSilence);
            }
        };

        checkSilence();
    };

    const stopRecording = () => {
        return new Promise((resolve) => {
            // Cleanup Analysis Loop
            if (animationFrame.current) cancelAnimationFrame(animationFrame.current);
            if (silenceTimeout.current) clearTimeout(silenceTimeout.current);

            if (!mediaRecorder.current) return resolve(null);

            mediaRecorder.current.onstop = () => {
                // Combine chunks into a single Blob
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
                resolve(audioBlob);

                // Cleanup Audio Context
                if (audioContext.current && audioContext.current.state !== 'closed') {
                    audioContext.current.close();
                }
            };

            if (mediaRecorder.current.state === 'recording') {
                mediaRecorder.current.stop();
            }

            setIsRecording(false);

            // Stop all tracks to release mic
            if (mediaRecorder.current.stream) {
                mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
            }
        });
    };

    return { isRecording, startRecording, stopRecording, volume };
};

export default useAudioRecorder;
