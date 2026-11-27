import { describe, expect, it } from 'vitest'
import { API_URL, apiUrl } from './api'

describe('apiUrl', () => {
  it('defaults to the local backend', () => {
    expect(API_URL).toBe('http://localhost:8000')
  })

  it('joins paths with exactly one slash', () => {
    expect(apiUrl('/health')).toBe('http://localhost:8000/health')
    expect(apiUrl('health')).toBe('http://localhost:8000/health')
  })
})
