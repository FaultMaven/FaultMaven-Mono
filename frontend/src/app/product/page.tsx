export default function ProductPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="py-20 px-6 bg-indigo-50 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            FaultMaven 1.0: Accelerate Diagnostics & Fixes with AI-Powered Troubleshooting
          </h1>
          <p className="text-lg text-gray-700">
            Empowering the Individual Engineer
          </p>
        </div>
      </section>

      {/* Intro Section */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-lg text-gray-700 mb-6">
            Welcome to FaultMaven 1.0, the foundational release of your personal AI Copilot, engineered to transform how individual DevOps engineers, SREs, and operations specialists tackle complex troubleshooting.
          </p>
          <p className="text-lg text-gray-700 mb-6">
            Our core mission with this initial version is to provide you with an intelligent, immediately accessible assistant that augments your expertise, streamlines your diagnostic workflow, and helps you resolve issues faster – all without requiring complex upfront system integrations.
          </p>
          <p className="text-lg text-gray-700">
            Core prototyping for these foundational features is complete, and active development is well underway.
          </p>
        </div>
      </section>

      {/* Interaction Section */}
      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            How You Interact with FaultMaven 1.0: A Seamless Experience
          </h2>
          <p className="text-lg text-gray-700 mb-6">
            FaultMaven 1.0 is designed to integrate smoothly into your existing troubleshooting workflow, providing powerful AI assistance without demanding complex setups or a steep learning curve. Our goal is to make interaction intuitive, efficient, and always place you in control.
          </p>

          <h3 className="text-xl font-medium text-gray-900 mt-8 mb-4">
            Your Command Center: The Browser Extension & Side-Panel
          </h3>
          <p className="text-gray-600 mb-4">
            At the heart of FaultMaven 1.0 is a lightweight browser extension. Once installed, it provides an always-accessible and adjustable side-panel right in your browser. This means your AI Copilot is ready to assist whenever and wherever your work takes you—whether you're examining monitoring dashboards, reviewing deployment pipelines, sifting through logs in a web interface, analyzing a discussion in a Slack channel (when viewed in your browser), reviewing details in a ServiceNow incident report, or reading technical documentation.
          </p>

          <h3 className="text-xl font-medium text-gray-900 mt-8 mb-4">
            Flexible Data Input – You’re in Control:
          </h3>
          <p className="text-gray-600 mb-4">
            FaultMaven 1.0 works with the specific context you provide, ensuring its analysis is targeted and relevant to the problem at hand. You control the information flow with simple, direct methods:
          </p>
          <ul className="list-disc pl-8 space-y-2 text-gray-600 mb-6">
            <li><strong>Copy & Paste:</strong> Easily paste error messages, log snippets, code excerpts, configuration details, or any relevant text directly into the side-panel.</li>
            <li><strong>File Upload:</strong> Securely upload various text-based files such as full log files, configuration files, exported metrics data, or system reports for FaultMaven to analyze.</li>
            <li><strong>Share Page Context:</strong> With your permission, share the textual content of your current browser page for broader situational awareness. This is ideal for capturing information from web-based tools like monitoring dashboards, internal wikis, or displayed Slack messages and discussion threads (when viewed via browser).</li>
          </ul>
          <p className="text-gray-600">
            This user-driven data input for 1.0 means no direct system integrations are needed to get started, allowing for rapid adoption and immediate use.
          </p>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            FaultMaven 1.0 In Action: What Key Features Can I Leverage?
          </h2>
          <p className="text-lg text-gray-700 mb-6">
            FaultMaven 1.0 puts powerful AI assistance directly at your fingertips, integrated seamlessly via its browser extension. Here are the key capabilities you can use right now to transform your troubleshooting:
          </p>
          <div className="space-y-8">
            <div className="border border-gray-200 p-6 rounded shadow-sm bg-white">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                AI-Powered Diagnostics & Root Cause Insights
              </h3>
              <p className="text-gray-600">
                Instantly gain clarity on complex issues. Provide FaultMaven with logs, error messages, or system context, and its AI will analyze the data to identify critical patterns, suggest likely root causes, and guide you with actionable next steps.
              </p>
            </div>

            <div className="border border-gray-200 p-6 rounded shadow-sm bg-white">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Instant Summaries & Draft Documentation
              </h3>
              <p className="text-gray-600">
                Effortlessly capture crucial information. As you troubleshoot, FaultMaven can generate concise summaries of your findings and help draft initial notes for documentation or post-mortem reports.
              </p>
            </div>

            <div className="border border-gray-200 p-6 rounded shadow-sm bg-white">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Intelligent Personal Knowledge Reuse
              </h3>
              <p className="text-gray-600">
                Stop reinventing the wheel with every new alert. Feed FaultMaven your existing runbooks, proven solutions from past incidents, and personal troubleshooting tips. It then intelligently surfaces this relevant, curated knowledge when similar situations arise.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Highlights */}
      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            FaultMaven 1.0: Technology Highlights
          </h2>
          <p className="text-gray-600 mb-6">
            FaultMaven 1.0 leverages advanced AI and thoughtful engineering to deliver its intelligent assistance. While the "magic" involves complex processes, our approach is grounded in creating practical, reliable, and secure capabilities that empower you. Here are a few key aspects of our technology:
          </p>

          <div className="space-y-8">
            <div className="border border-gray-200 p-6 rounded shadow-sm bg-white">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Intelligent Multi-Model AI Core</h3>
              <p className="text-gray-600">
                FaultMaven's AI engine uses multiple models working together to ensure accurate, consistent, and explainable insights across different domains and operational contexts.
              </p>
            </div>

            <div className="border border-gray-200 p-6 rounded shadow-sm bg-white">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Secure, User-Driven Data Handling</h3>
              <p className="text-gray-600">
                FaultMaven only acts on the data you explicitly choose to share. No sensitive system integration occurs unless you initiate it. We're building with strong security and privacy practices in mind.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Ready to Get Started with FaultMaven 1.0?
          </h2>
          <p className="text-lg text-gray-700 mb-8">
            If you're an experienced SRE or Ops engineer interested in getting early access, applying to become a Design Partner, or just want to learn more about what we're building, we'd love to hear from you.
          </p>
          <a
            href="/waitlist"
            className="inline-block px-8 py-3 text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition duration-200"
          >
            Apply for Private Preview Access
          </a>
        </div>
      </section>
    </>
  );
}
