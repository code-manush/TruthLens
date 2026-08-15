import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

// Path to your Python project root (go up from frontend/)
const PYTHON_ROOT = path.resolve(process.cwd(), '..');
const PYTHON_EXE  = path.join(PYTHON_ROOT, '.venv', 'Scripts', 'python.exe');
const MAIN_SCRIPT = path.join(PYTHON_ROOT, 'main.py');

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { url, text } = body;

    if (!url && !text) {
      return NextResponse.json({ error: 'Provide either a url or text field.' }, { status: 400 });
    }

    // Build args for main.py
    const args: string[] = [MAIN_SCRIPT, '--json'];
    if (url)  args.push('--url',  url);
    if (text) args.push('--text', text);

    const result = await new Promise<string>((resolve, reject) => {
      const proc = spawn(PYTHON_EXE, args, { 
        cwd: PYTHON_ROOT,
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
      });
      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (d) => { stdout += d.toString(); });
      proc.stderr.on('data', (d) => { stderr += d.toString(); });

      proc.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(stderr || `Process exited with code ${code}`));
        }
      });

      // 15 minute timeout to match Ollama
      setTimeout(() => {
        proc.kill();
        reject(new Error('Analysis timed out after 15 minutes. The AI model may be overloaded.'));
      }, 15 * 60 * 1000);
    });

    // Parse JSON output from Python
    const jsonMatch = result.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Could not parse scorecard JSON from backend output.');
    }
    const scorecard = JSON.parse(jsonMatch[0]);
    return NextResponse.json(scorecard);

  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : 'Internal server error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
