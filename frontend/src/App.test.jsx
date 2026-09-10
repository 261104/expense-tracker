import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import userEvent from '@testing-library/user-event'

import App from './App'

function response(body, ok = true, status = 200) {
  return { ok, status, json: async () => body }
}

const dashboardData = {
  items: [{ id: 1, amount: '125.00', category: 'Food', description: 'Lunch', payment_method: 'Card', date: '2026-09-10' }],
  page: 1,
  pages: 1,
  total: 1,
}
const statsData = {
  total_spending: '125.00',
  monthly_spending: '125.00',
  budget: '500.00',
  average_expense: '125.00',
  highest_expense: '125.00',
  lowest_expense: '125.00',
  category_breakdown: [{ category: 'Food', total: '125.00' }],
  monthly_breakdown: [{ year: 2026, month: 9, total: '125.00' }],
}

function mockDashboard() {
  global.fetch = vi.fn((url) => {
    if (url.includes('/expenses?')) return Promise.resolve(response(dashboardData))
    if (url.includes('/expenses/stats')) return Promise.resolve(response(statsData))
    if (url.includes('/budgets')) return Promise.resolve(response([]))
    return Promise.resolve(response({}))
  })
}

beforeEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
})

describe('authentication', () => {
  it('shows registration and logs in successfully', async () => {
    const user = userEvent.setup()
    global.fetch = vi.fn((url) => {
      if (url.includes('/auth/register')) return Promise.resolve(response({ id: 1, email: 'new@example.com' }, true, 201))
      if (url.includes('/auth/login')) return Promise.resolve(response({ access_token: 'test-token', token_type: 'bearer' }))
      if (url.includes('/expenses?')) return Promise.resolve(response(dashboardData))
      if (url.includes('/expenses/stats')) return Promise.resolve(response(statsData))
      if (url.includes('/budgets')) return Promise.resolve(response([]))
      return Promise.resolve(response({}))
    })
    render(<App />)

    await user.click(screen.getByRole('button', { name: /new here/i }))
    expect(screen.getByRole('heading', { name: /create your ledger/i })).toBeInTheDocument()
    await user.type(screen.getByLabelText('Email'), 'new@example.com')
    await user.type(screen.getByLabelText('Password'), 'Password123!')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => expect(screen.getByText(/your money, in focus/i)).toBeInTheDocument())
    expect(localStorage.getItem('ledger_token')).toBe('test-token')
  })

  it('shows an error for invalid login', async () => {
    const user = userEvent.setup()
    global.fetch = vi.fn(() => Promise.resolve(response({ detail: 'Incorrect email or password.' }, false, 401)))
    render(<App />)
    await user.type(screen.getByLabelText('Email'), 'wrong@example.com')
    await user.type(screen.getByLabelText('Password'), 'Password123!')
    await user.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText(/incorrect email or password/i)).toBeInTheDocument()
  })
})

describe('dashboard workflows', () => {
  it('renders protected data and logs out', async () => {
    const user = userEvent.setup()
    localStorage.setItem('ledger_token', 'test-token')
    mockDashboard()
    render(<App />)
    expect(await screen.findByText('Lunch')).toBeInTheDocument()
    expect(screen.getAllByText('INR 125.00').length).toBeGreaterThan(0)
    await user.click(screen.getByRole('button', { name: /sign out/i }))
    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
  })

  it('creates an expense from the form', async () => {
    localStorage.setItem('ledger_token', 'test-token')
    mockDashboard()
    const user = userEvent.setup()
    render(<App />)
    await screen.findByText('Lunch')
    global.fetch.mockImplementationOnce(() => Promise.resolve(response({ id: 2 }, true, 201)))
    await user.type(screen.getAllByLabelText('Amount')[0], '45.50')
    await user.type(screen.getByLabelText('Description'), 'Coffee')
    await user.click(screen.getByRole('button', { name: /add to ledger/i }))
    await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/expenses'), expect.objectContaining({ method: 'POST', headers: expect.objectContaining({ Authorization: 'Bearer test-token' }) })))
  })

  it('updates the category filter and reloads the list', async () => {
    localStorage.setItem('ledger_token', 'test-token')
    mockDashboard()
    const user = userEvent.setup()
    render(<App />)
    await screen.findByText('Lunch')
    const filter = screen.getByPlaceholderText(/filter category/i)
    fireEvent.change(filter, { target: { value: 'Food' } })
    await waitFor(() => expect(global.fetch.mock.calls.some(([url]) => url.includes('category=Food'))).toBe(true))
  })
})
