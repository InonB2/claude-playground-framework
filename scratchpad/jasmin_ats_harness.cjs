// Jasmin QA harness — extract computeAtsMatch from dashboard/index.html and run it.
const fs = require('fs');
const path = require('path');

const ROOT = 'D:/Claude Playground';
const dash = fs.readFileSync(path.join(ROOT, 'dashboard/index.html'), 'utf8');

// Extract the engine block: from "const ATS_STOP_WORDS" to "window.computeAtsMatch = computeAtsMatch;"
const startIdx = dash.indexOf('const ATS_STOP_WORDS');
const endMarker = 'window.computeAtsMatch = computeAtsMatch;';
const endIdx = dash.indexOf(endMarker);
if (startIdx < 0 || endIdx < 0) { console.error('Could not locate engine block'); process.exit(1); }
const engineSrc = dash.slice(startIdx, endIdx + endMarker.length);

// Shim DOMParser: strip script/style/noscript content then strip tags -> textContent
global.DOMParser = class {
  parseFromString(s) {
    let body = s;
    body = body.replace(/<(script|style|noscript)[^>]*>[\s\S]*?<\/\1>/gi, ' ');
    const text = body.replace(/<[^>]+>/g, ' ');
    return { body: { textContent: text }, querySelectorAll: () => [] };
  }
};
// The engine calls doc.querySelectorAll(...).forEach — our parsed doc must support it.
global.DOMParser = class {
  parseFromString(s) {
    let body = s.replace(/<(script|style|noscript)[^>]*>[\s\S]*?<\/\1>/gi, ' ');
    const textContent = body.replace(/<[^>]+>/g, ' ');
    return {
      body: { textContent },
      querySelectorAll: () => ({ forEach: () => {} })
    };
  }
};

global.window = {};
const computeAtsMatch = eval('(function(){' + engineSrc + '\nreturn computeAtsMatch;})()');

function run(label, cvPath, jdPath) {
  const cv = fs.readFileSync(cvPath, 'utf8');
  const jd = fs.readFileSync(jdPath, 'utf8');
  const r = computeAtsMatch(cv, jd);
  console.log(`${label}: score=${r.score}%  matched=${r.matched}/${r.totalKeywords}  cvTokens=${r.stats.cvTokens}`);
  return r;
}

const SE = 'owner_inbox/archive/cv_archive/ELBIT-SystemEng-PM-Netanya';
const TP = 'owner_inbox/archive/cv_archive/20248_TechnicalPM_Elbit_Netanya';

console.log('=== SysEng ===');
run('  v2', path.join(ROOT, SE, 'v2_Inon_Baasov_CV_SystemEngPM.html'), path.join(ROOT, SE, 'JD.txt'));
const se3 = run('  v3', path.join(ROOT, SE, 'v3_Inon_Baasov_CV_SystemEngPM.html'), path.join(ROOT, SE, 'JD.txt'));
console.log('  v3 gap (top 8):', se3.gap.slice(0,8).map(g=>g.kw).join(' | '));
console.log('  v3 matched includes c4i?', se3.gap.every(g=>g.kw!=='c4i') ? 'c4i NOT in gap (matched)' : 'c4i STILL in gap');

console.log('=== TechPM ===');
run('  v2', path.join(ROOT, TP, 'v2_Inon_Baasov_CV_TechnicalPM.html'), path.join(ROOT, TP, 'JD.txt'));
const tp3 = run('  v3', path.join(ROOT, TP, 'v3_Inon_Baasov_CV_TechnicalPM.html'), path.join(ROOT, TP, 'JD.txt'));
console.log('  v3 gap (top 8):', tp3.gap.slice(0,8).map(g=>g.kw).join(' | '));
console.log('  v3 c4i status:', tp3.gap.every(g=>g.kw!=='c4i') ? 'c4i NOT in gap (matched)' : 'c4i STILL in gap');
