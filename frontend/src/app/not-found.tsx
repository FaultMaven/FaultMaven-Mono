// src/app/not-found.tsx
export default function NotFound() {
  return (
    <main className="bg-white">
      <section className="py-20 px-6 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Page Not Found</h1>
        <p className="text-gray-600 mb-6">
          Sorry, the page you’re looking for doesn’t exist.
        </p>
        <a href="/" className="text-indigo-600 hover:text-indigo-800 underline">
          Return to Home
        </a>
      </section>
    </main>
  );
}
