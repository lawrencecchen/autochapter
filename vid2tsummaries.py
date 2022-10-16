from autochapter.vid2timestamps import get_diffs, get_timestamps
from autochapter.timestamps2summaries import get_pre_summarized_segments, summarize_segments, transcribe_video 

async def vid2summaries(video_url: str):
  print("Getting timestamps")
  diffs = get_diffs(video_url)
  timestamps = get_timestamps(diffs=diffs, threshold=0.3e8, min_segment_length=50)
  print("Transcribing video")
  transcribed_video = transcribe_video(video_url)
  segments = get_pre_summarized_segments(transcribed_video, timestamps)
  print("Summarizing segments (cohere)")
  summarized_segments = await summarize_segments(segments)
  
  out = []
  assert len(summarized_segments) == len(timestamps), "Summarized segments and timestamps should be the same length"
  for segment, timestamp in zip(summarized_segments, timestamps):
    out.append({
      "start_time": timestamp,
      "summary": segment,
    })
  return out


if __name__ == "__main__":
  import asyncio
  import os
  import json

  video_url = "videos/cs61a_lec1.mkv"
  out_dir = "tsummaries"
  summarized_segments = asyncio.run(vid2summaries(video_url))
  out_path = os.path.join(out_dir, video_url.split("/")[-1] + ".json")
  with open(out_path, "w") as f:
    json.dump(summarized_segments, f)