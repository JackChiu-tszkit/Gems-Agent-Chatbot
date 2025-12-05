import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  // Temporarily disabled StrictMode to prevent double-rendering issues with Google Sign-In
  // The App component already has duplicate initialization prevention logic
  // <StrictMode>
    <App />
  // </StrictMode>,
)
