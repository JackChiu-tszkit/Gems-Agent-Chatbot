import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from 'react'
import { jwtDecode, type JwtPayload } from 'jwt-decode'
import ReactMarkdown from 'react-markdown'
import './App.css'
import { CHAT_API_URL, GOOGLE_CLIENT_ID } from './config'

type MessageRole = 'user' | 'agent'

interface Message {
  id: string
  role: MessageRole
  text: string
}

interface UserProfile {
  name?: string
  email: string
  picture?: string
}

interface GoogleJwtPayload extends JwtPayload {
  email?: string
  name?: string
  picture?: string
}

const EMAIL_DOMAIN = '@randstad.no'

const generateId = () => crypto.randomUUID()

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)
  const [user, setUser] = useState<UserProfile | null>(null)

  const loginButtonRef = useRef<HTMLDivElement | null>(null)
  const isGoogleSignInInitialized = useRef(false) // Prevent duplicate initialization

  const isClientIdConfigured = GOOGLE_CLIENT_ID && !GOOGLE_CLIENT_ID.includes('YOUR_GOOGLE')
  const isChatApiConfigured = CHAT_API_URL && !CHAT_API_URL.includes('<my-cloud-run-service>')

  const isAuthorized = Boolean(user)

  const handleCredentialResponse = useCallback((credentialResponse: { credential: string }) => {
    console.log('Received Google credential')
    try {
      const decoded = jwtDecode<GoogleJwtPayload>(credentialResponse.credential)
      const email = decoded.email ?? ''
      console.log('Decoded email:', email)
      
      if (!email.endsWith(EMAIL_DOMAIN)) {
        setUser(null)
        setAuthError('Kun ansatte med @randstad.no kan bruke GEMS Agent.')
        console.warn('Email does not match required domain:', email)
        return
      }
      
      setUser({
        name: decoded.name ?? email,
        email,
        picture: decoded.picture,
      })
      setAuthError(null)
      console.log('Login successful, user:', decoded.name || email)
    } catch (err) {
      console.error('Error processing login:', err)
      setAuthError('Google pålogging feilet, prøv igjen.')
    }
  }, [])

  useEffect(() => {
    // Skip if already initialized
    if (isGoogleSignInInitialized.current) {
      return
    }

    if (!isClientIdConfigured || !loginButtonRef.current) {
      return
    }

    // Check if button already exists
    if (loginButtonRef.current.querySelector('iframe')) {
      console.log('Google Sign-In button already exists, skipping initialization')
      isGoogleSignInInitialized.current = true
      return
    }

    let timeoutId: ReturnType<typeof setTimeout> | null = null
    let checkInterval: ReturnType<typeof setInterval> | null = null

    // Wait for Google Identity Services script to load
    const initGoogleSignIn = () => {
      // Double-check to prevent duplicate initialization
      if (isGoogleSignInInitialized.current) {
        return
      }

      if (!window.google?.accounts?.id) {
        // Retry after a short delay if not loaded yet
        timeoutId = setTimeout(initGoogleSignIn, 100)
        return
      }

      // Check again if button already exists
      if (loginButtonRef.current?.querySelector('iframe')) {
        console.log('Google Sign-In button already exists, skipping initialization')
        isGoogleSignInInitialized.current = true
        return
      }

      try {
        console.log('Initializing Google Sign-In, Client ID:', GOOGLE_CLIENT_ID.substring(0, 20) + '...')
        console.log('Current origin:', window.location.origin)
        
        // Validate Client ID format
        if (!GOOGLE_CLIENT_ID.includes('.apps.googleusercontent.com')) {
          console.error('Invalid Client ID format:', GOOGLE_CLIENT_ID)
          setAuthError('Google Client ID configuration error')
          return
        }
        
        // Mark as initialized to prevent duplicates
        isGoogleSignInInitialized.current = true
        
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse,
          auto_select: false,
        })

        if (loginButtonRef.current && !loginButtonRef.current.querySelector('iframe')) {
          loginButtonRef.current.innerHTML = ''
          window.google.accounts.id.renderButton(loginButtonRef.current, {
            theme: 'filled_blue',
            size: 'large',
            width: 260,
            text: 'signin_with',
            shape: 'rectangular',
          })
          console.log('Google Sign-In button rendered')
        }
      } catch (error) {
        console.error('Failed to initialize Google Sign-In:', error)
        // Reset flag on failure to allow retry
        isGoogleSignInInitialized.current = false
        setAuthError('Kunne ikke laste Google pålogging. Prøv å oppdatere siden.')
      }
    }

    // Initialize immediately if already loaded
    if (window.google?.accounts?.id) {
      console.log('Google Identity Services loaded, initializing')
      initGoogleSignIn()
    } else {
      console.log('Waiting for Google Identity Services to load...')
      // Otherwise wait for it to load
      checkInterval = setInterval(() => {
        if (window.google?.accounts?.id) {
          console.log('Google Identity Services loaded, starting initialization')
          if (checkInterval) clearInterval(checkInterval)
          initGoogleSignIn()
        }
      }, 100)

      // Timeout after 10 seconds
      timeoutId = setTimeout(() => {
        if (checkInterval) clearInterval(checkInterval)
        if (!window.google?.accounts?.id) {
          console.error('Google Identity Services failed to load after 10 seconds')
          setAuthError('Kunne ikke laste Google pålogging. Sjekk internettforbindelsen eller oppdater siden.')
        }
      }, 10000)
    }

    // Cleanup function
    return () => {
      if (timeoutId) clearTimeout(timeoutId)
      if (checkInterval) clearInterval(checkInterval)
      // Note: Don't reset isGoogleSignInInitialized.current
      // Google Sign-In only needs to be initialized once
    }
  }, [handleCredentialResponse, isClientIdConfigured])

  const handleSignOut = () => {
    if (user?.email && window.google) {
      window.google.accounts.id.revoke(user.email, () => undefined)
    }
    setUser(null)
    setMessages([])
    setAuthError(null)
  }

  const sendMessage = async () => {
    const trimmed = inputValue.trim()
    if (!trimmed || isLoading) return

    const newUserMessage: Message = {
      id: generateId(),
      role: 'user',
      text: trimmed,
    }

    setMessages((prev) => [...prev, newUserMessage])
    setInputValue('')
    setIsLoading(true)
    setError(null)

    // Log message
    const logEntry = {
      timestamp: new Date().toISOString(),
      action: 'send_message',
      message: trimmed,
      apiUrl: CHAT_API_URL,
    }
    console.log('[GEMS Agent] Sending message:', logEntry)

    try {
      const startTime = Date.now()
      const response = await fetch(CHAT_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: trimmed }),
      })

      const duration = Date.now() - startTime
      console.log(`[GEMS Agent] API response:`, {
        status: response.status,
        statusText: response.statusText,
        duration: `${duration}ms`,
        url: CHAT_API_URL,
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('[GEMS Agent] API error:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText,
        })
        throw new Error(`API responded with status ${response.status}: ${response.statusText}`)
      }

      const data: { reply?: string } = await response.json()
      const replyText = data.reply?.trim()

      console.log('[GEMS Agent] Response data:', {
        hasReply: !!replyText,
        replyLength: replyText?.length || 0,
        replyPreview: replyText?.substring(0, 100) || 'No content',
      })

      if (!replyText) {
        throw new Error('Svarformatet mangler reply-feltet.')
      }

      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: 'agent',
          text: replyText,
        },
      ])

      console.log('[GEMS Agent] Message added to chat history')
    } catch (err) {
      const errorDetails = {
        error: err instanceof Error ? err.message : String(err),
        stack: err instanceof Error ? err.stack : undefined,
        timestamp: new Date().toISOString(),
      }
      console.error('[GEMS Agent] Error details:', errorDetails)
      setError('Kunne ikke hente svar fra GEMS Agent. Prøv igjen.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  const statusBanner = useMemo(() => {
    if (!isClientIdConfigured) {
      return 'Sett VITE_GOOGLE_CLIENT_ID i miljøvariablene før bruk.'
    }
    if (!isChatApiConfigured) {
      return 'Oppdater VITE_CHAT_API_URL til din Cloud Run chat-endepunkt.'
    }
    return null
  }, [isChatApiConfigured, isClientIdConfigured])

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-section">
          <img 
            src="/Randstad_Digital_Logo_Horizontal_Blue_RGB.png" 
            alt="Randstad Digital" 
            className="brand-logo"
          />
          <div className="brand-text">
            <p className="product">GEMS Agent</p>
            <p className="subtitle">Vertex AI + RAG på Randstad Digital data</p>
          </div>
        </div>
        {isAuthorized && (
          <div className="user-chip">
            {user?.picture && <img src={user.picture} alt={user.name} />}
      <div>
              <span className="user-name">{user?.name}</span>
              <span className="user-email">{user?.email}</span>
      </div>
            <button type="button" className="ghost-button" onClick={handleSignOut}>
              Logg ut
        </button>
          </div>
        )}
      </header>

      {statusBanner && <div className="status-banner">{statusBanner}</div>}

      {!isAuthorized ? (
        <section className="auth-card">
          <h2>Logg inn med Google Workspace</h2>
          <p>Tilgang er begrenset til @randstad.no-kontoer.</p>
          <div ref={loginButtonRef} aria-live="polite" style={{ minHeight: '40px' }} />
          {!isClientIdConfigured && (
            <p className="error">Google Client ID er ikke konfigurert.</p>
          )}
          {isClientIdConfigured && !window.google?.accounts?.id && (
            <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
              Laster Google pålogging...
            </p>
          )}
          {authError && <p className="error">{authError}</p>}
        </section>
      ) : (
        <>
          <section className="chat-panel">
            <div className="messages">
              {messages.length === 0 && (
                <div className="empty-state">
                  <h3>Hei! 👋</h3>
                  <p>Still et spørsmål om GEMS eller last opp kontekst i backenden.</p>
                </div>
              )}
              {messages.map((message) => (
                <article key={message.id} className={`bubble ${message.role}`}>
                  <span className="sender">{message.role === 'user' ? 'Deg' : 'GEMS Agent'}</span>
                  <div className="message-content">
                    {message.role === 'agent' ? (
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                    ) : (
                      <p>{message.text}</p>
                    )}
                  </div>
                </article>
              ))}
              {isLoading && (
                <article className="bubble agent loading">
                  <span className="sender">GEMS Agent</span>
                  <p>Skriver svar …</p>
                </article>
              )}
      </div>
            <form
              className="composer"
              onSubmit={(event) => {
                event.preventDefault()
                sendMessage()
              }}
            >
              <textarea
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Skriv meldingen din…"
                rows={2}
                disabled={isLoading}
              />
              <button type="submit" disabled={isLoading || !inputValue.trim()}>
                {isLoading ? 'Sender…' : 'Send'}
              </button>
            </form>
            {error && <p className="error">{error}</p>}
          </section>
        </>
      )}
    </div>
  )
}

export default App
