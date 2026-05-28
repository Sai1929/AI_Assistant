import { NextResponse } from 'next/server';
import { readFileSync } from 'fs';
import { join } from 'path';
import { execFile } from 'child_process';

export async function GET() {
  try {
    const p = join(process.cwd(), '..', 'evaluation', 'results.json');
    const raw = readFileSync(p, 'utf-8');
    return NextResponse.json(JSON.parse(raw));
  } catch {
    return NextResponse.json(null, { status: 404 });
  }
}

export async function POST() {
  // Trigger run_eval.py fast-mode, wait for completion, return fresh results
  const root = join(process.cwd(), '..');
  const script = join(root, 'scripts', 'run_eval.py');

  await new Promise<void>((resolve, reject) => {
    execFile(
      'python',
      [script],
      { cwd: root, timeout: 180_000 },
      (err) => (err ? reject(err) : resolve()),
    );
  });

  try {
    const p = join(root, 'evaluation', 'results.json');
    const raw = readFileSync(p, 'utf-8');
    return NextResponse.json(JSON.parse(raw));
  } catch {
    return NextResponse.json({ error: 'eval ran but results unreadable' }, { status: 500 });
  }
}
