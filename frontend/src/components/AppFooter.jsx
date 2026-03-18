import { Rocket, ExternalLink, Sparkles, ArrowRight, Mic } from 'lucide-react';

function AppFooter({ isAuthenticated, setCurrentPage, setShowAuth, onFooterNavigate }) {
  return (
    <footer className="footer footer-magnifique">
      <div className="footer-gradient" aria-hidden="true" />

      <div className="footer-shell">
        <div className="footer-topbar">
          <div className="footer-topbar-copy">
            <span className="footer-pill">
              <Sparkles size={14} />
              Human &amp; Hired
            </span>
            <h3>Practice today. Perform better in your next real interview.</h3>
          </div>
          <button
            className="btn btn-primary footer-primary-cta"
            onClick={() => {
              if (isAuthenticated) {
                setCurrentPage('interview');
                return;
              }
              setShowAuth(true);
            }}
          >
            <Rocket size={18} />
            {isAuthenticated ? 'Launch Interview' : 'Start Free Session'}
          </button>
        </div>

        <div className="footer-grid footer-grid-redesign">
          <div className="footer-brand">
            <div className="footer-brand-title">
              <img src="/logo.png" alt="Smart Voice Interviewer logo" className="brand-logo" />
              <div>
                <h3>Smart Voice Interviewer</h3>
                <p className="footer-brand-subtitle">AI-Powered Interview System</p>
              </div>
            </div>
            <p className="footer-brand-copy">
              Human-centric interview rehearsal for technical and behavioral rounds.
              Build confidence, sharpen delivery, and walk in ready.
            </p>

            <div className="footer-signals">
              <div className="footer-signal-item">
                <Mic size={15} />
                <span>Live voice practice</span>
              </div>
              <div className="footer-signal-item">
                <ArrowRight size={15} />
                <span>Actionable feedback loops</span>
              </div>
            </div>
          </div>

          <div className="footer-column">
            <h4>Platform</h4>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('mock-interviews'); }}>Mock Interviews</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('question-library'); }}>Question Library</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('progress-dashboard'); }}>Progress Dashboard</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('achievement-paths'); }}>Achievement Paths</a>
          </div>

          <div className="footer-column">
            <h4>Resources</h4>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('interview-playbooks'); }}>Interview Playbooks</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('coaching-tips'); }}>Coaching Tips</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('weekly-drills'); }}>Weekly Drills</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onFooterNavigate('roadmaps'); }}>Roadmaps</a>
          </div>

          <div className="footer-column footer-column-cta">
            <h4>Start Today</h4>
            <p>Run a 15-minute interview sprint and get instant feedback.</p>
            <button
              className="btn btn-primary"
              onClick={() => {
                if (isAuthenticated) {
                  setCurrentPage('dashboard');
                  return;
                }
                setShowAuth(true);
              }}
            >
              <Rocket size={18} />
              {isAuthenticated ? 'Open Dashboard' : 'Create Free Account'}
            </button>
            <a href="#" onClick={(e) => e.preventDefault()} className="footer-link-inline">
              Explore Product Tour <ExternalLink size={14} />
            </a>
          </div>
        </div>

        <div className="footer-bottom footer-bottom-redesign">
          <p>Powered by Sentence-BERT AI | Smart Voice Interviewer v2.0</p>
          <p>Designed for standout candidates</p>
        </div>
      </div>
    </footer>
  );
}

export default AppFooter;
