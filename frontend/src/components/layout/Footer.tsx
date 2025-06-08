'use client';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          {/* Logo + Social */}
          <div className="col-span-2 md:col-span-1">
            <a href="/" className="flex items-center mb-4">
              <img src="/images/fmlogo-light.svg" alt="FaultMaven Logo" className="h-6 w-auto mr-0" />
            </a>
            <p className="text-gray-600 text-sm mb-4">
              Empowering engineering and operations teams with actionable AI-driven insights and collaborative knowledge
            </p>
            <div className="flex space-x-4">
              <a href="https://x.com/faultmaven"  target="_blank" rel="noopener noreferrer" aria-label="X">
                <svg className="w-5 h-5 text-gray-600 hover:text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.057a6.14 6.14 0 0 1 2.21 2.348c.09.207.09.427.09.646 0 6.61-5.03 14.32-14.32 14.32-2.849 0-5.46-.829-7.64-2.05 2.517.295 4.968.199 7.29-.247-2.495 1.71-5.594 2.65-9.01 2.65-1.819 0-3.58-.107-5.286-.32v-.32c.72 1.593 2.213 2.75 4.096 3.21a6.12 6.12 0 0 1-2.772-.776c-.275-.137-.535-.294-.78-.467l-.01-.01c0 .22.01 .44.03 .66 1.584.92 3.455 1.47 5.45 1.47a10.86 10.86 0 0 0 6.98-2.397 5.42 5.42 0 0 0 1.93-3.795c0-.12-.01-.24-.02-.36A5.42 5.42 0 0 0 19 7.874 5.42 5.42 0 0 0 13.46 2.35c-3.62 0-6.56 2.94-6.56 6.56 0 .51.06 1.02.18 1.51a18.46 18.46 0 0 1-1.34-.07 10.14 10.14 0 0 0 5.52 1.62 5.06 5.06 0 0 1-2.32.87 5.4 5.4 0 0 0 4.05 2.36 10.16 10.16 0 0 1-2.56-.32c-.44.75-.69 1.58-.69 2.47 0 1.71 1.38 3.09 3.09 3.09a6.6 6.6 0 0 1-1.88.51c-.44.07-.89.11-1.34.11-.27 0-.54-.02-.81-.07a10.16 10.16 0 0 0 5.08 1.4c.96 0 1.87-.09 2.75-.26a14.3 14.3 0 0 0 8.82-8.82z" />
                </svg>
              </a>
              <a href="https://github.com/sterlanyu/FaultMaven"  target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg className="w-5 h-5 text-gray-600 hover:text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.61-3.36-1.34-3.36-1.34-.45-1.15-1.1-1.46-1.1-1.46-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.88 1.52 2.3 1.07 2.85.82.09-.65.35-1.07.63-1.31-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.29.1-2.69a9.1 9.1 0 0 1 2.5-1.31c.81-.42 1.67-.63 2.56-.64.09 0 .18.01.27.01.38.01.52.15.72.45l1.32 2.38c.72.13 1.47.2 2.23.2 6.61 0 10.19-5.5 10.19-10.19 0-1.78-.15-3.57-.46-5.28a15.29 15.29 0 0 0 11.11-11.11c2.51-.46 5.12-.7 7.77-.7.26 0 .52.01.78.03a15.29 15.29 0 0 0 4.82-1.32c.28-.17.54-.38.78-.63a15.29 15.29 0 0 0 4.82-1.32c.28-.17.54-.38.78-.63 0 .26.07.52.07.78 0 1.78-.9 3.46-2.48 4.7a6.14 6.14 0 0 1-5.68 0c-1.58 1.24-2.48 2.92-2.48 4.7 0 .26.03.52.07.78a15.29 15.29 0 0 1-4.82 1.32c-.26.02-.52.03-.78.03-6.61 0-12-5.39-12-12 0-.81.08-1.6.24-2.35A8.97 8.97 0 0 1 2.057 6.48C3.057 7.83 4.3 8.92 5.7 9.67.59 9.6 0 8.36 0 7.24c0-1.11.59-2.11 1.53-2.71a5.4 5.4 0 0 1-.63-1.62c0-1.11.63-1.94 1.46-2.25a5.4 5.4 0 0 1 1.99.77A5.4 5.4 0 0 1 5.09 4.22c0-.46.31-1.01.77-1.01.26 0 .51.1.69.27l1.57 1.96c.44.55.99.99 1.62.99.37 0 .72-.15 1-.43a1.72 1.72 0 0 0 2.4-.77c0-.26-.02-.52-.07-.77-.22-.03-.45-.05-.68-.05-1.03 0-1.93.44-2.53 1.17-.81-1.53-2.13-2.65-3.67-2.65-.3 0-.59.03-.87.08a5.4 5.4 0 0 0-4.8 3.52c-1.44.27-3-.3-4.13-1.13-.26.45-.4 1-.4 1.63 0 1.11.5 2.11 1.24 2.68a5.4 5.4 0 0 1-2.24-.61v.06c0 1.56 1.1 3.01 2.56 3.31a5.4 5.4 0 0 1-2.44.92c-.59 0-1.15-.17-1.64-.48a10.16 10.16 0 0 0 5.53 1.62c-3.17 2.47-6.02 3.65-9.06 3.65-.58 0-1.15-.03-1.71-.1a10.16 10.16 0 0 0 5.06 3.75c-3.17 0-6.02-1.18-8.38-3.14a10.16 10.16 0 0 0 3.76 4.22c-1.44.56-2.98.89-4.59.89-.3 0-.59-.02-.88-.05a15.29 15.29 0 0 0 7.72 2.16c9.29 0 14.32-7.71 14.32-14.32 0-.15-.01-.3-.02-.46a7.3 7.3 0 0 0 1.8-1.82z" />
                </svg>
              </a>
              <a href="https://linkedin.com/company/faultmaven"  target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <svg className="w-5 h-5 text-gray-600 hover:text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.45 2H3.55A1.45 1.45 0 0 0 2.05 3.45v17.1A1.45 1.45 0 0 0 3.55 22h16.9a1.45 1.45 0 0 0 1.45-1.45V3.45A1.45 1.45 0 0 0 20.45 2zM8.07 19h-3.4v-8.72h3.4V19zm-1.7-10.84a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6zm13.63 10.84h-3.4v-4.37c0-1.05-.02-2.4-1.47-2.4-1.47 0-1.7 1.14-1.7 2.33v4.44h-3.4c0 0 .05 7.25 0 8.72h-3.4V8.16h3.39v1.13h.05a3.7 3.7 0 0 1 3.34-1.7c3.24 0 3.79 2.25 3.79 5.2v6.34z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <strong className="font-medium text-gray-800 text-sm block mb-2">Product</strong>
            <ul className="mt-2 space-y-1 text-sm text-gray-600">
              <li><a href="/product" className="hover:text-indigo-600">Product</a></li>
              <li><a href="/use-cases" className="hover:text-indigo-600">Use Cases</a></li>
              <li><a href="/pricing" className="hover:text-indigo-600">Pricing</a></li>
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <strong className="font-medium text-gray-800 text-sm block mb-2">Company</strong>
            <ul className="mt-2 space-y-1 text-sm text-gray-600">
              <li><a href="/about" className="hover:text-indigo-600">About Us</a></li>
              <li><a href="/roadmap" className="hover:text-indigo-600">Our Vision</a></li>
              <li><a href="/contact" className="hover:text-indigo-600">Contact Us</a></li>
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <strong className="font-medium text-gray-800 text-sm block mb-2">Resources</strong>
            <ul className="mt-2 space-y-1 text-sm text-gray-600">
              <li><a href="/blog" className="hover:text-indigo-600">Blog</a></li>
              <li><a href="/faq" className="hover:text-indigo-600">FAQ</a></li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <strong className="font-medium text-gray-800 text-sm block mb-2">Legal</strong>
            <ul className="mt-2 space-y-1 text-sm text-gray-600">
              <li><a href="/privacy" className="hover:text-indigo-600">Privacy Policy</a></li>
              <li><a href="/terms" className="hover:text-indigo-600">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Divider & Copyright */}
        <div className="mt-8 pt-6 border-t border-gray-200 text-sm text-gray-500 text-center">
          &copy; {new Date().getFullYear()} FaultMaven. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
