// src/components/Header.tsx
'use client'; // Required for hooks like useAuth and usePathname

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation'; // Import usePathname
import { cn } from '@/lib/utils'; // Import cn utility
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext'; // Import useAuth hook
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle, // Helper for styling links like triggers
} from "@/components/ui/navigation-menu"; // Import NavigationMenu components

export function Header() {
  // Get authentication state and functions from context
  const { isAuthenticated, logout, isLoading } = useAuth();
  // Get current pathname for active link styling
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      {/* Main container uses flex and justify-between */}
      <div className="container flex h-16 items-center justify-between">

        {/* Left Group: Logo and Main Navigation */}
        <div className="flex items-center space-x-6">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <Image
              src="/fm-logo-standard.svg" // Ensure this matches your logo file in /public
              alt="FaultMaven Logo"
              width={32}
              height={32}
              className="object-contain"
              priority // Prioritize loading the logo
            />
            <span className="inline-block font-bold text-lg">FaultMaven</span>
          </Link>

          {/* Main Navigation Links (Hidden on small screens) */}
          <nav className="hidden md:flex">
            <NavigationMenu>
              <NavigationMenuList>
                {/* Products Dropdown */}
                <NavigationMenuItem>
                  <NavigationMenuTrigger>Products</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <div className="p-4 w-[200px] md:w-[300px]"> {/* Adjust width as needed */}
                      <p className="text-sm text-muted-foreground mb-2">
                        Explore FaultMaven features.
                      </p>
                      {/* TODO: Replace with actual links using ListItem helper perhaps */}
                      <Link href="/features/ai-analysis" className="block text-sm hover:bg-accent p-2 rounded">AI Analysis</Link>
                      <Link href="/features/agentic-query" className="block text-sm hover:bg-accent p-2 rounded">Agentic Query</Link>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                {/* Solutions Dropdown */}
                <NavigationMenuItem>
                  <NavigationMenuTrigger>Solutions</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <div className="p-4 w-[200px] md:w-[300px]">
                      <p className="text-sm text-muted-foreground mb-2">
                        How FaultMaven helps your team.
                      </p>
                      {/* TODO: Replace with actual links */}
                      <Link href="/solutions/mttr-reduction" className="block text-sm hover:bg-accent p-2 rounded">MTTR Reduction</Link>
                      <Link href="/solutions/sre-onboarding" className="block text-sm hover:bg-accent p-2 rounded">SRE Onboarding</Link>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                {/* Resources Dropdown */}
                <NavigationMenuItem>
                  <NavigationMenuTrigger>Resources</NavigationMenuTrigger>
                  <NavigationMenuContent>
                     <div className="p-4 w-[200px] md:w-[300px]">
                       <p className="text-sm text-muted-foreground mb-2">
                         Learn more and get help.
                       </p>
                       {/* TODO: Replace with actual links */}
                       <Link href="/blog" className="block text-sm hover:bg-accent p-2 rounded">Blog</Link>
                       <Link href="/docs" className="block text-sm hover:bg-accent p-2 rounded">Documentation</Link>
                     </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                {/* Pricing Link */}
                <NavigationMenuItem>
                   <Link href="/pricing" legacyBehavior passHref>
                     <NavigationMenuLink className={cn(
                        navigationMenuTriggerStyle(), // Style like a trigger
                        "transition-colors hover:text-foreground/80",
                        pathname === "/pricing" ? "text-foreground font-semibold" : "text-foreground/60" // Active state
                      )}>
                      Pricing
                     </NavigationMenuLink>
                   </Link>
                </NavigationMenuItem>

                 {/* Contact Sales Link */}
                 <NavigationMenuItem>
                   <Link href="/contact-sales" legacyBehavior passHref>
                     <NavigationMenuLink className={cn(
                        navigationMenuTriggerStyle(), // Style like a trigger
                        "transition-colors hover:text-foreground/80",
                         pathname === "/contact-sales" ? "text-foreground font-semibold" : "text-foreground/60" // Active state
                      )}>
                       Contact Sales
                     </NavigationMenuLink>
                   </Link>
                 </NavigationMenuItem>

              </NavigationMenuList>
            </NavigationMenu>
          </nav>
        </div>

        {/* Right Group: Auth Actions (Hidden on small screens) */}
        <div className="hidden md:flex items-center space-x-4">
          {/* Show loading indicator or links based on state */}
          {isLoading ? (
             // Optional: Add a small spinner using shadcn Skeleton or lucide-react
             <div className="text-sm text-muted-foreground animate-pulse">Loading...</div>
          ) : isAuthenticated ? (
            // --- Links/Buttons shown when LOGGED IN ---
            <>
              <Link href="/dashboard" className={cn("transition-colors hover:text-foreground/80 text-sm font-medium", pathname === "/dashboard" ? "text-foreground font-semibold" : "text-foreground/60")}>
                Dashboard
              </Link>
              {/* Call context logout function */}
              <Button variant="outline" size="sm" onClick={logout}>
                 Logout
              </Button>
            </>
          ) : (
            // --- Links/Buttons shown when LOGGED OUT ---
            <>
              <Link href="/login" className={cn("transition-colors hover:text-foreground/80 text-sm font-medium", pathname === "/login" ? "text-foreground font-semibold" : "text-foreground/60")}>
                Log in
              </Link>
              {/* TODO: Link Start Trial to Sign Up page or specific trial flow */}
              <Button size="sm">
                 Start trial
              </Button>
            </>
          )}
        </div>

        {/* Mobile Menu Button Placeholder (Visible only on small screens) */}
        <div className="md:hidden">
            {/* TODO: Implement actual mobile menu toggle button & drawer/panel */}
            <Button variant="ghost" size="icon">
              {/* Placeholder Icon */}
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
              <span className="sr-only">Toggle Menu</span>
            </Button>
        </div>

      </div>
    </header>
  );
}

// Optional Helper component for styling dropdown items consistently
// import { NavigationMenuLink } from "@/components/ui/navigation-menu";
// const ListItem = React.forwardRef<
//   React.ElementRef<"a">,
//   React.ComponentPropsWithoutRef<"a">
// >(({ className, title, children, ...props }, ref) => {
//   return (
//     <li>
//       <NavigationMenuLink asChild>
//         <a
//           ref={ref}
//           className={cn(
//             "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
//             className
//           )}
//           {...props}
//         >
//           <div className="text-sm font-medium leading-none">{title}</div>
//           <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
//             {children}
//           </p>
//         </a>
//       </NavigationMenuLink>
//     </li>
//   )
// })
// ListItem.displayName = "ListItem"
