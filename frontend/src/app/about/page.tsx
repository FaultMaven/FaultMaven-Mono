export default function AboutPage() {
  return (
    <main className="bg-white">
      <section className="py-20 px-6 bg-indigo-50 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
          Our Journey: Building Your Trusted AI Copilot for Operations
        </h1>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">The Spark: Why FaultMaven Exists</h2>
          <p className="text-gray-600 mb-4">
            FaultMaven wasn't born in a vacuum. It was sparked by over a decade spent on the front lines of complex operational environments, witnessing firsthand the immense pressure on engineers to maintain system reliability.
          </p>
          <p className="text-gray-600">
            There was a persistent realization: while monitoring systems and automation handle routine tasks, a significant gap remains in the nuanced, investigative work of deep troubleshooting. This inspired the creation of FaultMaven—a tool built to bridge that gap.
          </p>
        </div>
      </section>
    </main>
  );
}
