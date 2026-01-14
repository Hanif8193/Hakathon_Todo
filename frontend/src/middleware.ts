import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Middleware to protect routes that require authentication.
 *
 * Redirects unauthenticated users from /dashboard to /login.
 * Note: This is a client-side check based on token presence.
 * Server-side validation happens on each API request.
 */
export function middleware(request: NextRequest) {
  // Get token from cookies or headers
  const token = request.cookies.get('token')?.value

  // If accessing dashboard without token, redirect to login
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      const loginUrl = new URL('/login', request.url)
      return NextResponse.redirect(loginUrl)
    }
  }

  return NextResponse.next()
}

// Configure which routes use this middleware
export const config = {
  matcher: ['/dashboard/:path*']
}
