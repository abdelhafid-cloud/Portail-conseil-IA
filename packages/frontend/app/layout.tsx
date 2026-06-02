import { Manrope } from 'next/font/google'
import './globals.css'

const manrope = Manrope({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-manrope',
})

export const metadata = {
  title: 'Aether AI Consulting',
  description: 'Plateforme de conseil IA : consultant vocal, qualification et automatisation.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className={`${manrope.variable} antialiased`}>{children}</body>
    </html>
  )
}
