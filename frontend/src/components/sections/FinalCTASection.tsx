'use client';

export default function FinalCTASection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900 mb-8">
          Shape the Future of AIOps with FaultMaven
        </h2>
        <p className="text-lg text-gray-700 mb-10 max-w-3xl mx-auto text-center">
          FaultMaven is at a pivotal stage of development, and we're building it for—and with—forward-thinking engineers and organizations. While some details remain under wraps as we refine our core technology, this is your invitation to get involved early with a select group and help shape a truly transformative solution.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">For Experienced SREs & Operations Engineers</h3>
            <p className="text-gray-600 mb-4">
              Do you want an early look at FaultMaven 1.0 and a chance to provide crucial feedback that directly shapes its features? We're looking for design partners to share their toughest challenges and help us build the ultimate AI Copilot.
            </p>
            <a
              href="/waitlist"
              className="inline-block text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Apply for Our Private Preview →
            </a>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">For Visionary Investors & Strategic Partners</h3>
            <p className="text-gray-600 mb-4">
              We believe FaultMaven offers a unique approach to a significant market need, backed by seasoned expertise and a clear, phased roadmap. If you share our vision and are interested in growth opportunities:
            </p>
            <a
              href="/contact"
              className="inline-block text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Request Our Vision Deck →
            </a>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">For Passionate Innovators & Talent</h3>
            <p className="text-gray-600 mb-4">
              Excited by the mission to redefine operational troubleshooting with AI? We'll be looking for exceptional individuals to join our core team as we grow.
            </p>
            <a
              href="/contact"
              className="inline-block text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Express Interest in Future Roles →
            </a>
          </div>
        </div>
        <p className="text-center text-gray-600 mt-10">
          We’re building something we believe is truly special, and we’re eager to connect with those who want to be part of the journey from these early stages.
        </p>
      </div>
    </section>
  );
}
