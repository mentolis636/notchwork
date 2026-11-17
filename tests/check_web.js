// Checks that the cipher inside index.html gives the same output as notchwork.py.
// Run from the repo root with:  node tests/check_web.js

const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const block = html.match(/\/\/ ==== ENGINE START ====([\s\S]*?)\/\/ ==== ENGINE END ====/);
if (!block) {
  console.error('Could not find the engine block in index.html');
  process.exit(1);
}
const { Machine, ALPHABET, idx } = new Function(block[1] + '; return { Machine, ALPHABET, idx };')();

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'vectors.json'), 'utf8'));
let bad = 0;
for (const c of cases) {
  const machine = new Machine(Array.from(c.notches, idx), Array.from(c.start, idx));
  const coded = Array.from(c.text, ch => (ALPHABET.includes(ch) ? machine.encode(ch) : ch)).join('');
  if (coded !== c.coded) {
    bad++;
    console.error('Mismatch for notches ' + c.notches + ', start ' + c.start);
  }
}

console.log(cases.length - bad + ' of ' + cases.length + ' vectors match the Python version');
process.exit(bad ? 1 : 0);
