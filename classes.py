from enum import Enum
from pydantic import BaseModel


class VideoType(Enum):
    MINECRAFT = 0
    SUBWAYSURFER = 1


class NewVideoRequest(BaseModel):
    token: str
    video_id: str
    video_type: VideoType


class ResponseType(Enum):
    LOGIN_OK = 0
    TRANSCRIPT = 1
    SUMMARY = 2
    VIDEO_DONE = 3
    ERROR = 4


class LoginOkResponse(BaseModel):
    type: ResponseType = ResponseType.LOGIN_OK


class TranscriptResponse(BaseModel):
    type: ResponseType = ResponseType.TRANSCRIPT
    transcript: str


class SummaryResponse(BaseModel):
    type: ResponseType = ResponseType.SUMMARY
    summary: str


class VideoResponse(BaseModel):
    type: ResponseType = ResponseType.VIDEO_DONE
    video_id: int


class ErrorResponse(BaseModel):
    type: ResponseType = ResponseType.ERROR
    reason: str
