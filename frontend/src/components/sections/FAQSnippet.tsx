'use client';
import { useState } from 'react';

export default function FAQSnippet() {
  const [faqOpenIndex, setFaqOpenIndex] = useState(null);

  const toggleFAQ = (index) => {
    setFaqOpenIndex(faqOpenIndex === index ? null : index);
  };

  const faqSnippet = [
    {
      question: "What is FaultMaven 1.0, and how can I get involved early?",
      answer: "FaultMaven 1.0 is your personal AI Copilot, accessed via a simple browser extension, designed to help you troubleshoot complex operational issues with no initial system integration. We're currently inviting experienced SREs and Ops engineers to apply for our early access/design partner program to provide crucial feedback."
    },
    {
      question: "What kinds of operational challenges does FaultMaven 1.0 address?",
      answer: "FaultMaven 1.0 is being built to help you diagnose a variety of operational issues faster—from investigating incident alerts and user-reported problems to understanding performance degradations. It assists by analyzing the context you provide, summarizing information, and leveraging stored knowledge to guide your troubleshooting process."
    },
    {
      question: "Why isn’t everything about FaultMaven public yet?",
      answer: "FaultMaven is pioneering new approaches in AI-driven troubleshooting, and we're developing rapidly. We're sharing our vision and progress in stages while we work closely with early partners to refine core technology. For those interested in a deeper look – select design partners, potential investors, and future team members – we're happy to start a conversation."
    },
    {
      question: "How does FaultMaven handle my data securely?",
      answer: "Data security and privacy are foundational to FaultMaven. For 1.0, you provide data directly and securely via the browser extension. We are building with robust security measures and a policy focused on minimizing long-term storage of raw, sensitive operational data. Your trust is paramount."
    },
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-3xl mx-auto px-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900 mb-8">
          Your Questions Answered
        </h2>
        <p className="text-lg text-gray-700 text-center mb-8">
          We believe in clarity. Here are answers to some common initial questions:
        </p>
        <div className="space-y-4">
          {faqSnippet.map((item, idx) => (
            <div key={idx} className="border border-gray-200 p-6 rounded group">
              <button
                onClick={() => toggleFAQ(idx)}
                className="w-full text-left flex justify-between items-center focus:outline-none"
              >
                <span className="font-medium text-gray-900">{item.question}</span>
                <svg
                  className={`h-5 w-5 text-gray-500 transform transition-transform ${faqOpenIndex === idx ? 'rotate-180' : ''}`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {faqOpenIndex === idx && (
                <div className="px-6 pt-2 pb-4 text-gray-600">
                  {item.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
