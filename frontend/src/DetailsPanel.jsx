import React, { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ListChecks, Info, X, Plus, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const DetailsPanel = ({ open,
  person,
  mode = "details",
  assignment,
  onClose,
  onSwap,
  onReassign,
  canEdit,
  updateTrigger,
  setUpdateTrigger
}) => {
  const getAssignees = (assignment) => Object.entries(assignment.info).map(([id, nameNStatus]) => nameNStatus[0])

  const [reason, setReason] = useState("");
  const [reassign, setReassign] = useState(assignment? getAssignees(assignment) : []);

  useEffect(() => {
    setReason("");
    setReassign(assignment? getAssignees(assignment) : []);
  }, [assignment, mode]);

  
  const [pool, setPool] = useState(null);
  const [personInfo, setPersonInfo] = useState(null);
  useEffect(() => {
    if (person) {
      fetch(encodeURI(`/api/people/?person=${person}`), { method: "GET" })
        .then(res => res.json()
          .then(data => setPersonInfo(data)))
    } else {
      fetch("/api/people", { method: "GET" })
        .then(res => res.json()
          .then(data => setPool(data[assignment?.group])))
    }
  }, [person, updateTrigger])

  const handleToggleAvailability = (person, availability) => {
    fetch("/api/people/set-availability", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ person, availability }),
    })
      .then(resp => resp.json()
        .then(data => {
          if (!resp.ok) {
            alert(`Failed.\n${data?.error}`);
          }
          setUpdateTrigger(updateTrigger + 1);
        }))
  }
  const handleRemovePerson = (person) => {
    const repeatedName = prompt("You are trying to remove a person.\n"
                                + "This CANNOT be easily undone.\n"
                                + "Repeat the exact the name of the person "
                                + "you are trying to remove to continue. \n"
                                + "Once entered, you cannot undo it yourself.")
    if (repeatedName != person) {
      alert("The names do not match.")
    } else {
      fetch("/api/people/remove", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ person }),
      })
        .then(resp => resp.json()
          .then(data => {
            setUpdateTrigger(updateTrigger + 1);
            if (!resp.ok) {
              alert(`Failed.\n${data?.error}`);
            } else {
              alert(`${person} has been removed.`)
            }
          })
        )
    }
  }

  if (!open || !assignment && !person) return null;

  return (
    <AnimatePresence>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/30 z-40" onClick={onClose}/>
      <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 30, opacity: 0 }} className="fixed z-50 inset-x-0 bottom-0 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 w-full md:w-[720px] bg-white rounded-2xl shadow-xl border">
        <div className="p-4 border-b flex items-center justify-between">
          {mode == "editPerson" ? (
            <div className="font-semibold flex items-center gap-2">
              <UserRound className="w-4 h-4"/> {person}
            </div>
          ) : (
            <div className="font-semibold flex items-center gap-2">
              <ListChecks className="w-4 h-4"/> {assignment.name}
            </div>
          )}
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100"><X className="w-4 h-4"/></button>
        </div>

        {mode === "details" && (
          <div className="p-4 space-y-4">
            <div>
              <div className="text-sm text-gray-600">Assignees</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {Object.entries(assignment.info).map(([id, nameNStatus]) => (
                    <div 
                      key={id} 
                      className={`flex items-center gap-2 px-2.5 py-1 rounded-full border ${nameNStatus[1] ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"}`}
                    >
                      {nameNStatus[0]}
                    </div>
                ))}
              </div>
            </div>
            <div className="text-sm text-gray-600 flex items-center gap-2"><Users className="w-4 h-4"/> Pool: <code className="bg-gray-50 px-1.5 py-0.5 rounded">{assignment.group}</code></div>
            <div className="text-sm text-gray-600 flex items-center gap-2"><Calendar className="w-4 h-4"/> {assignment.execDate ? `Must be done on Sunday (${assignment.execDate})` : "Any day within the week"}</div>
            {canEdit && (
              <div className="pt-2">
                {/* <button onClick={() => onSwap()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 mr-2"><Shuffle className="w-4 h-4"/> Swap</button> */}
                <button onClick={() => onReassign()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 mr-2"><Shuffle className="w-4 h-4"/> Edit</button>
              </div>
            )}
          </div>
        )}

        {/* {mode === "swap" && (
          <div className="p-4 space-y-4">
            <div className="text-sm">Swap one of the current assignees with someone from the same pool. All changes are public.</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <div className="text-sm text-gray-600 mb-1">From (current assignee)</div>
                <select value={swapFrom} onChange={(e)=>setSwapFrom(e.target.value)} className="w-full border rounded-lg px-2 py-2">
                  <option value="">Select assignee…</option>
                  {assignment.assignees.map(p => <option key={p} value={p}>{p}</option>)}
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
        )} */}

        {mode === "editPerson" && (
          <div className="p-4 space-y-4">
              {personInfo &&
                personInfo["left_at_around"] === null ? (
                  <div className="flex justify-around">
                    <button 
                      className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
                      onClick={() => handleToggleAvailability(person, !personInfo["is_available"])}
                    >
                      {personInfo["is_available"] ? "Disable Temporarily" : "Enable"}
                    </button>
                    <button 
                      className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
                      onClick={() => handleRemovePerson(person)}
                    >
                      Remove
                    </button>
                  </div>
                ) : (
                  <div>
                    This person has left.
                  </div>
                )
              }
          </div>
        )}

        {mode === "reassign" && (
          <div className="p-4 space-y-4">
            <div className="text-sm">Pick exactly {assignment.num} assignee(s) from the pool.</div>
            <div className="flex flex-wrap gap-2">
              {pool.map(p => (
                <button 
                  key={p} 
                  onClick={() => setReassign(prev => 
                    prev.includes(p) 
                      ? prev.filter(x => x!==p) 
                      : prev.length < assignment.num ? [...prev, p] : prev)} 
                    className={`px-2.5 py-1.5 rounded-full border ${reassign.includes(p)?"bg-indigo-600 text-white border-indigo-600":"bg-white border-gray-300"}`}
                >
                  {p}
                </button>
              ))}
            </div>
            <div className="text-sm text-gray-600">Selected: {reassign.join(", ") || "—"}</div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Reason (optional)</div>
              <input value={reason} onChange={(e)=>setReason(e.target.value)} placeholder="e.g. I need to play minecraft" className="w-full border rounded-lg px-3 py-2"/>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">Cancel</button>
              <button onClick={()=>onReassign({ people: reassign, reason })} disabled={reassign.length !== assignment.num} className="px-3 py-2 rounded-lg bg-gray-900 text-white disabled:opacity-50">Save</button>
            </div>
          </div>
        )}

      </motion.div>
    </AnimatePresence>
  );
}


export {DetailsPanel};