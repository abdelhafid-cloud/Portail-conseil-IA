import Link from 'next/link'

const services = [
  {
    title: 'Stratégie IA',
    description: 'Adoption, gouvernance et feuilles de route pour les équipes dirigeantes.',
  },
  {
    title: 'Agents IA',
    description: 'Copilotes, qualification et automatisation des workflows métier.',
  },
  {
    title: 'Systèmes RAG',
    description: 'Recherche documentaire et assistants contextuels sur vos données.',
  },
  {
    title: 'Automatisation',
    description: 'Processus ventes, support et onboarding sans friction manuelle.',
  },
]

const steps = [
  {
    step: '01',
    title: 'Conversation naturelle',
    description: 'Le visiteur échange avec un consultant IA vocal ou texte, sans formulaire long.',
  },
  {
    step: '02',
    title: 'Qualification intelligente',
    description: 'L\'IA analyse le besoin, le budget et le contexte pour scorer l\'opportunité.',
  },
  {
    step: '03',
    title: 'Action immédiate',
    description: 'Recommandation de services, prise de rendez-vous et onboarding automatisé.',
  },
]

const platformFeatures = [
  'Consultant IA vocal et texte, disponible 24/7',
  'Mémoire des conversations et contexte métier',
  'Intégrations calendrier, e-mail et messagerie',
  'Scoring des leads et génération de propositions',
]

const stats = [
  { value: '93', label: 'Score lead moyen' },
  { value: '< 2 min', label: 'Prise de rendez-vous' },
  { value: '24/7', label: 'Disponibilité du consultant' },
]

const testimonials = [
  {
    quote: 'On a l\'impression de parler à un consultant senior qui comprend déjà notre contexte.',
    author: 'COO, groupe logistique',
  },
  {
    quote: 'Les conversations entrantes deviennent des opportunités qualifiées, sans friction.',
    author: 'Head of Growth, SaaS B2B',
  },
]

const faqs = [
  {
    question: 'Faut-il remplir un long formulaire ?',
    answer: 'Non. La qualification se fait naturellement par la conversation avec le consultant IA.',
  },
  {
    question: 'L\'IA se souvient-elle des échanges précédents ?',
    answer: 'Oui. Historique, résumés et contexte métier sont conservés entre les sessions.',
  },
  {
    question: 'Peut-on connecter Google Calendar ou WhatsApp ?',
    answer: 'Oui. La plateforme est conçue pour orchestrer rendez-vous et notifications.',
  },
]

