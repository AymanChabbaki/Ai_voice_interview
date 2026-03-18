import { Lock, ArrowRight, Layers3, Sparkles, CircleHelp } from 'lucide-react';

function ResourcePage({
  pageKey,
  title,
  section,
  description,
  highlights,
  isProtected,
  isAuthenticated,
  onPrimaryAction,
  onBackHome
}) {
  const modelSource =
    section === 'Platform'
      ? 'https://modelviewer.dev/shared-assets/models/RobotExpressive.glb'
      : 'https://modelviewer.dev/shared-assets/models/Astronaut.glb';

  const phaseSteps = [
    'Understand the framework',
    'Practice with guided prompts',
    'Apply in timed simulations',
    'Review and iterate with feedback'
  ];

  const faqs = [
    {
      q: `How often should I use ${title}?`,
      a: 'A focused 15-20 minute session, 3 to 4 times per week, creates reliable progress.'
    },
    {
      q: 'Can I combine this with live interview prep?',
      a: 'Yes. Use these modules as your daily training layer before live mock rounds.'
    },
    {
      q: 'What outcome should I track first?',
      a: 'Start with clarity and confidence consistency, then expand into speed and depth.'
    }
  ];

  return (
    <div className="resource-page">
      <section className="resource-hero resource-hero-rich">
        <div className="resource-hero-main">
          <p className="resource-section-label">{section}</p>
          <h2>{title}</h2>
          <p className="resource-description">{description}</p>

          <div className="resource-actions">
            {isProtected && !isAuthenticated ? (
              <button className="btn btn-primary btn-large" onClick={onPrimaryAction}>
                <Lock size={18} />
                Login to Continue
              </button>
            ) : (
              <button className="btn btn-primary btn-large" onClick={onPrimaryAction}>
                <ArrowRight size={18} />
                Open {title}
              </button>
            )}

            <button className="btn btn-secondary btn-large" onClick={onBackHome}>
              Back to Home
            </button>
          </div>

          <div className="resource-meta-row">
            <span><Sparkles size={14} /> Guided</span>
            <span><Layers3 size={14} /> Structured</span>
            <span><ArrowRight size={14} /> Actionable</span>
          </div>
        </div>

        <div className="resource-hero-visual">
          <model-viewer
            className="resource-model-viewer"
            src={modelSource}
            camera-controls
            auto-rotate
            shadow-intensity="1"
            environment-image="neutral"
          >
          </model-viewer>

          <div className="resource-hero-chip">Route: /{pageKey}</div>
        </div>
      </section>

      <section className="resource-grid resource-grid-rich">
        {highlights.map((item) => (
          <article key={item.title} className="resource-card">
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </article>
        ))}
      </section>

      <section className="resource-timeline">
        <h3>Execution Flow</h3>
        <div className="resource-timeline-grid">
          {phaseSteps.map((step, idx) => (
            <article key={step} className="resource-timeline-item">
              <span>0{idx + 1}</span>
              <p>{step}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="resource-deep-dive">
        <h3>Deep Dive Modules</h3>
        <div className="resource-deep-grid">
          {highlights.map((item, idx) => (
            <article key={`${item.title}-${idx}`}>
              <h4>{item.title}</h4>
              <p>{item.text} This module includes prompt drills, reflection checkpoints, and measurable outcomes.</p>
            </article>
          ))}
        </div>
      </section>

      <section className="resource-faq">
        <h3>Frequently Asked</h3>
        <div className="resource-faq-list">
          {faqs.map((faq) => (
            <article key={faq.q}>
              <h4><CircleHelp size={16} /> {faq.q}</h4>
              <p>{faq.a}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

export default ResourcePage;
