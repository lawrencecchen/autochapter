from autochapter.vid2timestamps import get_diffs, get_timestamps
import os
from autochapter.timestamps2summaries import get_pre_summarized_segments, summarize_segments, transcribe_video 

async def vid2summaries(video_url: str):
  print("Getting timestamps")
  diffs_save_path = os.path.join(os.getcwd(), "diffs", video_url.split("/")[-1].split(".")[0] + ".pkl")
  diffs = get_diffs(video_url=video_url, save_path=diffs_save_path)
  timestamps = get_timestamps(diffs=diffs, threshold=0.3e8, min_segment_length=15*30)
  print("Transcribing video")
  transcribed_save_path = os.path.join(os.getcwd(), "transcribed", video_url.split("/")[-1].split(".")[0] + ".json")
  print(video_url)
  transcribed_video = transcribe_video(video_url=video_url, save_path=transcribed_save_path)
  segments = get_pre_summarized_segments(transcribed_video, timestamps)
  print("Summarizing segments (cohere)")
  summarized_segments = await summarize_segments(segments)
  
  out = []
  # assert len(summarized_segments) == len(timestamps), "Summarized segments and timestamps should be the same length"
  for segment, timestamp in zip(summarized_segments, timestamps):
    out.append({
      "start_time": timestamp,
      "summary": segment,
    })
  return out


if __name__ == "__main__":
  import asyncio
  import json

  video_url = os.path.join(os.getcwd(), "videos/cs61a_lec1.mkv")
  out_dir = "tsummaries"
  summarized_segments = asyncio.run(vid2summaries(video_url))
  out_path = os.path.join(out_dir, video_url.split("/")[-1] + ".json")
  with open(out_path, "w") as f:
    json.dump(summarized_segments, f)
  print(f"Saved to {out_path}")