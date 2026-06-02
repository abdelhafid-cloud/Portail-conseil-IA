'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  checkHealth,
  consultantRespond,
  getApiBaseUrl,
  loginUser,
  registerUser,
} from '@/lib/api'

type TestResult = {
  name: string
  ok: boolean
  detail: string
}

export default function TestApiPage() {
  const [results, setResults] = useState<TestResult[]>([])
  const [running, setRunning] = useState(false)

  const runTests = async () => {
    setRunning(true)
    const next: TestResult[] = []

    try {
      const health = await checkHealth()
      next.push({
        name: 'Health check',
        ok: health.status === 'ok',
        detail: JSON.stringify(health),
      })
    } catch (error) {
      next.push({
        name: 'Health check',
        ok: false,
        detail: error instanceof Error ? error.message : 'Échec',
      })
    }

    try {
      const reply = await consultantRespond('Nous sommes une entreprise logistique avec 200 employés')
      next.push({
        name: 'Consultant IA',
        ok: Boolean(reply.reply),
        detail: reply.reply,
      })
    } catch (error) {
      next.push({
        name: 'Consultant IA',
        ok: false,
        detail: error instanceof Error ? error.message : 'Échec',
      })
    }

    const testEmail = `test_${Date.now()}@example.com`
    const password = 'Test1234!'

    try {
      const auth = await registerUser({
        email: testEmail,
        password,
        full_name: 'Test User',
        company_name: 'Test Co',
      })
      next.push({
        name: 'Inscription',
        ok: Boolean(auth.access_token),
        detail: `Utilisateur créé : ${auth.user.email}`,
      })
    } catch (error) {
      next.push({
        name: 'Inscription',
        ok: false,
        detail: error instanceof Error ? error.message : 'Échec',
      })
    }

    try {
      const auth = await loginUser(testEmail, password)
      next.push({
        name: 'Connexion',
        ok: Boolean(auth.access_token),
        detail: `Connecté : ${auth.user.full_name}`,
      })
    } catch (error) {
      next.push({
        name: 'Connexion',
        ok: false,
        detail: error instanceof Error ? error.message : 'Échec (normal si inscription échouée)',
      })
    }

    setResults(next)
    setRunning(false)
  }

  const allOk = results.length > 0 && results.every((r) => r.ok)

  return (
    <main className="section-shell min-h-screen py-12">
      <Link href="/" className="text-sm text-brand-muted hover:text-brand">
        ← Accueil
      </Link>

      <h1 className="mt-6 text-3xl font-bold text-brand">Test du backend</h1>
      <p className="mt-2 text-brand-muted">
        API : <code className="text-brand">{getApiBaseUrl()}</code>
      </p>

      <button
        type="button"
        onClick={() => void runTests()}
        disabled={running}
        className="btn-primary mt-6 disabled:opacity-50"
      >
        {running ? 'Tests en cours…' : 'Lancer les tests'}
      </button>

      {results.length > 0 && (
        <div className="mt-8 space-y-3">
          <p className={`font-semibold ${allOk ? 'text-brand' : 'text-red-700'}`}>
            {allOk ? 'Tous les tests ont réussi' : 'Certains tests ont échoué'}
          </p>
          {results.map((result) => (
            <div key={result.name} className="card">
              <div className="flex items-center justify-between gap-4">
                <h2 className="font-semibold text-brand">{result.name}</h2>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    result.ok ? 'bg-brand-pale text-brand' : 'bg-red-100 text-red-700'
                  }`}
                >
                  {result.ok ? 'OK' : 'Échec'}
                </span>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-brand-muted">{result.detail}</p>
            </div>
          ))}
        </div>
      )}

      <div className="card mt-8">
        <p className="section-label">Démarrer le backend</p>
        <pre className="mt-3 overflow-x-auto rounded-xl bg-brand-surface p-4 text-xs text-brand">
{`cd services/backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py`}
        </pre>
      </div>
    </main>
  )
}
