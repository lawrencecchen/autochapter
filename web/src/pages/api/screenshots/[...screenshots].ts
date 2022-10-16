import express from "express";
import { NextApiRequest, NextApiResponse } from "next";
import nextConnect from "next-connect";
import path from "node:path";

const apiRoute = nextConnect({
  onError(error, req: NextApiRequest, res: NextApiResponse) {
    res
      .status(501)
      .json({ error: `Sorry something Happened! ${error.message}` });
  },
  onNoMatch(req, res) {
    res.status(405).json({ error: `Method '${req.method}' Not Allowed` });
  },
});

apiRoute.use(
  "/api/screenshots",
  express.static(path.join(process.cwd(), "../screenshots"))
);

apiRoute.get((req: NextApiRequest, res: NextApiResponse) => {
  res.send("ok");
});

export default apiRoute;
