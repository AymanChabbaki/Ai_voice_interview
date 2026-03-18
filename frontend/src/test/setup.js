import '@testing-library/jest-dom/vitest'
import { afterEach, beforeEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

vi.mock('../confetti', () => ({
  celebrate: vi.fn(),
  fireworks: vi.fn(),
}))

const speechSynthesisMock = {
  cancel: vi.fn(),
  speak: vi.fn(),
}

class SpeechSynthesisUtteranceMock {
  constructor(text) {
    this.text = text
    this.rate = 1
    this.pitch = 1
    this.volume = 1
  }
}

class MockSpeechRecognition {
  constructor() {
    this.continuous = false
    this.interimResults = false
    this.lang = 'en-US'
    this.onresult = null
    this.onerror = null
    this.onend = null
  }

  start() {}

  stop() {
    if (typeof this.onend === 'function') {
      this.onend()
    }
  }
}

beforeEach(() => {
  vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000')
  vi.stubGlobal('fetch', vi.fn())
  vi.stubGlobal('alert', vi.fn())
  vi.stubGlobal('speechSynthesis', speechSynthesisMock)
  vi.stubGlobal('SpeechSynthesisUtterance', SpeechSynthesisUtteranceMock)
  vi.stubGlobal('SpeechRecognition', MockSpeechRecognition)
  vi.stubGlobal('webkitSpeechRecognition', MockSpeechRecognition)
  window.localStorage.clear()
})

afterEach(() => {
  cleanup()
  vi.unstubAllEnvs()
  vi.unstubAllGlobals()
  vi.clearAllMocks()
})