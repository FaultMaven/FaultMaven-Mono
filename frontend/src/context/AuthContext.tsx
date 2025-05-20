// src/context/AuthContext.tsx
'use client'; // Context Providers using hooks need to be Client Components

import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

// Define the shape of the context data
interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean; // To handle initial token check
  login: (newToken: string) => void;
  logout: () => void;
}

// Create the context with default values
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Define the Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Start loading initially

  useEffect(() => {
    // Check for token in localStorage on initial load
    try {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        // TODO: Optionally add token validation logic here (e.g., check expiry, call backend /me)
        setToken(storedToken);
      }
    } catch (error) {
      console.error("Failed to access localStorage:", error);
      // Handle cases where localStorage is disabled or inaccessible
    } finally {
      setIsLoading(false); // Finished initial check
    }
  }, []); // Empty dependency array ensures this runs only once on mount

  const login = (newToken: string) => {
    setToken(newToken);
    try {
      localStorage.setItem('authToken', newToken); // Store token
    } catch (error) {
       console.error("Failed to set token in localStorage:", error);
    }
    console.log("Auth Context: User logged in");
  };

  const logout = () => {
    setToken(null);
    try {
      localStorage.removeItem('authToken'); // Remove token
    } catch (error) {
        console.error("Failed to remove token from localStorage:", error);
    }
    console.log("Auth Context: User logged out");
    // TODO: Redirect to login page or homepage
    // Example: window.location.href = '/login'; (Simple redirect)
  };

  // Derive isAuthenticated from token state
  const isAuthenticated = !!token;

  const value = {
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook for easy context consumption
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
