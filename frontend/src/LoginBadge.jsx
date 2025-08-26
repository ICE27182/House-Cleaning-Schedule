import React, { useMemo, useState } from "react";
import { CheckCircle2, Circle, Users, Calendar, History, Shuffle, Pencil, ListChecks, Info, X, Plus, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const LoginBadge = ({ user, setUser }) => {
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
export {LoginBadge}