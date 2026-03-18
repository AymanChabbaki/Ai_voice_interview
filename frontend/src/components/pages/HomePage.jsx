import { useEffect, useState } from 'react';
import {
  Sparkles,
  Shield,
  BarChart3,
  Users,
  Target,
  Play,
  Rocket,
  TrendingUp,
  Flame,
  CheckCircle2,
  Crown,
  Brain,
  Mic,
  Lightbulb,
  Award,
  BookOpen,
  ArrowRight
} from 'lucide-react';

function HomePage({
  isAuthenticated,
  userProfile,
  setCurrentPage,
  setShowDashboard,
  setShowAuth
}) {
  const assistantLines = [
    "Don't click me. Your last click was already suspicious.",
    'Breathe. You are one focused session away from sounding elite.',
    'Your confidence is loading... please stop panic-scrolling.',
    'You are better than you think. Say it clearly and own the room.',
    'If chaos had a voice, it would still interview better after this practice.'
  ];

  const [assistantLineIndex, setAssistantLineIndex] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setAssistantLineIndex((prev) => (prev + 1) % assistantLines.length);
    }, 5200);

    return () => clearInterval(intervalId);
  }, [assistantLines.length]);

  return (
    <div className="home-page">
      <section className="home-hero home-hero-magnifique">
        <div className="hero-ambient" aria-hidden="true">
          <div className="hero-orb orb-one" />
          <div className="hero-orb orb-two" />
          <div className="hero-orb orb-three" />
        </div>

        <div className="home-hero-content">
          <div className="hero-badge">
            <Sparkles size={16} />
            <span>Magnifique AI Interview Studio</span>
          </div>
          <h1 className="home-hero-title">
            Speak with confidence.
            <span className="hero-title-accent"> Perform like a top candidate.</span>
          </h1>
          <p className="home-hero-subtitle">
            Cinematic practice sessions, real-time coaching, and detailed score intelligence
            in one focused interview command center.
          </p>

          <div className="hero-trust-strip">
            <div className="trust-pill">
              <Shield size={16} />
              <span>Private by default</span>
            </div>
            <div className="trust-pill">
              <BarChart3 size={16} />
              <span>Precision analytics</span>
            </div>
            <div className="trust-pill">
              <Users size={16} />
              <span>Built for fast growth</span>
            </div>
          </div>

          <div className="home-hero-cta">
            {isAuthenticated ? (
              <>
                <button
                  className="btn btn-primary btn-large"
                  onClick={() => setCurrentPage('dashboard')}
                >
                  <Target size={20} />
                  Go to Dashboard
                </button>
                <button
                  className="btn btn-secondary btn-large"
                  onClick={() => {
                    setCurrentPage('interview');
                    setShowDashboard(false);
                  }}
                >
                  <Play size={20} />
                  Start Interview
                </button>
              </>
            ) : (
              <>
                <button
                  className="btn btn-primary btn-large"
                  onClick={() => setShowAuth(true)}
                >
                  <Rocket size={20} />
                  Get Started Free
                </button>
                <button className="btn btn-secondary btn-large" onClick={() => setCurrentPage('question-library')}>
                  <Play size={20} />
                  Question Library
                </button>
              </>
            )}
          </div>

          <div className="hero-scroll-voice" aria-hidden="true">
            <span>Scroll with your voice • Speak clearly • Build presence • Win interviews •</span>
          </div>

          {isAuthenticated && userProfile && (
            <div className="home-user-stats">
              <div className="user-stat-item">
                <Target size={18} />
                <span>{userProfile.interview_count || 0} Interviews</span>
              </div>
              <div className="user-stat-item">
                <TrendingUp size={18} />
                <span>{userProfile.interview_count && userProfile.total_score
                  ? `${(userProfile.total_score / userProfile.interview_count).toFixed(1)}%`
                  : '0%'} Average</span>
              </div>
              <div className="user-stat-item">
                <Flame size={18} />
                <span>{userProfile.current_streak || 0} Day Streak</span>
              </div>
            </div>
          )}
        </div>

        <div className="home-hero-visual home-hero-surface">
          <model-viewer
            className="hero-model-floating"
            src="https://modelviewer.dev/shared-assets/models/Astronaut.glb"
            poster="https://modelviewer.dev/assets/poster-astronaut.webp"
            camera-controls
            auto-rotate
            shadow-intensity="1"
            environment-image="neutral"
            exposure="1"
          >
          </model-viewer>

          <div className="hero-floating-cards hero-floating-surface">
            <div className="floating-card">
              <CheckCircle2 size={20} />
              <span>Adaptive Question Flow</span>
            </div>
            <div className="floating-card">
              <Crown size={20} />
              <span>Elite Mode Feedback</span>
            </div>
          </div>
        </div>
      </section>

      <div className="assistant-3d-float">
        <div className="assistant-chat-bubble">{assistantLines[assistantLineIndex]}</div>
        <model-viewer
          className="assistant-model"
          src="https://modelviewer.dev/shared-assets/models/RobotExpressive.glb"
          auto-rotate
          shadow-intensity="1"
          environment-image="neutral"
          exposure="1"
          disable-zoom
        >
        </model-viewer>
      </div>

      <section className="home-section">
        <div className="section-header-center">
          <h2>Why Choose Our Platform?</h2>
          <p>Everything you need to succeed in your next interview</p>
        </div>
        <div className="home-features">
          <div className="home-feature-card">
            <div className="feature-icon-large">
              <Brain size={40} />
            </div>
            <h3>AI-Powered Questions</h3>
            <p>Get intelligent, contextual questions tailored to your experience level and target role</p>
          </div>
          <div className="home-feature-card">
            <div className="feature-icon-large">
              <Mic size={40} />
            </div>
            <h3>Voice Recognition</h3>
            <p>Practice with realistic voice input and text-to-speech for authentic interview simulation</p>
          </div>
          <div className="home-feature-card">
            <div className="feature-icon-large">
              <TrendingUp size={40} />
            </div>
            <h3>Progress Tracking</h3>
            <p>Monitor improvement with detailed analytics, performance metrics, and trend analysis</p>
          </div>
          <div className="home-feature-card">
            <div className="feature-icon-large">
              <Lightbulb size={40} />
            </div>
            <h3>Instant Feedback</h3>
            <p>Receive immediate AI-generated feedback with personalized improvement recommendations</p>
          </div>
          <div className="home-feature-card">
            <div className="feature-icon-large">
              <Award size={40} />
            </div>
            <h3>Achievement System</h3>
            <p>Unlock badges, maintain streaks, and stay motivated throughout your learning journey</p>
          </div>
          <div className="home-feature-card">
            <div className="feature-icon-large">
              <BookOpen size={40} />
            </div>
            <h3>50+ Categories</h3>
            <p>Practice across diverse topics from programming to system design and behavioral questions</p>
          </div>
        </div>
      </section>

      <section className="home-section home-how-it-works">
        <div className="section-header-center">
          <h2>How It Works</h2>
          <p>Get started in three simple steps</p>
        </div>
        <div className="how-it-works-steps">
          <div className="step-card">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Choose Your Topic</h3>
              <p>Select from 50+ categories including programming, system design, behavioral, and more</p>
            </div>
          </div>
          <div className="step-arrow">
            <ArrowRight size={32} />
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Practice Interview</h3>
              <p>Answer AI-generated questions using voice or text input in a realistic interview environment</p>
            </div>
          </div>
          <div className="step-arrow">
            <ArrowRight size={32} />
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Get Feedback</h3>
              <p>Receive detailed feedback, performance scores, and personalized course recommendations</p>
            </div>
          </div>
        </div>
      </section>

      <section className="home-section home-stats">
        <div className="stats-showcase">
          <div className="stat-showcase-item">
            <h3>10,000+</h3>
            <p>Interviews Completed</p>
          </div>
          <div className="stat-showcase-item">
            <h3>95%</h3>
            <p>User Satisfaction</p>
          </div>
          <div className="stat-showcase-item">
            <h3>50+</h3>
            <p>Question Categories</p>
          </div>
          <div className="stat-showcase-item">
            <h3>1000+</h3>
            <p>Active Users</p>
          </div>
        </div>
      </section>

      <section className="home-section home-cta">
        <div className="cta-content">
          <h2>Ready to Ace Your Next Interview?</h2>
          <p>Join thousands of successful candidates who improved their interview skills with our AI platform</p>
          {isAuthenticated ? (
            <button
              className="btn btn-primary btn-large"
              onClick={() => setCurrentPage('dashboard')}
            >
              <Target size={20} />
              Go to Dashboard
            </button>
          ) : (
            <button
              className="btn btn-primary btn-large"
              onClick={() => setShowAuth(true)}
            >
              <Rocket size={20} />
              Start Free Trial
            </button>
          )}
        </div>
      </section>
    </div>
  );
}

export default HomePage;
