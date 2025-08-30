// ...existing code...
import React, { useMemo, useState } from "react";
import {  UserRound } from "lucide-react";

const LoginBadge = ({ user, setUser }) => {
  const handleLogout = async () => {
    try {
      const resp = await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
      if (resp.ok) {
        setUser("");
      } else {
        const err = await resp.json().catch(()=>({ error: "logout failed" }));
        alert(err?.error || "Logout failed");
      }
    } catch (e) {
      alert("Network error during logout");
    }
  };

  const handleLogin = async () => {
    const name = prompt("Enter nickname (for logging changes)");
    if (!name) return;
    const password = prompt("Password (Default to qwerty123)");
    if (password === null) return;

    try {
      const resp = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ name, password }),
      });
      const data = await resp.json().catch(()=>({}));
      if (!resp.ok) {
        alert(data?.error || "Login failed");
        return;
      }
      setUser(data.name || name);
    } catch (err) {
      alert("Network error during login");
    }
  };

  return (
    <div className="flex items-center gap-2">
      {user ? (
        <>
          <div className="text-sm flex items-center gap-1 px-2 py-1 rounded-lg bg-gray-100"><UserRound className="w-4 h-4"/> {user}</div>
          <button onClick={handleLogout} className="text-sm px-2 py-1 rounded-lg bg-gray-100 hover:bg-gray-200">Logout</button>
        </>
      ) : (
        <button onClick={handleLogin} className="text-sm px-2.5 py-1.5 rounded-lg bg-gray-900 text-white hover:bg-black">Login to edit</button>
      )}
    </div>
  );
}
export {LoginBadge}
// ...existing code...