'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { fetchCurrentUser, loginRequest, registerRequest } from '@/lib/api/auth';
import { ACCESS_TOKEN_KEY } from '@/lib/auth/storage-keys';
import type { ApiUser } from '@/types/api';

type AuthState = {
  token: string | null;
  user: ApiUser | null;
  /** True until first storage + optional /me resolution finishes */
  bootstrapping: boolean;
};

type AuthContextValue = AuthState & {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function readStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

function writeStoredToken(token: string | null) {
  if (typeof window === 'undefined') return;
  if (token) sessionStorage.setItem(ACCESS_TOKEN_KEY, token);
  else sessionStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<ApiUser | null>(null);
  const [bootstrapping, setBootstrapping] = useState(true);

  useEffect(() => {
    const stored = readStoredToken();
    setToken(stored);
    if (!stored) {
      setBootstrapping(false);
      return;
    }
    fetchCurrentUser(stored)
      .then(setUser)
      .catch(() => {
        writeStoredToken(null);
        setToken(null);
        setUser(null);
      })
      .finally(() => setBootstrapping(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await loginRequest(email, password);
    writeStoredToken(res.access_token);
    setToken(res.access_token);
    const me = await fetchCurrentUser(res.access_token);
    setUser(me);
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    await registerRequest(email, password);
    await login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    writeStoredToken(null);
    setToken(null);
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    const me = await fetchCurrentUser(token);
    setUser(me);
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      bootstrapping,
      login,
      register,
      logout,
      refreshUser,
    }),
    [token, user, bootstrapping, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
