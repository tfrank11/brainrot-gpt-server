from video import add_audio_to_video, add_captions_to_video, check_if_can_make_video, download_pdf, download_source_video, get_brainrot_summary, get_text_from_pdf, get_word_timings, make_brainrot_audio, update_supabase_with_video
from classes import AudioResponse, ErrorResponse, NewVideoRequest, RequestType, ResponseType, LoginOkResponse, SummaryResponse, TranscriptResponse, VideoType
from deepgram import DeepgramClient, ClientOptionsFromEnv, PrerecordedOptions
from supabase_utils import get_uid_from_token
from supabase import Client, create_client
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from elevenlabs import ElevenLabs
from utils import silent_remove
from openai import OpenAI
from asyncio import sleep
import uuid
import os

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabaseClient: Client = create_client(url, key)
openAiClient = OpenAI()
deepgramClient: DeepgramClient = DeepgramClient("", ClientOptionsFromEnv())
elevenLabsClient = ElevenLabs(api_key=os.environ.get('ELEVEN_API_KEY'))

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            temp_pdf_path = f"{str(uuid.uuid4())}.pdf"
            temp_audio_path = f"{str(uuid.uuid4())}.mp3"
            temp_source_path = f"{str(uuid.uuid4())}.mp4"
            temp_video_no_caps_path = f"{str(uuid.uuid4())}.mp4"
            temp_final_video_path = f"{str(uuid.uuid4())}.mp4"
            data = await websocket.receive_json()
            print('new client request', data)
            if data['type'] == RequestType.LOGIN.value:
                input_id = str(uuid.uuid4())
                video_request = NewVideoRequest.model_validate(data)
                # Auth
                uid = get_uid_from_token(
                    supabase=supabaseClient, token=video_request.token)
                login_response = LoginOkResponse()
                await websocket.send_json(login_response.model_dump(mode='json'))

                # Handle PDF
                download_pdf(supabaseClient=supabaseClient,
                             pdf_id=video_request.pdf_id, uid=uid, temp_path=temp_pdf_path)
                transcript = get_text_from_pdf(temp_pdf_path)
                transcript_response = TranscriptResponse(transcript=transcript)
                await websocket.send_json(
                    transcript_response.model_dump(mode='json'))
                await sleep(0.1)

                # Brainrot summary and audio
                brainrot_summary = get_brainrot_summary(
                    openAiClient=openAiClient, transcript=transcript)
                brainrot_response = SummaryResponse(summary=brainrot_summary)
                await websocket.send_json(brainrot_response.model_dump(mode='json'))
                await sleep(0.1)

                make_brainrot_audio(
                    elevenLabsClient, summary=brainrot_summary, temp_audio_path=temp_audio_path)
                audio_response = AudioResponse()
                await websocket.send_json(audio_response.model_dump(mode='json'))
                await sleep(0.1)

                # Video generation
                download_source_video(
                    supabaseClient=supabaseClient, temp_path=temp_source_path)
                add_audio_to_video(
                    audio_path=temp_audio_path, source_path=temp_source_path, target_path=temp_video_no_caps_path)
                word_timings = get_word_timings(
                    deepgram=deepgramClient, audio_path=temp_audio_path)
                add_captions_to_video(
                    timings=word_timings, no_caps_video_path=temp_video_no_caps_path, final_video_path=temp_final_video_path)

                update_supabase_with_video(
                    supabaseClient=supabaseClient,
                    uid=uid,
                    input_id=input_id,
                    pdf_id=video_request.pdf_id,
                    transcript=transcript,
                    summary=brainrot_summary,
                    video_type=video_request.video_type,
                    final_video_path=temp_final_video_path)

                silent_remove(temp_pdf_path)
                silent_remove(temp_audio_path)
                silent_remove(temp_source_path)
                silent_remove(temp_video_no_caps_path)
                silent_remove(temp_final_video_path)
            else:
                raise ValueError('Unrecognized request type')

        except WebSocketDisconnect:
            print("Client disconnected")
            break  # Exit the loop if the client disconnects
        except Exception as e:
            error_response = ErrorResponse(
                type=ResponseType.ERROR,
                reason=f"Error processing request: {str(e)}"
            )
            try:
                await websocket.send_json(error_response.model_dump(mode='json'))
            except Exception as send_error:
                print(f"Failed to send error response: {send_error}")
