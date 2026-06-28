import "./globals.css";
import type { Metadata } from "next";
import AppBar from "../components/AppBar";

export const metadata: Metadata = {
  title: "Meridian Lending — Personal Installment Loans",
  description:
    "Apply for a personal installment loan from $1,000 to $50,000, review your Truth-in-Lending disclosure, and manage your loan online.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AppBar />
        <div className="page">{children}</div>
        <footer className="footer">
          <div className="footer-inner">
            <span>© {new Date().getFullYear()} Meridian Lending, Inc.</span>
            <span className="footer-muted">
              Member-grade fintech demo · NMLS #000000 · Equal Housing Lender
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
