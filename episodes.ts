const GQL_URL = "https://graphql.imdb.com/";
const SUGGEST_URL = "https://v3.sg.media-imdb.com/suggestion/x/";
const HEADERS = {
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
  "Content-Type": "application/json",
};
const MIN_RATIO = 0;

async function gql(query: string, variables?: Record<string, unknown>) {
  const res = await fetch(GQL_URL, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors?.length) throw new Error(json.errors[0].message);
  return json.data;
}

async function searchShow(query: string): Promise<{ id: string; name: string }> {
  const res = await fetch(`${SUGGEST_URL}${encodeURIComponent(query)}.json`, {
    headers: { "User-Agent": HEADERS["User-Agent"] },
  });
  const data = await res.json();
  const tvShow = data.d?.find(
    (d: any) => d.qid === "tvSeries" || d.qid === "tvMiniSeries",
  );
  if (!tvShow) throw new Error(`No show found for: ${query}`);
  return { id: tvShow.id, name: tvShow.l };
}

async function getShowName(titleId: string): Promise<string> {
  const data = await gql(`{ title(id: "${titleId}") { titleText { text } } }`);
  return data.title?.titleText?.text ?? "Unknown Show";
}

const EPISODES_QUERY = `
query($id: ID!, $first: Int!, $after: ID) {
  title(id: $id) {
    titleText { text }
    episodes {
      episodes(first: $first, after: $after) {
        edges {
          node {
            id
            titleText { text }
            series { episodeNumber { seasonNumber episodeNumber } }
            aggregateRatingsBreakdown {
              histogram { histogramValues { rating voteCount } }
            }
          }
        }
        pageInfo { hasNextPage endCursor }
        total
      }
    }
  }
}`;

function scoreFromHistogram(values: { rating: number; voteCount: number }[]) {
  if (!values?.length) return null;
  const sorted = [...values].sort((a, b) => b.rating - a.rating);
  const counts = sorted.map((v) => v.voteCount);
  const total = counts.reduce((a: number, b: number) => a + b, 0);
  if (total === 0) return null;
  const absScore = counts[0] + counts[1] - counts.at(-1)! - counts.at(-2)!;
  return { absScore, total };
}

async function getEpisodes(titleId: string, minRatio: number) {
  let after: string | undefined;
  let showName = "Unknown Show";
  const allNodes: any[] = [];

  for (;;) {
    const data = await gql(EPISODES_QUERY, { id: titleId, first: 250, after });
    const title = data.title;
    if (showName === "Unknown Show") showName = title.titleText?.text ?? "Unknown Show";
    const conn = title.episodes.episodes;
    for (const edge of conn.edges) allNodes.push(edge.node);
    if (!conn.pageInfo.hasNextPage) break;
    after = conn.pageInfo.endCursor;
  }

  const episodes: any[] = [];
  for (const node of allNodes) {
    const histValues = node.aggregateRatingsBreakdown?.histogram?.histogramValues;
    const result = scoreFromHistogram(histValues ?? []);
    if (!result || result.total === 0) continue;

    const ratio = result.absScore / result.total;
    if (ratio < minRatio) continue;

    const calculated = Math.round(result.absScore * ratio);
    const epNum = node.series?.episodeNumber;

    episodes.push({
      name: node.titleText.text,
      score: calculated,
      ratio: Math.round(ratio * 100) / 100,
      link: `https://www.imdb.com/title/${node.id}/`,
      season_number: epNum?.seasonNumber ?? null,
      episode_number: epNum?.episodeNumber ?? null,
    });
  }

  episodes.sort(
    (a: any, b: any) =>
      (a.season_number ?? -Infinity) - (b.season_number ?? -Infinity) ||
      (a.episode_number ?? -Infinity) - (b.episode_number ?? -Infinity),
  );

  return { showName: showName.replace(/^\d+\.\s*/, "").trim(), episodes };
}

// --- main ---

const input = Bun.argv[2];
if (!input) {
  console.log('Usage: bun episodes.ts <show-name-or-imdb-url> [min_ratio]');
  process.exit(1);
}

const minRatio = Bun.argv[3] ? parseFloat(Bun.argv[3]) : MIN_RATIO;
const titleMatch = input.match(/tt\d+/);

let titleId: string;
let showName: string;

if (titleMatch) {
  titleId = titleMatch[0];
  showName = await getShowName(titleId);
  console.log(`Found show: ${showName} (ID: ${titleId})`);
} else {
  const result = await searchShow(input);
  titleId = result.id;
  showName = result.name;
  console.log(`Found show: ${showName} (ID: ${titleId})`);
}

const { showName: resolvedName, episodes } = await getEpisodes(titleId, minRatio);
const finalName = resolvedName !== "Unknown Show" ? resolvedName : showName;

if (!episodes.length) {
  console.log("No episodes passed the minimum ratio threshold.");
  process.exit(0);
}

const seasons: Record<number, { season_number: number; total_score: number }> = {};
for (const ep of episodes) {
  if (ep.season_number != null) {
    seasons[ep.season_number] ??= { season_number: ep.season_number, total_score: 0 };
    seasons[ep.season_number].total_score += ep.score;
  }
}

const results = {
  EpisodesChronological: episodes,
  EpisodesSorted: [...episodes].sort((a: any, b: any) => b.score - a.score),
  Seasons: Object.values(seasons).sort((a, b) => b.total_score - a.total_score),
};

const dir = `${import.meta.dir}/shows`;
await Bun.write(`${dir}/.keep`, "");
const filePath = `${dir}/${finalName}.json`;
await Bun.write(filePath, JSON.stringify(results, null, 2));
console.log(`Saved ${episodes.length} episodes to ${filePath}`);
