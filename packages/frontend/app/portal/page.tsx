'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FormEvent, useEffect, useState } from 'react'
import { createAppointment, createLead, listAppointments, type Appointment } from '@/lib/api'
import { clearSession, getSession, type AuthSession } from '@/lib/auth'

const metrics = [
  ['Score lead', '93'],
  ['Probabilité', '87 %'],
  ['Priorité', 'Haute'],
  ['Valeur estimée', '20–50 k€'],
]

const modules = [
  'Consultant IA',
  'Intelligence lead',
  'Base de connaissances',
  'Rendez-vous',
  'Propositions',
  'Analytique',
]

function defaultAppointmentDate(): string {
  const date = new Date()
  date.setDate(date.getDate() + 2)
  date.setHours(10, 0, 0, 0)
  const offset = date.getTimezoneOffset()
  const local = new Date(date.getTime() - offset * 60_000)
  return local.toISOString().slice(0, 16)
}

function formatAppointmentDate(iso: string): string {
  return new Date(iso).toLocaleString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function PortalPage() {
  const router = useRouter()
  const [session, setSession] = useState<AuthSession | null>(null)
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [scheduledAt, setScheduledAt] = useState(defaultAppointmentDate)
  const [phone, setPhone] = useState('')
  const [notes, setNotes] = useState('')
  const [booking, setBooking] = useState(false)
  const [bookingError, setBookingError] = useState<string | null>(null)
  const [bookingSuccess, setBookingSuccess] = useState<string | null>(null)

  const loadAppointments = async (accessToken: string) => {
    try {
      const data = await listAppointments(accessToken)
      setAppointments(data.items)
    } catch {
      setAppointments([])
    }
  }

  useEffect(() => {
    const current = getSession()
    if (!current) {
      router.replace('/login')
      return
    }
    setSession(current)
    void loadAppointments(current.access_token)
  }, [router])

  const handleLogout = () => {
    clearSession()
    router.push('/login')
  }

  const handleBookAppointment = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!session) return

    setBookingError(null)
    setBookingSuccess(null)
    setBooking(true)

    try {
      const { lead } = await createLead(
        {
          full_name: session.user.full_name,
          email: session.user.email,
          phone: phone.trim(),
          company_name: session.user.company_name ?? 'Non renseignée',
          business_goals: 'Session conseil IA depuis le portail',
          source: 'portal',
        },
        session.access_token,
      )

      const { appointment } = await createAppointment(
        {
          lead_id: lead.id,
          scheduled_at: new Date(scheduledAt).toISOString(),
          duration_minutes: 30,
          notes: notes.trim() || undefined,
        },
        session.access_token,
      )

      setBookingSuccess(
        `Rendez-vous confirmé pour le ${formatAppointmentDate(appointment.scheduled_at)}. Vous recevrez une confirmation par e-mail ou WhatsApp.`,
      )
      setNotes('')
      await loadAppointments(session.access_token)
    } catch (err) {
      setBookingError(err instanceof Error ? err.message : 'Impossible de réserver le rendez-vous')
    } finally {
      setBooking(false)
    }
  }

  if (!session) {
    return (
      <main className="section-shell flex min-h-screen items-center justify-center py-10">
        <p className="text-brand-muted">Chargement…</p>
      </main>
    )
  }

  return (
    <main className="section-shell min-h-screen py-10">
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-label">Espace connecté</p>
          <h1 className="mt-2 text-3xl font-bold text-brand sm:text-4xl">Portail conseil IA</h1>
          <p className="mt-3 max-w-2xl text-brand-muted">
            Bienvenue, {session.user.full_name}. Contexte mémorisé, qualification des leads et suivi jusqu&apos;à la livraison.
          </p>
        </div>
        <button type="button" onClick={handleLogout} className="btn-secondary px-4 py-2 text-sm">
          Déconnexion
        </button>
      </div>

      <div className="card mb-6">
        <p className="text-sm text-brand-muted">Compte connecté</p>
        <p className="mt-1 font-medium text-brand">{session.user.email}</p>
        {session.user.company_name && (
          <p className="mt-1 text-sm text-brand-muted">{session.user.company_name}</p>
        )}
      </div>

      <section className="card mb-6">
        <p className="section-label">Rendez-vous</p>
        <h2 className="mt-2 text-xl font-semibold text-brand">Prendre un rendez-vous</h2>
        <p className="mt-2 text-sm text-brand-muted">
          Choisissez une date et une heure pour une session conseil de 30 minutes avec notre équipe.
        </p>

        <form className="mt-6 space-y-4" onSubmit={(event) => void handleBookAppointment(event)}>
          {bookingError && (
            <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {bookingError}
            </p>
          )}
          {bookingSuccess && (
            <p className="rounded-xl border border-brand-accent/30 bg-brand-pale px-4 py-3 text-sm text-brand">
              {bookingSuccess}
            </p>
          )}

          <label className="block">
            <span className="mb-1.5 block text-sm text-brand-muted">Numéro WhatsApp</span>
            <input
              type="tel"
              required
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
              className="w-full max-w-md rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
              placeholder="+212600000000"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block text-sm text-brand-muted">Date et heure</span>
            <input
              type="datetime-local"
              required
              value={scheduledAt}
              onChange={(event) => setScheduledAt(event.target.value)}
              className="w-full max-w-md rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block text-sm text-brand-muted">Notes (optionnel)</span>
            <textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              rows={3}
              placeholder="Sujet de la session, contexte métier…"
              className="w-full rounded-xl border border-brand-accent/30 bg-brand-surface px-4 py-2.5 text-brand outline-none focus:border-brand"
            />
          </label>

          <button type="submit" disabled={booking} className="btn-primary px-6 py-3 disabled:opacity-50">
            {booking ? 'Réservation…' : 'Confirmer le rendez-vous'}
          </button>
        </form>

        {appointments.length > 0 && (
          <div className="mt-8 border-t border-brand-accent/20 pt-6">
            <h3 className="font-semibold text-brand">Vos rendez-vous</h3>
            <ul className="mt-4 space-y-3">
              {appointments.map((appointment) => (
                <li
                  key={appointment.id}
                  className="rounded-xl border border-brand-accent/25 bg-brand-surface p-4"
                >
                  <p className="font-medium text-brand">{formatAppointmentDate(appointment.scheduled_at)}</p>
                  <p className="mt-1 text-sm text-brand-muted">
                    Durée : {appointment.duration_minutes} min · Statut : {appointment.status}
                  </p>
                  {appointment.meeting_url && (
                    <a
                      href={appointment.meeting_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-block text-sm font-medium text-brand hover:underline"
                    >
                      Rejoindre la visio
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map(([label, value]) => (
          <div key={label} className="card">
            <p className="text-sm text-brand-muted">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-brand">{value}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="card">
          <p className="section-label">Consultant IA</p>
          <h2 className="mt-2 text-xl font-semibold text-brand">Conversation en cours</h2>
          <div className="mt-4 space-y-3 rounded-xl border border-brand-accent/25 bg-brand-surface p-4">
            <p className="rounded-lg border border-brand-accent/30 bg-white p-3 text-sm text-brand">
              Lors de notre dernier échange, vous avez mentionné environ 500 tickets support par jour.
            </p>
            <p className="ml-auto max-w-[90%] rounded-lg bg-brand p-3 text-sm text-white">
              Nous voulons réduire le triage manuel et créer un assistant pour le support.
            </p>
            <p className="rounded-lg border border-brand-accent/30 bg-white p-3 text-sm text-brand">
              Je recommande des agents IA, une base RAG et de l&apos;automatisation. Souhaitez-vous un rendez-vous cette semaine ?
            </p>
          </div>
          <Link href="/" className="btn-primary mt-4 inline-block">
            Ouvrir le consultant IA
          </Link>
        </section>

        <section className="card">
          <p className="section-label">Modules</p>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {modules.map((module) => (
              <div
                key={module}
                className="rounded-lg border border-brand-accent/25 bg-brand-surface px-3 py-2 text-sm text-brand"
              >
                {module}
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}
