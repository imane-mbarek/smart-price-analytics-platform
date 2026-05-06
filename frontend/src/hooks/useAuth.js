import { createContext, useContext, useEffect, useState } from "react";
import { login as apiLogin, register as apiRegister, logout as apiLogout } from "../services/api";

const Ctx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (!localStorage.getItem("access")) {
      localStorage.removeItem("user");
      return null;
    }
    const s = localStorage.getItem("user");
    return s ? JSON.parse(s) : null;
  });

  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener("auth:logout", onLogout);
    return () => window.removeEventListener("auth:logout", onLogout);
  }, []);

  const login = async (creds) => {
    const { data } = await apiLogin(creds);
    localStorage.setItem("access",  data.access);
    localStorage.setItem("refresh", data.refresh);
    const u = { username: creds.username };
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);
  };

  const register = async (form) => {
    await apiRegister(form);
    await login({ username: form.username, password: form.password });
  };

  const logout = () => {
    apiLogout();
    localStorage.removeItem("user");
    setUser(null);
  };

  return <Ctx.Provider value={{ user, login, register, logout }}>{children}</Ctx.Provider>;
}

export default function useAuth() { return useContext(Ctx); }
