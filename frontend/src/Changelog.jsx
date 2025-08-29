import { useState, useEffect } from 'react'
import { History } from 'lucide-react'

const Changelog = ({ weeksFromNow = 3, limit } = {}) => {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)

    const now = new Date()
    const toIso = now.toISOString()
    const fromDate = new Date(now.getTime() - (weeksFromNow * 7 * 24 * 60 * 60 * 1000))
    const fromIso = fromDate.toISOString()

    let url = `/api/changelog?from=${encodeURIComponent(fromIso)}&to=${encodeURIComponent(toIso)}`
    if (typeof limit === 'number' && limit > 0) {
      url += `&limit=${limit}`
    }

    // prefer promise .then chaining per request
    fetch(url, { credentials: 'include' })
      .then((res) => res.json().then((j) => ({ ok: res.ok, body: j })))
      .then(({ ok, body }) => {
        if (!ok) throw new Error(body?.error || 'Failed to load changelog')
        setEntries(Array.isArray(body.entries) ? body.entries : [])
      })
      .catch((err) => setError(err.message || 'Network error'))
      .finally(() => setLoading(false))
  }, [weeksFromNow, limit])

  return (
    <div className="rounded-2xl border bg-white p-4">
      <div className="font-semibold mb-3 flex items-center gap-2">
        <History className="w-4 h-4" /> Change log
      </div>
      <div className="text-sm text-gray-500 mb-3">
        Showing changes from the last {weeksFromNow} week{weeksFromNow !== 1 ? 's' : ''}.
      </div>

      {loading ? (
        <div className="text-sm text-gray-500">Loading…</div>
      ) : error ? (
        <div className="text-sm text-red-500">Error: {error}</div>
      ) : entries.length === 0 ? (
        <div className="text-sm text-gray-500">No entries in this range.</div>
      ) : (
        <ul className="space-y-2">
          {entries.map((e, idx) => {
            const created = e.created_at ? new Date(e.created_at) : null
            const timeStr = created ? created.toLocaleString() : e.created_at
            return (
              <li key={idx} className="text-sm">
                <div className="text-gray-600">{timeStr}</div>
                <div className="text-gray-900">{e.description}</div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

export default Changelog