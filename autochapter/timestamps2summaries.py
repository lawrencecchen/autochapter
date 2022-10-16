#!/usr/bin/env python
# coding: utf-8

# In[1]:


from typing import List
import whisper
import os
import json
import cohere
import httpx
import asyncio


# In[2]:


COHERE_API_KEY = "8rLIrm60Gf9mSmeIF2RHxv1TNcjXpHFDZ9XnqjD2"
cohere = cohere.Client(COHERE_API_KEY)


# In[3]:


# def timestamps2summaries(video_url: str, timestamps: List[int], output_dir: str):
#   transcribed = model.transcribe(video_url)
#   print(transcribed)
#   # transcribed["timestamps"]


# In[4]:


print("Loading Whisper")
model = whisper.load_model("tiny")
print("Loaded Whisper")

def transcribe_video(video_url: str):
  # video_transcribed_path = os.path.join("../transcribed", video_url.split("/")[-1].split(".")[0] + ".json")
  video_transcribed_path = video_url
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


# transcribed = transcribe_video("videos/cs61a_lec1.mkv")


# In[49]:


from functools import wraps, partial

def summarize(passage: str):
  print("passage:", passage)
  response = cohere.generate(
    model='large',
    prompt=f"""Your task is to summarize each passage into a short description. Always use a 3rd person, dispassioned tone. Do NOT use first or second person.

Begin.

Passage: So today we're going to be doing a software engineering lecture. This is a somewhat of an experiment. So I'm going to give you some backscore and why it's happening. So interesting note that in 2003, Yish and earlier, 61A had two days a week, Monday, Wednesdays of technical topics. And then Friday was always something else. Now sometimes that was some social implications thing where we talked about the impact of computing. I mean, as we were before, I was like, you're age at the time. So they would talk about alternate topics, whatever it may be.

TLDR: Introduction
--
Passage: Now poverty is one of those things that is surprisingly hard to quantify which is the first real issue for governments that are trying to address this issue. Incomes are the most used metric, and almost every statistic you have likely heard on the issue will say something like these people live on less than 2 dollars a day, and for what it’s worth we have done exactly the same thing already in this video. But there are two problems with this, the first is that some people can be extremely comfortable with not much income. Some retirees would be a good example of this. They might own their own home fully paid off and have a nice pile of cash savings so they are very comfortable, but with interest rates as low as they are they might technically have an income below the internationally accepted poverty line.

TLDR: Measuring poverty
--
Passage: {passage}

TLDR:
""",
    # prompt=f'Passage: Is Wordle getting tougher to solve? Players seem to be convinced that the game has gotten harder in recent weeks ever since The New York Times bought it from developer Josh Wardle in late January. The Times has come forward and shared that this likely isn’t the case. That said, the NYT did mess with the back end code a bit, removing some offensive and sexual language, as well as some obscure words There is a viral thread claiming that a confirmation bias was at play. One Twitter user went so far as to claim the game has gone to “the dusty section of the dictionary” to find its latest words.\n\nTLDR: Wordle has not gotten more difficult to solve.\n--\nPassage: ArtificialIvan, a seven-year-old, London-based payment and expense management software company, has raised $190 million in Series C funding led by ARG Global, with participation from D9 Capital Group and Boulder Capital. Earlier backers also joined the round, including Hilton Group, Roxanne Capital, Paved Roads Ventures, Brook Partners, and Plato Capital.\n\nTLDR: ArtificialIvan has raised $190 million in Series C funding.\n--\nPassage: {passage}\n\nTLDR:',
    max_tokens=50,
    temperature=0.8,
    k=0,
    p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop_sequences=["--"],
    return_likelihoods='NONE')
  # print('Prediction: {}'.format(response.generations[0].text))
  return response.generations[0].text.replace("--", "").strip()

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


# summarize(transcribed["text"][0:2000])


# In[8]:


async def get_async(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)


# In[41]:


# all units should be in seconds
def get_pre_summarized_segments(transcribed, timestamps: List[int], max_duration=300):
  pre_summarized_segments = []
  ts = timestamps[0]
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
      while segment_start < ts:
        segment_start = next_segment["start"]
        segment = next_segment
        i_segment += 1
        next_segment = segments[i_segment + 1] if i_segment + 1 < len(segments) else None
        
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

# transcribed = transcribe_video("videos/cs61a_lec1.mkv")
# fake_timestamps = [1200, 1500]
# segments = get_pre_summarized_segments(transcribed, fake_timestamps)
# segments


# In[51]:


# transcribed = transcribe_video("videos/cs61a_lec1.mkv")
# fake_timestamps = [0, 100]
# segments = get_pre_summarized_segments(transcribed, fake_timestamps)
# segments
# summaries = await summarize_segments(segments)
# summaries

