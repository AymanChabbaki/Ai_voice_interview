import { Flame, History, Trophy, User, LogOut, Rocket, Compass, LayoutDashboard, Mic2, Sparkles } from 'lucide-react';

function AppNavbar({
  currentPage,
  setCurrentPage,
  isAuthenticated,
  userProfile,
  setShowHistory,
  setShowAchievements,
  setShowProfile,
  handleLogout,
  setShowAuth
}) {
  const navItems = [
    { key: 'magique', label: 'Explore', icon: <Compass size={15} />, hint: 'Discover tracks' },
    ...(isAuthenticated
      ? [
          { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={15} />, hint: 'Track progress' },
          { key: 'interview', label: 'Interview', icon: <Mic2 size={15} />, hint: 'Practice now' }
        ]
      : [])
  ];

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title header-brand" style={{ cursor: 'pointer' }} onClick={() => setCurrentPage('home')}>
          <img src="/navbarlogo.png" alt="Smart Voice Interviewer navbar logo" className="navbar-logo" />
          <div>
            <h1>Smart Voice Interviewer</h1>
            <p className="subtitle">AI-Powered Interview System</p>
          </div>
        </div>

        <div className="navbar-center">
          {navItems.map((item) => (
            <button
              key={item.key}
              className={`nav-pill nav-pill-rich ${currentPage === item.key ? 'active' : ''}`}
              onClick={() => setCurrentPage(item.key)}
            >
              <span className="nav-pill-icon">{item.icon}</span>
              <span className="nav-pill-copy">
                <strong>{item.label}</strong>
                <small>{item.hint}</small>
              </span>
            </button>
          ))}
        </div>

        <div className="navbar-signal" title="Human & Hired mode active">
          <Sparkles size={14} />
          <span>Human & Hired</span>
        </div>

        <div className="header-actions">
          {userProfile && (
            <>
              <div className="streak-badge" title={`${userProfile.current_streak || 0} day streak!`}>
                <Flame size={18} className={userProfile.current_streak > 0 ? 'flame-active' : ''} />
                <span>{userProfile.current_streak || 0}</span>
              </div>
              <button
                className="icon-button"
                onClick={() => setShowHistory(true)}
                title="Interview History"
              >
                <History size={24} />
              </button>
              <button
                className="icon-button"
                onClick={() => setShowAchievements(true)}
                title="Achievements"
              >
                <Trophy size={24} />
                {userProfile.achievements && userProfile.achievements.length > 0 && (
                  <span className="badge-count">{userProfile.achievements.length}</span>
                )}
              </button>
            </>
          )}

          {isAuthenticated ? (
            <>
              <button
                className="profile-button"
                onClick={() => setShowProfile(true)}
                title="User Profile"
              >
                {userProfile ? (
                  <span className="profile-avatar">{userProfile.name.charAt(0).toUpperCase()}</span>
                ) : (
                  <User size={20} />
                )}
              </button>
              <button
                className="logout-button"
                onClick={handleLogout}
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </>
          ) : (
            <button
              className="btn btn-primary btn-small"
              onClick={() => setShowAuth(true)}
            >
              <Rocket size={18} />
              Get Started
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

export default AppNavbar;
