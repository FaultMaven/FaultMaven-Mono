// src/app/login/page.tsx
import { LoginForm } from "@/components/LoginForm"; // Import the form component

export default function LoginPage() {
  return (
    <div className="flex flex-col items-center justify-center pt-10">
      <h1 className="text-2xl font-semibold mb-6">Login to FaultMaven</h1>
      <div className="w-full max-w-sm">
         <LoginForm /> {/* <-- Use the LoginForm component */}
      </div>
      {/* TODO: Add link to Sign up page later */}
    </div>
  );
}
