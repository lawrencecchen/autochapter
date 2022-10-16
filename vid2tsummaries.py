from autochapter.vid2timestamps import get_diffs, get_timestamps
from autochapter.timestamps2summaries import get_pre_summarized_segments, summarize_segments, transcribe_video 

async def vid2summaries(video_url: str):
  diffs = get_diffs(video_url)
  timestamps = get_timestamps(diffs=diffs, threshold=0.3e8, min_segment_length=50)
  transcribed_video = transcribe_video(video_url)
  segments = get_pre_summarized_segments(transcribed_video, timestamps)
  summarized_segments = await summarize_segments(segments)
  return summarized_segments


if __name__ == "__main__":
  import asyncio
  video_url = "videos/cs61a_lec1.mkv"
  summarized_segments = asyncio.run(vid2summaries(video_url))
  # summarized_segments =  vid2summaries(video_url)
  print(summarized_segments)