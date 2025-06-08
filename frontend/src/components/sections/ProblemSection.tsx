'use client';

export default function ProblemSection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900 mb-8">
          Facing These Tough Operational Challenges?
        </h2>
        <p className="text-lg text-gray-700 mb-10 max-w-3xl mx-auto text-center">
          If you're an engineer on the front lines, you know the daily battle of keeping complex systems running smoothly. When issues strike, the pressure is immense, and often it feels like you're up against the same frustrating hurdles.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Endless Toil & Slow Resolutions</h3>
            <p className="text-gray-600">
              Spending too much valuable time on repetitive, manual troubleshooting steps that lead to slow incident response, human error, and ever-increasing MTTR?
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Crippling Alert Fatigue</h3>
            <p className="text-gray-600">
              Drowning in a sea of alerts, struggling to distinguish critical signals from noise, and worried about missing the truly urgent issues?
            </p>
          </div>
          <div className="p-6 border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Vanishing Tribal Knowledge</h3>
            <p className="text-gray-600">
              Constantly reinventing the wheel due to scattered information, unclear procedures, or outdated runbooks whenever a critical problem arises?
            </p>
          </div>
        </div>
        <p className="text-center text-gray-600 mt-10">
          These obstacles don't just slow you down; they impact innovation, team morale, and the bottom line. FaultMaven is being built to change that.
        </p>
      </div>
    </section>
  );
}
