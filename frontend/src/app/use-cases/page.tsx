export default function UseCasesPage() {
  return (
    <main className="bg-white">
      {/* Hero Section */}
      <section className="py-20 px-6 bg-indigo-50 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            FaultMaven 1.0 in Action: Solving Real-World Operational Challenges
          </h1>
          <p className="text-lg text-gray-700">
            Understanding theory is one thing; seeing a tool tackle real-world problems is another.
          </p>
        </div>
      </section>

      {/* Intro Section */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-lg text-gray-700 mb-6">
            This page dives into practical scenarios where FaultMaven 1.0 acts as your indispensable AI Copilot,
            helping individual engineers like you navigate complex operational challenges with greater speed, clarity, and confidence.
          </p>
          <p className="text-lg text-gray-700">
            Each use case below illustrates how, by leveraging FaultMaven 1.0 through its intuitive browser extension and
            the information you provide, you can transform your approach to troubleshooting—from initial alert or symptom to rapid insight.
          </p>
        </div>
      </section>

      {/* Use Case 3: Navigating a 3 AM Server Error Spike */}
      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Use Case 3: Navigating a 3 AM Server Error Spike</h2>
          <p className="text-gray-600 mb-4">
            The Challenge:
          </p>
          <p className="text-gray-600 mb-4">
            An on-call SRE is paged at 3 AM due to a sudden spike in 500 errors on a critical web service. Initial dashboards show the errors, but the root cause isn't immediately obvious, and time is a factor.
          </p>

          <p className="text-gray-600 mb-4">
            FaultMaven in Action: AI-Guided Path to Clarity
          </p>
          <p className="text-gray-600 mb-4">
            The SRE opens their FaultMaven AI Copilot in their browser side-panel while viewing their primary monitoring dashboard.
          </p>

          <p className="text-gray-600 mb-4">
            Contextual Data Input: They copy key error log snippets and relevant metrics (error rates, service health) from their monitoring tools and paste them into FaultMaven.
          </p>

          <p className="text-gray-600 mb-4">
            Focused Inquiry: The SRE asks, "What's causing this 500 error spike on the web service using this provided data?"
          </p>

          <p className="text-gray-600 mb-4">
            AI-Powered Analysis: FaultMaven analyzes the submitted logs and metrics, identifying a correlation: database connection timeouts are occurring concurrently with the 500 errors.
          </p>

          <p className="text-gray-600 mb-4">
            Clear Insights Delivered: FaultMaven reports: "Based on the data provided, the 500 errors appear linked to database connection timeouts. Web service CPU and memory metrics seem normal, suggesting the issue may not be resource exhaustion on the web service itself. Further investigation into database logs and connection pool status is advisable."
          </p>

          <p className="text-gray-600 mb-4">
            Actionable, Guided Next Steps: FaultMaven suggests: "To investigate further, you might want to retrieve more detailed database logs from the incident period. A command similar to [kubectl logs your-db-pod --since=1h --tail=500 | grep -i 'timeout|error|limit'] could be useful. Alternatively, would you like to focus on analyzing connection pool metrics if you can provide them?"
          </p>

          <p className="text-gray-600 mb-4">
            Deeper Dive with New Data: Following the guidance, the SRE retrieves the relevant database logs, pastes them into FaultMaven, and asks for analysis. FaultMaven parses these new logs, highlighting specific error messages indicating that database connection limits are being reached.
          </p>

          <p className="text-gray-600 mb-4">
            The Outcome:
          </p>
          <p className="text-gray-600">
            With a clear root cause pinpointed by FaultMaven's analysis of the provided data, the SRE can confidently take targeted action, such as adjusting the database connection pool size. Once the issue is mitigated, FaultMaven can assist in drafting a concise summary of the diagnostic steps and findings for the incident record: "Critical 500 error spike on web service resolved. Root cause identified as exhausted database connections. Remediation: Increased database connection pool size."
          </p>

          <p className="text-gray-600 mt-4">
            Result: The diagnostic process is significantly accelerated, leading to faster Mean Time To Resolution (MTTR). The on-call engineer feels more supported and less burdened by having an AI Copilot to help analyze data and suggest concrete investigative paths.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Ready to See FaultMaven in Action?
          </h2>
          <p className="text-lg text-gray-700 mb-8">
            If you're interested in early access, applying to become a Design Partner, or simply want to stay informed about FaultMaven's development, we'd love to hear from you.
          </p>
          <a
            href="/waitlist"
            className="inline-block px-8 py-3 text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition duration-200"
          >
            Join the Waitlist →
          </a>
        </div>
      </section>
    </main>
  );
}
