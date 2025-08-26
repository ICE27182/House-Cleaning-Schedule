import React, { useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ListChecks, Info, X, Plus, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const AssigneeChip = ({ name, active, onToggle }) => {
  return (
    <button onClick={onToggle} className={`flex items-center gap-2 px-2.5 py-1 rounded-full border ${active ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"}`}>
      {active ? <CheckCircle2 className="w-4 h-4"/> : <Circle className="w-4 h-4"/>}
      <span className="text-sm">{name}</span>
    </button>
  );
}

const ChoreCard = ({ a, onOpen, onToggle, canEdit }) => {
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
export {ChoreCard}