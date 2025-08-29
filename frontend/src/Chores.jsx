import { Pencil } from 'lucide-react'
import React, { useEffect, useState } from 'react'

const ChoreCard = ({chore, canEdit}) => {
  return (
    <div key={chore.id} className="border rounded-2xl p-4">
      <div className="font-medium mb-2">{chore.name}</div>
      <div className='text-sm mb-2 truncate'>{chore.description}</div>
      <div className="text-sm text-gray-600">Number of assignees: {chore.assignee_count}</div>
      <div className="text-sm text-gray-600 mb-2">{chore.frequency}</div>
      {/* <div className="flex flex-wrap gap-2">
        <button 
          disabled={!canEdit} 
          onClick={()=>openPanel(chore, "reassign")}
          className="px-2.5 py-1.5 rounded-lg bg-indigo-600 text-white disabled:opacity-50"
        >
          <Pencil className="w-4 h-4 inline mr-1"/> Edit
        </button>
      </div> */}
    </div>
  )
}

const Chores = (canEdit) => {
  const [chores, setChores] = useState([])
  useEffect(() => {
    fetch("/api/chores", { method: "GET" })
      .then(response => response.json()
        .then(data => setChores(data)))
  }, [])
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {chores && chores.map(chore => <ChoreCard key={chore.id} chore={chore} canEdit={canEdit} />)}
    </div>
  )
}

export default Chores