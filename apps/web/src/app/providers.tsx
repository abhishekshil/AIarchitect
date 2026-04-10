'use client';

import { AuthProvider } from '@/context/auth-context';
import { UiModeProvider } from '@/context/ui-mode-context';
import type { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <UiModeProvider>{children}</UiModeProvider>
    </AuthProvider>
  );
}
