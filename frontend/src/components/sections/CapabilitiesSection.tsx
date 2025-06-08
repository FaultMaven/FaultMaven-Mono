'use client';

export default function CapabilitiesSection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900 mb-8">
          FaultMaven 1.0 In Action: What Key Features Can I Leverage?
        </h2>
        <p className="text-lg text-gray-700 mb-10 max-w-3xl mx-auto text-center">
          FaultMaven 1.0 puts powerful AI assistance directly at your fingertips, integrated seamlessly via its browser extension. Here are the key capabilities you can use right now to transform your troubleshooting:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI-Powered Diagnostics & Root Cause Insights</h3>
            <p className="text-gray-600">
              Instantly gain clarity on complex issues. Provide FaultMaven with logs, error messages, or system context, and its AI will analyze the data to identify critical patterns, suggest likely root causes, and guide you with actionable next steps.
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Instant Summaries & Draft Documentation</h3>
            <p className="text-gray-600">
              Effortlessly capture crucial information. As you troubleshoot, FaultMaven can generate concise summaries of your findings and help draft initial notes for documentation or post-mortem reports.
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Intelligent Personal Knowledge Reuse</h3>
            <p className="text-gray-600">
              Stop reinventing the wheel with every new alert. Feed FaultMaven your existing runbooks, proven solutions from past incidents, and personal troubleshooting tips. It then intelligently surfaces this relevant knowledge when similar situations arise.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
