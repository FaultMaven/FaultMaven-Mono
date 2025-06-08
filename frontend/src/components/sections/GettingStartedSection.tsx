'use client';

export default function GettingStartedSection() {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900 mb-8">
          Getting Started with FaultMaven 1.0: How Do I Use It?
        </h2>
        <p className="text-lg text-gray-700 mb-10 max-w-3xl mx-auto text-center">
          With FaultMaven 1.0, experiencing powerful AI-driven troubleshooting doesn't require a leap of faith or complex setup. We believe in a quick start without the usual risks, offering an easy entry point designed for smart, iterative interaction. Here’s how simply you can begin leveraging your AI Copilot:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <div className="text-indigo-600 text-4xl font-bold mb-2">1</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Instant Install: Get Ready in Seconds</h3>
            <p className="text-gray-600">
              Add the FaultMaven browser extension with just a few clicks. It’s an effortless setup, allowing you to start validating its capabilities immediately without any upfront commitment or system changes.
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <div className="text-indigo-600 text-4xl font-bold mb-2">2</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Share Context: Your Data, Your Way</h3>
            <p className="text-gray-600">
              When you need assistance, engage FaultMaven via its intuitive side-panel. Share error messages, logs (by copy-pasting or uploading files), or the context of your current browser page. You control the interaction.
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <div className="text-indigo-600 text-4xl font-bold mb-2">3</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Get Actionable Insights: Iterate and Resolve</h3>
            <p className="text-gray-600">
              FaultMaven's AI instantly analyzes your input, initiating a continuous and progressive dialogue. Receive actionable insights, potential root cause hypotheses, clear answers, and intelligent next-step recommendations that evolve as you explore the problem together.
            </p>
          </div>
        </div>
        <p className="text-center text-gray-600 mt-10">
          No vendor lock-in. No integration hell. Just smarter troubleshooting, right away.
        </p>
      </div>
    </section>
  );
}
