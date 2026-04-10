'use client';

import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

export type UiMode = 'beginner' | 'advanced';

type UiModeContextValue = {
  mode: UiMode;
  setMode: (mode: UiMode) => void;
  isAdvanced: boolean;
};

const STORAGE_KEY = 'aspe-ui-mode';

const UiModeContext = createContext<UiModeContextValue | null>(null);

export function UiModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<UiMode>('beginner');

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === 'advanced' || stored === 'beginner') {
      setModeState(stored);
    }
  }, []);

  function setMode(nextMode: UiMode) {
    setModeState(nextMode);
    window.localStorage.setItem(STORAGE_KEY, nextMode);
  }

  const value = useMemo(
    () => ({
      mode,
      setMode,
      isAdvanced: mode === 'advanced',
    }),
    [mode],
  );

  return <UiModeContext.Provider value={value}>{children}</UiModeContext.Provider>;
}

export function useUiMode() {
  const ctx = useContext(UiModeContext);
  if (!ctx) throw new Error('useUiMode must be used inside UiModeProvider');
  return ctx;
}

export function useScreenUiMode(screenKey: string) {
  const { mode, isAdvanced } = useUiMode();
  void screenKey;

  return {
    mode,
    isAdvanced,
    localMode: undefined,
    effectiveMode: mode,
    isEffectiveAdvanced: isAdvanced,
    setLocalMode: () => {
      /* Single global mode only */
    },
  };
}
