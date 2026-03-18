import { Sparkles, Rocket, ArrowRight } from 'lucide-react';

function MagiquePage({ isAuthenticated, setCurrentPage, setShowAuth }) {
  return (
    <div className="magique-page">
      <section className="magique-hero">
        <div className="magique-hero-content">
          <div className="hero-badge">
            <Sparkles size={16} />
            <span>Magique Experience</span>
          </div>
          <h2>From Practice Sessions to Performance Presence</h2>
          <p>
            This immersive track helps you structure stronger stories, control your pace,
            and answer with confidence under pressure.
          </p>
          <div className="magique-actions">
            <button
              className="btn btn-primary btn-large"
              onClick={() => {
                if (isAuthenticated) {
                  setCurrentPage('interview');
                  return;
                }
                setShowAuth(true);
              }}
            >
              <Rocket size={20} />
              {isAuthenticated ? 'Start Interview Sprint' : 'Unlock Magique'}
            </button>
            <button
              className="btn btn-secondary btn-large"
              onClick={() => setCurrentPage('home')}
            >
              <ArrowRight size={20} />
              Back to Home
            </button>
          </div>
        </div>

        <div className="magique-visual">
          <div className="magique-orbit" aria-hidden="true" />
          <div className="magique-score-card">
            <h3>Live Presence Meter</h3>
            <div className="presence-bars">
              <div className="presence-row">
                <span>Clarity</span>
                <div className="presence-track"><div className="presence-fill fill-a" /></div>
              </div>
              <div className="presence-row">
                <span>Structure</span>
                <div className="presence-track"><div className="presence-fill fill-b" /></div>
              </div>
              <div className="presence-row">
                <span>Confidence</span>
                <div className="presence-track"><div className="presence-fill fill-c" /></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="magique-grid">
        <article className="magique-card">
          <h3>Story Sculptor</h3>
          <p>Shape your answers into concise narratives with a clear challenge, action, and impact.</p>
        </article>
        <article className="magique-card">
          <h3>Pressure Simulator</h3>
          <p>Rehearse under timed prompts so your delivery stays calm when real interviews intensify.</p>
        </article>
        <article className="magique-card">
          <h3>Signal Booster</h3>
          <p>Improve confidence, pacing, and precision through focused micro-feedback loops.</p>
        </article>
      </section>
    </div>
  );
}

export default MagiquePage;
