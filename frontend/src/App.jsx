import React, { useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ListChecks, Info, X, Plus, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * House Chores – React + Tailwind Prototype
 * -------------------------------------------------
 * What this demo shows
 * - Main dashboard (This Week & Next Week)
 * - More Info page (task details, checklist, rotation preview, history)
 * - Schedule changing page (Swap / Reassign with optional reason)
 * - Mark/unmark done without login
 * - Lightweight mock auth for edit actions
 * - Round-robin generator with random-ordered pools; pointer advances weekly
 *
 * Notes
 * - This is a front-end prototype; API calls are stubbed.
 * - Replace `api` functions with real Flask routes.
 */

// -------------- Mock Data (from your JSON) --------------
const CHORE_DEFS = [
  { name: "Kitchen Cleaning", pool: "namelist.json", num: 2, freq: "weekly" },
  { name: "House Vacuuming", pool: "namelist.json", num: 2, freq: "weekly" },
  { name: "Basement Cleaning", pool: "namelist.json", num: 1, freq: "weekly" },
  { name: "Glass Garbage", pool: "namelist.json", num: 1, freq: { type: "biweekly", offset: 1, day: "any" } },
  { name: "Cardboard Garbage", pool: "namelist.json", num: 1, freq: { type: "weeks_list", year: 2025, weeks: [2,6,10,14,19,24,28,32,36,41,45,49], day: "Sunday" } },
  { name: "Organic Garbage", pool: "namelist.json", num: 1, freq: { type: "biweekly", offset: 0, day: "Sunday" } },
  { name: "Plastic Garbage", pool: "namelist.json", num: 1, freq: { type: "biweekly", offset: 1, day: "Sunday" } },
  { name: "Toilet & Bathroom Cleaning North", pool: "namelist_north.json", num: 1, freq: "weekly" },
  { name: "Toilet & Bathroom Cleaning South", pool: "namelist_south.json", num: 1, freq: "weekly" },
  { name: "Toilet & Bathroom Cleaning Second Floor", pool: "namelist_second_floor.json", num: 1, freq: "weekly" },
];

// Pools in random order; new names inserted randomly; old names removed
const POOLS = {
  "namelist.json": ["Nil","Isabelle","Pati","Sam","Costas","Hannah","Amina","Ismail","Minh","Justin","Korina","Waqar"],
  "namelist_north.json": ["Amina","Ismail","Hannah"],
  "namelist_south.json": ["Sam","Costas","Minh"],
  "namelist_second_floor.json": ["Nil","Isabelle","Pati"],
};

// -------------- Utilities --------------
function isoWeek(d = new Date()) {
  // ISO week number: Mon-Sun
  const target = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNr = (target.getUTCDay() + 6) % 7; // Mon=0..Sun=6
  target.setUTCDate(target.getUTCDate() - dayNr + 3);
  const firstThursday = new Date(Date.UTC(target.getUTCFullYear(),0,4));
  const diff = target - firstThursday;
  return {
    year: target.getUTCFullYear(),
    week: 1 + Math.round(diff / 604800000),
  };
}

const rng = (seed) => {
  // quick LCG for deterministic shuffles in the preview
  let s = seed % 2147483647; if (s <= 0) s += 2147483646;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
};

function rotateAssignments({ week, year, chores, pools, ring = {} }) {
  const out = [];
  const rand = rng(year * 100 + week);
  const sunday = (/* sunday of ISO week */) => {
    // find Monday
    const simple = (y,w) => {
      const jan4 = new Date(Date.UTC(y,0,4));
      const day = jan4.getUTCDay() || 7; // 1..7
      const monday = new Date(jan4);
      monday.setUTCDate(jan4.getUTCDate() - day + 1 + (w-1)*7);
      return monday;
    };
    const mon = simple(year, week);
    const sun = new Date(mon); sun.setUTCDate(mon.getUTCDate()+6);
    return sun.toISOString().slice(0,10);
  };

  chores.forEach((c) => {
    // frequency check for this week
    const show = (() => {
      if (c.freq === "weekly") return true;
      if (c.freq?.type === "biweekly") {
        return (week % 2) === (c.freq.offset || 0);
      }
      if (c.freq?.type === "weeks_list") {
        return c.freq.year === year && c.freq.weeks.includes(week);
      }
      return true;
    })();

    if (!show) return;

    const pool = pools[c.pool] || [];
    const pointer = ring[c.name] ?? 0;
    const assignees = Array.from({ length: c.num }, (_, i) => pool[(pointer + i) % pool.length]).filter(Boolean);

    out.push({
      id: `${year}-${week}-${c.name}`,
      name: c.name,
      poolKey: c.pool,
      frequency: c.freq,
      num: c.num,
      assignees,
      done: [],
      execDate: c.freq?.day === "Sunday" ? sunday() : null, // only for day-specific chores
      lastChange: null,
      notes: "",
      history: [],
    });
  });

  return out;
}

// -------------- API (stubs) --------------
const api = {
  mark: async (assignmentId, person) => ({ ok: true }),
  unmark: async (assignmentId, person) => ({ ok: true }),
  swap: async (assignmentId, from, to, reason) => ({ ok: true }),
  reassign: async (assignmentId, people, reason) => ({ ok: true }),
};

// -------------- UI Components --------------
function WeekSwitcher({ cur, set }) {
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

function AssigneeChip({ name, active, onToggle }) {
  return (
    <button onClick={onToggle} className={`flex items-center gap-2 px-2.5 py-1 rounded-full border ${active ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"}`}>
      {active ? <CheckCircle2 className="w-4 h-4"/> : <Circle className="w-4 h-4"/>}
      <span className="text-sm">{name}</span>
    </button>
  );
}

function ChoreCard({ a, onOpen, onToggle, canEdit }) {
  const allDone = a.assignees.every(p => a.done.includes(p));
  const dayBadge = a.execDate ? `Due Sun ${a.execDate.slice(5)}` : "Any day this week";
  return (
    <motion.div layout className={`rounded-2xl border p-4 shadow-sm bg-white ${allDone ? "ring-1 ring-emerald-200" : ""}`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="font-semibold text-gray-900 flex items-center gap-2">
            <ListChecks className="w-4 h-4"/> {a.name}
          </div>
          <div className="text-xs text-gray-500 mt-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> {dayBadge}</div>
        </div>
        <div className={`text-xs px-2 py-0.5 rounded-full ${allDone ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-amber-50 text-amber-700 border border-amber-200"}`}>{allDone ? "All done" : "In progress"}</div>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {a.assignees.map((p) => (
          <AssigneeChip key={p} name={p} active={a.done.includes(p)} onToggle={() => onToggle(a.id, p)} />
        ))}
      </div>

      <div className="mt-4 flex items-center gap-2">
        <button onClick={() => onOpen(a)} className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-gray-200"><Info className="w-4 h-4"/> Details</button>
        {canEdit && (
          <button onClick={() => onOpen(a, "edit")} className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"><Pencil className="w-4 h-4"/> Edit</button>
        )}
      </div>
    </motion.div>
  );
}

function DetailsPanel({ open, mode = "details", a, onClose, onSwap, onReassign, pools, canEdit }) {
  const [reason, setReason] = useState("");
  const [swapFrom, setSwapFrom] = useState("");
  const [swapTo, setSwapTo] = useState("");
  const [reassign, setReassign] = useState(a?.assignees || []);

  React.useEffect(() => {
    setReason("");
    setSwapFrom("");
    setSwapTo("");
    setReassign(a?.assignees || []);
  }, [a, mode]);

  if (!open || !a) return null;

  const pool = pools[a.poolKey] || [];

  return (
    <AnimatePresence>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/30 z-40" onClick={onClose}/>
      <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 30, opacity: 0 }} className="fixed z-50 inset-x-0 bottom-0 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 w-full md:w-[720px] bg-white rounded-2xl shadow-xl border">
        <div className="p-4 border-b flex items-center justify-between">
          <div className="font-semibold flex items-center gap-2"><ListChecks className="w-4 h-4"/> {a.name} — Week {a.id.split("-")[1]}</div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100"><X className="w-4 h-4"/></button>
        </div>

        {mode === "details" && (
          <div className="p-4 space-y-4">
            <div>
              <div className="text-sm text-gray-600">Assignees</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {a.assignees.map(p => <span key={p} className={`px-2 py-1 text-sm rounded-full border ${a.done.includes(p)?"bg-emerald-50 border-emerald-200 text-emerald-700":"bg-gray-50 border-gray-200"}`}>{p}</span>)}
              </div>
            </div>
            <div className="text-sm text-gray-600 flex items-center gap-2"><Users className="w-4 h-4"/> Pool: <code className="bg-gray-50 px-1.5 py-0.5 rounded">{a.poolKey}</code></div>
            <div className="text-sm text-gray-600 flex items-center gap-2"><Calendar className="w-4 h-4"/> {a.execDate ? `Must be done on Sunday (${a.execDate})` : "Any day within the week"}</div>
            <div>
              <div className="text-sm text-gray-600 mb-1 flex items-center gap-2"><History className="w-4 h-4"/> Recent changes</div>
              {a.history?.length ? (
                <ul className="text-sm space-y-1">
                  {a.history.map((h, i) => <li key={i} className="flex items-start gap-2"><span className="text-gray-400">•</span><span>{h}</span></li>)}
                </ul>
              ) : (<div className="text-sm text-gray-400">No changes yet.</div>)}
            </div>
            {canEdit && (
              <div className="pt-2">
                <button onClick={() => onSwap()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 mr-2"><Shuffle className="w-4 h-4"/> Swap</button>
                <button onClick={() => onReassign()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-900 text-white hover:bg-black"><Pencil className="w-4 h-4"/> Reassign</button>
              </div>
            )}
          </div>
        )}

        {mode === "swap" && (
          <div className="p-4 space-y-4">
            <div className="text-sm">Swap one of the current assignees with someone from the same pool. All changes are public.</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <div className="text-sm text-gray-600 mb-1">From (current assignee)</div>
                <select value={swapFrom} onChange={(e)=>setSwapFrom(e.target.value)} className="w-full border rounded-lg px-2 py-2">
                  <option value="">Select assignee…</option>
                  {a.assignees.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">To (replacement from pool)</div>
                <select value={swapTo} onChange={(e)=>setSwapTo(e.target.value)} className="w-full border rounded-lg px-2 py-2">
                  <option value="">Select person…</option>
                  {pool.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Reason (optional)</div>
              <input value={reason} onChange={(e)=>setReason(e.target.value)} placeholder="e.g., out of town" className="w-full border rounded-lg px-3 py-2"/>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">Cancel</button>
              <button onClick={()=>onSwap({ from: swapFrom, to: swapTo, reason })} className="px-3 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">Confirm swap</button>
            </div>
          </div>
        )}

        {mode === "reassign" && (
          <div className="p-4 space-y-4">
            <div className="text-sm">Pick exactly {a.num} assignee(s) from the pool.</div>
            <div className="flex flex-wrap gap-2">
              {pool.map(p => (
                <button key={p} onClick={()=>setReassign(prev => prev.includes(p)? prev.filter(x=>x!==p) : prev.length < a.num ? [...prev, p] : prev)} className={`px-2.5 py-1.5 rounded-full border ${reassign.includes(p)?"bg-indigo-600 text-white border-indigo-600":"bg-white border-gray-300"}`}>
                  {p}
                </button>
              ))}
            </div>
            <div className="text-sm text-gray-600">Selected: {reassign.join(", ") || "—"}</div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Reason (optional)</div>
              <input value={reason} onChange={(e)=>setReason(e.target.value)} placeholder="e.g., balancing workload" className="w-full border rounded-lg px-3 py-2"/>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">Cancel</button>
              <button onClick={()=>onReassign({ people: reassign, reason })} disabled={reassign.length !== a.num} className="px-3 py-2 rounded-lg bg-gray-900 text-white disabled:opacity-50">Save</button>
            </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

function LoginBadge({ user, setUser }) {
  return (
    <div className="flex items-center gap-2">
      {user ? (
        <>
          <div className="text-sm flex items-center gap-1 px-2 py-1 rounded-lg bg-gray-100"><UserRound className="w-4 h-4"/> {user}</div>
          <button onClick={()=>setUser("")} className="text-sm px-2 py-1 rounded-lg bg-gray-100 hover:bg-gray-200">Logout</button>
        </>
      ) : (
        <button onClick={()=>{
          const name = prompt("Enter nickname (for logging changes)");
          if (name) setUser(name);
        }} className="text-sm px-2.5 py-1.5 rounded-lg bg-gray-900 text-white hover:bg-black">Login to edit</button>
      )}
    </div>
  );
}

// -------------- Main App --------------
export default function App() {
  const [week, setWeek] = useState(isoWeek());
  const [user, setUser] = useState("");
  const [mode, setMode] = useState("dashboard"); // 'dashboard' | 'details' | 'edit'
  const [active, setActive] = useState(null); // active assignment
  const canEdit = Boolean(user);

  const assignments = useMemo(() => rotateAssignments({ week: week.week, year: week.year, chores: CHORE_DEFS, pools: POOLS }), [week]);
  const [doneMap, setDoneMap] = useState({}); // assignmentId -> Set(names)

  // reflect done state onto assignments
  const cards = assignments.map(a => ({ ...a, done: Array.from(doneMap[a.id] || new Set()) }));

  const openDetails = (a, toMode = "details") => {
    setActive(a);
    setMode(toMode === "edit" ? "edit" : "details");
  };

  const onToggle = async (assignmentId, person) => {
    setDoneMap(prev => {
      const s = new Set(prev[assignmentId] || []);
      if (s.has(person)) s.delete(person); else s.add(person);
      return { ...prev, [assignmentId]: s };
    });
  };

  const [panel, setPanel] = useState({ open: false, mode: "details" });
  const openPanel = (a, m = "details") => { setActive(a); setPanel({ open: true, mode: m }); };

  const handleSwap = async ({ from, to, reason }) => {
    if (!from || !to || from === to) return alert("Pick two different people.");
    // update active card locally
    setDoneMap(prev => ({ ...prev, [active.id]: new Set([...((prev[active.id])||new Set())].filter(x => x!==from)) }));
    active.assignees = active.assignees.map(x => x===from? to : x);
    active.history.unshift(`${user||"Someone"} swapped ${from} → ${to}${reason?` (${reason})`:``}`);
    setPanel({ open: false, mode: "details" });
  };

  const handleReassign = async ({ people, reason }) => {
    if (!people || people.length !== active.num) return;
    const removed = active.assignees.filter(x => !people.includes(x));
    setDoneMap(prev => ({ ...prev, [active.id]: new Set([...((prev[active.id])||new Set())].filter(x => people.includes(x))) }));
    active.assignees = people;
    active.history.unshift(`${user||"Someone"} reassigned ${removed.join(", ")} → ${people.join(", ")}${reason?` (${reason})`:``}`);
    setPanel({ open: false, mode: "details" });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-500 to-white">
      <header className="sticky top-0 z-30 backdrop-blur bg-white/70 border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gray-900 text-white grid place-items-center font-bold">D</div>
            <div className="font-semibold">House Chores</div>
          </div>
          <WeekSwitcher cur={week} set={setWeek} />
          <LoginBadge user={user} setUser={setUser} />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex items-center gap-2 mb-4">
          <button onClick={()=>setMode("dashboard")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='dashboard'? 'bg-gray-900 text-white' : 'bg-white'} `}>Dashboard</button>
          <button onClick={()=>setMode("details")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='details'? 'bg-gray-900 text-white' : 'bg-white'} `}>More Info</button>
          <button onClick={()=>setMode("edit")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='edit'? 'bg-gray-900 text-white' : 'bg-white'} `}>Schedule Changes</button>
        </div>

        {mode === "dashboard" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {cards.map((a) => (
              <ChoreCard key={a.id} a={a} onOpen={(card, m)=>openPanel(card, m)} onToggle={onToggle} canEdit={canEdit} />
            ))}
          </div>
        )}

        {mode === "details" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <section className="md:col-span-2">
              <div className="rounded-2xl border bg-white p-4">
                <div className="font-semibold mb-3 flex items-center gap-2"><Info className="w-4 h-4"/> What to do</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                  <li>Follow the checklist on the chore card.</li>
                  <li>Garbage chores must be done on their designated day (usually Sunday).</li>
                  <li>Mark yourself done when finished. Undo if you made a mistake.</li>
                </ul>
              </div>
            </section>
            <aside>
              <div className="rounded-2xl border bg-white p-4">
                <div className="font-semibold mb-3 flex items-center gap-2"><History className="w-4 h-4"/> Global Activity (demo)</div>
                <div className="text-sm text-gray-500">All swaps/reassignments will appear here with who/when/why.</div>
              </div>
            </aside>
          </div>
        )}

        {mode === "edit" && (
          <div className="rounded-2xl border bg-white p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="font-semibold flex items-center gap-2"><Pencil className="w-4 h-4"/> Schedule Changes</div>
              {!canEdit && <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">Login to make changes</div>}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cards.map(a => (
                <div key={a.id} className="border rounded-2xl p-4">
                  <div className="font-medium mb-2">{a.name}</div>
                  <div className="text-sm text-gray-600 mb-2">Assignees: {a.assignees.join(", ") || "—"}</div>
                  <div className="flex flex-wrap gap-2">
                    <button disabled={!canEdit} onClick={()=>openPanel(a, "swap")} className="px-2.5 py-1.5 rounded-lg bg-indigo-600 text-white disabled:opacity-50"><Shuffle className="w-4 h-4 inline mr-1"/> Swap</button>
                    <button disabled={!canEdit} onClick={()=>openPanel(a, "reassign")} className="px-2.5 py-1.5 rounded-lg bg-gray-900 text-white disabled:opacity-50"><Pencil className="w-4 h-4 inline mr-1"/> Reassign</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <DetailsPanel
        open={panel.open}
        mode={panel.mode === "edit" ? "reassign" : panel.mode}
        a={active}
        onClose={()=>setPanel({ open: false, mode: "details" })}
        onSwap={(payload)=>handleSwap(payload)}
        onReassign={(payload)=>handleReassign(payload)}
        pools={POOLS}
        canEdit={canEdit}
      />

      <footer className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-gray-400">All changes are public to everyone on the LAN.</footer>
    </div>
  );
}
