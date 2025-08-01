import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/icons/Logo';

export default function Home() {
  return (
    <div className="flex flex-col min-h-dvh bg-background">
      <header className="px-4 lg:px-6 h-14 flex items-center">
        <Link href="/" className="flex items-center justify-center gap-2" prefetch={false}>
          <Logo className="h-6 w-6 text-primary" />
          <span className="font-bold font-headline text-lg">Shayaka Connect</span>
        </Link>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-[1fr] lg:gap-12">
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-4 text-center">
                  <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none font-headline text-primary">
                    Welcome to Shayaka Connect
                  </h1>
                  <p className="max-w-[600px] text-foreground/80 md:text-xl mx-auto">
                    Connecting students and teachers for a seamless learning experience. Join our community and unlock your potential.
                  </p>
                </div>
                <div className="flex flex-col gap-2 min-[400px]:flex-row justify-center">
                  <Button asChild size="lg" className="bg-accent text-accent-foreground hover:bg-accent/90">
                    <Link href="/signup">
                      Get Started
                    </Link>
                  </Button>
                  <Button asChild variant="secondary" size="lg">
                    <Link href="/login">
                      Login
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="flex items-center justify-center p-4">
        <p className="text-xs text-muted-foreground">&copy; 2024 Shayaka Connect. All rights reserved.</p>
      </footer>
    </div>
  );
}
