import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Auth uses sessionStorage + client AuthGuard for Phase 13.
 * Add cookie-based checks here when moving tokens to httpOnly cookies.
 */
export function middleware(_request: NextRequest) {
  void _request;
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/projects/:path*'],
};
