import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import CandidateList from './CandidateList'

const candidate = {
  candidate_name: 'Jane Doe',
  match_score: 92.5,
  matched_skills: ['Python', 'FastAPI'],
  missing_skills: ['Kubernetes'],
  justification: 'Strong backend experience.',
  qualified: true,
}

describe('CandidateList', () => {
  it('shows an empty state', () => {
    render(<CandidateList candidates={[]} />)
    expect(screen.getByText(/no candidates match/i)).toBeInTheDocument()
  })

  it('renders score, skills and justification', () => {
    render(<CandidateList candidates={[candidate]} />)
    expect(screen.getByText('Jane Doe')).toBeInTheDocument()
    expect(screen.getByText('92.5%')).toBeInTheDocument()
    expect(screen.getByText(/Python/)).toBeInTheDocument()
    expect(screen.getByText(/Kubernetes/)).toBeInTheDocument()
    expect(screen.getByText('Strong backend experience.')).toBeInTheDocument()
  })

  it('falls back to a placeholder name', () => {
    render(<CandidateList candidates={[{ ...candidate, candidate_name: null, missing_skills: [] }]} />)
    expect(screen.getByText('Unknown Candidate')).toBeInTheDocument()
    expect(screen.queryByText(/Missing Skills/)).not.toBeInTheDocument()
  })
})
