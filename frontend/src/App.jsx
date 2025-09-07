import { useEffect, useState } from "react";
import { Pencil, Info, ListRestart, ExternalLink, Code2 } from "lucide-react";
import { DetailsPanel } from "./DetailsPanel";
import { WeekSwitcher} from "./WeekSwitcher";
import { LoginBadge } from "./LoginBadge";
import { AssignmentCard } from "./AssignmentCard";
import Changelog from "./Changelog";
import People from "./People";
import Chores from "./Chores";


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

// -------------- Main App --------------
export default function App() {
  const [week, setWeek] = useState(isoWeek());
  const [user, setUser] = useState("");
  // 'dashboard' | 'details' | 'people' | 'chores' | 'items' | 'editPerson' | 'addPerson'
  const [mode, setMode] = useState("dashboard");
  const [assignment, setAssignment] = useState(null); // active assignment
  const canEdit = Boolean(user);
  const [assignments, setAssignments] = useState(null);
  const [person, setPerson] = useState(null);
  const [updateTrigger, setUpdateTrigger] = useState(0)

  // Automatically login with cookie
  useEffect(() => {
    let mounted = true;
    fetch("/api/auth/me", { credentials: "include" })
    .then(async (res) => {
      if (!mounted) return;
      if (!res.ok) return setUser("");
      const data = await res.json().catch(()=>({}));
      setUser(data?.name || "");
    })
    .catch(()=> {
      if (mounted) setUser("");
    });
    return () => { mounted = false; };
  }, [updateTrigger]);
  
  useEffect(() => {
    if (mode === "dashboard") {
      const url = `/api/schedules?year=${week.year}&week=${week.week}`;
      fetch(url, { method: "GET", credentials: "include" })
        .then(response => response.json()
          .then(data => setAssignments(data)))
        .catch(() => setAssignments(null));
    }
  }, [mode, week])

  const openDetails = (a, toMode = "details") => {
    setAssignment(a);
    setMode(toMode === "edit" ? "edit" : "details");
  };

  const [panel, setPanel] = useState({ open: false, mode: "details" });
  const openPanel = (a, m = "details") => { setAssignment(a); setPanel({ open: true, mode: m }); };

  const handleSwap = async ({ from, to, reason }) => {
    if (!from || !to || from === to) return alert("Pick two different people.");
    // update active card locally
    setDoneMap(prev => ({ ...prev, [assignment.id]: new Set([...((prev[assignment.id])||new Set())].filter(x => x!==from)) }));
    assignment.assignees = assignment.assignees.map(x => x===from? to : x);
    assignment.history.unshift(`${user||"Someone"} swapped ${from} → ${to}${reason?` (${reason})`:``}`);
    setPanel({ open: false, mode: "details" });
  };

  const handleReassign = async ({ people, reason }) => {
    if (!people || people.length !== assignment.num) return;
    const removed = assignment.assignees.filter(x => !people.includes(x));
    setDoneMap(prev => ({ ...prev, [assignment.id]: new Set([...((prev[assignment.id])||new Set())].filter(x => people.includes(x))) }));
    assignment.assignees = people;
    assignment.history.unshift(`${user||"Someone"} reassigned ${removed.join(", ")} → ${people.join(", ")}${reason?` (${reason})`:``}`);
    setPanel({ open: false, mode: "details" });
  };

  const handleResetFutureSchedules = () => {
    const reason = prompt("Are you sure you want to reset all future schedules?\n"
                          + "Enter the reason to reset.");
    fetch("/api/schedules/reset-future-schedules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ reason: reason }),
    })
      .then((resp) =>
        resp
          .json()
          .then((data) => {
            setUpdateTrigger(updateTrigger + 1);
            if (!resp.ok) {
              alert(`Failed.\n${data?.error}`);
            } else {
              alert(`The schedules have been reset.`);
            }
          })
          .catch(() => {
            setUpdateTrigger(updateTrigger + 1);
          })
      )
      .catch((err) => {
        console.error("Network error:", err);
        alert("Network error");
      });
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-500 to-white">
      <header className="sticky top-0 z-30 backdrop-blur bg-white/70 border-b">
        <div className="max-w-6xl mx-auto px-2 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gray-900 text-white grid place-items-center font-bold">D</div>
            <div className="font-semibold">House Chores</div>
          </div>
          {mode === "dashboard" && <WeekSwitcher cur={week} set={setWeek} />}
          <LoginBadge user={user} setUser={setUser} />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-4">
          <button onClick={()=>setMode("dashboard")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='dashboard'? 'bg-gray-900 text-white' : 'bg-white'} `}>Dashboard</button>
          <button onClick={()=>setMode("people")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='people'? 'bg-gray-900 text-white' : 'bg-white'} `}>People</button>
          <button onClick={()=>setMode("chores")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='chores'? 'bg-gray-900 text-white' : 'bg-white'} `}>Chores</button>
          <button onClick={()=>setMode("misc")} className={`px-3 py-1.5 rounded-xl text-sm border ${mode==='misc'? 'bg-gray-900 text-white' : 'bg-white'} `}>Misc</button>
        </div>

        {mode === "dashboard" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {assignments && Object.entries(assignments.schedule).map(([choreName, info], i) => (
              <AssignmentCard 
                key={i}
                choreName={choreName}
                info={info} 
                dayBadge={assignments["due_days"][choreName]}
                onOpen={(info, m)=>openPanel(info, m)} 
                canEdit={canEdit} 
                updateTrigger={updateTrigger} 
                setUpdateTrigger={setUpdateTrigger}
              />
            ))}
          </div>
        )}

        {mode === "people" && (
          <div className="rounded-2xl border bg-white p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="font-semibold flex items-center gap-2"><Pencil className="w-4 h-4"/>People</div>
              {canEdit ? (
                  <button
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 mr-2"
                    onClick={() => setPanel({ open: true, mode: "addPerson"})}
                  >
                    Add a new housemate
                  </button>
                ) : (
                  <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">
                    Login to make changes
                  </div>
                )
              }
            </div>
            <People
              user={user}
              setPerson={setPerson}
              setPanel={setPanel}
              updateTrigger={updateTrigger}
              setUpdateTrigger={setUpdateTrigger}
            />
          </div>
        )}

        {mode === "chores" && (
          <div className="rounded-2xl border bg-white p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="font-semibold flex items-center gap-2"><Pencil className="w-4 h-4"/>Chores (Editing support is coming)</div>
              {!canEdit && <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">Login to make changes</div>}
            </div>
            <Chores />
          </div>
        )}

        {mode === "misc" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <section className="md:col-span-2">
              <div className="rounded-2xl border bg-white p-4">
                <div className="font-semibold mb-3 flex items-center gap-2"><Info className="w-4 h-4"/> What to do</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                  <li>Follow the checklist on the chore card.</li>
                  <li>Mark yourself done when finished. Undo if you made a mistake.</li>
                  <li>Sign in to make changes to existing schedules. All changes will be recorded and are visible to everyone</li>
                  <li>The abilities to add/remove/change persons and chores on the website are yet to be added.</li>
                  <li>
                    The website is open-sourced. 
                    You can find the code via the link at the bottom of the page. 
                    All private informations such as names, chore descriptions 
                    and database are excluded.
                  </li>
                </ul>
                <div className="flex flex-col md:flex-row gap-4 text-center my-3 gpa-2">
                  <div className="inline-block border-2 rounded-2xl p-2 font-semibold items-center gap-2 hover:bg-blue-950 hover:text-white">
                    <a href="http://minecraft.fandom.com">
                      <ExternalLink className="inline w-4 h-4"/> Common item trackers
                    </a>

                  </div>
                  {user &&
                    <button
                      className="inline-block border-2 rounded-2xl p-2 font-semibold items-center gap-2 hover:bg-blue-950 hover:text-white"
                      onClick={handleResetFutureSchedules}
                    >
                      <ListRestart className="inline w-4 h-4"/> Reset Future Schedules
                    </button>
                  }
                </div>
              </div>
            </section>
            <aside>
              <Changelog updateTrigger={updateTrigger} />
            </aside>
          </div>
        )}

      </main>

      <DetailsPanel
        open={panel.open}
        mode={panel.mode === "edit" ? "reassign" : panel.mode}
        assignment={assignment}
        person={person}
        onClose={()=>setPanel({ open: false, mode: "details" })}
        onSwap={(payload)=>handleSwap(payload)}
        onReassign={(payload)=>handleReassign(payload)}
        canEdit={canEdit}
        updateTrigger={updateTrigger}
        setUpdateTrigger={setUpdateTrigger}
      />

      <footer className="flex flex-col gap-4 max-w-6xl mx-auto px-4 py-8 text-center text-white items-center justify-center">
        <div className="flex flex-row justify-center items-center gap-4">
          <div className="border-0 border-black bg-[#020408] hover:border-2 rounded-2xl p-3">
            <a href="https://github.com/ICE27182"><ExternalLink className="inline h-4 w-4 mr-2" />Github</a>
          </div>
          <div className="border-0 border-black bg-[#020408] hover:border-2 rounded-2xl p-3">
            <a href="https://github.com/ICE27182/House-Cleaning-Schedule">
              <Code2 className="inline h-4 w-4 mr-2" />Source Code
            </a>
          </div>
        </div>
        <div className="text-[#9cdcff] font-extrabold">ICE27182</div>
      </footer>
    </div>
  );
}
