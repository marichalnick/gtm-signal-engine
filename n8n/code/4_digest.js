// Build a daily digest in Markdown and HTML (one output item).
const items = $input.all().map(i => i.json);
const date = new Date().toISOString().slice(0, 10);

if (items.length === 0) {
  return [{ json: { date, count: 0, markdown: `# Signal digest ${date}\n\nNo new signals above the threshold today.`, html: `<h2>Signal digest ${date}</h2><p>No new signals above the threshold today.</p>` } }];
}

const md = [
  `# Signal digest ${date}`,
  ``,
  `${items.length} new signal(s). All come from news coverage: **verify the primary source before using one in outreach.**`,
  ``,
  `| Score | Watch | Trigger | Age | Headline |`,
  `|---:|---|---|---:|---|`,
  ...items.map(s => `| ${s.score} | ${s.watch} | ${s.trigger} | ${s.age_days}d | [${s.title.replace(/\|/g, "/")}](${s.link}) |`),
].join("\n");

const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
const html = `<h2>Signal digest ${date}</h2>
<p>${items.length} new signal(s). Verify the primary source before using one in outreach.</p>
<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Score</th><th>Watch</th><th>Trigger</th><th>Age</th><th>Headline</th></tr>
${items.map(s => `<tr><td>${s.score}</td><td>${esc(s.watch)}</td><td>${s.trigger}</td><td>${s.age_days}d</td><td><a href="${esc(s.link)}">${esc(s.title)}</a></td></tr>`).join("\n")}
</table>`;

return [{ json: { date, count: items.length, markdown: md, html } }];
