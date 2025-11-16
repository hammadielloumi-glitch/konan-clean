// src/utils/htmlExport.js
export function conversationToHTML({ title = 'Conversation KONAN', messages = [], annexes = [] }) {
  const esc = (s = '') => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Collecte de toutes les citations pour notes
  let noteIndex = 0;
  const footnotes = [];
  const htmlMsgs = messages.map((m) => {
    // Attacher des renvois [n] dans le texte si citations présentes
    let body = esc(m.content);
    if (Array.isArray(m.citations) && m.citations.length) {
      const localMarks = m.citations.map((c) => {
        noteIndex += 1;
        footnotes.push({ n: noteIndex, ...c });
        return `[${noteIndex}] ${c.code} – Art. ${c.article}`;
      });
      body += `\n\n${localMarks.map((t) => `• ${esc(t)}`).join('\n')}`;
    }
    return `
    <div style="margin:8px 0;padding:12px;border-radius:12px;background:${m.role === 'user' ? '#0F172A' : '#111827'};color:#E5E7EB">
      <div style="font-weight:600;margin-bottom:4px">${m.role === 'user' ? 'Utilisateur' : 'KONAN ⚖️'}</div>
      <pre style="white-space:pre-wrap;margin:0;font-family:Inter,system-ui">${body}</pre>
    </div>`;
  }).join('');

  const htmlNotes = footnotes.length
    ? `
    <h2 style="color:#93C5FD;margin-top:24px">Références</h2>
    <ol>
      ${footnotes.map(fn => `<li style="margin-bottom:6px"><a href="${esc(fn.url || '#')}" style="color:#93C5FD;text-decoration:none">${esc(fn.code)} — Art. ${esc(fn.article)}</a></li>`).join('')}
    </ol>`
    : '';

  const htmlAnnexes = annexes.length
    ? `
    <h2 style="color:#93C5FD;margin-top:24px">Annexes</h2>
    <ul>
      ${annexes.map(a => `<li><a style="color:#93C5FD;text-decoration:none" href="${esc(a.url)}">${esc(a.name)} (${esc(a.mime||'')})</a></li>`).join('')}
    </ul>`
    : '';

  return `<!doctype html>
  <html><head><meta charset="utf-8"><title>${esc(title)}</title></head>
  <body style="background:#0B1220;color:#E5E7EB;font-family:Inter,system-ui;padding:16px">
    <h1 style="color:#93C5FD">${esc(title)}</h1>
    ${htmlMsgs}
    ${htmlNotes}
    ${htmlAnnexes}
  </body></html>`;
}
