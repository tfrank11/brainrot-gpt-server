from classes import ErrorResponse, NewVideoRequest, ResponseType, LoginOkResponse
from fastapi import FastAPI, WebSocket
from supabase import Client, create_client
import os

from supabase_utils import get_uid_from_token

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabaseClient: Client = create_client(url, key)

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            video_request = NewVideoRequest.model_validate(data)
            uid = get_uid_from_token(
                supabase=supabaseClient, token=video_request.token)
            if uid:
                login_response = LoginOkResponse()
                await websocket.send_json(login_response.model_dump(mode='json'))

        except ValueError as e:
            error_response = ErrorResponse(
                type=ResponseType.ERROR,
                reason=f"Invalid request format: {str(e)}"
            )
            await websocket.send_json(error_response.model_dump(mode='json'))
