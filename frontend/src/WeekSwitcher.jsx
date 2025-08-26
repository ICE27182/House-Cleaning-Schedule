const WeekSwitcher = ({ cur, set }) => {
  const prev = () => {
    let w = cur.week - 1, y = cur.year;
    if (w < 1) { y -= 1; w = 52; }
    set({ year: y, week: w });
  };
  const next = () => {
    let w = cur.week + 1, y = cur.year;
    if (w > 53) { y += 1; w = 1; }
    set({ year: y, week: w });
  };
  return (
    <div className="flex items-center gap-2">
      <button className="px-3 py-1 rounded-xl bg-gray-100 hover:bg-gray-200" onClick={prev}>◀︎</button>
      <div className="text-xl font-semibold tabular-nums">Week {cur.week} · {cur.year}</div>
      <button className="px-3 py-1 rounded-xl bg-gray-100 hover:bg-gray-200" onClick={next}>▶︎</button>
    </div>
  );
}
export {WeekSwitcher}