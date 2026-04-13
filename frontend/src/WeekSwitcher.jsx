import { useEffect, useState } from "react";

const isoWeekToRange = (year, week) => {
  // Jan 4 is always in ISO week 1
  const jan4 = new Date(Date.UTC(year, 0, 4));
  // convert JS Sun=0..Sat=6 to ISO Mon=0..Sun=6
  const dayNr = (jan4.getUTCDay() + 6) % 7;
  const monWeek1 = new Date(jan4);
  monWeek1.setUTCDate(jan4.getUTCDate() - dayNr); // Monday of week 1 (UTC)

  // Monday of requested week
  const mon = new Date(monWeek1);
  mon.setUTCDate(monWeek1.getUTCDate() + (week - 1) * 7);

  // Sunday of requested week
  const sun = new Date(mon);
  sun.setUTCDate(mon.getUTCDate() + 6);

  const fmt = (d) =>
    String(d.getUTCDate()).padStart(2, "0") + "." + String(d.getUTCMonth() + 1).padStart(2, "0");

  return `${fmt(mon)}-${fmt(sun)}`;
}

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
      <div className="flex flex-col items-center">
        <div className="text-xl font-semibold tabular-nums">Week {cur.week} </div>
        <div className="text-sm font-semibold tabular-nums">{isoWeekToRange(cur.year, cur.week)} {cur.year}</div>
      </div>
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