import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌐</span>
            <h1 className="text-xl font-bold">Turjuman</h1>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="outline">Dashboard</Button>
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <section className="space-y-6 pb-8 pt-6 md:pb-12 md:pt-10 lg:py-32">
          <div className="container flex max-w-[64rem] flex-col items-center gap-4 text-center">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
              Turjuman - LLM Powered Books & Long Text Translator
            </h1>
            <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
              Translate books and long documents using LLMs while preserving the original meaning and style.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/dashboard/new-translation">
                <Button size="lg">Start Translating</Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline" size="lg">Dashboard</Button>
              </Link>
            </div>
          </div>
        </section>
        <section className="container space-y-6 py-8 md:py-12 lg:py-24">
          <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center">
            <h2 className="text-3xl font-bold leading-[1.1] sm:text-3xl md:text-5xl">
              Features
            </h2>
            <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
              Turjuman offers a comprehensive set of features for translating books and long documents.
            </p>
          </div>
          <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-3">
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="font-bold">Deep Translation Mode</h3>
                  <p className="text-sm text-muted-foreground">
                    Comprehensive workflow with terminology unification, critique, and revision steps for higher quality and consistency.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="font-bold">Quick Translation Mode</h3>
                  <p className="text-sm text-muted-foreground">
                    Streamlined workflow that bypasses terminology unification, critique, and revision steps for faster processing.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="font-bold">Smart Chunking</h3>
                  <p className="text-sm text-muted-foreground">
                    Intelligently identifies and preserves special elements like code blocks, images, URLs, and footnotes.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="font-bold">Glossary Management</h3>
                  <p className="text-sm text-muted-foreground">
                    Create and manage custom glossaries to ensure consistent terminology throughout your translations.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="font-bold">Multiple LLM Providers</h3>
                  <p className="text-sm text-muted-foreground">
                    Support for various LLM providers including OpenAI, Anthropic, Google, and local models via Ollama.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-6">
              <div className="flex h-[180px] flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="font-bold">Job History</h3>
                  <p className="text-sm text-muted-foreground">
                    Track all translation jobs with detailed status information and download completed translations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
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
