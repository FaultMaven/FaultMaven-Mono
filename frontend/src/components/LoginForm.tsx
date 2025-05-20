// src/components/LoginForm.tsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation'; // Import for redirection
import { Button } from "@/components/ui/button";
import {
  Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { loginUser } from '@/lib/auth';
import { useAuth } from '@/context/AuthContext'; // <-- Import useAuth hook
import { Loader2 } from "lucide-react";

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth(); // <-- Get login function from context
  const router = useRouter(); // <-- Hook for redirection

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await loginUser(email, password);
      console.log('Login successful:', result);

      // --- Use context to update auth state ---
      login(result.access_token);
      // --- Redirect to dashboard ---
      router.push('/dashboard');

    } catch (err) {
      console.error('Login failed:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during login.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl">Login</CardTitle>
        <CardDescription>
          Enter your email below to login to your account
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="grid gap-4">
          {error && (
            <div className="p-3 bg-destructive/15 border border-destructive/30 rounded-md">
               <p className="text-sm font-medium text-destructive">{error}</p>
            </div>
          )}
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email" type="email" placeholder="m@example.com" required
              value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password" type="password" placeholder="••••••••" required
              value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading}
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>
        </CardFooter>
      </form>
       <CardFooter className="flex justify-center">
          <p className="mt-2 text-center text-sm text-muted-foreground">
              (Test: test@example.com / password)
          </p>
       </CardFooter>
    </Card>
  );
}
