#!/usr/bin/env python
# coding: utf-8

# In[21]:


from typing import List
import whisper
import os
import json
import cohere
import httpx
import asyncio


# In[34]:


COHERE_API_KEY = "8rLIrm60Gf9mSmeIF2RHxv1TNcjXpHFDZ9XnqjD2"
cohere = cohere.Client(COHERE_API_KEY)


# In[3]:


# def timestamps2summaries(video_url: str, timestamps: List[int], output_dir: str):
#   transcribed = model.transcribe(video_url)
#   print(transcribed)
#   # transcribed["timestamps"]


# In[4]:


model = whisper.load_model("tiny")

def transcribe_video(video_url: str):
  video_transcribed_path = os.path.join("transcribed", video_url.split("/")[-1].split(".")[0] + ".json")
  print(video_transcribed_path)
  if os.path.exists(video_transcribed_path):
    with open(video_transcribed_path) as f:
      return json.load(f)
  else:
    result = model.transcribe(video_url)
    with open(video_transcribed_path, "w") as f:
      json.dump(result, f)
    return result


# In[5]:


transcribed = transcribe_video("videos/cs61a_lec1.mkv")


# In[40]:


from functools import wraps, partial

def summarize(passage: str):
  response = cohere.generate(
    model='large',
    prompt=f'Passage: Is Wordle getting tougher to solve? Players seem to be convinced that the game has gotten harder in recent weeks ever since The New York Times bought it from developer Josh Wardle in late January. The Times has come forward and shared that this likely isn’t the case. That said, the NYT did mess with the back end code a bit, removing some offensive and sexual language, as well as some obscure words There is a viral thread claiming that a confirmation bias was at play. One Twitter user went so far as to claim the game has gone to “the dusty section of the dictionary” to find its latest words.\n\nTLDR: Wordle has not gotten more difficult to solve.\n--\nPassage: ArtificialIvan, a seven-year-old, London-based payment and expense management software company, has raised $190 million in Series C funding led by ARG Global, with participation from D9 Capital Group and Boulder Capital. Earlier backers also joined the round, including Hilton Group, Roxanne Capital, Paved Roads Ventures, Brook Partners, and Plato Capital.\n\nTLDR: ArtificialIvan has raised $190 million in Series C funding.\n--\nPassage: {passage}\n\nTLDR:',
    max_tokens=50,
    temperature=0.8,
    k=0,
    p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop_sequences=["--"],
    return_likelihoods='NONE')
  # print('Prediction: {}'.format(response.generations[0].text))
  return response.generations[0].text

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run 

@async_wrap
def async_summarize(passage: str):
  return summarize(passage).strip()


# In[7]:


summarize(transcribed["text"][0:2000])


# In[8]:


fake_timestamps = [0, 100, 200, 300, 400, 500]


# In[22]:


async def get_async(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)


# In[41]:


# all units should be in seconds
def get_pre_summarized_segments(transcribed, timestamps: List[int], max_duration=300):
  pre_summarized_segments = []
  ts = 0
  max_ts = timestamps[-1] + max_duration
  i_timestamp = 0
  i_segment = 0
  segments = transcribed["segments"]

  while ts < max_ts and i_segment < len(segments) and i_timestamp < len(timestamps):
    segment = segments[i_segment]
    next_segment = segments[i_segment + 1] if i_segment + 1 < len(segments) else None
    segment_start = segment["start"]

    if len(pre_summarized_segments) <= i_timestamp:
      pre_summarized_segments.append("")
    
    if next_segment is None:
      pre_summarized_segments[i_timestamp] += segment["text"]
    else:
      if segment_start <= timestamps[i_timestamp] + max_duration and next_segment["start"] > timestamps[i_timestamp]:
        pre_summarized_segments[i_timestamp] += segment["text"]
      else:
        i_timestamp += 1
      ts = next_segment["start"]
    i_segment += 1

  stripped_segments = [segment.strip() for segment in pre_summarized_segments]

  return stripped_segments

async def summarize_segments(segments: List[str]):
  summaries = await asyncio.gather(*map(async_summarize, segments))
  return summaries

segments = get_pre_summarized_segments(transcribed, fake_timestamps)
summaries = await summarize_segments(segments)
summaries
# summaries = [summarize(segment) for segment in segments]
# summaries

