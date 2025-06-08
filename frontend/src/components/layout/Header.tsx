'use client';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center h-12">
        {/* Left-aligned: Logo + Primary Nav */}
        <nav className="flex space-x-6 text-sm font-medium">
          <a href="/" className="flex items-center">
            <img src="/images/fmlogo-light.svg" alt="FaultMaven Logo" className="h-8 w-auto mr-0" />
          </a>
          <a href="/product" className="text-gray-700 hover:text-indigo-600">Product</a>
          <a href="/use-cases" className="text-gray-700 hover:text-indigo-600">Use Cases</a>
          <a href="/roadmap" className="text-gray-700 hover:text-indigo-600">Roadmap</a>
          <div className="relative group">
            <span className="cursor-pointer text-gray-700 hover:text-indigo-600">Resources</span>
            <ul className="absolute hidden group-hover:block mt-1 bg-white border rounded shadow-md py-2 w-32 text-sm text-gray-700 z-50">
              <li><a href="/blog" className="block px-4 py-2 hover:bg-indigo-50">Blog</a></li>
              <li><a href="/faq" className="block px-4 py-2 hover:bg-indigo-50">FAQ</a></li>
            </ul>
          </div>
          <a href="/pricing" className="text-gray-700 hover:text-indigo-600">Pricing</a>
          <a href="/contact" className="text-gray-700 hover:text-indigo-600">Contact</a>
        </nav>

        {/* Right-aligned: Sign In + Join Waitlist */}
        <nav className="flex space-x-4 text-sm font-medium">
          <a href="/waitlist" className="text-gray-700 hover:text-indigo-600">Sign In</a>
          <a
            href="/waitlist"
            className="px-4 py-1 rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition"
          >
            Join Waitlist
          </a>
        </nav>
      </div>
    </header>
  );
}
