import type { Metadata } from 'next';
import { Cormorant_Garamond, Lora, Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const display = Cormorant_Garamond({ subsets: ['latin'], weight: ['400','500','600','700'], style: ['normal','italic'], variable: '--font-display' });
const body = Lora({ subsets: ['latin'], weight: ['400','500','600'], style: ['normal','italic'], variable: '--font-body' });
const ui = Inter({ subsets: ['latin'], weight: ['400','500','600','700'], variable: '--font-ui' });
const mono = JetBrains_Mono({ subsets: ['latin'], weight: ['400','500'], variable: '--font-mono' });

export const metadata: Metadata = {
  title: 'Lectio — Scripture-grounded Christian AI',
  description: 'A scripture-grounded study companion with denomination-aware theology and hallucination prevention.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${ui.variable} ${mono.variable} h-full`}>
      <body className="h-full bg-paper text-ink antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
