import Hero from "@/components/sections/Hero";
import ProblemSection from "@/components/sections/ProblemSection";
import ApproachSection from "@/components/sections/ApproachSection";
import CapabilitiesSection from "@/components/sections/CapabilitiesSection";
import GettingStartedSection from "@/components/sections/GettingStartedSection";
import VisionSnippet from "@/components/sections/VisionSnippet";
import FAQSnippet from "@/components/sections/FAQSnippet";
import FinalCTASection from "@/components/sections/FinalCTASection";

export default function Home() {
  return (
    <main>
      <Hero />
      <ProblemSection />
      <ApproachSection />
      <CapabilitiesSection />
      <GettingStartedSection />
      <VisionSnippet />
      <FAQSnippet />
      <FinalCTASection />
    </main>
  );
}
