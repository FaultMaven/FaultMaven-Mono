'use client';
export default function Hero() {
  return (
    <section className="pt-16 pb-20 bg-gradient-to-b from-white via-blue-50 to-white text-center">
      <div className="max-w-4xl mx-auto px-6">
        <h1 className="text-4xl md:text-5xl font-extrabold leading-tight mb-4 text-gray-900">
          Troubleshoot Faster, Smarter, with FaultMaven
        </h1>
        <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
          Your evolving AI Copilot—built <span className="italic">with</span> engineers like you—delivering real-time insights and guided solutions to dramatically reduce Mean Time To Resolution (MTTR) across your toughest operational challenges.
        </p>
        <a
          href="/waitlist"
          className="inline-block px-8 py-3 text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition duration-200"
        >
          Get Early Access Updates & Help Shape FaultMaven
        </a>
        <hr className="my-10 border-gray-200" />
        <p className="text-sm text-gray-500">
          Built on deep tech landscape experience and real-world operational insights.
        </p>
        <p className="text-sm font-semibold text-gray-700 mt-1">
          Forged by seasoned SREs, Operations specialists, and AI experts.
        </p>
      </div>
    </section>
  );
}
