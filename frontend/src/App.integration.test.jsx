import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import App, { parseApiErrorMessage } from './App';

describe('App integration-style boot test', () => {
  it('renders landing content and performs initial API calls safely', async () => {
    const fetchMock = vi.fn((url) => {
      if (String(url).includes('/health')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ status: 'healthy' }),
        });
      }

      if (String(url).includes('/categories')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ top_categories: { Python: 2, DevOps: 1 } }),
        });
      }

      return Promise.resolve({
        ok: false,
        json: async () => ({ detail: 'not found' }),
      });
    });

    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('scrollTo', vi.fn());

    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /Smart Voice Interviewer/i })).toBeInTheDocument();
    });

    expect(fetchMock).toHaveBeenCalled();
  });
});

describe('parseApiErrorMessage', () => {
  it('returns fallback for invalid JSON body', async () => {
    const response = {
      json: async () => {
        throw new Error('invalid json');
      },
    };

    const message = await parseApiErrorMessage(response, 'fallback message');
    expect(message).toBe('fallback message');
  });

  it('extracts fastapi detail array messages', async () => {
    const response = {
      json: async () => ({
        detail: [{ msg: 'Password must be at least 8 characters' }],
      }),
    };

    const message = await parseApiErrorMessage(response, 'fallback message');
    expect(message).toContain('Password must be at least 8 characters');
  });
});
