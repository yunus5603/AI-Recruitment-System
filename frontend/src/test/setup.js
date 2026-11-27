import '@testing-library/jest-dom/vitest'
import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// jsdom does not implement scrolling
window.HTMLElement.prototype.scrollIntoView = vi.fn()

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})
