export default function FAQPage() {
  const faqs = [
    {
      q: "What is FaultMaven 1.0, and how can I get involved early?",
      a: "FaultMaven 1.0 is your personal AI Copilot, accessed via a simple browser extension, designed to help you troubleshoot complex operational issues with no initial system integration. We're currently inviting experienced SREs and Ops engineers to apply for our early access/design partner program to provide crucial feedback."
    },
    {
      q: "What kinds of operational challenges does FaultMaven 1.0 address?",
      a: "FaultMaven 1.0 is being built to help you diagnose a variety of operational issues faster—from investigating incident alerts and user-reported problems to understanding performance degradations. It assists by analyzing the context you provide, summarizing information, and leveraging stored knowledge to guide your troubleshooting process."
    },
    {
      q: "Why isn’t everything about FaultMaven public yet?",
      a: "FaultMaven is pioneering new approaches in AI-driven troubleshooting, and we're developing rapidly. We're sharing our vision and progress in stages while we work closely with early partners to refine core technology. For those interested in a deeper look – select design partners, potential investors, and future team members – we're happy to start a conversation."
    },
    {
      q: "How does FaultMaven handle your data securely?",
      a: "Data security and privacy are foundational to FaultMaven. For 1.0, you provide data directly and securely via the browser extension. We are building with robust security measures and a policy focused on minimizing long-term storage of raw, sensitive operational data from your specific troubleshooting sessions. Your trust is paramount."
    }
  ];
  return (
    <main className="bg-white">
      <section className="py-20 px-6 bg-indigo-50 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h1>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-3xl mx-auto">
          <p className="text-lg text-gray-700 mb-6">
            We’re committed to clarity and transparency as FaultMaven evolves. Here are answers to some initial questions.
          </p>
          <p className="text-lg text-gray-700 mb-6">
            This page will grow and be updated regularly based on your feedback and our journey together.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {faqs.map((item, idx) => (
              <details key={idx} className="border border-gray-200 p-4 rounded group">
                <summary className="flex justify-between items-center cursor-pointer list-none font-medium text-gray-900">
                  {item.q}
                  <svg className="ml-4 h-5 w-5 text-gray-500 transition-transform group-open:rotate-180" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="mt-2 text-gray-600">
                  {item.a}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
