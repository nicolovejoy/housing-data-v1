import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'HUD Fair Market Rent Explorer',
  description: 'Interactive exploration of HUD Fair Market Rent data',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">
        <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <h1 className="text-3xl font-bold">HUD Fair Market Rent Explorer</h1>
            <p className="text-blue-100 text-sm mt-1">
              Interactive exploration of rental market data across the United States
            </p>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
