import { useRouter } from "next/router";
import invariant from "tiny-invariant";
import { useEffect, useRef, useState } from "react";
import { trpc } from "../utils/trpc";
import { useDebounce } from "../hooks/useDebounce";
import Link from "next/link";

// def video_url_to_name(video_url: str):
//   return video_url.split("/")[-1].split(".")[0]
function videoUrlToName(videoUrl: string) {
  // @ts-ignore
  return videoUrl.split("/").slice(-1)[0].split(".")[0];
}

export default function Video() {
  const router = useRouter();
  const videoQuery = router.query.video && String(router.query.video);
  const timeQuery = router.query.t && Number(router.query.t);
  const searchQueryParam = router.query.q && String(router.query.q);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [searchTerm, setSearchTerm] = useState(searchQueryParam || "");
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  useEffect(() => {
    if (debouncedSearchTerm && videoQuery) {
      router.push(`/${videoQuery}?q=${debouncedSearchTerm}`);
    }
  }, [debouncedSearchTerm, videoQuery]);
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.currentTime = timeQuery || 0;
    }
  }, [timeQuery]);
  const video = trpc.video.getVideo.useQuery(
    {
      path: String(videoQuery),
    },
    {
      enabled: !!videoQuery,
    }
  );
  const searchQuery = trpc.video.search.useQuery(
    {
      q: String(searchQueryParam),
    },
    {
      enabled: !!searchQueryParam,
    }
  );
  if (!videoQuery) {
    return null;
  }

  const videoUrl =
    videoQuery && `/api/videos/${videoQuery}`.replace(".json", "");

  function formatSeconds(seconds: number) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.round(seconds % 60);
    return [h, m > 9 ? m : h ? "0" + m : m || "0", s > 9 ? s : "0" + s]
      .filter(Boolean)
      .join(":");
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="p-4 overflow-auto border-r max-w-md w-full">
        <h1 className="font-semibold text-xl mb-1.5">
          <Link href="/">Summary</Link>
        </h1>
        <ol className="border-b">
          {video.data
            ?.filter((chapter) => chapter.summary.replace("--", "").length > 0)
            .map((chapter) => (
              <li className="normal-nums" key={chapter.start_time}>
                <button
                  className="text-left border-t py-2 grow flex max-w-md w-full"
                  onClick={() => {
                    invariant(videoRef.current, "videoRef.current is null");
                    videoRef.current.currentTime = chapter.start_time;
                    setSearchTerm(chapter.summary.replace("--", ""));
                  }}
                >
                  <img
                    src={
                      "/api/screenshots" +
                      chapter.meta.screenshot_path.replace(
                        "/Users/lawrencechen/fun/autochapter/screenshots",
                        ""
                      )
                    }
                    className="aspect-video h-14 mr-2 border"
                  />
                  <div>
                    <p className="line-clamp-2 text-sm">
                      {chapter.summary.replace("--", "")}
                    </p>
                    <p className="bg-blue-200/50 font-semibold inline text-xs px-1 text-blue-700 py-0.5">
                      {formatSeconds(chapter.start_time)}
                    </p>
                  </div>
                </button>
              </li>
            ))}
        </ol>
      </div>

      <div className="flex flex-col">
        <input
          type="text"
          value={searchTerm}
          placeholder="Ask a question"
          onChange={(e) => {
            setSearchTerm(e.target.value);
            // router.push(`/${videoQuery}?q=${e.target.value}`);
          }}
          className="placeholder:text-neutral-400 text-2xl px-3 py-2 border-b focus:outline-none font-light"
        />
        <div className="grow bg-black flex items-center">
          <video className="w-full" controls src={videoUrl} ref={videoRef} />
        </div>
      </div>

      {(searchQuery.isLoading || searchQuery.data) && (
        <div className="p-4 overflow-auto border-l max-w-md w-full">
          <h1 className="font-semibold text-xl mb-1.5">Related</h1>
          <ol className="border-b">
            {searchQuery.data?.result?.map((chapter, i) => {
              // console.log(chapter);
              const [title, meta] = chapter.split("__INTERNAL__:");
              // __timestamp__=3612__
              const timestamp = meta?.match(/__timestamp__=(\d+)__/)?.[1];
              invariant(timestamp, "timestamp is null");
              // __video_name__=cs61a_lec1
              const videoUnformatted = meta?.match(/__video_name__=(.+)/)?.[1];
              const videoName = videoUrlToName(videoUnformatted ?? "");
              const videoFileName = videoUnformatted
                ?.replace("/Users/lawrencechen/fun/autochapter/tsummaries/", "")
                .replace(".json", "");
              invariant(videoUnformatted, "videoName is null");
              return (
                <li className="normal-nums" key={i}>
                  <Link
                    href={`/${videoFileName}.json?t=${timestamp}?q=${searchTerm}`}
                    // className="text-left border-t py-2 grow flex max-w-md w-full"
                  >
                    <div className="text-left border-t py-2 grow flex max-w-md w-full">
                      <img
                        src={`/api/screenshots/${videoName}/${timestamp}.jpg`}
                        className="aspect-video h-14 mr-2 border"
                      />
                      <div>
                        <p className="line-clamp-2 text-sm">
                          {title?.replace("--", "")}
                        </p>
                        <p className="bg-blue-200/50 font-semibold inline text-xs px-1 text-blue-700 py-0.5">
                          {timestamp && formatSeconds(Number(timestamp))}
                        </p>
                      </div>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ol>
        </div>
      )}
    </div>
  );
}
