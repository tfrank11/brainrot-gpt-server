from deepgram import DeepgramClient, PrerecordedOptions
from classes import AudioTiming, VideoType
from elevenlabs import ElevenLabs, save
from supabase import Client
from openai import OpenAI
import moviepy
import PyPDF2
import json



def check_if_can_make_video():
    return True


def download_pdf(supabaseClient: Client, uid: str, pdf_id: str, temp_path: str):
    print('download_pdf')
    with open(temp_path, "wb+") as f:
        response = supabaseClient.storage.from_("docs").download(
            f"{uid}/{pdf_id}.pdf"
        )
        f.write(response)


def get_text_from_pdf(pdf_path: str):
    print('get_text_from_pdf')
    transcript = ""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            transcript += page.extract_text()
    text = transcript.encode('utf-8', 'ignore').decode('utf-8')
    text = transcript.replace('\u0000', '')
    return text


def get_brainrot_summary(openAiClient: OpenAI, transcript: str):
    print('get_brainrot_summary')
    response = openAiClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user",
                   "content": f"""Make a brainrot-themed voiceover summary for the following tex. use words like "rizz" and other brainrot/gen-z/tiktok things. Dont go too hard with the brainrot stuff. It should still sound vaguely normal. It should not exceed roughly ~45 seconds of material. Do not use exclamation points. Here is the transcript: {transcript}.

                        the result should be a json object with the following fields
                        - summary
                        - title (a 3-6 word title)

                       """}],
        response_format={"type": "json_object"},
        functions=[{
              "name": "process_summary",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "summary": {"type": "string"},
                      "title": {"type": "string"},
                  },
                  "required": ["summary", "title"]
              }
        }],
        function_call={"name": "process_summary"}
    )

    result = json.loads(
        response.choices[0].message.function_call.arguments)  # type: ignore

    return result


def make_brainrot_audio(elevenLabsClient: ElevenLabs, summary: str, temp_audio_path: str):
    print('make_brainrot_audio')
    audio = elevenLabsClient.generate(
        text=summary,
        voice="Adam",
        model="eleven_monolingual_v1"
    )
    save(audio, temp_audio_path)


def download_source_video(supabaseClient: Client, temp_path: str, video_type: VideoType):
    print('download_source_video')
    with open(temp_path, "wb+") as f:
        name = "minecraft.mp4"
        if video_type == VideoType.SUBWAYSURFER:
            name = "subway.mp4"
        # more types soon perhaps
        response = supabaseClient.storage.from_("brainrot_source").download(
            name
        )
        f.write(response)


def get_word_timings(deepgram: DeepgramClient, audio_path: str) -> list[AudioTiming]:
    print('get_word_timings')
    with open(audio_path, "rb") as file:
        buffer = file.read()

    options = PrerecordedOptions(
        smart_format=True,
        model="nova-2",
        language="en",
        detect_language=True,
        punctuate=True,
        utterances=True,
    )

    payload = {
        "buffer": buffer,
    }

    response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

    # Extract word timings from the response
    words = []
    for word in response.results.channels[0].alternatives[0].words:
        timing = AudioTiming(
            word=word.word, start_time=word.start, end_time=word.end)
        words.append(timing)
    return words


def process_video(audio_path: str, source_path: str, timings: list[AudioTiming], final_video_path: str):
    print('process_video')
    my_clip = moviepy.VideoFileClip(source_path)
    my_clip = my_clip.with_volume_scaled(0.25)
    audio_background = moviepy.AudioFileClip(audio_path)
    my_clip = my_clip.subclipped(0, audio_background.duration)
    final_audio = moviepy.CompositeAudioClip([my_clip.audio, audio_background])
    final_clip = my_clip.with_audio(final_audio)
    font_path = "./assets/Arial.ttf"
    text_clips = []
    for timing in timings:
        text_clip = (moviepy.TextClip(text=timing.word,
                                      font_size=70,
                                      color='white',
                                      stroke_color='black',
                                      stroke_width=2,
                                      font=font_path)
                     .with_position('center')
                     .with_start(timing.start_time)
                     .with_duration(timing.end_time - timing.start_time))
        text_clips.append(text_clip)

    final_video = moviepy.CompositeVideoClip(
        [final_clip] + text_clips)
    final_video.write_videofile(
        final_video_path, audio_codec='aac', fps=24, threads=8)


def update_supabase_with_video(supabaseClient: Client, uid: str, input_id: str, pdf_id: str, transcript: str, summary: str, title: str, video_type: VideoType, final_video_path: str, video_id: str):
    print('update_supabase_with_video', uid, input_id)
    with open(final_video_path, 'rb') as f:
        supabaseClient.storage.from_("videos").upload(
            file=f,
            path=f"{uid}/{video_id}.mp4",
            file_options={"cache-control": "3600",
                          "upsert": "false", "content-type": "video/mp4"},
        )
    supabaseClient.table('inputs').upsert({
        "uid": uid,
        "input_id": input_id,
        "video_id": video_id,
        "pdf_id": pdf_id,
        "transcript": transcript,
        "title": title,
        "summary": summary,
        "video_type": video_type.value,
    }).execute()
    print('done uploading')
