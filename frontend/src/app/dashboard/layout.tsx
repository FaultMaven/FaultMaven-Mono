// src/app/dashboard/layout.tsx
import React from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <section className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div>{children}</div>
    </section>
  );
}

