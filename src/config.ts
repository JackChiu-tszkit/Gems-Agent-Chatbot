/**
 * Configuration is centralized here for easy injection across different deployment environments.
 *
 * - Local development: uses http://localhost:8080/chat
 * - Cloud Run deployment: uses relative path /chat (same service as backend)
 * - `VITE_GOOGLE_CLIENT_ID` should be set to your Google OAuth Web Client ID
 */

// Detect if running in development mode
const isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development'

// Use full URL for local development, relative path for production
const DEFAULT_CHAT_URL = isDevelopment 
  ? 'http://localhost:8080/chat'  // Local development
  : '/chat'  // Cloud Run unified deployment

const DEFAULT_GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_OAUTH_CLIENT_ID' // TODO: Replace with actual OAuth Client ID

export const CHAT_API_URL =
  import.meta.env.VITE_CHAT_API_URL?.toString().trim() || DEFAULT_CHAT_URL

export const GOOGLE_CLIENT_ID =
  import.meta.env.VITE_GOOGLE_CLIENT_ID?.toString().trim() || DEFAULT_GOOGLE_CLIENT_ID


