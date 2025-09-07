import { useEffect, useState } from "react";
import {Users, Calendar, Shuffle, ListChecks, X, UserRound } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const getAssignees = (assignment) => Object.entries(assignment.info).map(([id, nameNStatus]) => nameNStatus[0]);

/* Subcomponents for each mode ------------------------------------------------- */
const DetailsView = ({ assignment, canEdit, onReassign }) => (
  <div className="p-4 space-y-4">
    <div>
      <div className="text-sm text-gray-600">Assignees</div>
      <div className="mt-2 flex flex-wrap gap-2">
        {Object.entries(assignment.info).map(([id, nameNStatus]) => (
          <div
            key={id}
            className={`flex items-center gap-2 px-2.5 py-1 rounded-full border ${
              nameNStatus[1]
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"
            }`}
          >
            {nameNStatus[0]}
          </div>
        ))}
      </div>
    </div>

    <div className="text-sm text-gray-600 flex items-center gap-2">
      <Users className="w-4 h-4" /> Pool:
      <code className="bg-gray-50 px-1.5 py-0.5 rounded">{assignment.group}</code>
    </div>

    <div className="text-sm text-gray-600 flex items-center gap-2">
      <Calendar className="w-4 h-4" />
      {assignment.dayBadge}
    </div>

    {/* {canEdit && (
      <div className="pt-2">
        <button onClick={() => onReassign()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 mr-2">
          <Shuffle className="w-4 h-4" /> Edit
        </button>
      </div>
    )} */}
  </div>
);

const EditPersonView = ({ person, personInfo, onToggleAvailability, onRemovePerson }) => (
  <div className="p-4 space-y-4">
    {personInfo && personInfo.left_at_around === null ? (
      <div className="flex justify-around">
        <button
          className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
          onClick={() => onToggleAvailability(person, !personInfo.is_available)}
        >
          {personInfo.is_available ? "Disable Temporarily" : "Enable"}
        </button>
        <button
          className="text-sm inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
          onClick={() => onRemovePerson(person)}
        >
          Remove
        </button>
      </div>
    ) : (
      <div>This person has left.</div>
    )}
  </div>
);

const AddPersonView = ({ addName, setAddName, addGroup, setAddGroup, onAdd, onClose }) => (
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
      <button onClick={onClose} className="px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">
        Cancel
      </button>
      <button onClick={onAdd} className="px-3 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
        Add person
      </button>
    </div>
  </div>
);

const ReassignView = ({ assignment, pool = [], reassign, setReassign, reason, setReason, onSave, onClose }) => (
  <div className="p-4 space-y-4">
    <div className="text-sm">Pick exactly {assignment.num} assignee(s) from the pool.</div>
    <div className="flex flex-wrap gap-2">
      {pool.map((p) => (
        <button
          key={p}
          onClick={() =>
            setReassign((prev) =>
              prev.includes(p) ? prev.filter((x) => x !== p) : prev.length < assignment.num ? [...prev, p] : prev
            )
          }
          className={`px-2.5 py-1.5 rounded-full border ${reassign.includes(p) ? "bg-indigo-600 text-white border-indigo-600" : "bg-white border-gray-300"}`}
        >
          {p}
        </button>
      ))}
    </div>
    <div className="text-sm text-gray-600">Selected: {reassign.join(", ") || "—"}</div>
    <div>
      <div className="text-sm text-gray-600 mb-1">Reason (optional)</div>
      <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. I need to play minecraft" className="w-full border rounded-lg px-3 py-2" />
    </div>
    <div className="flex justify-end gap-2">
      <button onClick={onClose} className="px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">
        Cancel
      </button>
      <button onClick={() => onSave({ people: reassign, reason })} disabled={reassign.length !== assignment.num} className="px-3 py-2 rounded-lg bg-gray-900 text-white disabled:opacity-50">
        Save
      </button>
    </div>
  </div>
);

