import { useCallback, useEffect, useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Education', 'Travel', 'Other']
const blankExpense = { amount: '', category: 'Food', description: '', payment_method: 'Card', date: new Date().toISOString().slice(0, 10) }

async function request(path, options = {}, token) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || 'The request could not be completed.')
  }
  return response.status === 204 ? null : response.json()
}

function AuthScreen({ onLogin }) {
  const [registering, setRegistering] = useState(false)
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      if (registering) await request('/auth/register', { method: 'POST', body: JSON.stringify(form) })
      const body = new URLSearchParams({ username: form.email, password: form.password })
      const response = await fetch(`${API_URL}/auth/login`, { method: 'POST', body })
      if (!response.ok) throw new Error('Incorrect email or password.')
      onLogin((await response.json()).access_token)
    } catch (requestError) { setError(requestError.message) } finally { setBusy(false) }
  }
  return <main className="auth-shell"><div className="auth-copy"><span className="eyebrow">PERSONAL FINANCE / 01</span><h1>Make every rupee tell a story.</h1><p>A calm, clear place to understand where your money goes and what comes next.</p></div><form className="auth-card" onSubmit={submit}><div className="brand-mark">ledger<span>.</span></div><h2>{registering ? 'Create your ledger' : 'Welcome back'}</h2><p className="muted">{registering ? 'Start with a private account.' : 'Sign in to your spending overview.'}</p><label>Email<input type="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label><label>Password<input type="password" minLength="8" required value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>{error && <div className="error">{error}</div>}<button className="primary" disabled={busy}>{busy ? 'Working...' : registering ? 'Create account' : 'Sign in'}</button><button className="text-button" type="button" onClick={() => { setRegistering(!registering); setError('') }}>{registering ? 'Already have an account? Sign in' : 'New here? Create an account'}</button></form></main>
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('ledger_token'))
  const [data, setData] = useState({ items: [], page: 1, pages: 0, total: 0 })
  const [stats, setStats] = useState(null)
  const [budgets, setBudgets] = useState([])
  const [filters, setFilters] = useState({ category: '', sort_by: 'date', order: 'desc', page: 1 })
  const [expense, setExpense] = useState(blankExpense)
  const [editingId, setEditingId] = useState(null)
  const [budget, setBudget] = useState({ month: `${new Date().toISOString().slice(0, 7)}-01`, category: '', amount: '' })
  const [error, setError] = useState('')
  const money = (value) => `INR ${Number(value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  function login(nextToken) { localStorage.setItem('ledger_token', nextToken); setToken(nextToken) }
  function logout() { localStorage.removeItem('ledger_token'); setToken(null) }
  const load = useCallback(async () => {
    if (!token) return
    try {
      const params = new URLSearchParams({ page: filters.page, limit: 8, sort_by: filters.sort_by, order: filters.order })
      if (filters.category) params.set('category', filters.category)
      const [nextData, nextStats, nextBudgets] = await Promise.all([request(`/expenses?${params}`, {}, token), request('/expenses/stats', {}, token), request('/budgets', {}, token)])
      setData(nextData); setStats(nextStats); setBudgets(nextBudgets); setError('')
    } catch (requestError) { setError(requestError.message) }
  }, [filters, token])
  // The effect synchronizes the dashboard with the authenticated API state.
  // oxlint-disable-next-line react/set-state-in-effect
  useEffect(() => { load() }, [load])
  async function saveExpense(event) {
    event.preventDefault()
    try { await request(editingId ? `/expenses/${editingId}` : '/expenses', { method: editingId ? 'PUT' : 'POST', body: JSON.stringify({ ...expense, amount: Number(expense.amount) }) }, token); setExpense(blankExpense); setEditingId(null); load() } catch (requestError) { setError(requestError.message) }
  }
  async function removeExpense(id) {
    if (!window.confirm('Delete this expense?')) return
    try { await request(`/expenses/${id}`, { method: 'DELETE' }, token); load() } catch (requestError) { setError(requestError.message) }
  }
  async function saveBudget(event) {
    event.preventDefault()
    try { await request('/budgets', { method: 'POST', body: JSON.stringify({ ...budget, category: budget.category || null, amount: Number(budget.amount) }) }, token); setBudget({ ...budget, amount: '' }); load() } catch (requestError) { setError(requestError.message) }
  }
  if (!token) return <AuthScreen onLogin={login} />
  return <div className="app-shell"><header className="topbar"><div className="brand-mark">ledger<span>.</span></div><div className="top-actions"><span className="status-dot">Live</span><button className="text-button" onClick={logout}>Sign out</button></div></header><main className="content"><section className="welcome"><div><span className="eyebrow">OVERVIEW / SEPTEMBER 2026</span><h1>Your money, in focus.</h1></div><p className="muted">A private view of the habits behind your balance.</p></section>{error && <div className="error banner">{error}</div>}<section className="metric-grid"><div className="metric metric-dark"><span>Total spend</span><strong>{money(stats?.total_spending)}</strong><small>Across your ledger</small></div><div className="metric"><span>This month</span><strong>{money(stats?.monthly_spending || stats?.total_spending)}</strong><small>Current period</small></div><div className="metric"><span>Top category</span><strong>{stats?.category_breakdown?.[0]?.category || 'No data'}</strong><small>{stats?.category_breakdown?.[0] ? money(stats.category_breakdown[0].total) : 'Start adding expenses'}</small></div><div className="metric metric-accent"><span>Budget remaining</span><strong>{money(stats?.budget ? Number(stats.budget) - Number(stats.monthly_spending) : 0)}</strong><small>Monthly envelope</small></div></section><section className="workspace"><div className="panel expense-panel"><div className="panel-heading"><div><span className="eyebrow">ACTIVITY</span><h2>Recent expenses</h2></div><span className="count">{data.total} entries</span></div><div className="toolbar"><input placeholder="Filter category" value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value, page: 1 })} /><select value={filters.sort_by} onChange={(event) => setFilters({ ...filters, sort_by: event.target.value })}><option value="date">Newest</option><option value="amount">Amount</option><option value="category">Category</option></select><select value={filters.order} onChange={(event) => setFilters({ ...filters, order: event.target.value })}><option value="desc">Descending</option><option value="asc">Ascending</option></select></div><div className="expense-list">{data.items.length === 0 ? <div className="empty">No expenses match this view.</div> : data.items.map((item) => <article className="expense-row" key={item.id}><div className="category-chip">{item.category.slice(0, 1)}</div><div className="expense-detail"><strong>{item.description || item.category}</strong><span>{item.category} Â· {item.date} Â· {item.payment_method || 'Other'}</span></div><strong className="expense-amount">{money(item.amount)}</strong><button className="icon-button" onClick={() => { setEditingId(item.id); setExpense(item) }}>Edit</button><button className="icon-button danger-text" onClick={() => removeExpense(item.id)}>Delete</button></article>)}</div><div className="pagination"><button disabled={data.page <= 1} onClick={() => setFilters({ ...filters, page: data.page - 1 })}>Previous</button><span>Page {data.page} of {Math.max(data.pages, 1)}</span><button disabled={data.page >= data.pages} onClick={() => setFilters({ ...filters, page: data.page + 1 })}>Next</button></div></div><div className="side-stack"><form className="panel form-panel" onSubmit={saveExpense}><div className="panel-heading"><div><span className="eyebrow">{editingId ? 'EDIT ENTRY' : 'NEW ENTRY'}</span><h2>{editingId ? 'Update expense' : 'Add expense'}</h2></div></div><label>Amount<input type="number" min="0.01" step="0.01" required value={expense.amount} onChange={(event) => setExpense({ ...expense, amount: event.target.value })} /></label><label>Category<select value={expense.category} onChange={(event) => setExpense({ ...expense, category: event.target.value })}>{categories.map((item) => <option key={item}>{item}</option>)}</select></label><label>Description<input value={expense.description} onChange={(event) => setExpense({ ...expense, description: event.target.value })} /></label><label>Payment method<input value={expense.payment_method} onChange={(event) => setExpense({ ...expense, payment_method: event.target.value })} /></label><label>Date<input type="date" required value={expense.date} onChange={(event) => setExpense({ ...expense, date: event.target.value })} /></label><button className="primary">{editingId ? 'Save changes' : 'Add to ledger'}</button>{editingId && <button type="button" className="text-button" onClick={() => { setEditingId(null); setExpense(blankExpense) }}>Cancel edit</button>}</form><form className="panel form-panel" onSubmit={saveBudget}><div className="panel-heading"><div><span className="eyebrow">PLANNING</span><h2>Monthly budget</h2></div></div><label>Month<input type="month" required value={budget.month.slice(0, 7)} onChange={(event) => setBudget({ ...budget, month: `${event.target.value}-01` })} /></label><label>Category <span className="muted">(optional)</span><input placeholder="All categories" value={budget.category} onChange={(event) => setBudget({ ...budget, category: event.target.value })} /></label><label>Amount<input type="number" min="0.01" step="0.01" required value={budget.amount} onChange={(event) => setBudget({ ...budget, amount: event.target.value })} /></label><button className="secondary">Set budget</button>{budgets.length > 0 && <div className="budget-list">{budgets.slice(0, 3).map((item) => <span key={item.id}>{item.category || 'All'} Â· {money(item.amount)}</span>)}</div>}</form></div></section></main></div>
}

export default App
