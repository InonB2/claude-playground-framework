import React, { useState } from 'react';
import ScrollReveal from '../ScrollReveal';
import ProductCard from '../ProductCard';
import ProductModal from '../ProductModal';

const products = [
  {
    tag: 'AI · Video · SaaS',
    name: 'TouchE',
    subtitle: 'AI-Powered Interactive Video Platform',
    role: 'Co-Founder & CPO',
    version: 'v4.2',
    health: 99,
    link: 'https://touche.live',
    icon: '🎬',
    stack: ['AWS', 'AI/ML', 'Android / iOS / SmartTV', 'No-Code CMS'],
    metrics: [
      { label: 'Raised', value: '$2.5M' },
      { label: 'Uptime', value: '99.99%' },
      { label: 'Efficiency', value: '+38%' },
      { label: 'Engagement', value: '+24%' },
    ],
    caseStuDy: [
      {
        heading: 'Problem',
        body: 'Video platforms were passive. Broadcasters like HOT, Paramount & Ozon needed real-time interactivity, personalization and shoppable experiences — without expensive custom engineering.',
      },
      {
        heading: 'Solution',
        body: 'Built an AI-powered interactive video platform with real-time overlays, a recommendation engine, and a no-code creator studio. Architected to handle millions of concurrent sessions at 99.99% uptime.',
      },
      {
        heading: 'Impact',
        body: 'Raised $2.5M (JVP-backed), signed HOT · Paramount · Lion\'s Gate · Ozon, improved operator efficiency by 38%, and lifted viewer engagement by 24%.',
      },
    ],
  },
  {
    tag: 'FinTech · Payments · B2B',
    name: 'Arena Plus',
    subtitle: 'Credit Card Processing & Payments Platform',
    role: 'Senior Product Manager',
    version: 'v3.1',
    health: 96,
    link: null,
    icon: '💳',
    stack: ['Payments Processing', 'B2B Enterprise', 'FinTech APIs', 'Compliance'],
    metrics: [
      { label: 'Sector', value: 'FinTech' },
      { label: 'Type', value: 'Credit Card Processing' },
      { label: 'Market', value: 'B2B Enterprise' },
      { label: 'Scope', value: 'Full Platform PM' },
    ],
    caseStuDy: [
      {
        heading: 'Problem',
        body: 'Businesses processing credit card payments faced slow, unreliable, and opaque payment flows. Existing platforms lacked the UX and API quality enterprise clients demanded.',
      },
      {
        heading: 'Solution',
        body: 'Led end-to-end product management of Arena Plus — a B2B credit card processing platform. Owned roadmap, cross-functional delivery, compliance flows, and merchant-facing dashboards.',
      },
      {
        heading: 'Impact',
        body: 'Shipped multiple platform versions serving enterprise merchants, improving transaction reliability, onboarding speed, and developer API quality across the payment stack.',
      },
    ],
  },
  {
    tag: 'FinTech · Trading · Analytics',
    name: 'TradePulse Journal Pro',
    subtitle: 'Professional Trading Journal & Analytics',
    role: 'Founder & Builder',
    version: 'v1.0',
    health: 100,
    link: null,
    icon: '📈',
    stack: ['React', 'Base44', 'FinTech UX', 'Analytics'],
    metrics: [
      { label: 'Status', value: 'Live' },
      { label: 'Build', value: '3 weeks' },
      { label: 'Domain', value: 'FinTech' },
      { label: 'Users', value: 'Traders' },
    ],
    caseStuDy: [
      {
        heading: 'Problem',
        body: 'No trading journal tracked psychology alongside P&L. Traders lacked a tool that combined analytics, emotional discipline, and actionable pattern recognition in one place.',
      },
      {
        heading: 'Solution',
        body: 'Built TradePulse Journal Pro from scratch in 3 weeks — a full FinTech analytics platform for professional traders featuring trade logging, P&L dashboards, and behavioral pattern insights.',
      },
      {
        heading: 'Impact',
        body: 'Went from zero to live product in under a month. Validated in 20 user interviews. Demonstrates ability to ship fast, high-quality FinTech products independently.',
      },
    ],
  },
  {
    tag: 'Consumer · Hebrew · Mobile',
    name: 'Family Flow',
    subtitle: 'Family Task & Chore Management App',
    role: 'Founder & Builder',
    version: 'v1.0',
    health: 98,
    link: null,
    icon: '👨‍👩‍👧',
    stack: ['React', 'Hebrew RTL', 'TypeScript', 'Mobile-first'],
    metrics: [
      { label: 'Status', value: 'Live' },
      { label: 'Build', value: '2 weeks' },
      { label: 'Language', value: 'Hebrew RTL-first' },
      { label: 'Users', value: 'Israeli Families' },
    ],
    caseStuDy: [
      {
        heading: 'Problem',
        body: 'Israeli families lacked a native Hebrew-first app to coordinate household chores, tasks and responsibilities. Existing tools were generic, English-only, and not designed for family dynamics.',
      },
      {
        heading: 'Solution',
        body: 'Built a Hebrew-first RTL family coordination app in 2 weeks. Covers chore assignment, family task boards, gamified progress, and age-appropriate task difficulty.',
      },
      {
        heading: 'Impact',
        body: 'Live product with active Israeli family users. Demonstrates speed of execution, consumer UX sensibility, and deep cultural product awareness.',
      },
    ],
  },
  {
    tag: 'IN DEVELOPMENT · 2026',
    name: 'BuildAR Pro',
    subtitle: 'AI-Powered AR Construction & DIY Platform',
    role: 'Co-Founder & CPO',
    version: 'v0.9',
    health: 80,
    link: null,
    icon: '🥽',
    stack: ['AR/VR', 'Computer Vision', 'AI/ML', 'React Native', '3D Rendering'],
    metrics: [
      { label: 'Core Tech', value: 'AR' },
      { label: 'Guidance', value: 'AI' },
      { label: 'Market', value: 'B2C/B2B' },
      { label: 'Launch', value: '2026' },
    ],
    caseStuDy: [
      {
        heading: 'Problem',
        body: 'Construction and DIY projects suffer from poor spatial planning, costly mistakes, and no real-time expert guidance. Professionals and amateurs alike waste time and money on preventable errors.',
      },
      {
        heading: 'Process',
        body: 'Conducted 40+ interviews with contractors, architects, and DIY hobbyists. Identified three recurring pain points: spatial measurement errors, material waste from poor planning, and lack of step-by-step expert guidance on-site.',
      },
      {
        heading: 'Solution',
        body: 'Mobile AR app that overlays 3D models onto real environments, providing AI-guided step-by-step construction instructions, real-time error detection, material estimation, and progress tracking — all through the phone camera.',
      },
      {
        heading: 'My Role',
        body: 'Co-founder and CPO. Leading product vision, UX architecture, AR pipeline design, go-to-market strategy, and investor narrative. Building the team and roadmap from 0→1.',
      },
      {
        heading: 'Impact',
        body: 'Pre-launch. Architecture validated. MVP scoped for Q3 2026 beta with 10 construction firms and 50 DIY power users.',
      },
      {
        heading: 'What I Learned',
        body: 'AR UX demands a fundamentally different design language — the interface must disappear. The best AR feature is the one users forget they\'re using.',
      },
    ],
  },
  {
    tag: 'GenAI · Enterprise · Consulting',
    name: 'AiRakoon',
    subtitle: 'Enterprise AI Platform Strategy',
    role: 'Strategic Consultant',
    version: 'v1.0',
    health: 100,
    link: null,
    icon: '🤖',
    stack: ['GenAI Strategy', 'LLM Architecture', 'Enterprise B2B', 'GTM'],
    metrics: [
      { label: 'Domain', value: 'GenAI' },
      { label: 'Roadmap', value: '12-month plan' },
      { label: 'Pilot', value: 'Closed' },
      { label: 'Market', value: 'Enterprise B2B' },
    ],
    caseStuDy: [
      {
        heading: 'Problem',
        body: 'AiRakoon, an enterprise AI platform, had strong technology but no clear product-market fit, positioning, or go-to-market strategy. They needed a product leader, not just a consultant.',
      },
      {
        heading: 'Solution',
        body: 'Embedded as strategic product advisor — defined ICP, repositioned the platform, built a 12-month roadmap, and designed a pilot program to close enterprise accounts.',
      },
      {
        heading: 'Impact',
        body: 'Delivered product-market fit framework, closed first enterprise pilot, and built the GTM playbook. AiRakoon moved from concept to paying enterprise customers.',
      },
    ],
  },
];

export default function PortfolioSection() {
  const [selected, setSelected] = useState(null);

  return (
    <div className="min-h-screen py-24 relative">
      <div className="max-w-7xl mx-auto px-6">
        <ScrollReveal>
          <p className="font-mono text-sm text-primary tracking-wider mb-3">// PORTFOLIO</p>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight">
            Products I've <span className="text-primary">Shipped.</span>
          </h2>
          <p className="text-muted-foreground mt-4 max-w-2xl text-sm">
            From co-founding an AI startup to leading enterprise FinTech — here's what I've built.
          </p>
        </ScrollReveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-14">
          {products.map((p, i) => (
            <ScrollReveal key={p.name} delay={i * 0.1}>
              <ProductCard product={p} onClick={() => setSelected(p)} />
            </ScrollReveal>
          ))}
        </div>
      </div>

      {selected && <ProductModal product={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}