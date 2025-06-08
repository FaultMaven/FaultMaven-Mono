export default function WaitlistPage() {
  return (
    <main className="bg-white">
      <section className="py-20 px-6 bg-indigo-50 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
          Get Early Access to FaultMaven & Help Shape the Future of AI Troubleshooting
        </h1>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-lg text-gray-700 mb-6">
            FaultMaven 1.0, your personal AI Copilot, is currently in active development, and we're inviting forward-thinking engineers like you to be among the first to experience its benefits and provide invaluable feedback.
          </p>
          <p className="text-lg text-gray-700 mb-6">
            By joining our waitlist, you'll get:
          </p>
          <ul className="list-disc pl-8 space-y-2 text-gray-600">
            <li>Priority access to early availability spots</li>
            <li>Exclusive updates on our development progress</li>
            <li>An opportunity to influence FaultMaven’s direction</li>
          </ul>
          <p className="text-lg text-gray-700 mt-6">
            Ready to get started? Join the waitlist below.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <form className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded shadow-sm"
              />
            </div>
            <button
              type="submit"
              className="w-full px-6 py-3 bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Join the Early Access Waitlist
            </button>
          </form>
          <p className="mt-4 text-sm text-gray-500">
            By joining, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </section>
    </main>
  );
}
