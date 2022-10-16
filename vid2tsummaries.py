from autochapter.vid2timestamps import get_diffs, get_timestamps
import os
from autochapter.timestamps2summaries import extract_meta, get_pre_summarized_segments, summarize_segments, transcribe_video 

async def vid2summaries(video_url: str):
  print("Getting timestamps")
  video_name = video_url.split("/")[-1].split(".")[0]
  diffs_save_path = os.path.join(os.getcwd(), "diffs", video_name + ".pkl")
  diffs = get_diffs(video_url=video_url, save_path=diffs_save_path)
  timestamps = get_timestamps(diffs=diffs, threshold=0.3e8, min_segment_length=40*30)
  print("Extracting meta (screenshots + titles)")
  meta = extract_meta(video_url=video_url, video_name=video_name, timestamps=timestamps)
  print("meta--->", meta)
  print("Transcribing video")
  transcribed_save_path = os.path.join(os.getcwd(), "transcribed", video_name + ".json")
  transcribed_video = transcribe_video(video_url=video_url, save_path=transcribed_save_path)
  segments = get_pre_summarized_segments(transcribed_video, timestamps)
  print("segments",segments)
  print(f"Summarizing segments (cohere).")
  summarized_segments = await summarize_segments(segments)
  
  out = []
  # assert len(summarized_segments) == len(timestamps), "Summarized segments and timestamps should be the same length"
  for segment, timestamp, meta in zip(summarized_segments, timestamps, meta):
    out.append({
      "start_time": timestamp,
      "summary": segment,
      "meta": meta
    })
  return out


if __name__ == "__main__":
  import asyncio
  import json

  video_url = os.path.join(os.getcwd(), "videos/Lecture 16 ｜ Adversarial Examples and Adversarial Training [CIfsB_EYsVI].webm")
  out_dir = "tsummaries"
  summarized_segments = asyncio.run(vid2summaries(video_url))
  out_path = os.path.join(out_dir, video_url.split("/")[-1] + ".json")
  with open(out_path, "w") as f:
    json.dump(summarized_segments, f)
  print(f"Saved to {out_path}")