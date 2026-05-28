import { NextResponse } from 'next/server';
import { readFileSync } from 'fs';
import { join } from 'path';

export async function GET() {
  try {
    const p = join(process.cwd(), '..', 'evaluation', 'results.json');
    const raw = readFileSync(p, 'utf-8');
    return NextResponse.json(JSON.parse(raw));
  } catch {
    return NextResponse.json(null, { status: 404 });
  }
}
