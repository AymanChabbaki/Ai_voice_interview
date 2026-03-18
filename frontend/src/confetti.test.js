import confetti from 'canvas-confetti';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { celebrate, fireworks } from './confetti';

vi.mock('canvas-confetti', () => ({
  default: vi.fn(),
}));

describe('confetti helpers', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('celebrate triggers confetti bursts', () => {
    celebrate();
    vi.advanceTimersByTime(800);
    expect(confetti).toHaveBeenCalled();
  });

  it('fireworks triggers confetti bursts', () => {
    fireworks();
    vi.advanceTimersByTime(600);
    expect(confetti).toHaveBeenCalled();
  });
});
