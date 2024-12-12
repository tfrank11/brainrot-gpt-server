from enum import IntEnum
from pydantic import BaseModel


class VideoType(IntEnum):
    MINECRAFT = 0
    SUBWAYSURFER = 1


class InputInfo:
    uid: str
    input_id: str
    video_id: str
    pdf_id: str
    transcript: str
    summary: str
    video_type: VideoType


class RequestType(IntEnum):
    LOGIN = 0
    HEARTBEAT = 1


class NewVideoRequest(BaseModel):
    type: RequestType = RequestType.LOGIN
    token: str
    pdf_id: str
    video_type: VideoType


class ResponseType(IntEnum):
    ERROR = 0
    LOGIN_OK = 1
    TRANSCRIPT = 2
    SUMMARY = 3
    AUDIO_DONE = 4
    WORD_TIMINGS_DONE = 5
    PROCESS_VIDEO_DONE = 6
    VIDEO_DONE = 7


class TypeOnlyResponse(BaseModel):
    type: ResponseType


class TranscriptResponse(BaseModel):
    type: ResponseType = ResponseType.TRANSCRIPT
    transcript: str


class SummaryResponse(BaseModel):
    type: ResponseType = ResponseType.SUMMARY
    summary: str


class VideoResponse(BaseModel):
    type: ResponseType = ResponseType.VIDEO_DONE
    video_id: str


class ErrorResponse(BaseModel):
    type: ResponseType = ResponseType.ERROR
    reason: str


class AudioTiming(BaseModel):
    word: str
    start_time: float
    end_time: float
