import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import ChatInterface from './ChatInterface'

describe('ChatInterface', () => {
  // Regression: the audio hook used to return an undefined variable, which
  // threw on every render and blanked the interview page.
  it('renders without crashing', () => {
    render(<ChatInterface />)
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument()
  })

  it('runs code through the backend and shows the output', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ success: true, output: '4\n', error: null }), { status: 200 }),
    )
    render(<ChatInterface />)

    fireEvent.change(screen.getByPlaceholderText(/write your python code/i), {
      target: { value: 'print(2 + 2)' },
    })
    fireEvent.click(screen.getByText(/run code/i))

    await waitFor(() => expect(screen.getByText('4')).toBeInTheDocument())
    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('http://localhost:8000/interview/execute-code')
    expect(JSON.parse(options.body)).toEqual({ code: 'print(2 + 2)', language: 'python' })
  })
})
