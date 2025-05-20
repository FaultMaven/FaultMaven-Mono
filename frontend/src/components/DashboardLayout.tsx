import React from "react";

type DashboardLayoutProps = {
  children: React.ReactNode;
};

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="px-4 py-3 bg-white shadow">
        <h1 className="text-xl font-bold">Dashboard</h1>
      </header>
      <main className="flex-1 p-4">{children}</main>
    </div>
  );
};

