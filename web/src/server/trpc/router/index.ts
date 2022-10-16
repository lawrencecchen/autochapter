// src/server/router/index.ts
import fs from "node:fs/promises";
import path from "node:path";
import { z } from "zod";
import { t } from "../trpc";
import { exampleRouter } from "./example";

const root = path.join(process.cwd(), "..");
const tsummaries = path.join(root, "tsummaries");

const videoRouter = t.router({
  search: t.procedure
    .input(z.object({ q: z.string().min(1) }))
    .output(z.object({ result: z.array(z.string()) }))
    .query(async ({ input }) => {
      console.log({ input });
      const res = await fetch(`http://127.0.0.1:8000/search?q=${input.q}`, {
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((r) => r.json())
        .catch((e) => console.error(e));
      console.log(res);
      return res;
    }),
  listVideos: t.procedure.query(async () => {
    const videos = await fs.readdir(tsummaries);
    return videos;
  }),
  getVideo: t.procedure
    .input(z.object({ path: z.string() }))
    .output(
      z.array(
        z.object({
          start_time: z.number(),
          summary: z.string(),
          meta: z.object({
            screenshot_path: z.string(),
            title: z.any().nullish(),
          }),
        })
      )
    )
    .query(async ({ input }) => {
      const filePath = path.join(tsummaries, input.path);
      const file = await fs.readFile(filePath);
      return JSON.parse(file.toString());
    }),
});

export const appRouter = t.router({
  example: exampleRouter,
  video: videoRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;
