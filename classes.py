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


class NewVideoRequest(BaseModel):
    type: RequestType = RequestType.LOGIN
    token: str
    pdf_id: str
    video_type: VideoType


class ResponseType(IntEnum):
    LOGIN_OK = 0
    TRANSCRIPT = 1
    SUMMARY = 2
    AUDIO_DONE = 3
    VIDEO_DONE = 4
    ERROR = 5


class LoginOkResponse(BaseModel):
    type: ResponseType = ResponseType.LOGIN_OK


class TranscriptResponse(BaseModel):
    type: ResponseType = ResponseType.TRANSCRIPT
    transcript: str


class SummaryResponse(BaseModel):
    type: ResponseType = ResponseType.SUMMARY
    summary: str


class AudioResponse(BaseModel):
    type: ResponseType = ResponseType.AUDIO_DONE


class VideoResponse(BaseModel):
    type: ResponseType = ResponseType.VIDEO_DONE
    video_id: int


class ErrorResponse(BaseModel):
    type: ResponseType = ResponseType.ERROR
    reason: str


class AudioTiming(BaseModel):
    word: str
    start_time: float
    end_time: float
