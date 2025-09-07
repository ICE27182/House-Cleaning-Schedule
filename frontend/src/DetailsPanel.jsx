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

  // new state for addPerson mode
  const [addName, setAddName] = useState("");
  const [addGroup, setAddGroup] = useState("everyone");
  // reset when mode changes
  useEffect(() => {
    setAddName("");
    setAddGroup("everyone");
  }, [mode]);

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

  // handler for adding a person (used in addPerson mode)
  const handleAddPerson = () => {
    const name = (addName || "").trim();
    const group = addGroup;
    if (!name) {
      alert("Name is required");
      return;
    }
    fetch("/api/people/add/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ person: name, group }),
    })
      .then(resp => resp.json()
        .then(data => {
          console.log(data);
          if (!resp.ok || !data?.ok) {
            alert(`Failed to add person.\n${data?.error}`);
            return;
          }
          // trigger refresh and close panel
          setUpdateTrigger((t) => (t ?? 0) + 1);
          onClose();
        })
        .catch(() => {
          if (resp.ok) {
            setUpdateTrigger((t) => (t ?? 0) + 1);
            onClose();
          }
        })
      )
      .catch((err) => {
        console.error("Network error:", err);
        alert("Network error while adding person");
      });
  }

  if (!open || !assignment && !person && !(mode === "addPerson")) return null;

  return (
    <AnimatePresence>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/30 z-40" onClick={onClose}/>
      <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 30, opacity: 0 }} className="fixed z-50 inset-x-0 bottom-0 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 w-full md:w-[720px] bg-white rounded-2xl shadow-xl border">
        <div className="p-4 border-b flex items-center justify-between">
          {mode === "editPerson" ? (
            <div className="font-semibold flex items-center gap-2">
              <UserRound className="w-4 h-4"/> {person}
            </div>
          ) : (
            mode === "addPerson" ? (
              <div className="font-semibold flex items-center gap-2">
              <UserRound className="w-4 h-4"/> Add a new housemate
            </div>
            ) : (
              <div className="font-semibold flex items-center gap-2">
                <ListChecks className="w-4 h-4"/> {assignment.name}
              </div>
            )
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
                <button onClick={() => onReassign()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 mr-2"><Shuffle className="w-4 h-4"/> Edit</button>
              </div>
            )}
          </div>
        )}

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

        {mode === "addPerson" && (
          <div className="p-4 space-y-4">
            <div>
              <div className="text-sm text-gray-600 mb-1">Name</div>
              <input 
                value={addName} 
                onChange={(e) => setAddName(e.target.value)} 
                placeholder="Enter a unique name" 
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Group</div>
              <select value={addGroup} onChange={(e) => setAddGroup(e.target.value)} className="w-full border rounded-lg px-3 py-2">
                <option value="main_gate">Uses the bathroom close the main gate</option>
                <option value="stairs">Uses the bathroom close the stairs</option>
                <option value="upstairs">Uses the bathroom upstairs</option>
                <option value="everyone">Uses the bathroom in their own room</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={onClose} className="px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">Cancel</button>
              <button onClick={handleAddPerson} className="px-3 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">Add person</button>
            </div>
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