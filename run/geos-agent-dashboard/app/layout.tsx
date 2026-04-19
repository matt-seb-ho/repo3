import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ACP/X JSONL Viewer",
  description: "Inspect ACP, Claude Code, and transcript JSONL logs."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
