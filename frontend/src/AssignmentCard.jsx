import React, { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ListChecks, Info, X, Plus, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const AssigneeChip = ({ 
  name, 
  active, 
  assignmentID,
  updateTrigger,
  setUpdateTrigger,
}) => {
  const [isActive, setIsActive] = useState(active)
  const onToggle = () => {
    const url = (isActive
                 ? `/api/schedules/mark-not-done?assignment_id=${assignmentID}`
                 : `/api/schedules/mark-done?assignment_id=${assignmentID}`);
    fetch(url, { method: "POST" })
      .then(response => response.json()
        .then(() => {
          setIsActive(!isActive);
        })
        .then(() => {
          setUpdateTrigger(updateTrigger+1);
        })
      );
  }
  return (
    <button onClick={onToggle} className={`flex items-center gap-2 px-2.5 py-1 rounded-full border ${isActive ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"}`}>
      {isActive ? <CheckCircle2 className="w-4 h-4"/> : <Circle className="w-4 h-4"/>}
      <span className="text-sm">{name}</span>
    </button>
  );
}

const AssignmentCard = ({ 
  choreName, 
  info, 
  dayBadge, 
  onOpen, 
  canEdit,
  updateTrigger,
  setUpdateTrigger,
}) => {
  return (
    <motion.div layout className={`rounded-2xl border p-4 shadow-sm bg-white`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="font-semibold text-gray-900 flex items-center gap-2">
            <ListChecks className="w-4 h-4"/> {choreName}
          </div>
          <div className="text-xs text-gray-500 mt-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> {dayBadge}</div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {Object.entries(info).map(([id, nameNStatus]) => (
          <AssigneeChip 
            key={id} 
            name={nameNStatus[0]} 
            active={nameNStatus[1]} 
            assignmentID={id}
            updateTrigger={updateTrigger}
            setUpdateTrigger={setUpdateTrigger}
          />
        ))}
      </div>

      <div className="mt-4 flex items-center gap-2">
        <button onClick={() => onOpen(info)} className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-gray-200"><Info className="w-4 h-4"/> Details</button>
        {canEdit && (
          <button onClick={() => onOpen(info, "edit")} className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"><Shuffle className="w-4 h-4"/> Edit</button>
        )}
      </div>
    </motion.div>
  );
}
export {AssignmentCard}