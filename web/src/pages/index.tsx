import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { trpc } from "../utils/trpc";

const Home: NextPage = () => {
  const videos = trpc.video.listVideos.useQuery();

  return (
    <>
      <Head>
        <title>autochapter</title>
        <meta name="description" content="autochapter" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="p-4">
        <h1 className="text-2xl font-semibold mb-2">Archived videos</h1>
        <ol className="space-y-1.5">
          {videos.data?.map((video) => (
            <li key={video} className="list-decimal list-inside">
              <Link href={`/${video}`}>{video}</Link>
            </li>
          ))}
        </ol>
      </div>
    </>
  );
};

export default Home;
