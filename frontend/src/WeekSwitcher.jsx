import { useEffect, useState } from "react";

const WeekSwitcher = ({ cur, set }) => {
  const [prev, setPrev] = useState(null)
  const [next, setNext] = useState(null)
  useEffect(() => {
    const urlLast = `/api/schedules/last-week?year=${cur.year}&week=${cur.week}`
    fetch(urlLast, { method: "GET" })
      .then(response => response.json()
        .then(data => setPrev(data))
      )
  }, [cur])
  useEffect(() => {
    const urlNext = `/api/schedules/next-week?year=${cur.year}&week=${cur.week}`
    fetch(urlNext, { method: "GET" })
      .then(response => response.json()
        .then(data => setNext(data))
      )
  }, [cur])
  return (
    <div className="flex items-center gap-2">
      {prev && <button 
        className="px-3 py-1 rounded-xl bg-gray-100 hover:bg-gray-200" 
        onClick={() => set(prev)}
      >
        ◀︎
      </button>}
      <div className="text-xl font-semibold tabular-nums">Week {cur.week} · {cur.year}</div>
      {next && <button
        className="px-3 py-1 rounded-xl bg-gray-100 hover:bg-gray-200" 
        onClick={() => set(next)}
      >
        ▶︎
      </button>}
    </div>
  );
}
export {WeekSwitcher}