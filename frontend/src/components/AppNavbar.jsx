import { Flame, History, Trophy, User, LogOut, Rocket } from 'lucide-react';

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
          <button
            className={`nav-pill ${currentPage === 'magique' ? 'active' : ''}`}
            onClick={() => setCurrentPage('magique')}
          >
            Explore
          </button>
          {isAuthenticated && (
            <>
              <button
                className={`nav-pill ${currentPage === 'dashboard' ? 'active' : ''}`}
                onClick={() => setCurrentPage('dashboard')}
              >
                Dashboard
              </button>
              <button
                className={`nav-pill ${currentPage === 'interview' ? 'active' : ''}`}
                onClick={() => setCurrentPage('interview')}
              >
                Interview
              </button>
            </>
          )}
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
