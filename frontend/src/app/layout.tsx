import './globals.css';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>FaultMaven | AI Copilot for Operations</title>
        <meta name="description" content="FaultMaven is an AI Copilot built with engineers for smarter incident response and troubleshooting." />
      </head>
      <body className="bg-gray-50 text-gray-900 flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
