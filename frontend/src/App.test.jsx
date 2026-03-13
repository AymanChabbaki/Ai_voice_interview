import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

const jsonResponse = (payload, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => payload,
})

const installFetchMock = ({ authenticated = false } = {}) => {
  fetch.mockImplementation(async (url, options = {}) => {
    if (url.endsWith('/health')) {
      return jsonResponse({ status: 'healthy' })
    }

    if (url.endsWith('/categories')) {
      return jsonResponse({
        top_categories: {
          'Frontend Development': 12,
          React: 8,
        },
      })
    }

    if (url.endsWith('/me')) {
      if (!authenticated) {
        return jsonResponse({ detail: 'Unauthorized' }, false, 401)
      }

      return jsonResponse({
        user_id: 7,
        username: 'ada',
        email: 'ada@example.com',
      })
    }

    if (url.includes('/profile/7/history')) {
      return jsonResponse({ history: [] })
    }

    if (url.includes('/profile/7')) {
      return jsonResponse({
        profile: {
          name: 'Ada Lovelace',
          email: 'ada@example.com',
          bio: 'First programmer',
          experience_level: 'Advanced',
          interests: ['React'],
          current_streak: 3,
          achievements: [],
          interview_count: 4,
          total_score: 320,
        },
      })
    }

    if (url.endsWith('/login') && options.method === 'POST') {
      return jsonResponse({
        access_token: 'token-123',
        user: {
          user_id: 7,
          username: 'ada',
          email: 'ada@example.com',
        },
      })
    }

    if (url.endsWith('/interview/start') && options.method === 'POST') {
      return jsonResponse({
        session_id: 'session-1',
        current_question: {
          index: 0,
          question: 'Explain the virtual DOM.',
          expected_answer: 'A representation of the UI.',
        },
        total_questions: 3,
      })
    }

    throw new Error(`Unhandled fetch request: ${url}`)
  })
}

describe('App', () => {
  it('renders the landing page and loads API status', async () => {
    installFetchMock()

    render(<App />)

    expect(screen.getByRole('heading', { name: /smart voice interviewer/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /get started free/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /watch demo/i })).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText(/connected/i)).toBeInTheDocument()
    })
    expect(screen.getByText(/master your interview skills with ai/i)).toBeInTheDocument()
  })

  it('opens the auth modal and switches to registration mode', async () => {
    installFetchMock()
    const user = userEvent.setup()

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/connected/i)).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /get started free/i }))

    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /^register$/i }))

    expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/your.email@example.com/i)).toBeInTheDocument()
  })

  it('lets an authenticated user open the interview start screen', async () => {
    installFetchMock({ authenticated: true })
    const user = userEvent.setup()
    window.localStorage.setItem('token', 'token-123')

    render(<App />)

    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /go to dashboard/i }).length).toBeGreaterThan(0)
    })

    await user.click(screen.getAllByRole('button', { name: /start interview/i })[0])

    expect(await screen.findByRole('heading', { name: /start your interview/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/select topic/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /start interview/i })).toBeDisabled()
  })
})