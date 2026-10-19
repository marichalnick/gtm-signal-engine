// Remove duplicates within this run AND across runs, then keep the best signals.
// Cross-run memory uses workflow static data. It is only used on scheduled runs,
// so manual test runs always show the full result.
const MIN_SCORE = 30;
const TOP_N = 15;

const scheduled = $execution.mode === 'trigger';
const memory = scheduled ? $getWorkflowStaticData('global') : {};
memory.seen = memory.seen || {};

// Highest score first, so when the same story appears in several outlets we keep the best one.
const sorted = $input.all().sort((a, b) => b.json.score - a.json.score);
const seenNow = new Set();
const fresh = [];
for (const item of sorted) {
  const key = item.json.link || item.json.title;
  const story = item.json.story;            // same story, different outlet
  if (seenNow.has(key) || seenNow.has(story) || memory.seen[key]) continue;
  seenNow.add(key); seenNow.add(story);
  if (item.json.score < MIN_SCORE) continue;
  fresh.push(item);
}

// Remember what we reported, and forget entries older than 120 days.
const today = new Date().toISOString().slice(0, 10);
for (const i of fresh) memory.seen[i.json.link || i.json.title] = today;
const cutoff = new Date(Date.now() - 120 * 86400000).toISOString().slice(0, 10);
for (const [k, d] of Object.entries(memory.seen)) if (d < cutoff) delete memory.seen[k];

return fresh
  .sort((a, b) => b.json.score - a.json.score)
  .slice(0, TOP_N);
