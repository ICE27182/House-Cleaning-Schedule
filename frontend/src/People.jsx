import { ClipboardList } from 'lucide-react'
import React, { useEffect, useState } from 'react'

const People = () => {
  const [nameLists, setNameLists] = useState(null)
  useEffect(() => {
    fetch("/api/people", { method: "GET" })
      .then(response => response.json()
        .then(data => setNameLists(data)))
  }, [])
  return (
   <div className="flex flex-col flex-wrap gap-4">
    {nameLists && Object.entries(nameLists).map(([namelistName, namelist], i) => (
          <div key={i} className="flex flex-col gap-2">
            <div className="font-semibold flex items-center gap-2"><ClipboardList />{namelistName}</div>
            <div className="flex flex-wrap gap-2 mx-6">
              {Object.entries(namelist)
                .sort(([nameA, avaiA], [nameB, avaiB]) => 
                  avaiA === avaiB 
                  ? nameA.localeCompare(nameB)
                  : avaiB - avaiA)
                .map(([name, isAvailable], j) => (
                <button 
                  key={j}
                  className={`px-2.5 py-1.5 rounded-full ${isAvailable ? "bg-white border border-gray-300" : "text-white bg-gray-200"}`}
                >
                  {name}
                </button>
              ))}
            </div>
            <div className="mx-4 mb-2 mt-1 border-1 border-blue-950"></div>
          </div>
        )
    )}
  </div>
  )
}

export default People