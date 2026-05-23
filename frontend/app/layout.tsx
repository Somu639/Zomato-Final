import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ZM — Restaurant Recommendations",
  description: "AI-powered restaurant picks from the Zomato dataset",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
