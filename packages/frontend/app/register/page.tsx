'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FormEvent, useState } from 'react'
import { registerUser } from '@/lib/api'
import { saveSession } from '@/lib/auth'

export default function RegisterPage() {
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const session = await registerUser({
        email: email.trim(),
        password,
        full_name: fullName.trim(),
        company_name: companyName.trim() || undefined,
      })
      saveSession(session)
      router.push('/portal')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Inscription impossible')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="section-shell flex min-h-screen items-center py-12">
      <div className="mx-auto grid w-full max-w-4xl gap-8 lg:grid-cols-2">
        <section className="space-y-4">
          <p className="section-label">Inscription</p>
          <h1 className="text-3xl font-bold text-brand sm:text-4xl">
            Rejoindre la plateforme
          </h1>
          <p className="text-brand-muted leading-relaxed">
            Créez votre compte pour accéder au portail conseil IA et à l&apos;historique de vos conversations.
          </p>
        </section>

        <section className="card">
          <h2 className="text-xl font-semibold text-brand">Créer un compte</h2>
          <form className="mt-6 space-y-4" onSubmit={(event) => void handleSubmit(event)}>
            {error && (
              <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </p>
            )}
            <label className="block">
              <span className="mb-1.5 block text-sm text-brand-muted">Nom complet</span>
              <input
                type="text"
                required
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="w-full rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
                placeholder="Jean Dupont"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm text-brand-muted">Entreprise (optionnel)</span>
              <input
                type="text"
                value={companyName}
                onChange={(event) => setCompanyName(event.target.value)}
                className="w-full rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
                placeholder="Ma Société"
              />
            </label>
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
                minLength={8}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
                placeholder="••••••••"
              />
            </label>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3 disabled:opacity-50">
              {loading ? 'Création…' : 'Créer mon compte'}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-brand-muted">
            Déjà inscrit ?{' '}
            <Link href="/login" className="font-medium text-brand hover:underline">
              Se connecter
            </Link>
          </p>
        </section>
      </div>
    </main>
  )
}
