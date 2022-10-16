# Autochapter

Automatically chapter your videos.

![](readme_media/Screen%20Shot%202022-10-16%20at%204.06.35%20PM.png)

## Architecture

1. OpenCV heuristics for chapter transitions
2. Audio -> text via Whisper (OpenAI)
3. Natural language processing generation via Cohere fine tuned on custom prompt to summarize
4. Cohere semantic search embeddings finds related chapters