export function LandingPage() {
  return (
    <div className="pb-20">
      <header className="section-shell flex items-center justify-between py-6">
        <span className="text-lg font-semibold text-brand">Aether AI Consulting</span>
        <nav className="hidden items-center gap-6 text-sm text-brand-muted md:flex">
          <a href="#expertises" className="transition hover:text-brand">Expertises</a>
          <a href="#fonctionnement" className="transition hover:text-brand">Fonctionnement</a>
          <a href="#plateforme" className="transition hover:text-brand">Plateforme</a>
          <a href="#resultats" className="transition hover:text-brand">Résultats</a>
          <a href="#contact" className="transition hover:text-brand">Contact</a>
        </nav>
        <Link href="/login" className="btn-primary">
          Connexion
        </Link>
      </header>

      {/* Section 1 — Hero */}
      <section id="hero" className="section-shell py-12 sm:py-16">
        <div className="mx-auto max-w-2xl text-center">
          <p className="section-label mb-4">Conseil IA pour l&apos;entreprise</p>
          <h1 className="text-balance text-4xl font-bold tracking-tight text-brand sm:text-5xl">
            Chaque visiteur devient une conversation qualifiée
          </h1>
          <p className="mt-5 text-lg leading-relaxed text-brand-muted">
            Un consultant IA vocal qualifie vos prospects, recommande des services et oriente vers la prise de rendez-vous — sans formulaires longs.
          </p>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <Link href="/login" className="btn-primary px-6 py-3">
              Démarrer
            </Link>
            <a href="#contact" className="btn-secondary px-6 py-3">
              Nous contacter
            </a>
          </div>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-3">
          {stats.map((item) => (
            <div key={item.label} className="card text-center">
              <p className="text-3xl font-bold text-brand">{item.value}</p>
              <p className="mt-1 text-sm text-brand-muted">{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Section 2 — Expertises */}
      <section id="expertises" className="section-shell py-14">
        <div className="mb-8 text-center">
          <p className="section-label">Expertises</p>
          <h2 className="mt-3 text-2xl font-semibold text-brand sm:text-3xl">Ce que nous déployons</h2>
          <p className="mx-auto mt-3 max-w-xl text-brand-muted">
            De la stratégie à l&apos;exécution, une offre complète pour structurer votre transformation IA.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {services.map((service) => (
            <article key={service.title} className="card">
              <h3 className="text-lg font-semibold text-brand">{service.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-brand-muted">{service.description}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Section 3 — Fonctionnement */}
      <section id="fonctionnement" className="section-shell py-14">
        <div className="mb-8 text-center">
          <p className="section-label">Fonctionnement</p>
          <h2 className="mt-3 text-2xl font-semibold text-brand sm:text-3xl">Trois étapes, zéro friction</h2>
          <p className="mx-auto mt-3 max-w-xl text-brand-muted">
            Du premier message à la prise de rendez-vous, tout est guidé par le consultant IA.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {steps.map((item) => (
            <article key={item.step} className="card">
              <span className="text-sm font-bold text-brand-accent">{item.step}</span>
              <h3 className="mt-2 text-lg font-semibold text-brand">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-brand-muted">{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Section 4 — Plateforme */}
      <section id="plateforme" className="section-shell py-14">
        <div className="grid items-center gap-8 lg:grid-cols-2">
          <div>
            <p className="section-label">Plateforme</p>
            <h2 className="mt-3 text-2xl font-semibold text-brand sm:text-3xl">
              Un socle IA pour conseiller, qualifier et livrer
            </h2>
            <p className="mt-4 leading-relaxed text-brand-muted">
              Aether centralise les conversations, la mémoire métier et les workflows pour que chaque échange produise une action concrète : qualification, planification ou escalade vers un expert humain.
            </p>
            <Link href="/login" className="btn-primary mt-6">
              Explorer le portail
            </Link>
          </div>
          <ul className="space-y-3">
            {platformFeatures.map((feature) => (
              <li
                key={feature}
                className="card flex items-start gap-3 py-4"
              >
                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-accent" />
                <span className="text-sm leading-relaxed text-brand">{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Section 5 — Résultats, FAQ & Contact */}
      <section id="resultats" className="section-shell py-14">
        <div className="mb-8 text-center">
          <p className="section-label">Résultats</p>
          <h2 className="mt-3 text-2xl font-semibold text-brand sm:text-3xl">Ils nous font confiance</h2>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {testimonials.map((item) => (
            <blockquote key={item.author} className="card">
              <p className="leading-relaxed text-brand">&ldquo;{item.quote}&rdquo;</p>
              <footer className="mt-4 text-sm text-brand-muted">— {item.author}</footer>
            </blockquote>
          ))}
        </div>

        <div id="contact" className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="card">
            <p className="section-label">Contact</p>
            <h3 className="mt-3 text-xl font-semibold text-brand">Prêt à échanger ?</h3>
            <p className="mt-3 text-sm leading-relaxed text-brand-muted">
              Connectez-vous au portail ou écrivez-nous pour lancer une consultation.
            </p>
            <div className="mt-6 flex flex-col gap-2 sm:flex-row">
              <Link href="/login" className="btn-primary">
                Accéder au portail
              </Link>
              <a href="mailto:hello@aether-consulting.ai" className="btn-secondary">
                hello@aether-consulting.ai
              </a>
            </div>
          </div>

          <div className="card">
            <p className="section-label">FAQ</p>
            <div className="mt-4 space-y-3">
              {faqs.map((item) => (
                <details
                  key={item.question}
                  className="rounded-xl border border-brand-accent/25 bg-brand-surface px-4 py-3"
                >
                  <summary className="cursor-pointer text-sm font-semibold text-brand">
                    {item.question}
                  </summary>
                  <p className="mt-2 text-sm leading-relaxed text-brand-muted">{item.answer}</p>
                </details>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
