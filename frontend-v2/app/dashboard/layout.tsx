'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, 
  PlusCircle, 
  Clock, 
  Book, 
  Settings, 
  Menu, 
  X,
  Sun,
  Moon,
  Laptop
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useTheme } from 'next-themes'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // After mounting, we have access to the theme
  useEffect(() => {
    setMounted(true)
  }, [])

  const routes = [
    {
      href: '/dashboard',
      label: 'Dashboard',
      icon: <Home className="h-5 w-5" />,
      active: pathname === '/dashboard',
    },
    {
      href: '/dashboard/new-translation',
      label: 'New Translation',
      icon: <PlusCircle className="h-5 w-5" />,
      active: pathname === '/dashboard/new-translation',
    },
    {
      href: '/dashboard/history',
      label: 'History',
      icon: <Clock className="h-5 w-5" />,
      active: pathname === '/dashboard/history',
    },
    {
      href: '/dashboard/glossary',
      label: 'Glossary',
      icon: <Book className="h-5 w-5" />,
      active: pathname === '/dashboard/glossary',
    },
    {
      href: '/dashboard/settings',
      label: 'Settings',
      icon: <Settings className="h-5 w-5" />,
      active: pathname === '/dashboard/settings',
    },
  ]

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
            <Link href="/" className="flex items-center gap-2">
              <span className="text-2xl">🌐</span>
              <h1 className="text-xl font-bold">Turjuman</h1>
            </Link>
          </div>
          <div className="flex items-center gap-2">
            {mounted && (
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setTheme('light')}
                  className={theme === 'light' ? 'bg-accent' : ''}
                >
                  <Sun className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setTheme('dark')}
                  className={theme === 'dark' ? 'bg-accent' : ''}
                >
                  <Moon className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setTheme('system')}
                  className={theme === 'system' ? 'bg-accent' : ''}
                >
                  <Laptop className="h-5 w-5" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>
      <div className="container flex-1 items-start md:grid md:grid-cols-[220px_1fr] md:gap-6 lg:grid-cols-[240px_1fr] lg:gap-10">
        <aside className={`fixed top-16 z-30 -ml-2 hidden h-[calc(100vh-4rem)] w-full shrink-0 overflow-y-auto border-r md:sticky md:block ${isMobileMenuOpen ? 'fixed inset-0 z-40 block bg-background/80 backdrop-blur-sm' : 'hidden md:block'}`}>
          <div className="py-6 pr-6 lg:py-8">
            <nav className="flex flex-col gap-2">
              {routes.map((route) => (
                <Link
                  key={route.href}
                  href={route.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Button
                    variant={route.active ? 'secondary' : 'ghost'}
                    className="w-full justify-start gap-2"
                  >
                    {route.icon}
                    {route.label}
                  </Button>
                </Link>
              ))}
            </nav>
          </div>
        </aside>
        <main className="flex w-full flex-col overflow-hidden py-6">
          {children}
        </main>
      </div>
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Turjuman - LLM Powered Books & Long Text Translator
          </p>
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            <a 
              href="https://github.com/abdallah-ali-abdallah/turjuman-book-translator" 
              target="_blank" 
              rel="noreferrer"
              className="font-medium underline underline-offset-4"
            >
              GitHub Repository
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}
