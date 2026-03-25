import { useState, useEffect } from 'react';
import './App.css';
import { celebrate, fireworks } from './confetti';
import AppNavbar from './components/AppNavbar';
import HomePage from './components/pages/HomePage';
import ResourcePage from './components/pages/ResourcePage';
import AppFooter from './components/AppFooter';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Brain, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  TrendingUp, 
  Award, 
  BookOpen, 
  Play, 
  RefreshCw,
  AlertCircle,
  Loader2,
  Target,
  ArrowRight,
  ExternalLink,
  Mic,
  MicOff,
  Volume2,
  Trophy,
  Flame,
  History,
  Timer,
  LogOut,
  User,
  Star,
  Medal,
  Zap,
  Crown,
  Sparkles,
  BarChart3,
  Calendar,
  FileText,
  Rocket,
  Shield,
  Lightbulb,
  Users
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
const CATEGORIES_RETRY_DELAY_MS = 5000;
const MAX_CATEGORIES_RETRIES = 12;
const USERNAME_REGEX = /^[a-zA-Z0-9_]{3,32}$/;

const FOOTER_PAGES = {
  'mock-interviews': {
    section: 'Platform',
    title: 'Mock Interviews',
    requiresAuth: true,
    description: 'Run realistic interview simulations with adaptive prompts and score breakdowns.',
    highlights: [
      { title: 'Role-based prompts', text: 'Practice with focused prompts aligned to your target role and level.' },
      { title: 'Timed rounds', text: 'Train response structure under realistic pressure windows.' },
      { title: 'Answer review', text: 'Get clear feedback on quality, clarity, and confidence.' }
    ]
  },
  'question-library': {
    section: 'Platform',
    title: 'Question Library',
    requiresAuth: false,
    description: 'Explore curated interview question sets across technical and behavioral categories.',
    highlights: [
      { title: 'Category coverage', text: 'Browse system design, algorithms, frontend, backend, and behavioral topics.' },
      { title: 'Difficulty levels', text: 'Move from beginner to advanced with structured progression.' },
      { title: 'Practice ready', text: 'Turn any question into a practice session in seconds.' }
    ]
  },
  'progress-dashboard': {
    section: 'Platform',
    title: 'Progress Dashboard',
    requiresAuth: true,
    description: 'Track interview performance trends and identify areas with highest improvement ROI.',
    highlights: [
      { title: 'Score trends', text: 'Visualize accuracy and communication improvement over time.' },
      { title: 'Weak spots', text: 'Find recurring pain points to prioritize your next practice cycle.' },
      { title: 'Momentum view', text: 'Monitor streaks and consistency to maintain growth cadence.' }
    ]
  },
  'achievement-paths': {
    section: 'Platform',
    title: 'Achievement Paths',
    requiresAuth: true,
    description: 'Unlock milestone paths designed to build confidence and interview consistency.',
    highlights: [
      { title: 'Milestone ladders', text: 'Complete focused challenge tracks with increasing complexity.' },
      { title: 'Skill badges', text: 'Earn visible proof-points for readiness and consistency.' },
      { title: 'Practice goals', text: 'Set weekly goals that align to your next interview timeline.' }
    ]
  },
  'interview-playbooks': {
    section: 'Resources',
    title: 'Interview Playbooks',
    requiresAuth: false,
    description: 'Structured frameworks for answering common and high-pressure interview questions.',
    highlights: [
      { title: 'Answer frameworks', text: 'Use practical structures to keep responses concise and convincing.' },
      { title: 'Scenario examples', text: 'Study high-quality examples for technical and behavioral rounds.' },
      { title: 'Execution tips', text: 'Avoid common pitfalls and communicate with stronger signal.' }
    ]
  },
  'coaching-tips': {
    section: 'Resources',
    title: 'Coaching Tips',
    requiresAuth: false,
    description: 'Micro-coaching insights that improve confidence, pacing, and interviewer engagement.',
    highlights: [
      { title: 'Delivery polish', text: 'Improve tone, pace, and confidence without sounding robotic.' },
      { title: 'Communication habits', text: 'Reduce filler and increase answer clarity in real time.' },
      { title: 'Interviewer alignment', text: 'Frame your value in language hiring teams care about.' }
    ]
  },
  'weekly-drills': {
    section: 'Resources',
    title: 'Weekly Drills',
    requiresAuth: false,
    description: 'Weekly challenge cycles to sharpen consistency and maintain interview readiness.',
    highlights: [
      { title: 'Short sprints', text: '10 to 20 minute focused drills for busy preparation windows.' },
      { title: 'Topic rotation', text: 'Cycle through technical, behavioral, and communication goals.' },
      { title: 'Measurable growth', text: 'Use small, repeatable drills to build compounding progress.' }
    ]
  },
  roadmaps: {
    section: 'Resources',
    title: 'Roadmaps',
    requiresAuth: false,
    description: 'Preparation roadmaps that guide your journey from baseline practice to interview day.',
    highlights: [
      { title: '4-week plans', text: 'Follow practical preparation timelines with clear checkpoints.' },
      { title: 'Role-specific tracks', text: 'Use plans tailored to frontend, backend, and full-stack targets.' },
      { title: 'Final-week prep', text: 'Use confidence routines before your real interview window.' }
    ]
  }
};

const PROTECTED_PAGES = ['dashboard', 'interview', 'mock-interviews', 'progress-dashboard', 'achievement-paths'];

const PAGE_TO_PATH = {
  home: '/',
  dashboard: '/dashboard',
  interview: '/interview',
  'mock-interviews': '/platform/mock-interviews',
  'question-library': '/platform/question-library',
  'progress-dashboard': '/platform/progress-dashboard',
  'achievement-paths': '/platform/achievement-paths',
  'interview-playbooks': '/resources/interview-playbooks',
  'coaching-tips': '/resources/coaching-tips',
  'weekly-drills': '/resources/weekly-drills',
  roadmaps: '/resources/roadmaps'
};

