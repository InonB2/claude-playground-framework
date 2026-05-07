import React from 'react';
import { ArrowDown, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import ScrollReveal from '../components/ScrollReveal';
import FloatingBlobs from '../components/FloatingBlobs';
import MetricCard from '../components/MetricCard';
import PortfolioSection from '../components/sections/PortfolioSection';
import AboutSection from '../components/sections/AboutSection';
import CareerSection from '../components/sections/CareerSection';
import InsightsSection from '../components/sections/InsightsSection';
import RoadmapSection from '../components/sections/RoadmapSection';
import ContactSection from '../components/sections/ContactSection';

const PROFILE_PHOTO = 'https://base44.app/api/apps/69e9e364459ecbf538b7c62f/files/mp/public/69e9e364459ecbf538b7c62f/7c22df058_inon_profile_selected.jpg';

export default function Home() {
  return (
    <div>
      {/* ── SCROLLABLE BACKGROUND ─────────────────────────── */}
      <div
        className="fixed inset-0 -z-10 bg-cover bg-center pointer-events-none"
        style={{ backgroundImage: `url('https://media.base44.com/images/public/69f0d5ee32f2078f5a76299d/7830adabe_generated_image.png')`, opacity: 0.18 }}
      />

      {/* ── HERO ──────────────────────────────────────────── */}
      <section id="home" className="relative min-h-screen flex items-center justify-center pt-16">
        <FloatingBlobs />

        {/* Faint scrolling commit hashes */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
          <div className="font-mono text-xs leading-6 text-foreground whitespace-pre animate-[scroll_60s_linear_infinite]">
            {Array.from({ length: 80 }, (_, i) => (
              <div key={i}>commit {Math.random().toString(16).slice(2, 10)} — product_launch_v{(i % 5) + 1}.{i % 10}</div>
            ))}
          </div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
          <div className="flex flex-col-reverse lg:flex-row items-center gap-12 lg:gap-20">
            {/* Left content */}
            <div className="flex-1 text-center lg:text-left">
              <ScrollReveal>
                <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/28 rounded-full px-4 py-1.5 mb-7">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse inline-block" />
                  <span className="font-mono text-[11px] text-primary font-bold tracking-[1.5px]">
                    OPEN TO SENIOR PM / CPO ROLES — TEL AVIV &amp; REMOTE
                  </span>
                </div>
              </ScrollReveal>

              <ScrollReveal delay={0.1}>
                <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight">
                  I Build Products{' '}
                  <span className="text-primary">That Scale.</span>
                </h1>
              </ScrollReveal>

              <ScrollReveal delay={0.2}>
                <p className="text-lg md:text-xl font-bold text-foreground/80 mt-6 max-w-xl mx-auto lg:mx-0 leading-relaxed">
                  Co-Founder. CPO. Builder.<br />
                  $2.5M raised. Six products.<br />
                  <span className="text-muted-foreground font-normal text-base">Most PMs just plan to deliver.</span>
                </p>
              </ScrollReveal>

              <ScrollReveal delay={0.25}>
                <p className="text-sm text-muted-foreground mt-4 max-w-xl mx-auto lg:mx-0 leading-[1.85]">
                  I spent 6 years as Co-Founder &amp; CPO of TouchE — an AI video platform I built from zero, raised $2.5M for, and shipped to millions of concurrent users across 4 countries. Paramount. Lion&apos;s Gate. JVP. That wasn&apos;t luck. That was judgment, speed, and executive reach.
                </p>
                <p className="text-sm text-muted-foreground/60 mt-2 max-w-xl mx-auto lg:mx-0 leading-relaxed italic">
                  Now I&apos;m looking for the next problem worth owning.
                </p>
                <p className="text-xs text-muted-foreground/40 mt-2 max-w-xl mx-auto lg:mx-0 leading-relaxed">
                  10+ years · Technion B.Sc. Engineering + Executive MBA · AI · FinTech · Enterprise
                </p>
              </ScrollReveal>

              <ScrollReveal delay={0.3}>
                <div className="flex flex-col sm:flex-row gap-4 mt-10 justify-center lg:justify-start">
                  <a href="#portfolio" data-clickable>
                    <Button size="lg" className="gap-2 text-base px-8">
                      See My Work <ArrowDown className="w-4 h-4" />
                    </Button>
                  </a>
                  <a href="https://media.base44.com/files/public/69f0d5ee32f2078f5a76299d/aa1837a95_InonBaasovV2SM1STG.pdf" target="_blank" rel="noopener noreferrer" data-clickable>
                    <Button variant="outline" size="lg" className="gap-2 text-base px-8 border-border hover:border-primary hover:text-primary">
                      <Download className="w-4 h-4" /> Download CV
                    </Button>
                  </a>
                </div>
              </ScrollReveal>
            </div>

            {/* Right - Profile Photo */}
            <ScrollReveal delay={0.2} direction="left" className="flex-shrink-0">
              <div className="relative">
                <div className="absolute inset-0 -m-4 rounded-full border border-primary/20 animate-[spin_20s_linear_infinite]" />
                <div className="absolute inset-0 -m-8 rounded-full border border-primary/10 animate-[spin_30s_linear_infinite_reverse]" />
                <div className="absolute inset-0 -m-2 rounded-full bg-primary/20 blur-2xl animate-pulse-glow" />
                <div className="relative w-56 h-56 md:w-72 md:h-72 rounded-full overflow-hidden border-2 border-primary/50 shadow-2xl shadow-primary/20">
                  <img src={PROFILE_PHOTO} alt="Inon Baasov" className="w-full h-full object-cover" />
                </div>
                <div className="absolute -top-2 right-4 flex items-center gap-1.5 bg-card/90 backdrop-blur px-3 py-1.5 rounded-full border border-border/50">
                  <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                  <span className="font-mono text-[10px] text-accent">ACTIVE</span>
                </div>
              </div>
            </ScrollReveal>
          </div>

          {/* Metrics */}
          <ScrollReveal delay={0.4}>
            <div className="grid grid-cols-3 gap-4 mt-20">
              <MetricCard value={2.5} prefix="$" suffix="M" label="Raised" decimals={1} />
              <MetricCard value={99.99} suffix="%" label="Uptime" decimals={2} />
              <MetricCard value={38} suffix="%" label="Efficiency ↑" />
            </div>
          </ScrollReveal>

          {/* Scroll hint */}
          <div className="flex justify-center mt-16">
            <a href="#portfolio" data-clickable className="flex flex-col items-center gap-2 text-muted-foreground hover:text-primary transition-colors animate-bounce">
              <span className="font-mono text-[10px] tracking-wider">SCROLL</span>
              <ArrowDown className="w-4 h-4" />
            </a>
          </div>
        </div>
      </section>

      {/* ── PORTFOLIO ────────────────────────────────────── */}
      <section id="portfolio">
        <PortfolioSection />
      </section>

      {/* ── ABOUT ────────────────────────────────────────── */}
      <section id="about">
        <AboutSection />
      </section>

      {/* ── CAREER ───────────────────────────────────────── */}
      <section id="career">
        <CareerSection />
      </section>

      {/* ── ROADMAP ──────────────────────────────────────── */}
      <section id="roadmap">
        <RoadmapSection />
      </section>

      {/* ── INSIGHTS ─────────────────────────────────────── */}
      <section id="insights">
        <InsightsSection />
      </section>

      {/* ── CONTACT ──────────────────────────────────────── */}
      <section id="contact">
        <ContactSection />
      </section>
    </div>
  );
}