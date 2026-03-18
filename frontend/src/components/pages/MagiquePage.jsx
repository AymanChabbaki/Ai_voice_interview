import { Sparkles, Rocket, ArrowRight, CheckCircle2, Waves, Timer, Brain, Star } from 'lucide-react';

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

          <div className="magique-quick-metrics">
            <div>
              <strong>15 min</strong>
              <span>Focus sprints</span>
            </div>
            <div>
              <strong>3x</strong>
              <span>Feedback depth</span>
            </div>
            <div>
              <strong>Live</strong>
              <span>Voice guidance</span>
            </div>
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

          <model-viewer
            className="magique-model-viewer"
            src="https://modelviewer.dev/shared-assets/models/RobotExpressive.glb"
            camera-controls
            auto-rotate
            shadow-intensity="1"
            environment-image="neutral"
          >
          </model-viewer>
        </div>
      </section>

      <section className="magique-grid">
        <article className="magique-card">
          <Waves size={18} />
          <h3>Story Sculptor</h3>
          <p>Shape your answers into concise narratives with a clear challenge, action, and impact.</p>
        </article>
        <article className="magique-card">
          <Timer size={18} />
          <h3>Pressure Simulator</h3>
          <p>Rehearse under timed prompts so your delivery stays calm when real interviews intensify.</p>
        </article>
        <article className="magique-card">
          <Brain size={18} />
          <h3>Signal Booster</h3>
          <p>Improve confidence, pacing, and precision through focused micro-feedback loops.</p>
        </article>
      </section>

      <section className="magique-journey">
        <h3>Magique Journey</h3>
        <div className="magique-journey-steps">
          {[
            'Warm-up speaking drill',
            'Adaptive interview round',
            'Precision feedback and retry',
            'Confidence replay session'
          ].map((step, index) => (
            <div key={step} className="journey-step">
              <span className="journey-index">0{index + 1}</span>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="magique-testimonials">
        <h3>Candidate Signal</h3>
        <div className="magique-testimonial-grid">
          <article>
            <Star size={16} />
            <p>"I stopped rambling and started answering with structure in one week."</p>
          </article>
          <article>
            <CheckCircle2 size={16} />
            <p>"The pressure mode made real interviews feel far less intimidating."</p>
          </article>
          <article>
            <Sparkles size={16} />
            <p>"I could hear and see my progress instead of guessing if I improved."</p>
          </article>
        </div>
      </section>
    </div>
  );
}

export default MagiquePage;
