// Watchlist: one Google News RSS query per theme or account.
// Edit this list to track your own accounts. No API key needed.
const watchlist = [
  { watch: "New security leader",     query: 'appoints CISO OR "chief information security officer" Belgium OR Netherlands' },
  { watch: "AI rollout in finance",   query: 'bank OR insurer "rolls out" AI assistants Europe' },
  { watch: "AI Act readiness",        query: '"AI Act" compliance bank OR insurer' },
  { watch: "Belgian scale-up funding",query: 'Belgian startup raises "Series A" OR "Series B"' },
  { watch: "AI governance hiring",    query: '"AI governance" lead OR head hiring Europe' },
  // Add accounts the same way, e.g.:
  // { watch: "Acme Bank", query: '"Acme Bank" AI OR CISO OR funding' },
];

return watchlist.map(w => ({
  json: {
    watch: w.watch,
    query: w.query,
    url: "https://news.google.com/rss/search?q=" + encodeURIComponent(w.query) + "&hl=en&gl=BE&ceid=BE:en",
  },
}));
