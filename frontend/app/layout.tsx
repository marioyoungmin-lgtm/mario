import './globals.css';
import type { Metadata } from 'next';
import { ReactNode } from 'react';

/** Root layout required by Next.js app router. */
export const metadata: Metadata = {
  title: 'LifeOS 0-21',
  description: 'AI-assisted life dashboard for ages 0-21',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
