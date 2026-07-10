// nightshift install counter — anonymous tally, no PII.
// POST /api/i  -> records one install, returns { ok, count }
// GET  /api/i  -> returns { count }
// Degrades to { count: null } if the DB is unreachable, so the page never breaks.
import { neon } from '@neondatabase/serverless';

let sql = null;

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Access-Control-Allow-Origin', '*');
  try {
    if (!process.env.DATABASE_URL) return res.status(200).json({ count: null });
    sql = sql || neon(process.env.DATABASE_URL);
    if (req.method === 'POST') {
      let source = 'install.sh', version = null;
      try {
        const b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
        if (b.source) source = String(b.source).slice(0, 64);
        if (b.version) version = String(b.version).slice(0, 32);
      } catch { /* keep defaults */ }
      await sql`INSERT INTO nightshift_installs (source, version) VALUES (${source}, ${version})`;
    }
    const rows = await sql`SELECT count(*)::int AS count FROM nightshift_installs`;
    return res.status(200).json({ count: rows[0].count });
  } catch (e) {
    console.error('install-counter:', e);
    return res.status(200).json({ count: null });
  }
}
