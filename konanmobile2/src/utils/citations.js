// src/utils/citations.js
/**
 * Injecte des marqueurs [n] pour chaque citation dans le texte.
 * Stratégie:
 * 1) Cherche premier match fort "Art. <article>" (ou "Article <article>") ou code.
 * 2) Si non trouvé, insère [n] en fin de paragraphe.
 * N'insère qu'une fois par citation.
 *
 * @param {string} content Markdown de la réponse
 * @param {Array<{code:string, article:string, url?:string}>} citations
 * @returns {string}
 */
export function injectInlineCitations(content, citations) {
    if (!Array.isArray(citations) || !citations.length || !content) return content;
  
    let out = content;
    const used = new Set();
    // Pour éviter de déplacer les index après insertions, on reconstruit en segments.
    // On fait des remplacements prudents par RegExp non globales avec échappement.
    const tryInsert = (pattern, marker) => {
      const re = new RegExp(pattern, 'i'); // premier match
      const m = out.match(re);
      if (!m) return false;
      const idx = m.index + m[0].length;
      out = out.slice(0, idx) + ` [${marker}]` + out.slice(idx);
      return true;
    };
  
    citations.forEach((c, i) => {
      const n = i + 1;
      if (used.has(n)) return;
      const art = (c.article || '').toString().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const code = (c.code || '').toString().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  
      // 1) "Art. <article>" ou "Article <article>"
      const ok1 = art && tryInsert(`(Art\\.|Article)\\s*${art}\\b`, n);
      if (ok1) { used.add(n); return; }
  
      // 2) "<code>" puis "Art. <article>" plus loin
      const ok2 = code && tryInsert(`${code}\\b`, n);
      if (ok2) { used.add(n); return; }
  
      // 3) append à la fin du premier paragraphe
      const pBreak = out.indexOf('\n\n');
      if (pBreak > -1) {
        out = out.slice(0, pBreak) + ` [${n}]` + out.slice(pBreak);
      } else {
        out = out + ` [${n}]`;
      }
      used.add(n);
    });
  
    return out;
  }
  