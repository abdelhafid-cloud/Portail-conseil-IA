'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FormEvent, useState } from 'react'
import { loginUser } from '@/lib/api'
import { saveSession } from '@/lib/auth'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const session = await loginUser(email.trim(), password)
      saveSession(session)
      router.push('/portal')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connexion impossible')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="section-shell flex min-h-screen items-center py-12">
      <div className="mx-auto grid w-full max-w-4xl gap-8 lg:grid-cols-2">
        <section className="space-y-4">
          <p className="section-label">Authentification</p>
          <h1 className="text-3xl font-bold text-brand sm:text-4xl">
            Espace conseil IA
          </h1>
          <p className="text-brand-muted leading-relaxed">
            Connectez-vous pour reprendre vos conversations, accéder à l&apos;historique et aux outils du portail.
          </p>
        </section>

        <section className="card">
          <h2 className="text-xl font-semibold text-brand">Connexion</h2>
          <form className="mt-6 space-y-4" onSubmit={(event) => void handleSubmit(event)}>
            {error && (
              <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </p>
            )}
            <label className="block">
              <span className="mb-1.5 block text-sm text-brand-muted">E-mail</span>
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
                placeholder="nom@entreprise.com"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm text-brand-muted">Mot de passe</span>
              <input
                type="password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
                placeholder="••••••••"
              />
            </label>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3 disabled:opacity-50">
              {loading ? 'Connexion…' : 'Continuer'}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-brand-muted">
            Pas encore de compte ?{' '}
            <Link href="/register" className="font-medium text-brand hover:underline">
              Créer un compte
            </Link>
          </p>
          <div className="mt-4 flex justify-between text-sm text-brand-muted">
            <Link href="/" className="hover:text-brand">
              Accueil
            </Link>
            <Link href="/portal" className="hover:text-brand">
              Portail
            </Link>
          </div>
        </section>
      </div>
    </main>
  )
}
