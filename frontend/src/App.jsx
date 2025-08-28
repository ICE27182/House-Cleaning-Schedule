import React, { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ClipboardList, Info, X, Plus, UserRound, TabletSmartphone } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { DetailsPanel } from "./DetailsPanel";
import { WeekSwitcher} from "./WeekSwitcher";
import { LoginBadge } from "./LoginBadge";
import { ChoreCard } from "./ChoreCard";

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
const isoWeek = (d = new Date()) => {
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

const rotateAssignments = ({ week, year, chores, pools, ring = {} }) => {
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


// -------------- Main App --------------
export default function App() {
  const [week, setWeek] = useState(isoWeek());
  const [user, setUser] = useState("");
  const [mode, setMode] = useState("dashboard"); // 'dashboard' | 'details' | 'people' | 'chores' | 'items'
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
          {mode === "dashboard" && <WeekSwitcher cur={week} set={setWeek} />}
          <LoginBadge user={user} setUser={setUser} />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex items-center gap-2 mb-4">
          <button onClick={()=>setMode("dashboard")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='dashboard'? 'bg-gray-900 text-white' : 'bg-white'} `}>Dashboard</button>
          <button onClick={()=>setMode("people")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='people'? 'bg-gray-900 text-white' : 'bg-white'} `}>People</button>
          <button onClick={()=>setMode("chores")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='chores'? 'bg-gray-900 text-white' : 'bg-white'} `}>Chores</button>
          <button onClick={()=>setMode("items")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='items'? 'bg-gray-900 text-white' : 'bg-white'} `}>Common items to buy</button>
          <button onClick={()=>setMode("details")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='details'? 'bg-gray-900 text-white' : 'bg-white'} `}>More Info</button>
        </div>

        {mode === "dashboard" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {cards.map((a) => (
              <ChoreCard key={a.id} a={a} onOpen={(card, m)=>openPanel(card, m)} onToggle={onToggle} canEdit={canEdit} />
            ))}
          </div>
        )}

        {mode === "people" && (
          <div className="rounded-2xl border bg-white p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="font-semibold flex items-center gap-2"><Pencil className="w-4 h-4"/>People (Editing support is coming)</div>
              {!canEdit && <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">Login to make changes</div>}
            </div>
            <div className="flex flex-col flex-wrap gap-4">
              {Object.entries(POOLS).map(([namelistName, namelist]) => (
                <div className="flex flex-col gap-2">
                  <div className="font-semibold flex items-center gap-2"><ClipboardList />{namelistName}</div>
                  <div className="flex flex-wrap gap-2 mx-6">
                    {namelist.map(p => (
                      <button 
                        key={p}
                        className={`px-2.5 py-1.5 rounded-full border "bg-white border-gray-300"}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                  <div className="mx-4 mb-2 mt-1 border-1 border-blue-950"></div>
                </div>
              ))}
            </div>
          </div>
        )}

        {mode === "chores" && (
          <div className="rounded-2xl border bg-white p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="font-semibold flex items-center gap-2"><Pencil className="w-4 h-4"/>Chores (Editing support is coming)</div>
              {!canEdit && <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">Login to make changes</div>}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cards.map(a => (
                <div key={a.id} className="border rounded-2xl p-4">
                  <div className="font-medium mb-2">{a.name}</div>
                  <div className="text-sm text-gray-600 mb-2">Assignees: {a.assignees.join(", ") || "—"}</div>
                  <div className="flex flex-wrap gap-2">
                    <button 
                      disabled={!canEdit} 
                      onClick={()=>openPanel(a, "swap")}
                      className="px-2.5 py-1.5 rounded-lg bg-indigo-600 text-white disabled:opacity-50"
                    >
                      <Pencil className="w-4 h-4 inline mr-1"/> Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {mode === "items" && (
          <div className="rounded-2xl border bg-white p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="font-semibold flex items-center gap-2"><Pencil className="w-4 h-4"/>Common Items</div>
            </div>
            <p>To be added</p>
            <p>Maybe a matrix just like what we had with numbers instead of ticks in its cells. And left click to add one and right click (onContextMenu) to decrease one?</p>
          </div>
        )}

        {mode === "details" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <section className="md:col-span-2">
              <div className="rounded-2xl border bg-white p-4">
                <div className="font-semibold mb-3 flex items-center gap-2"><Info className="w-4 h-4"/> What to do</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                  <li>Follow the checklist on the chore card.</li>
                  <li>Mark yourself done when finished. Undo if you made a mistake.</li>
                  <li>Sign in to make changes to existing schedules. All changes will be recorded and are visible to everyone</li>
                  <li>The abilities to add/remove/change persons and chores on the website are yet to be added.</li>
                </ul>
              </div>
            </section>
            <aside>
              <div className="rounded-2xl border bg-white p-4">
                <div className="font-semibold mb-3 flex items-center gap-2"><History className="w-4 h-4"/> Changes made</div>
                <div className="text-sm text-gray-500">All swaps/reassignments will appear here with who/when/why.</div>
              </div>
            </aside>
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
