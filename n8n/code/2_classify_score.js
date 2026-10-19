// Classify each article into a trigger type and score it.
// score = trigger strength x recency decay (half-life 21 days).
const HALF_LIFE_DAYS = 21;
const MAX_AGE_DAYS = 90;

const TRIGGERS = [
  { type: "new_exec",      strength: 0.8,  re: /\b(appoint(s|ed)?|names?|hires?|joins? as|new)\b.*\b(CISO|CIO|CTO|CDO|CRO|chief|head of)\b/i },
  { type: "funding_ma",    strength: 0.8,  re: /\b(raises?|funding|series [a-e]|acquires?|acquisition|merger)\b/i },
  { type: "ai_rollout",    strength: 0.9,  re: /\b(rolls? out|deploys?|launch(es)?|pilot(s)?|adopts?)\b.*\b(AI|copilot|agent|GenAI|LLM)\b/i },
  { type: "hiring",        strength: 0.75, re: /\b(hiring|vacanc|job opening|recruit)\b/i },
  { type: "breach_incident", strength: 0.85, re: /\b(breach|cyber ?attack|incident|ransomware|outage)\b/i },
  { type: "regulation",    strength: 0.5,  re: /\b(AI Act|DORA|NIS2|GDPR|regulat|fine[sd]?)\b/i },
];

const now = Date.now();

const out = [];
const input = $input.all();
for (let i = 0; i < input.length; i++) {
  const item = input[i];
  const a = item.json;
  if (!a.title) continue;                       // failed feed or empty item
  const text = `${a.title} ${a.contentSnippet || ""}`;

  const trig = TRIGGERS.find(t => t.re.test(text));
  if (!trig) continue;                           // news, but not a trigger

  const published = new Date(a.isoDate || a.pubDate || now).getTime();
  const ageDays = Math.max(0, Math.round((now - published) / 86400000));
  if (ageDays > MAX_AGE_DAYS) continue;          // context, not a trigger

  const decay = Math.pow(0.5, ageDays / HALF_LIFE_DAYS);
  // Which watchlist query produced this article? Follow n8n's item linking back to the Watchlist node.
  let watch = "unknown";
  try { watch = $('Watchlist').itemMatching(i).json.watch; } catch (e) {}

  // Google News titles end with " - Source name". The source is secondary until a human checks the primary source.
  const source = (a.title.match(/ - ([^-]+)$/) || [])[1] || "unknown";

  out.push({
    json: {
      watch,
      trigger: trig.type,
      title: a.title,
      story: a.title.replace(/ - [^-]+$/, "").toLowerCase().replace(/[^a-z0-9 ]/g, "").split(" ").slice(0, 4).join(" "),
      link: a.link,
      source,
      published: new Date(published).toISOString().slice(0, 10),
      age_days: ageDays,
      score: Math.round(trig.strength * decay * 100),
      verification: "secondary (news): check the primary source before using in outreach",
    },
  });
}
return out;
