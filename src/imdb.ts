const GQL_URL = "https://graphql.imdb.com/";
const SUGGEST_URL = "https://v3.sg.media-imdb.com/suggestion/x/";
const HEADERS = {
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
  "Content-Type": "application/json",
};

/** Resize an IMDb image URL by replacing ._V1_.jpg with ._V1_SX{width}.jpg */
export function resizeImg(url: string | null, width: number): string | null {
  if (!url) return null;
  return url.replace(/\._V1_.*\.jpg$/, `._V1_SX${width}.jpg`);
}

export interface Episode {
  name: string;
  score: number;
  ratio: number;
  link: string;
  season_number: number | null;
  episode_number: number | null;
  imageUrl: string | null;
}

export interface EpisodesResult {
  showName: string;
  showImageUrl: string | null;
  episodes: Episode[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function gql(query: string, variables?: Record<string, unknown>): Promise<any> {
  const res = await fetch(GQL_URL, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors?.length) throw new Error(json.errors[0].message);
  return json.data;
}

export async function searchShow(
  query: string,
): Promise<{ id: string; name: string }> {
  const res = await fetch(`${SUGGEST_URL}${encodeURIComponent(query)}.json`, {
    headers: { "User-Agent": HEADERS["User-Agent"] },
  });
  const data = await res.json();
  const tvShow = data.d?.find(
    (d: { qid?: string }) => d.qid === "tvSeries" || d.qid === "tvMiniSeries",
  );
  if (!tvShow) throw new Error(`No show found for: ${query}`);
  return { id: tvShow.id, name: tvShow.l };
}

export async function getShowName(titleId: string): Promise<string> {
  const data = await gql(`{ title(id: "${titleId}") { titleText { text } } }`);
  return data.title?.titleText?.text ?? "Unknown Show";
}

const EPISODES_QUERY = `
query($id: ID!, $first: Int!, $after: ID) {
  title(id: $id) {
    titleText { text }
    primaryImage { url }
    episodes {
      episodes(first: $first, after: $after) {
        edges {
          node {
            id
            titleText { text }
            primaryImage { url }
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

interface GqlEpisodeNode {
  id: string;
  titleText: { text: string };
  primaryImage: { url: string } | null;
  series: { episodeNumber: { seasonNumber: number; episodeNumber: number } } | null;
  aggregateRatingsBreakdown: {
    histogram: { histogramValues: { rating: number; voteCount: number }[] };
  } | null;
}

function scoreFromHistogram(
  values: { rating: number; voteCount: number }[],
): { absScore: number; total: number } | null {
  if (!values?.length) return null;
  const sorted = [...values].sort((a, b) => b.rating - a.rating);
  const counts = sorted.map((v) => v.voteCount);
  const total = counts.reduce((a, b) => a + b, 0);
  if (total === 0) return null;
  const absScore = counts[0] + counts[1] - counts.at(-1)! - counts.at(-2)!;
  return { absScore, total };
}

export async function getEpisodes(
  titleId: string,
  minRatio: number,
  onProgress?: (done: number, total: number) => void,
): Promise<EpisodesResult> {
  let after: string | undefined;
  let showName = "Unknown Show";
  let showImageUrl: string | null = null;
  const allNodes: GqlEpisodeNode[] = [];

  // Paginate through all episodes
  for (;;) {
    const data = await gql(EPISODES_QUERY, { id: titleId, first: 250, after });
    const title = data.title;
    if (showName === "Unknown Show") {
      showName = title.titleText?.text ?? "Unknown Show";
    }
    if (!showImageUrl) {
      showImageUrl = title.primaryImage?.url ?? null;
    }
    const conn = title.episodes.episodes;
    for (const edge of conn.edges) {
      allNodes.push(edge.node);
    }
    if (!conn.pageInfo.hasNextPage) break;
    after = conn.pageInfo.endCursor;
  }

  // Score all episodes from the already-fetched histogram data
  const total = allNodes.length;
  const episodes: Episode[] = [];

  for (let i = 0; i < allNodes.length; i++) {
    const node = allNodes[i];
    onProgress?.(i + 1, total);

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
      imageUrl: node.primaryImage?.url ?? null,
    });
  }

  episodes.sort(
    (a, b) =>
      (a.season_number ?? -Infinity) - (b.season_number ?? -Infinity) ||
      (a.episode_number ?? -Infinity) - (b.episode_number ?? -Infinity),
  );

  return { showName: showName.replace(/^\d+\.\s*/, "").trim(), showImageUrl, episodes };
}
