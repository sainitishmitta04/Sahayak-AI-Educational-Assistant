import Link from 'next/link';
import { AuthCard } from '@/components/auth/AuthCard';
import { LoginForm } from '@/components/auth/LoginForm';
import { Button } from '@/components/ui/button';

export default function LoginPage() {
  return (
    <AuthCard
      title="Login to Shayaka"
      description="Enter your credentials to access your account."
      footerContent={
        <p className="text-sm text-muted-foreground">
          Don&apos;t have an account?{' '}
          <Button variant="link" asChild className="p-0 h-auto text-primary">
             <Link href="/signup">Sign up</Link>
          </Button>
        </p>
      }
    >
      <LoginForm />
    </AuthCard>
  );
}
