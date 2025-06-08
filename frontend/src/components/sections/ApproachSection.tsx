'use client';

export default function ApproachSection() {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900 mb-8">
          What Makes FaultMaven's Approach Different?
        </h2>
        <p className="text-lg text-gray-700 mb-10 max-w-3xl mx-auto text-center">
          We're not just applying AI to old problems; we're fundamentally rethinking how engineers can overcome operational complexity.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Your AI Teammate: Intelligent Partnership, Not Impersonal Automation</h3>
            <p className="text-gray-600">
              Team up with FaultMaven, your expert AI Copilot. It rapidly sifts through complexity to surface critical insights and illuminate potential paths, <strong className="text-gray-900">inspiring new perspectives and amplifying your expertise, not sidelining it.</strong> While it dramatically accelerates your workflow, <strong className="text-gray-900">you direct the investigation and make all final calls.</strong> This human-centric control ensures an effective, <strong className="text-gray-900">safe, and accountable</strong> approach to resolving complex challenges.
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Purpose-Built for Operational Complexity</h3>
            <p className="text-gray-600">
              This isn't a generic AI adapted for troubleshooting. FaultMaven is being developed from the ground up by seasoned engineers and domain experts who understand the unique pressures and data intricacies of modern operations. It's tailored to "think" like an experienced SRE, focusing on the signals and contexts that truly matter.
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Clarity and Action, Not Just Data Lakes</h3>
            <p className="text-gray-600">
              Our focus isn't just on analyzing vast amounts of data, but on transforming that data into clear, understandable insights and concrete, actionable recommendations. FaultMaven aims to cut through the noise, providing the clarity you need to act decisively and effectively.
            </p>
          </div>
        </div>
        <p className="text-center text-gray-600 mt-10">
          This philosophy guides every stage of FaultMaven's development, from its initial 1.0 offering to its future as an integrated team expert.
        </p>
      </div>
    </section>
  );
}
