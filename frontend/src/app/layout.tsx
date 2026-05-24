import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ZM — AI Restaurant Recommendations",
  description:
    "Personalized restaurant picks by location, budget, cuisine, and rating — powered by real data and AI explanations.",
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
