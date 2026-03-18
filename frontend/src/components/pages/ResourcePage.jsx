import { Lock, ArrowRight } from 'lucide-react';

function ResourcePage({
  title,
  section,
  description,
  highlights,
  isProtected,
  isAuthenticated,
  onPrimaryAction,
  onBackHome
}) {
  return (
    <div className="resource-page">
      <section className="resource-hero">
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
      </section>

      <section className="resource-grid">
        {highlights.map((item) => (
          <article key={item.title} className="resource-card">
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

export default ResourcePage;