const PATH_TO_PAGE = Object.fromEntries(
  Object.entries(PAGE_TO_PATH).map(([page, path]) => [path, page])
);

export const parseApiErrorMessage = async (response, fallbackMessage) => {
  try {
    const errData = await response.json();
    const detail = errData && errData.detail;

    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const messages = detail
        .map((item) => {
          if (typeof item === 'string') return item;
          if (item && typeof item.msg === 'string') return item.msg;
          return null;
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join('; ');
      }
    }
  } catch {
    // ignore JSON parsing errors and use fallback
  }

  return fallbackMessage;
};

// Token management
const getToken = () => localStorage.getItem('token');
const setToken = (token) => localStorage.setItem('token', token);
const removeToken = () => localStorage.removeItem('token');

// API helper with auth
const apiCall = async (url, options = {}) => {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };
  
  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401) {
    removeToken();
    window.location.reload();
  }
  
  return response;
};

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  // Authentication States
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
  const [authForm, setAuthForm] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    bio: '',
    experience_level: 'Beginner'
  });

  const [categories, setCategories] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(3);
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isCategoriesLoading, setIsCategoriesLoading] = useState(true);
  const [isProfileLoading, setIsProfileLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  
  // User Profile States
  const [showProfile, setShowProfile] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({
    name: '',
    email: '',
    bio: '',
    experience_level: 'Beginner',
    interests: []
  });
  const [editMode, setEditMode] = useState(false);
  
  // New Magic Features States
  const [showAchievements, setShowAchievements] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [interviewHistory, setInterviewHistory] = useState([]);
  const [newAchievements, setNewAchievements] = useState([]);
  const [questionStartTime, setQuestionStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [showDashboard, setShowDashboard] = useState(true);
  const [showAuth, setShowAuth] = useState(false);

  const currentPage = PATH_TO_PAGE[location.pathname] || 'home';
  const setCurrentPage = (page) => {
    const nextPath = PAGE_TO_PATH[page] || PAGE_TO_PATH.home;
    navigate(nextPath);
  };

  // Check authentication on mount
  useEffect(() => {
    const token = getToken();
    if (token) {
      verifyToken();
    }
  }, []);

  useEffect(() => {
    if (!PATH_TO_PAGE[location.pathname]) {
      navigate(PAGE_TO_PATH.home, { replace: true });
    }
  }, [location.pathname, navigate]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [location.pathname]);

  const verifyToken = async () => {
    try {
      const response = await apiCall(`${API_BASE_URL}/me`);
      if (response.ok) {
        const user = await response.json();
        setCurrentUser(user);
        setIsAuthenticated(true);
        loadUserProfile(user.user_id);
      } else {
        removeToken();
      }
    } catch (err) {
      console.error('Token verification failed:', err);
      removeToken();
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: authForm.username,
          password: authForm.password
        })
      });

      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, 'Login failed'));
      }

      const data = await response.json();
      setToken(data.access_token);
      setCurrentUser(data.user);
      setIsAuthenticated(true);
      loadUserProfile(data.user.user_id);
      setAuthForm({ username: '', email: '', password: '', name: '', bio: '', experience_level: 'Beginner' });
      setShowAuth(false);
      setCurrentPage('dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const username = authForm.username.trim();
      const email = authForm.email.trim();
      const password = authForm.password;
      const name = authForm.name.trim();

      if (!USERNAME_REGEX.test(username)) {
        throw new Error('Username must be 3-32 characters and contain only letters, numbers, or underscores.');
      }

      if (password.length < 8) {
        throw new Error('Password must be at least 8 characters.');
      }

      if (name.length < 2) {
        throw new Error('Name must be at least 2 characters.');
      }

      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          email,
          password,
          name
        })
      });

      if (!response.ok) {
        throw new Error(await parseApiErrorMessage(response, 'Registration failed'));
      }

      const data = await response.json();
      setToken(data.access_token);
      setCurrentUser(data.user);
      setIsAuthenticated(true);
      loadUserProfile(data.user.user_id);
      setAuthForm({ username: '', email: '', password: '', name: '', bio: '', experience_level: 'Beginner' });
      setShowAuth(false);
      setCurrentPage('dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    removeToken();
    setIsAuthenticated(false);
    setCurrentUser(null);
    setUserProfile(null);
    setResults(null);
    setSessionId(null);
    setCurrentQuestion(null);
    setInterviewHistory([]);
  };

  const navigateFooterPage = (pageKey) => {
    const page = FOOTER_PAGES[pageKey];
    if (!page) return;

    if (page.requiresAuth && !isAuthenticated) {
      setAuthMode('login');
      setShowAuth(true);
      return;
    }

    setCurrentPage(pageKey);
  };

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        if (finalTranscript) {
          setAnswer(prev => prev + finalTranscript);
        }
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'no-speech') {
          setError('No speech detected. Please try again.');
        } else if (event.error === 'not-allowed') {
          setError('Microphone access denied. Please allow microphone access.');
        }
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, []);

  // Check API health on mount
  useEffect(() => {
    checkAPIHealth();
    loadCategories();
    loadUserProfile();
  }, []);

  // Protect dashboard and interview pages - require authentication
  useEffect(() => {
    if (!isAuthenticated && PROTECTED_PAGES.includes(currentPage)) {
      setShowAuth(true);
      setAuthMode('login');
      setCurrentPage('home');
    }
  }, [currentPage, isAuthenticated]);

  // Timer for questions
  useEffect(() => {
    if (currentQuestion && questionStartTime) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - questionStartTime) / 1000));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [currentQuestion, questionStartTime]);

  useEffect(() => {
    // Inject model-viewer once so we can render a lightweight web-hosted 3D scene in the hero.
    if (document.querySelector('script[data-model-viewer="true"]')) {
      return;
    }

    const script = document.createElement('script');
    script.type = 'module';
    script.src = 'https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js';
    script.setAttribute('data-model-viewer', 'true');
    document.head.appendChild(script);
  }, []);

  const checkAPIHealth = async () => {
    try {
      await fetch(`${API_BASE_URL}/health`);
    } catch (err) {
      setError('Cannot connect to backend API. Check the frontend API base URL configuration and backend availability.');
    }
  };

  const loadCategories = async (attempt = 0) => {
    if (attempt === 0) {
      setIsCategoriesLoading(true);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/categories`);
      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        const detail = data && typeof data.detail === 'string' ? data.detail : `HTTP ${response.status}`;

        if (response.status === 503 && attempt < MAX_CATEGORIES_RETRIES) {
          setTimeout(() => loadCategories(attempt + 1), CATEGORIES_RETRY_DELAY_MS);
          return;
        }

        throw new Error(detail);
      }

      const hasTopCategories = data && data.top_categories && typeof data.top_categories === 'object';
      const hasAllCategories = data && Array.isArray(data.categories);

      if (!hasTopCategories && !hasAllCategories) {
        throw new Error('Invalid categories payload from API');
      }

      const categoryNames = hasAllCategories
        ? data.categories
        : Object.keys(data.top_categories);

      setCategories(categoryNames.map(name => ({ name })));
      setIsCategoriesLoading(false);
    } catch (err) {
      console.error('Failed to load categories:', err);
      setCategories([]);
      setIsCategoriesLoading(false);
    }
  };

  // Profile Management Functions
  const loadUserProfile = async (userId = null) => {
    const id = userId || (currentUser && currentUser.user_id);
    if (id) {
      setIsProfileLoading(true);

      try {
        const response = await apiCall(`${API_BASE_URL}/profile/${id}`);
        if (response.ok) {
          const data = await response.json();
          setUserProfile(data.profile);
          setProfileForm({
            name: data.profile.name,
            email: data.profile.email,
            bio: data.profile.bio || '',
            experience_level: data.profile.experience_level || 'Beginner',
            interests: data.profile.interests || []
          });
          
          // Load interview history
          const historyResponse = await apiCall(`${API_BASE_URL}/profile/${id}/history`);
          if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            setInterviewHistory(historyData.history || []);
          }
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
      } finally {
        setIsProfileLoading(false);
      }
    }
  };

  const updateProfile = async () => {
    if (!currentUser) return;

    setLoading(true);
    try {
      const response = await apiCall(`${API_BASE_URL}/profile/${currentUser.user_id}`, {
        method: 'PUT',
        body: JSON.stringify(profileForm)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setUserProfile(data.profile);
        setEditMode(false);
        setError(null);
      } else {
        setError(data.detail || 'Failed to update profile');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInterestAdd = (interest) => {
    if (interest && !profileForm.interests.includes(interest)) {
      setProfileForm({
        ...profileForm,
        interests: [...profileForm.interests, interest]
      });
    }
  };

  const handleInterestRemove = (interest) => {
    setProfileForm({
      ...profileForm,
      interests: profileForm.interests.filter(i => i !== interest)
    });
  };

  const startInterview = async () => {
    if (!selectedTopic) {
      setError('Please select a topic');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestBody = { 
        topic: selectedTopic, 
        num_questions: numQuestions
      };
      
      // Add user_id if authenticated
      if (currentUser) {
        requestBody.user_id = currentUser.user_id;
      }
      
      const response = await apiCall(`${API_BASE_URL}/interview/start`, {
        method: 'POST',
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start interview');
      }

      setSessionId(data.session_id);
      setCurrentQuestion({
        ...data.current_question,
        number: 1,
        total: data.total_questions
      });
      setQuestionStartTime(Date.now());
      setElapsedTime(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim()) {
      setError('Please provide an answer');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiCall(`${API_BASE_URL}/interview/answer`, {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          question_index: currentQuestion.index,
          answer: answer
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to submit answer');
      }

      // Show result briefly
      alert(`${data.status}\nScore: ${(data.score * 100).toFixed(1)}%`);

      setAnswer('');

      if (data.completed) {
        // Interview completed, load results
        loadResults();
      } else {
        // Move to next question
        setCurrentQuestion({
          ...data.next_question,
          number: currentQuestion.number + 1,
          total: currentQuestion.total
        });
        setQuestionStartTime(Date.now());
        setElapsedTime(0);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadResults = async () => {
    setLoading(true);
    try {
      const response = await apiCall(`${API_BASE_URL}/interview/results/${sessionId}`);
      const data = await response.json();
      setResults(data);
      setCurrentQuestion(null);
      
      // Celebration if passed!
      if (data.pass_rate >= 60) {
        setTimeout(() => fireworks(), 300);
      }
      
      // Update user profile and check achievements
      if (currentUser) {
        const updateResponse = await apiCall(`${API_BASE_URL}/profile/${currentUser.user_id}/update-after-interview`, {
          method: 'POST',
          body: JSON.stringify({
            session_id: sessionId,
            topic: data.topic,
            pass_rate: data.pass_rate,
            average_score: data.average_score,
            total_questions: data.total_questions,
            passed: data.passed
          })
        });
        
        if (updateResponse.ok) {
          const updateData = await updateResponse.json();
          setUserProfile(updateData.profile);
          
          // Show achievements if any
          if (updateData.new_achievements && updateData.new_achievements.length > 0) {
            setNewAchievements(updateData.new_achievements);
            setTimeout(() => celebrate(), 500);
          }
          
          // Reload history
          loadUserProfile();
        }
      }
    } catch (err) {
      setError('Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const resetInterview = () => {
    setSessionId(null);
    setCurrentQuestion(null);
    setAnswer('');
    setResults(null);
    setError(null);
    setSelectedTopic('');
    setNewAchievements([]);
    setQuestionStartTime(null);
    setElapsedTime(0);
    setCurrentPage('dashboard');
    if (isListening && recognition) {
      recognition.stop();
      setIsListening(false);
    }
  };

  const toggleListening = () => {
    if (!recognition) {
      setError('Speech recognition is not supported in your browser.');
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      setError(null);
      recognition.start();
      setIsListening(true);
    }
  };

  const speakQuestion = () => {
    if (!currentQuestion) return;
    
    if ('speechSynthesis' in window) {
      // Stop any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(currentQuestion.question);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    } else {
      setError('Text-to-speech is not supported in your browser.');
    }
  };

  return (
    <div className="app">
      <AppNavbar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        isAuthenticated={isAuthenticated}
        userProfile={userProfile}
        setShowHistory={setShowHistory}
        setShowAchievements={setShowAchievements}
        setShowProfile={setShowProfile}
        handleLogout={handleLogout}
        setShowAuth={setShowAuth}
      />

      <main className="main">
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <span><strong>Error:</strong> {error}</span>
          </div>
        )}

        {currentPage === 'home' && !sessionId && !results && (
          <HomePage
            isAuthenticated={isAuthenticated}
            userProfile={userProfile}
            setCurrentPage={setCurrentPage}
            setShowDashboard={setShowDashboard}
            setShowAuth={setShowAuth}
          />
        )}

        {FOOTER_PAGES[currentPage] && !sessionId && !results && (
          <ResourcePage
            pageKey={currentPage}
            section={FOOTER_PAGES[currentPage].section}
            title={FOOTER_PAGES[currentPage].title}
            description={FOOTER_PAGES[currentPage].description}
            highlights={FOOTER_PAGES[currentPage].highlights}
            isProtected={FOOTER_PAGES[currentPage].requiresAuth}
            isAuthenticated={isAuthenticated}
            onPrimaryAction={() => {
              if (FOOTER_PAGES[currentPage].requiresAuth && !isAuthenticated) {
                setAuthMode('login');
                setShowAuth(true);
                return;
              }

              if (currentPage === 'mock-interviews') {
                setCurrentPage('interview');
                return;
              }

              if (currentPage === 'progress-dashboard') {
                setCurrentPage('dashboard');
                return;
              }

              if (currentPage === 'achievement-paths') {
                setShowAchievements(true);
                return;
              }
            }}
            onBackHome={() => setCurrentPage('home')}
          />
        )}

        {/* Dashboard - Show when user navigates to dashboard */}
        {currentPage === 'dashboard' && !sessionId && !results && (
          <>
            {/* Dashboard for logged-in users */}
            {isAuthenticated && isProfileLoading && !userProfile && (
              <div className="dashboard dashboard-skeleton">
                <div className="dashboard-welcome skeleton-card">
                  <div className="welcome-content">
                    <div className="skeleton skeleton-line skeleton-line-title" />
                    <div className="skeleton skeleton-line skeleton-line-subtitle" />
                  </div>
                  <div className="skeleton skeleton-btn" />
                </div>

                <div className="stats-grid">
                  {[1, 2, 3, 4].map((item) => (
                    <div key={item} className="stat-card stat-card-skeleton">
                      <div className="skeleton skeleton-circle" />
                      <div className="skeleton skeleton-line" />
                      <div className="skeleton skeleton-line skeleton-line-short" />
                    </div>
                  ))}
                </div>

                <div className="dashboard-section skeleton-card">
                  <div className="skeleton skeleton-line skeleton-line-title" />
                  <div className="skeleton-list">
                    {[1, 2, 3].map((item) => (
                      <div key={item} className="skeleton skeleton-row" />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {isAuthenticated && userProfile && (
              <div className="dashboard">
                {/* Welcome Section */}
                <div className="dashboard-welcome">
                  <div className="welcome-content">
                    <h2>Welcome back, {userProfile.name}! 👋</h2>
                    <p>Ready to sharpen your skills today?</p>
                  </div>
                  <button 
                    className="btn btn-primary btn-large"
                    onClick={() => setCurrentPage('interview')}
                  >
                    <Play size={20} />
                    Start New Interview
                  </button>
                </div>

                {/* Stats Grid */}
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-icon-wrapper" style={{background: 'rgba(99, 102, 241, 0.15)'}}>
                      <Target size={24} style={{color: 'var(--primary)'}} />
                    </div>
                    <div className="stat-content">
                      <h3>{userProfile.interview_count || 0}</h3>
                      <p>Total Interviews</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon-wrapper" style={{background: 'rgba(16, 185, 129, 0.15)'}}>
                      <CheckCircle2 size={24} style={{color: 'var(--success)'}} />
                    </div>
                    <div className="stat-content">
                      <h3>
                        {userProfile.interview_count && userProfile.total_score 
                          ? `${(userProfile.total_score / userProfile.interview_count).toFixed(1)}%` 
                          : '0%'}
                      </h3>
                      <p>Pass Rate</p>
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon-wrapper" style={{background: 'rgba(245, 158, 11, 0.15)'}}>
                      <Flame size={24} style={{color: 'var(--warning)'}} />
                    </div>
                    <div className="stat-content">
                      <h3>{userProfile.current_streak || 0}</h3>
                      <p>Day Streak</p>
                    </div>
                  </div>



                  <div className="stat-card">
                    <div className="stat-icon-wrapper" style={{background: 'rgba(139, 92, 246, 0.15)'}}>
                      <Trophy size={24} style={{color: '#8b5cf6'}} />
                    </div>
                    <div className="stat-content">
                      <h3>{userProfile.achievements ? userProfile.achievements.length : 0}</h3>
                      <p>Achievements</p>
                    </div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="dashboard-section">
                  <div className="section-header">
                    <div className="section-title">
                      <History size={24} />
                      <h3>Recent Activity</h3>
                    </div>
                    <button 
                      className="btn btn-secondary btn-small"
                      onClick={() => setShowHistory(true)}
                    >
                      View All
                      <ArrowRight size={16} />
                    </button>
                  </div>
                  
                  {interviewHistory.length > 0 ? (
                    <div className="recent-activity-list">
                      {interviewHistory.slice(0, 3).map((item, idx) => (
                        <div key={idx} className="activity-item">
                          <div className="activity-icon">
                            {item.pass_rate >= 60 ? (
                              <CheckCircle2 size={20} style={{color: 'var(--success)'}} />
                            ) : (
                              <XCircle size={20} style={{color: 'var(--error)'}} />
                            )}
                          </div>
                          <div className="activity-content">
                            <h4>{item.topic}</h4>
                            <p>{item.questions_count} questions • Score: {item.pass_rate.toFixed(1)}%</p>
                          </div>
                          <div className="activity-date">
                            <Calendar size={16} />
                            <span>{new Date(item.date).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <FileText size={48} style={{opacity: 0.3}} />
                      <p>No interviews yet. Start your first one!</p>
                    </div>
                  )}
                </div>

                {/* Quick Actions */}
                <div className="dashboard-section">
                  <div className="section-header">
                    <div className="section-title">
                      <Rocket size={24} />
                      <h3>Quick Actions</h3>
                    </div>
                  </div>
                  
                  <div className="quick-actions-grid">
                    <div className="action-card" onClick={() => setCurrentPage('interview')}>
                      <Play size={32} />
                      <h4>Start Interview</h4>
                      <p>Begin a new practice session</p>
                    </div>
                    
                    <div className="action-card" onClick={() => setShowAchievements(true)}>
                      <Trophy size={32} />
                      <h4>Achievements</h4>
                      <p>View your milestones</p>
                    </div>
                    
                    <div className="action-card" onClick={() => setShowProfile(true)}>
                      <User size={32} />
                      <h4>Profile</h4>
                      <p>Update your information</p>
                    </div>
                    
                    <div className="action-card" onClick={() => setShowHistory(true)}>
                      <BarChart3 size={32} />
                      <h4>History</h4>
                      <p>Review past interviews</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Hero for non-logged users */}
            {!isAuthenticated && (
              <div className="hero-section">
                <div className="hero-content">
                  <div className="hero-badge">
                    <Sparkles size={16} />
                    <span>AI-Powered Interview System</span>
                  </div>
                  <h1>Master Your Interview Skills</h1>
                  <p className="hero-subtitle">
                    Practice with AI-driven mock interviews, get instant feedback, 
                    and track your progress to land your dream job.
                  </p>
                  <div className="hero-cta">
                    <button 
                      className="btn btn-primary btn-large"
                      onClick={() => setShowAuth(true)}
                    >
                      Get Started Free
                      <ArrowRight size={20} />
                    </button>
                  </div>
                </div>

                {/* Features Grid */}
                <div className="features-grid">
                  <div className="feature-card">
                    <div className="feature-icon">
                      <Brain size={32} />
                    </div>
                    <h3>AI-Powered Questions</h3>
                    <p>Get intelligent questions tailored to your experience level and interests</p>
                  </div>

                  <div className="feature-card">
                    <div className="feature-icon">
                      <Mic size={32} />
                    </div>
                    <h3>Voice Recognition</h3>
                    <p>Practice with voice input and text-to-speech for realistic interview experience</p>
                  </div>

                  <div className="feature-card">
                    <div className="feature-icon">
                      <TrendingUp size={32} />
                    </div>
                    <h3>Track Progress</h3>
                    <p>Monitor your improvement with detailed analytics and performance metrics</p>
                  </div>

                  <div className="feature-card">
                    <div className="feature-icon">
                      <Award size={32} />
                    </div>
                    <h3>Earn Achievements</h3>
                    <p>Unlock badges and maintain streaks to stay motivated on your journey</p>
                  </div>

                  <div className="feature-card">
                    <div className="feature-icon">
                      <Target size={32} />
                    </div>
                    <h3>Multiple Categories</h3>
                    <p>Practice across various topics from programming to system design</p>
                  </div>

                  <div className="feature-card">
                    <div className="feature-icon">
                      <Lightbulb size={32} />
                    </div>
                    <h3>Instant Feedback</h3>
                    <p>Receive immediate AI-generated feedback and personalized recommendations</p>
                  </div>
                </div>

                {/* Social Proof */}
                <div className="social-proof">
                  <div className="proof-stat">
                    <h3>1000+</h3>
                    <p>Interviews Conducted</p>
                  </div>
                  <div className="proof-stat">
                    <h3>95%</h3>
                    <p>Satisfaction Rate</p>
                  </div>
                  <div className="proof-stat">
                    <h3>50+</h3>
                    <p>Question Categories</p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Start Interview Screen */}
        {currentPage === 'interview' && !sessionId && !results && (
          <div className="start-screen">
            <button 
              className="btn btn-secondary"
              onClick={() => setCurrentPage('dashboard')}
              style={{marginBottom: '1.5rem'}}
            >
              <ArrowRight size={18} style={{transform: 'rotate(180deg)'}} />
              Back to Dashboard
            </button>
            
            <div className="card main-card">
              <div className="card-header">
                <Target size={28} className="card-icon" />
                <h2>Start Your Interview</h2>
              </div>
              
              <div className="form-group">
                <label htmlFor="topic">
                  <BookOpen size={18} />
                  Select Topic
                </label>
                <select
                  id="topic"
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="select"
                  disabled={isCategoriesLoading}
                >
                  <option value="">{isCategoriesLoading ? 'Loading topics...' : '-- Choose a topic --'}</option>
                  {categories.map((cat) => (
                    <option key={cat.name} value={cat.name}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="numQuestions">
                  <Clock size={18} />
                  Number of Questions
                </label>
                <input
                  id="numQuestions"
                  type="number"
                  min="1"
                  max="10"
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                  className="input"
                />
              </div>

              <button
                onClick={startInterview}
                disabled={loading || !selectedTopic}
                className="btn btn-primary btn-large"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Start Interview
                  </>
                )}
              </button>
            </div>

            <div className="info-card">
              <div className="info-header">
                <BookOpen size={24} />
                <h3>Available Categories</h3>
              </div>
              <div className="categories-grid">
                {isCategoriesLoading ? (
                  Array.from({ length: 8 }).map((_, idx) => (
                    <div key={idx} className="category-item category-item-skeleton">
                      <div className="skeleton skeleton-chip" />
                      <div className="skeleton skeleton-line" />
                    </div>
                  ))
                ) : (
                  categories.slice(0, 8).map((cat) => (
                    <div key={cat.name} className="category-item">
                      <Target size={16} className="category-icon" />
                      <span>{cat.name}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Interview Screen */}
        {currentQuestion && (
          <div className="interview-screen">
            <div className="progress-section">
              <div className="progress-info">
                <Clock size={20} />
                <span className="progress-text">
                  Question {currentQuestion.number} of {currentQuestion.total}
                </span>
              </div>
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{ width: `${(currentQuestion.number / currentQuestion.total) * 100}%` }}
                />
              </div>
              <div className="progress-percentage">
                {Math.round((currentQuestion.number / currentQuestion.total) * 100)}%
              </div>
            </div>

            <div className="card question-card">
              <div className="question-header">
                <div className="question-badges">
                  <span className="badge badge-category">
                    <BookOpen size={14} />
                    {currentQuestion.category}
                  </span>
                  <span className="badge badge-difficulty">
                    <TrendingUp size={14} />
                    {currentQuestion.difficulty}
                  </span>
                </div>
                <div className="timer-display">
                  <Timer size={18} />
                  <span>{Math.floor(elapsedTime / 60)}:{String(elapsedTime % 60).padStart(2, '0')}</span>
                </div>
              </div>

              <div className="question-content">
                <Brain size={28} className="question-icon" />
                <h3 className="question-text">{currentQuestion.question}</h3>
                <button 
                  onClick={speakQuestion}
                  className="btn-speak"
                  title="Listen to question"
                >
                  <Volume2 size={20} />
                </button>
              </div>

              <div className="form-group">
                <label htmlFor="answer">
                  <Target size={18} />
                  Your Answer
                </label>
                <div className="answer-input-container">
                  <textarea
                    id="answer"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder={isListening ? "Listening... Speak now" : "Type or click the microphone to speak your answer"}
                    rows="8"
                    className={`textarea ${isListening ? 'listening' : ''}`}
                  />
                  <button
                    onClick={toggleListening}
                    className={`btn-mic ${isListening ? 'listening' : ''}`}
                    title={isListening ? "Stop recording" : "Start recording"}
                    type="button"
                  >
                    {isListening ? <MicOff size={24} /> : <Mic size={24} />}
                  </button>
                </div>
                {isListening && (
                  <div className="listening-indicator">
                    <span className="pulse"></span>
                    <span>Recording...</span>
                  </div>
                )}
              </div>

              <button
                onClick={submitAnswer}
                disabled={loading || !answer.trim()}
                className="btn btn-primary btn-large"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={20} />
                    Submit Answer
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Results Screen */}
        {results && (
          <div className="results-screen">
            <div className="card results-card">
              <div className="results-header">
                <Award size={32} className="results-icon" />
                <h2>Interview Results</h2>
              </div>

              <div className="results-summary">
                <div className="stat-card stat-primary">
                  <TrendingUp size={24} className="stat-icon" />
                  <div className="stat-value">{results.pass_rate.toFixed(1)}%</div>
                  <div className="stat-label">Pass Rate</div>
                </div>
                <div className="stat-card stat-success">
                  <CheckCircle2 size={24} className="stat-icon" />
                  <div className="stat-value">{results.passed}/{results.total_questions}</div>
                  <div className="stat-label">Passed</div>
                </div>
                <div className="stat-card stat-info">
                  <Target size={24} className="stat-icon" />
                  <div className="stat-value">{(results.average_score * 100).toFixed(1)}%</div>
                  <div className="stat-label">Avg Score</div>
                </div>
              </div>

              <div className={`result-status status-${results.summary.status.toLowerCase()}`}>
                {results.summary.status === 'PASS' ? (
                  <CheckCircle2 size={32} className="status-icon" />
                ) : (
                  <XCircle size={32} className="status-icon" />
                )}
                <div>
                  <h3>{results.summary.status}</h3>
                  <p>{results.summary.message}</p>
                </div>
              </div>

              <div className="answers-list">
                <h3>
                  <BookOpen size={22} />
                  Question-by-Question Results
                </h3>
                {results.answers.map((ans, idx) => (
                  <div key={idx} className={`answer-item ${ans.passed ? 'passed' : 'failed'}`}>
                    <div className="answer-header">
                      <span className="answer-number">Q{idx + 1}</span>
                      <span className={`answer-status ${ans.passed ? 'pass' : 'fail'}`}>
                        {ans.passed ? (
                          <>
                            <CheckCircle2 size={16} />
                            PASS
                          </>
                        ) : (
                          <>
                            <XCircle size={16} />
                            FAIL
                          </>
                        )}
                      </span>
                      <span className="answer-score">{(ans.score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="answer-question"><strong>Question:</strong> {ans.question}</div>
                    <div className="answer-user-response">
                      <strong>Your Answer:</strong>
                      <div className="user-answer-text">{ans.user_answer || 'No answer provided'}</div>
                    </div>
                    <div className="answer-correct-response">
                      <strong>Expected Answer:</strong>
                      <div className="correct-answer-text">{ans.correct_answer || 'Not available'}</div>
                    </div>
                    <div className="answer-details">
                      <span className="badge">
                        <BookOpen size={12} />
                        {ans.category}
                      </span>
                      <span className="badge">
                        <TrendingUp size={12} />
                        {ans.difficulty}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {results.recommendations.length > 0 && (
                <div className="recommendations">
                  <h3>
                    <Brain size={22} />
                    AI-Recommended Courses
                  </h3>
                  <p className="rec-subtitle">Based on your performance, these courses will help you improve</p>
                  {results.recommendations.map((rec, idx) => (
                    <div key={idx} className="recommendation-item">
                      <div className="rec-header">
                        <Award size={20} className="rec-icon" />
                        <h4>{rec.course_title}</h4>
                        <span className="relevance-badge">
                          {(rec.relevance_score * 100).toFixed(0)}% Match
                        </span>
                      </div>
                      <div className="rec-category">
                        <span className="badge">
                          <Target size={12} />
                          {rec.category}
                        </span>
                      </div>
                      <div className="rec-details">
                        <span className="rec-info">
                          <Target size={14} />
                          {rec.platform}
                        </span>
                        <span className="rec-info">
                          <BookOpen size={14} />
                          {rec.provider}
                        </span>
                        <span className="rec-info">
                          <TrendingUp size={14} />
                          {rec.difficulty}
                        </span>
                      </div>
                      <a href={rec.url} target="_blank" rel="noopener noreferrer" className="btn btn-small">
                        <span>View Course</span>
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  ))}
                </div>
              )}

              <button onClick={resetInterview} className="btn btn-secondary btn-large">
                <RefreshCw size={20} />
                Start New Interview
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Profile Modal */}
      {showProfile && (
        <div className="modal-overlay" onClick={() => setShowProfile(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editMode ? 'Edit Profile' : 'User Profile'}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowProfile(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              {editMode ? (
                <div className="profile-form">
                  <div className="form-group">
                    <label>Name *</label>
                    <input
                      type="text"
                      className="input"
                      value={profileForm.name}
                      onChange={(e) => setProfileForm({...profileForm, name: e.target.value})}
                      placeholder="Enter your name"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Email *</label>
                    <input
                      type="email"
                      className="input"
                      value={profileForm.email}
                      onChange={(e) => setProfileForm({...profileForm, email: e.target.value})}
                      placeholder="Enter your email"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Bio</label>
                    <textarea
                      className="input"
                      value={profileForm.bio}
                      onChange={(e) => setProfileForm({...profileForm, bio: e.target.value})}
                      placeholder="Tell us about yourself"
                      rows="3"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Experience Level</label>
                    <select
                      className="select"
                      value={profileForm.experience_level}
                      onChange={(e) => setProfileForm({...profileForm, experience_level: e.target.value})}
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                      <option value="Expert">Expert</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label>Interests</label>
                    <div className="interests-input">
                      <input
                        type="text"
                        className="input"
                        placeholder="Add an interest (press Enter)"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && e.target.value) {
                            handleInterestAdd(e.target.value);
                            e.target.value = '';
                          }
                        }}
                      />
                    </div>
                    <div className="interests-list">
                      {profileForm.interests.map((interest, idx) => (
                        <span key={idx} className="interest-tag">
                          {interest}
                          <button onClick={() => handleInterestRemove(interest)}>×</button>
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="modal-actions">
                    <button
                      className="btn btn-primary"
                      onClick={updateProfile}
                      disabled={loading}
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setEditMode(false);
                        setProfileForm({
                          name: userProfile.name,
                          email: userProfile.email,
                          bio: userProfile.bio || '',
                          experience_level: userProfile.experience_level || 'Beginner',
                          interests: userProfile.interests || []
                        });
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="profile-view">
                  <div className="profile-avatar-large">
                    {userProfile.name.charAt(0).toUpperCase()}
                  </div>
                  
                  <div className="profile-info">
                    <div className="profile-field">
                      <strong>Name:</strong>
                      <span>{userProfile.name}</span>
                    </div>
                    
                    <div className="profile-field">
                      <strong>Email:</strong>
                      <span>{userProfile.email}</span>
                    </div>
                    
                    {userProfile.bio && (
                      <div className="profile-field">
                        <strong>Bio:</strong>
                        <span>{userProfile.bio}</span>
                      </div>
                    )}
                    
                    <div className="profile-field">
                      <strong>Experience Level:</strong>
                      <span className="badge">{userProfile.experience_level}</span>
                    </div>
                    
                    {userProfile.interests && userProfile.interests.length > 0 && (
                      <div className="profile-field">
                        <strong>Interests:</strong>
                        <div className="interests-list">
                          {userProfile.interests.map((interest, idx) => (
                            <span key={idx} className="interest-tag">{interest}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="profile-stats">
                      <div className="stat-item">
                        <strong>Interviews:</strong>
                        <span>{userProfile.interview_count || 0}</span>
                      </div>
                      <div className="stat-item">
                        <strong>Average Score:</strong>
                        <span>{((userProfile.total_score || 0) / Math.max(userProfile.interview_count || 1, 1)).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="modal-actions">
                    <button
                      className="btn btn-primary"
                      onClick={() => setEditMode(true)}
                    >
                      Edit Profile
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Achievements Modal */}
      {showAchievements && userProfile && (
        <div className="modal-overlay" onClick={() => setShowAchievements(false)}>
          <div className="modal-content achievements-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="header-with-icon">
                <Trophy size={28} className="header-icon-badge" />
                <h2>Your Achievements</h2>
              </div>
              <button className="modal-close" onClick={() => setShowAchievements(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="achievements-grid">
                {[
                  {id: 'first_interview', title: 'Getting Started', description: 'Complete your first interview', icon: Sparkles},
                  {id: 'perfect_score', title: 'Perfect Score', description: 'Achieve 100% pass rate', icon: Star},
                  {id: 'ten_interviews', title: 'Dedicated Learner', description: 'Complete 10 interviews', icon: Award},
                  {id: 'five_day_streak', title: 'On Fire', description: '5 day streak maintained', icon: Flame},
                  {id: 'fifty_interviews', title: 'Master Learner', description: 'Complete 50 interviews', icon: Crown}
                ].map(achievement => {
                  const unlocked = userProfile.achievements && userProfile.achievements.includes(achievement.id);
                  const IconComponent = achievement.icon;
                  return (
                    <div key={achievement.id} className={`achievement-card ${unlocked ? 'unlocked' : 'locked'}`}>
                      <div className="achievement-icon">
                        {unlocked ? (
                          <IconComponent size={32} className="achievement-icon-unlocked" />
                        ) : (
                          <Medal size={32} className="achievement-icon-locked" />
                        )}
                      </div>
                      <div className="achievement-info">
                        <h4>{unlocked ? achievement.title : 'Locked'}</h4>
                        <p>{unlocked ? achievement.description : 'Keep going to unlock!'}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History Modal */}
      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📚 Interview History</h2>
              <button className="modal-close" onClick={() => setShowHistory(false)}>×</button>
            </div>
            <div className="modal-body">
              {interviewHistory.length === 0 ? (
                <p className="empty-state">No interviews yet. Start your first interview!</p>
              ) : (
                <div className="history-list">
                  {interviewHistory.slice().reverse().map((item, idx) => (
                    <div key={idx} className="history-item">
                      <div className="history-header">
                        <h4>{item.topic}</h4>
                        <span className={`history-badge ${item.pass_rate >= 60 ? 'pass' : 'fail'}`}>
                          {item.pass_rate >= 60 ? 'PASSED' : 'FAILED'}
                        </span>
                      </div>
                      <div className="history-details">
                        <span><Clock size={14} /> {new Date(item.date).toLocaleDateString()}</span>
                        <span><Target size={14} /> {item.pass_rate.toFixed(1)}%</span>
                        <span><BookOpen size={14} /> {item.passed}/{item.questions_count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* New Achievements Notification */}
      {newAchievements.length > 0 && (
        <div className="achievement-notification">
          <div className="achievement-notification-content">
            <Trophy size={32} />
            <div>
              <h3>New Achievement Unlocked!</h3>
              {newAchievements.map((ach, idx) => (
                <p key={idx}><strong>{ach.title}</strong> - {ach.description}</p>
              ))}
            </div>
            <button onClick={() => setNewAchievements([])}>×</button>
          </div>
        </div>
      )}

      {/* Authentication Modal */}
      {showAuth && !isAuthenticated && (
        <div className="modal-overlay" onClick={() => setShowAuth(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{maxWidth: '500px'}}>
            <div className="modal-header">
              <h2>{authMode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
              <button className="modal-close" onClick={() => setShowAuth(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="auth-tabs">
                <button
                  className={authMode === 'login' ? 'active' : ''}
                  onClick={() => { setAuthMode('login'); setError(null); }}
                >
                  Login
                </button>
                <button
                  className={authMode === 'register' ? 'active' : ''}
                  onClick={() => { setAuthMode('register'); setError(null); }}
                >
                  Register
                </button>
              </div>

              {error && (
                <div className="error-message" style={{marginTop: '1rem'}}>
                  <AlertCircle size={20} />
                  <span>{error}</span>
                </div>
              )}

              {authMode === 'login' ? (
                <form onSubmit={handleLogin} className="auth-form">
                  <div className="form-group">
                    <label>Username</label>
                    <input
                      type="text"
                      value={authForm.username}
                      onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}
                      required
                      placeholder="Enter your username"
                    />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input
                      type="password"
                      value={authForm.password}
                      onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                      required
                      placeholder="Enter your password"
                    />
                  </div>
                  <button type="submit" className="auth-submit" disabled={loading}>
                    {loading ? (
                      <>
                        <Loader2 size={20} className="spin" />
                        <span>Logging in...</span>
                      </>
                    ) : (
                      'Login'
                    )}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleRegister} className="auth-form">
                  <div className="form-group">
                    <label>Username *</label>
                    <input
                      type="text"
                      value={authForm.username}
                      onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}
                      required
                      placeholder="Choose a username"
                    />
                  </div>
                  <div className="form-group">
                    <label>Email *</label>
                    <input
                      type="email"
                      value={authForm.email}
                      onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                      required
                      placeholder="your.email@example.com"
                    />
                  </div>
                  <div className="form-group">
                    <label>Password *</label>
                    <input
                      type="password"
                      value={authForm.password}
                      onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                      required
                      minLength="8"
                      placeholder="At least 8 characters"
                    />
                  </div>
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input
                      type="text"
                      value={authForm.name}
                      onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                      required
                      placeholder="Your full name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Bio</label>
                    <textarea
                      value={authForm.bio}
                      onChange={(e) => setAuthForm({ ...authForm, bio: e.target.value })}
                      placeholder="Tell us about yourself..."
                      rows="3"
                    />
                  </div>
                  <div className="form-group">
                    <label>Experience Level *</label>
                    <select
                      value={authForm.experience_level}
                      onChange={(e) => setAuthForm({ ...authForm, experience_level: e.target.value })}
                      required
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                      <option value="Expert">Expert</option>
                    </select>
                  </div>
                  <button type="submit" className="auth-submit" disabled={loading}>
                    {loading ? (
                      <>
                        <Loader2 size={20} className="spin" />
                        <span>Creating account...</span>
                      </>
                    ) : (
                      'Register'
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      )}

      <AppFooter
        isAuthenticated={isAuthenticated}
        setCurrentPage={setCurrentPage}
        setShowAuth={setShowAuth}
        onFooterNavigate={navigateFooterPage}
      />
    </div>
  );
}

export default App;

