// Base URL of the FastAPI backend. Set VITE_API_URL at build time to point the
// UI at a deployed API; defaults to the local dev server.
export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

export const apiUrl = (path) => `${API_URL}${path.startsWith('/') ? path : `/${path}`}`;