/* Parent DetailsPanel -------------------------------------------------------- */
const DetailsPanel = ({
  open,
  person,
  mode = "details",
  assignment,
  onClose,
  onSwap,
  onReassign,
  canEdit,
  updateTrigger,
  setUpdateTrigger,
}) => {
  const [reason, setReason] = useState("");
  const [reassign, setReassign] = useState(assignment ? getAssignees(assignment) : []);
  const [addName, setAddName] = useState("");
  const [addGroup, setAddGroup] = useState("everyone");
  const [pool, setPool] = useState([]);
  const [personInfo, setPersonInfo] = useState(null);

  useEffect(() => {
    setReason("");
    setReassign(assignment ? getAssignees(assignment) : []);
  }, [assignment, mode]);

  useEffect(() => {
    setAddName("");
    setAddGroup("everyone");
  }, [mode]);

  useEffect(() => {
    if (person) {
      fetch(encodeURI(`/api/people/?person=${encodeURIComponent(person)}`), { method: "GET" })
        .then((res) =>
          res
            .json()
            .then((data) => setPersonInfo(data))
            .catch(() => setPersonInfo(null))
        )
        .catch(() => setPersonInfo(null));
    } else if (assignment) {
      fetch(`/api/people?group=${encodeURIComponent(assignment.group)}`, { method: "GET" })
        .then((res) =>
          res
            .json()
            .then((data) => setPool(Array.isArray(data) ? data : data?.[assignment.group] ?? []))
            .catch(() => setPool([]))
        )
        .catch(() => setPool([]));
    }
  }, [person, assignment, updateTrigger]);

  const triggerRefresh = () => setUpdateTrigger((t) => (t ?? 0) + 1);

  const handleToggleAvailability = (personName, availability) => {
    fetch("/api/people/set-availability", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ person: personName, availability }),
    })
      .then((resp) =>
        resp
          .json()
          .then((data) => {
            if (!resp.ok) alert(`Failed.\n${data?.error}`);
            triggerRefresh();
          })
          .catch(() => {
            if (resp.ok) triggerRefresh();
          })
      )
      .catch((err) => {
        console.error("Network error:", err);
        alert("Network error");
      });
  };

  const handleRemovePerson = (personName) => {
    const repeatedName = prompt(
      "You are trying to remove a person.\n" +
        "This CANNOT be easily undone.\n" +
        "Repeat the exact the name of the person you are trying to remove to continue. \n" +
        "Once continued, you cannot undo it yourself."
    );
    if (repeatedName !== personName) {
      alert("The names do not match.");
      return;
    }
    fetch("/api/people/remove", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ person: personName }),
    })
      .then((resp) =>
        resp
          .json()
          .then((data) => {
            triggerRefresh();
            if (!resp.ok) {
              alert(`Failed.\n${data?.error}`);
            } else {
              alert(`${personName} has been removed.`);
            }
          })
          .catch(() => {
            triggerRefresh();
          })
      )
      .catch((err) => {
        console.error("Network error:", err);
        alert("Network error");
      });
  };

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
      .then((resp) =>
        resp
          .json()
          .then((data) => {
            if (!resp.ok || !data?.ok) {
              alert(`Failed to add person.\n${data?.error}`);
              return;
            }
            triggerRefresh();
            onClose();
          })
          .catch(() => {
            if (resp.ok) {
              triggerRefresh();
              onClose();
            }
          })
      )
      .catch((err) => {
        console.error("Network error:", err);
        alert("Network error while adding person");
      });
  };

  const handleSaveReassign = ({ people, reason: r }) => {
    onReassign({ people, reason: r });
    onClose();
  };

  if (!open || (!assignment && !person && mode !== "addPerson")) return null;

  return (
    <AnimatePresence>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/30 z-40" onClick={onClose} />
      <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 30, opacity: 0 }} className="fixed z-50 inset-x-0 bottom-0 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 w-full md:w-[720px] bg-white rounded-2xl shadow-xl border">
        <div className="p-4 border-b flex items-center justify-between">
          {mode === "editPerson" ? (
            <div className="font-semibold flex items-center gap-2">
              <UserRound className="w-4 h-4" /> {person}
            </div>
          ) : mode === "addPerson" ? (
            <div className="font-semibold flex items-center gap-2">
              <UserRound className="w-4 h-4" /> Add a new housemate
            </div>
          ) : (
            <div className="font-semibold flex items-center gap-2">
              <ListChecks className="w-4 h-4" /> {assignment?.name}
            </div>
          )}
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100">
            <X className="w-4 h-4" />
          </button>
        </div>

        {mode === "details" && <DetailsView assignment={assignment} canEdit={canEdit} onReassign={onReassign} />}

        {mode === "editPerson" && <EditPersonView person={person} personInfo={personInfo} onToggleAvailability={handleToggleAvailability} onRemovePerson={handleRemovePerson} />}

        {mode === "addPerson" && <AddPersonView addName={addName} setAddName={setAddName} addGroup={addGroup} setAddGroup={setAddGroup} onAdd={handleAddPerson} onClose={onClose} />}

        {mode === "reassign" && <ReassignView assignment={assignment} pool={pool} reassign={reassign} setReassign={setReassign} reason={reason} setReason={setReason} onSave={handleSaveReassign} onClose={onClose} />}
      </motion.div>
    </AnimatePresence>
  );
};

export {DetailsPanel};