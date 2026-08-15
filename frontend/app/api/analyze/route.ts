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
<<<<<<< HEAD
      const proc = spawn(PYTHON_EXE, args, { 
        cwd: PYTHON_ROOT,
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
      });
      let stdout = '';
=======
      const proc = spawn(PYTHON_EXE, args, {
        cwd: PYTHON_ROOT,
        env: {
          ...process.env,
          // Force the Python child process to use UTF-8 for all I/O on Windows
          PYTHONIOENCODING: 'utf-8',
          PYTHONUTF8: '1',
        },
      });
      const chunks: Buffer[] = [];
>>>>>>> 5e247bcf80486eba680c196d050d414d6171064e
      let stderr = '';

      // Collect raw bytes so we can decode as UTF-8 (avoids cp1252 mangling)
      proc.stdout.on('data', (d: Buffer) => { chunks.push(d); });
      proc.stderr.on('data', (d: Buffer) => { stderr += d.toString('utf-8'); });

      proc.on('close', (code) => {
        const stdout = Buffer.concat(chunks).toString('utf-8');
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
