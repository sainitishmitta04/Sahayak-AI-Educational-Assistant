import type { ReactNode } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Logo } from '@/components/icons/Logo';
import Link from 'next/link';

type AuthCardProps = {
  title: string;
  description: string;
  children: ReactNode;
  footerContent: ReactNode;
};

export function AuthCard({ title, description, children, footerContent }: AuthCardProps) {
  return (
    <div className="flex items-center justify-center min-h-dvh bg-background p-4">
      <Card className="w-full max-w-sm border-2 shadow-lg">
        <CardHeader className="text-center">
          <Link href="/" className="inline-block mx-auto mb-4" aria-label="Back to home">
            <Logo className="h-12 w-12 text-primary" />
          </Link>
          <CardTitle className="font-headline text-2xl">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          {children}
        </CardContent>
        <CardFooter className="text-center block">
          {footerContent}
        </CardFooter>
      </Card>
    </div>
  );
}
