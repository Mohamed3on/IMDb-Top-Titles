const arg = Bun.argv[2];
if (!arg) {
  console.log("Usage: bun title.ts <imdb-url-or-title-id>");
  process.exit(1);
}

const titleId = arg.match(/tt\d+/)?.[0];
if (!titleId) {
  console.log(`Could not extract title ID from: ${arg}`);
  process.exit(1);
}

const res = await fetch(`https://www.imdb.com/title/${titleId}/ratings`, {
  headers: { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15", "Accept-Language": "en-US" },
});
const html = await res.text();
const match = html.match(/<script id="__NEXT_DATA__" type="application\/json">(.+?)<\/script>/);
if (!match) { console.log(`No data found for ${titleId}`); process.exit(1); }

const { props: { pageProps: { contentData: content } } } = JSON.parse(match[1]);
const { titleText: { text: name }, ratingsSummary: { aggregateRating: rating, voteCount } } = content.entityMetadata;

const ratings = content.histogramData.histogramValues
  .sort((a: any, b: any) => b.rating - a.rating)
  .map((v: any) => v.voteCount);

const absScore = ratings[0] + ratings[1] - ratings.at(-1) - ratings.at(-2);
const total = ratings.reduce((a: number, b: number) => a + b, 0);
const ratio = total > 0 ? absScore / total : 0;
const score = Math.round(absScore * ratio);

console.log(name);
console.log(`IMDb Rating: ${rating}/10 (${voteCount.toLocaleString()} votes)`);
console.log(`Score: ${score} | Ratio: ${ratio.toFixed(2)}`);
console.log(`Top votes (10,9): ${ratings[0].toLocaleString()} + ${ratings[1].toLocaleString()}`);
console.log(`Bottom votes (1,2): ${ratings.at(-1).toLocaleString()} + ${ratings.at(-2).toLocaleString()}`);
