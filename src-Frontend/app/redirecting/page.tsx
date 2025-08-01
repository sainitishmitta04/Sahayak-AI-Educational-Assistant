'use client';

import { useEffect } from 'react';
import { Loader2 } from 'lucide-react';

// IMPORTANT: Change this URL to your actual Shayaka website address.
const REDIRECT_URL = 'https://sahayakrelu-157046984477.us-central1.run.app/';

export default function RedirectingPage() {
  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.href = REDIRECT_URL;
    }, 2000); // 2-second delay

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-dvh bg-background">
      <div className="flex flex-col items-center space-y-4 text-center p-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <h1 className="text-2xl font-semibold font-headline text-foreground">
          Connecting to Shayaka...
        </h1>
        
        <p className="text-muted-foreground">
          You are being redirected. Please wait a moment.
        </p>
      </div>
    </div>
  );
}
