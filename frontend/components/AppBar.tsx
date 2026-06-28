"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearSession, getUser, type SessionUser } from "../lib/api";

export default function AppBar() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  // Read session on mount + whenever route changes (login/logout reflect quickly).
  useEffect(() => {
    setMounted(true);
    setUser(getUser());
  }, [pathname]);

  function logout() {
    clearSession();
    setUser(null);
    router.push("/login");
  }

  const navLink = (href: string, label: string) => {
    const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
    return (
      <Link href={href} className={`nav-link${active ? " nav-link-active" : ""}`}>
        {label}
      </Link>
    );
  };

  return (
    <header className="appbar">
      <div className="appbar-inner">
        <Link href="/" className="wordmark">
          <span className="wordmark-mark" aria-hidden>
            ◆
          </span>
          <span className="wordmark-text">
            Meridian<span className="wordmark-thin"> Lending</span>
          </span>
        </Link>

        <nav className="appbar-nav">
          {navLink("/", "Home")}
          {navLink("/apply", "Apply")}
          {navLink("/servicing", "Servicing")}
        </nav>

        <div className="appbar-auth">
          {/* Avoid hydration mismatch: render auth state only after mount. */}
          {!mounted ? null : user ? (
            <>
              <span className="auth-user">
                {user.name || user.username}
                <span className="auth-role">{user.role}</span>
              </span>
              <button className="btn-ghost btn-sm" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <Link href="/login" className="btn-ghost btn-sm">
              Log in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
