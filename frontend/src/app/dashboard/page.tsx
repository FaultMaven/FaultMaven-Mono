// src/app/dashboard/page.tsx
'use client'; // Need hooks, so this must be a Client Component

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext'; // Import useAuth
import { DashboardLayout } from "@/components/DashboardLayout";
import { ChatInterface } from "@/components/ChatInterface";
import { DataInputArea } from "@/components/DataInputArea";
import { Loader2 } from 'lucide-react'; // Example loader

export default function DashboardPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If finished loading auth state and user is not authenticated, redirect
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Only render dashboard if authenticated
  if (isAuthenticated) {
     return (
        <DashboardLayout>
          <div className="flex flex-col h-full">
            {/* ... rest of dashboard content from previous step ... */}
             <h1 className="text-2xl font-semibold mb-4 flex-shrink-0">Dashboard</h1>
             <div className="flex-grow overflow-y-auto mb-4 border rounded p-2 bg-muted/40">
               Chat History Area (Placeholder)
             </div>
             <div className="flex-shrink-0">
                <ChatInterface />
             </div>
             <div className="flex-shrink-0 mt-4">
                <DataInputArea />
             </div>
          </div>
        </DashboardLayout>
     );
  }

  // Return null or redirecting state if not authenticated (should be caught by useEffect)
  return null;
}
