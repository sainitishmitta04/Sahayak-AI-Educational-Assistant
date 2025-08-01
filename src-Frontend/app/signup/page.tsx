import Link from 'next/link';
import { AuthCard } from '@/components/auth/AuthCard';
import { SignupForm } from '@/components/auth/SignupForm';
import { Button } from '@/components/ui/button';

export default function SignupPage() {
  return (
    <AuthCard
      title="Create an account"
      description="Join Shayaka today to start connecting."
      footerContent={
        <p className="text-sm text-muted-foreground">
          Already have an account?{' '}
           <Button variant="link" asChild className="p-0 h-auto text-primary">
             <Link href="/login">Login</Link>
           </Button>
        </p>
      }
    >
      <SignupForm />
    </AuthCard>
  );
}
