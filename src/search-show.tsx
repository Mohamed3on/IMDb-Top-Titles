import {
  List,
  ActionPanel,
  Action,
  showToast,
  Toast,
  Icon,
  LocalStorage,
  Color,
} from "@raycast/api";
import { useState, useCallback, useEffect } from "react";
import { searchShow, getShowName, getEpisodes, resizeImg, type Episode } from "./imdb";

type SortMode = "score" | "chronological";

interface CachedShow {
  showName: string;
  showImageUrl: string | null;
  episodes: Episode[];
  timestamp: number;
}

function timeAgo(ts: number): string {
  const sec = Math.floor((Date.now() - ts) / 1000);
  if (sec < 60) return "just now";
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const days = Math.floor(hr / 24);
  return `${days}d ago`;
}

function ratioTag(ratio: number): { text: string; color: Color } {
  const pct = Math.round(ratio * 100);
  if (pct >= 80) return { text: `${pct}%`, color: Color.Green };
  if (pct >= 50) return { text: `${pct}%`, color: Color.Yellow };
  return { text: `${pct}%`, color: Color.Red };
}

export default function Command(props: {
  arguments: { query?: string; minRatio?: string };
}) {
  const minRatio = props.arguments?.minRatio
    ? parseFloat(props.arguments.minRatio)
    : 0;
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [showName, setShowName] = useState("");
  const [showImageUrl, setShowImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sortMode, setSortMode] = useState<SortMode>("chronological");
  const [progress, setProgress] = useState("");
  const [searchText, setSearchText] = useState(props.arguments?.query ?? "");
  const [cachedAt, setCachedAt] = useState<number | null>(null);

  const resolveTitleId = useCallback(async (query: string): Promise<{ titleId: string; name: string }> => {
    const titleMatch = query.match(/tt\d+/);
    if (titleMatch) {
      return { titleId: titleMatch[0], name: await getShowName(titleMatch[0]) };
    }
    const result = await searchShow(query);
    return { titleId: result.id, name: result.name };
  }, []);

  const fetchAndCache = useCallback(async (titleId: string, name: string) => {
    setProgress(`Fetching episodes for ${name}...`);

    const { showName: resolved, showImageUrl: imgUrl, episodes: eps } = await getEpisodes(
      titleId,
      minRatio,
      (done, total) => {
        setProgress(`Scoring episodes... ${done}/${total}`);
      },
    );

    const finalName = resolved !== "Unknown Show" ? resolved : name;
    const now = Date.now();

    const cached: CachedShow = { showName: finalName, showImageUrl: imgUrl, episodes: eps, timestamp: now };
    await LocalStorage.setItem(`episodes:${titleId}`, JSON.stringify(cached));

    setShowName(finalName);
    setShowImageUrl(imgUrl);
    setEpisodes(eps);
    setCachedAt(now);

    if (eps.length === 0) {
      await showToast({ style: Toast.Style.Failure, title: "No episodes passed the ratio threshold" });
    }
  }, [minRatio]);

  const doSearch = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setIsLoading(true);
    setEpisodes([]);
    setShowName("");
    setShowImageUrl(null);
    setCachedAt(null);
    setProgress("Searching...");

    try {
      const { titleId, name } = await resolveTitleId(query);
      setShowName(name);

      // Check cache
      const raw = await LocalStorage.getItem<string>(`episodes:${titleId}`);
      if (raw) {
        const cached: CachedShow = JSON.parse(raw);
        setShowName(cached.showName);
        setShowImageUrl(cached.showImageUrl ?? null);
        setEpisodes(cached.episodes);
        setCachedAt(cached.timestamp);
        setIsLoading(false);
        setProgress("");
        return;
      }

      await fetchAndCache(titleId, name);
    } catch (e) {
      await showToast({ style: Toast.Style.Failure, title: "Error", message: String(e) });
    } finally {
      setIsLoading(false);
      setProgress("");
    }
  }, [resolveTitleId, fetchAndCache]);

  useEffect(() => {
    if (props.arguments?.query?.trim()) {
      doSearch(props.arguments.query.trim());
    }
  }, []);

  const doRefresh = useCallback(async () => {
    const query = searchText.trim();
    if (!query) return;
    setIsLoading(true);
    setCachedAt(null);
    setProgress("Refreshing...");

    try {
      const { titleId, name } = await resolveTitleId(query);
      await fetchAndCache(titleId, name);
      await showToast({ style: Toast.Style.Success, title: "Episodes refreshed" });
    } catch (e) {
      await showToast({ style: Toast.Style.Failure, title: "Refresh failed", message: String(e) });
    } finally {
      setIsLoading(false);
      setProgress("");
    }
  }, [searchText, resolveTitleId, fetchAndCache]);

  const sorted =
    sortMode === "score"
      ? [...episodes].sort((a, b) => b.score - a.score)
      : episodes;

  // Group by season
  const seasons = new Map<number | null, Episode[]>();
  for (const ep of sorted) {
    const key = ep.season_number;
    if (!seasons.has(key)) seasons.set(key, []);
    seasons.get(key)!.push(ep);
  }

  const toggleSort = () =>
    setSortMode((m) => (m === "score" ? "chronological" : "score"));

  const navTitle = showName
    ? cachedAt
      ? `${showName} — ${timeAgo(cachedAt)}`
      : showName
    : "IMDb Episodes";

  return (
    <List
      isLoading={isLoading}
      searchText={searchText}
      onSearchTextChange={setSearchText}
      searchBarPlaceholder="Show name or IMDb URL..."
      navigationTitle={navTitle}
      isShowingDetail={episodes.length > 0}
      throttle
    >
      {episodes.length === 0 ? (
        <List.EmptyView
          title={
            isLoading
              ? progress
              : searchText
                ? "Press Enter to search"
                : "Enter a show name or IMDb URL"
          }
          icon={isLoading ? Icon.Clock : Icon.MagnifyingGlass}
          actions={
            !isLoading ? (
              <ActionPanel>
                <Action
                  title="Search"
                  icon={Icon.MagnifyingGlass}
                  onAction={() => doSearch(searchText)}
                />
              </ActionPanel>
            ) : undefined
          }
        />
      ) : (
        Array.from(seasons.entries()).map(([season, eps]) => (
          <List.Section
            key={String(season)}
            title={season != null ? `Season ${season}` : "Unknown Season"}
            subtitle={`${eps.length} episodes`}
          >
            {eps.map((ep, i) => {
              const tag = ratioTag(ep.ratio);
              return (
                <List.Item
                  key={`${season}-${i}`}
                  title={ep.name}
                  subtitle={
                    ep.season_number != null && ep.episode_number != null
                      ? `S${ep.season_number}E${ep.episode_number}`
                      : undefined
                  }
                  icon={{ source: resizeImg(ep.imageUrl, 100) ?? resizeImg(showImageUrl, 100) ?? Icon.Tv, fallback: Icon.Tv }}
                  accessories={[
                    { tag: { value: tag.text, color: tag.color } },
                  ]}
                  detail={
                    <List.Item.Detail
                      markdown={
                        `${resizeImg(ep.imageUrl, 600) ? `![Episode](${resizeImg(ep.imageUrl, 600)})\n\n` : resizeImg(showImageUrl, 600) ? `![Show](${resizeImg(showImageUrl, 600)})\n\n` : ""}` +
                        `## ${ep.name}\n` +
                        (ep.season_number != null && ep.episode_number != null
                          ? `Season ${ep.season_number}, Episode ${ep.episode_number}\n\n`
                          : "\n")
                      }
                      metadata={
                        <List.Item.Detail.Metadata>
                          <List.Item.Detail.Metadata.Label
                            title="Score"
                            text={ep.score.toLocaleString()}
                            icon={Icon.Star}
                          />
                          <List.Item.Detail.Metadata.TagList title="Ratio">
                            <List.Item.Detail.Metadata.TagList.Item
                              text={tag.text}
                              color={tag.color}
                            />
                          </List.Item.Detail.Metadata.TagList>
                          <List.Item.Detail.Metadata.Separator />
                          <List.Item.Detail.Metadata.Link
                            title="IMDb"
                            text="Open on IMDb"
                            target={ep.link}
                          />
                        </List.Item.Detail.Metadata>
                      }
                    />
                  }
                  actions={
                    <ActionPanel>
                      <Action.OpenInBrowser title="Open on IMDb" url={ep.link} />
                      <Action.CopyToClipboard
                        title="Copy Link"
                        content={ep.link}
                      />
                      <Action
                        title={`Sort by ${sortMode === "score" ? "Chronological" : "Score"}`}
                        icon={Icon.ArrowsContract}
                        shortcut={{ modifiers: ["cmd"], key: "s" }}
                        onAction={toggleSort}
                      />
                      <Action
                        title="Refresh Episodes"
                        icon={Icon.ArrowClockwise}
                        shortcut={{ modifiers: ["cmd"], key: "r" }}
                        onAction={doRefresh}
                      />
                    </ActionPanel>
                  }
                />
              );
            })}
          </List.Section>
        ))
      )}
    </List>
  );
}
