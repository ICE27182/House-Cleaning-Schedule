import React, { useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ListChecks, Info, X, Plus, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const DetailsPanel = ({ open, mode = "details", a, onClose, onSwap, onReassign, pools, canEdit }) => {
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
                <button 
                  key={p} 
                  onClick={() => setReassign(prev => 
                    prev.includes(p) 
                      ? prev.filter(x => x!==p) 
                      : prev.length < a.num ? [...prev, p] : prev)} 
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
              <button onClick={()=>onReassign({ people: reassign, reason })} disabled={reassign.length !== a.num} className="px-3 py-2 rounded-lg bg-gray-900 text-white disabled:opacity-50">Save</button>
            </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}


export {DetailsPanel};