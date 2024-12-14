## BrainRot GPT (Backend)

Turn PDFs into short form, digestible videos. Perfect if you have a sub-30 second attention span. 

[Live Site](https://www.brainrot-gpt.com/)

<img src="https://i.imgur.com/YnQ8HV8.png" width="600" >

## Technology Stack

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#)
[![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?logo=supabase&logoColor=fff)](https://supabase.com/)
[![Deepgram](https://img.shields.io/badge/Deepgram-black)](https://deepgram.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-white)](https://elevenlabs.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-grey)](https://openai.com/api/)
[![Heroku](https://img.shields.io/badge/Heroku-430098?logo=heroku&logoColor=fffe)](#)

## Features


1. **Upload PDF**: Users can upload a PDF document through the interface.
2. **Processing**: The backend processes the PDF to extract text and generate a summary using OpenAI's GPT-4o-mini.
3. **Audio Generation**: A voiceover is created based on the summary using ElevenLabs. This is the familiar TikTok voice.
4. **Video Creation**: The application combines the audio with a source video using MoviePy, adding text overlays for captions.
5. **Download**: Users can download the final video once processing is complete.

## Key Services/Libraries Used

- **Supabase**: For authentication and database.
- **OpenAI**: For generating summaries from the extracted text.
- **ElevenLabs**: For creating voiceovers based on the summary.
- **Deepgram**: For transcribing the audio and getting timestamps for each word.
- **MoviePy**: For video processing, including combining audio with a source video and adding text overlays.

## Also See

[Brainrot GPT Web](https://github.com/tfrank11/brainrot-gpt-web)
