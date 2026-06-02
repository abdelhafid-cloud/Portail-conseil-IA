'use client'

import { useMemo, useState } from 'react'
import { consultantRespond } from '@/lib/api'

const quickPrompts = [
  'Entreprise logistique',
  'Base de connaissances',
  'Qualifier un lead',
]

const starterMessages = [
  {
    role: 'assistant',
    content: 'Bonjour. Parlez-moi de votre entreprise, de votre principal défi et du résultat attendu.',
  },
]

export function FloatingConsultant() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState(starterMessages)
  const [draft, setDraft] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  const lastMessage = useMemo(() => messages[messages.length - 1], [messages])

  const sendMessage = async (content: string) => {
    const text = content.trim()
    if (!text || isLoading) return

    setApiError(null)
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setDraft('')
    setIsLoading(true)

    try {
      const data = await consultantRespond(text)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setApiError('Backend indisponible. Démarrez le serveur sur le port 9000.')
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: "Je n'arrive pas à joindre le serveur. Vérifiez que le backend tourne (python main.py).",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const startVoiceCapture = () => {
    setIsListening(true)
    window.setTimeout(() => {
      setIsListening(false)
      void sendMessage('Nous souhaitons automatiser le support et la qualification commerciale.')
    }, 1200)
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-3">
      {isOpen && (
        <aside className="w-[min(100vw-2rem,340px)]">
          <div className="card p-4 shadow-lg">
            <div className="mb-3 flex items-center justify-between gap-2">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-brand-muted">
                  Consultant IA
                </p>
                <p className="text-sm text-brand">{isLoading ? 'Réflexion…' : 'Connecté API'}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-brand-pale px-2.5 py-1 text-xs font-medium text-brand">
                  En ligne
                </span>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="flex h-8 w-8 items-center justify-center rounded-full border border-brand-accent/30 text-brand-muted transition hover:bg-brand-pale hover:text-brand"
                  aria-label="Fermer le consultant IA"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="space-y-3 rounded-xl border border-brand-accent/25 bg-brand-surface p-3">
              {apiError && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                  {apiError}
                </p>
              )}

              <div className="max-h-56 space-y-2 overflow-y-auto">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`max-w-[90%] rounded-xl px-3 py-2 text-sm leading-relaxed ${
                      message.role === 'assistant'
                        ? 'border border-brand-accent/30 bg-white text-brand'
                        : 'ml-auto bg-brand text-white'
                    }`}
                  >
                    {message.content}
                  </div>
                ))}
              </div>

              <p className="line-clamp-2 text-xs text-brand-muted">{lastMessage?.content}</p>

              <div className="flex flex-wrap gap-1.5">
                {quickPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    disabled={isLoading}
                    onClick={() => void sendMessage(prompt)}
                    className="rounded-lg border border-brand-accent/30 bg-white px-2 py-1 text-xs text-brand transition hover:bg-brand-pale disabled:opacity-50"
                  >
                    {prompt}
                  </button>
                ))}
              </div>

              <div className="flex gap-2">
                <input
                  value={draft}
                  disabled={isLoading}
                  onChange={(event) => setDraft(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') void sendMessage(draft)
                  }}
                  placeholder="Votre message..."
                  className="min-w-0 flex-1 rounded-lg border border-brand-accent/30 bg-white px-3 py-2 text-sm text-brand outline-none placeholder:text-brand-light focus:border-brand disabled:opacity-50"
                />
                <button
                  type="button"
                  disabled={isLoading}
                  onClick={() => void sendMessage(draft)}
                  className="btn-primary shrink-0 px-3 disabled:opacity-50"
                >
                  {isLoading ? '…' : 'Envoyer'}
                </button>
              </div>

              <button
                type="button"
                disabled={isLoading}
                onClick={startVoiceCapture}
                className={`w-full rounded-lg border px-3 py-2 text-sm font-medium transition disabled:opacity-50 ${
                  isListening
                    ? 'border-brand bg-brand-pale text-brand'
                    : 'border-brand-accent/30 bg-white text-brand hover:bg-brand-pale'
                }`}
              >
                {isListening ? 'Écoute en cours…' : 'Démarrer la voix'}
              </button>
            </div>
          </div>
        </aside>
      )}

      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="btn-primary flex items-center gap-2 px-5 py-3 shadow-lg"
        aria-expanded={isOpen}
        aria-label={isOpen ? 'Fermer le consultant IA' : 'Ouvrir le consultant IA'}
      >
        {isOpen ? 'Fermer' : 'Consultant IA'}
      </button>
    </div>
  )
}
