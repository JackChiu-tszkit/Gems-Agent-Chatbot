interface CredentialResponse {
  credential: string
  select_by?: string
  clientId?: string
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (options: {
            client_id: string
            callback: (response: CredentialResponse) => void
            auto_select?: boolean
          }) => void
          renderButton: (
            parent: HTMLElement,
            options: google.accounts.id.GsiButtonConfiguration,
          ) => void
          prompt: () => void
          revoke: (hint: string, callback: () => void) => void
        }
      }
    }
  }
}

export {}

