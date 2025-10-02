# from openai import OpenAI
# client = OpenAI(
#   api_key=API_KEY
# )

# response = client.responses.create(
#   model="gpt-4o-mini",
#   input="최근 AI 동향을 2025년 최신으로 검색해 정리해 줄 수 있어?",
#   store=True,
# )

# print(response.output_text);
# 1 end =======================================

# import os
# os.environ["OPENAI_API_KEY"] = API_KEY
#  langchain 과 langchain-openai를 install 해줍니다.
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

# response = chat.predict("why python is the most popular language? answer in Korean")

# print(response)
# 2 end ======================================이건 안됨


import os
import uuid
import asyncio
from typing import List, Dict, Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 실제 OpenAI API 연동용
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, BaseMessage
from langchain.callbacks.base import AsyncCallbackHandler

import tiktoken
from dotenv import load_dotenv

# ----- 환경변수 로드 -----
load_dotenv()
API_KEY = os.getenv('GPT_API_KEY')  # .env에 저장된 API_KEY 불러오기

# ----- 기본 설정 -----
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 1.0
MAX_CONTEXT_TOKENS = 1200
SYSTEM_PROMPT = (
    "너는 간결하고 정확하게 답하는 한국어 비서야. "
    "답변이 길어질 때는 핵심부터 요약하고, 코드/명령은 블록으로 제시해줘."
)

# FastAPI 기본 세팅
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 세션별 대화 저장
SESSIONS: Dict[str, List[BaseMessage]] = {}
SESSION_SUMMARY: Dict[str, str] = {}

# ----- 토큰 계산 함수 -----
def num_tokens_from_messages(messages: List[BaseMessage], model: str = MODEL_NAME) -> int:
    enc = tiktoken.encoding_for_model(model) if model in tiktoken.list_encoding_names() else tiktoken.get_encoding("cl100k_base")
    total = 0
    for m in messages:
        total += len(enc.encode(m.content))
    return total

def num_tokens_from_text(text: str, model: str = MODEL_NAME) -> int:
    enc = tiktoken.encoding_for_model(model) if model in tiktoken.list_encoding_names() else tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

# ----- 오래된 대화 요약 함수 -----
async def summarize_text(text: str) -> str:
    """오래된 히스토리를 짧게 요약"""
    if not text.strip():
        return ""
    if not API_KEY:
        # 💡 API_KEY가 없을 경우 Mock 응답
        return "[요약(Mock)] 오래된 대화를 요약했습니다."
    llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0, openai_api_key=API_KEY)
    prompt = f"다음 대화를 한 문단으로 매우 간결히 요약해줘(한국어):\n\n{text}"
    result = await llm.apredict(prompt)
    return result.strip()

async def trim_context(session_id: str) -> None:
    """대화 토큰이 많아지면 오래된 내용 요약 후 제거"""
    history = SESSIONS.get(session_id, [])
    if not history:
        return

    summary = SESSION_SUMMARY.get(session_id, "")
    base: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    if summary:
        base.append(SystemMessage(content=f"[이전 요약]\n{summary}"))

    recent: List[BaseMessage] = []
    for msg in reversed(history):
        recent.append(msg)
        if num_tokens_from_messages(base + list(reversed(recent))) > MAX_CONTEXT_TOKENS:
            recent.pop()
            break

    kept = list(reversed(recent))
    removed_count = len(history) - len(kept)

    if removed_count > 0:
        old_text = "\n".join([m.content for m in history[:removed_count]])
        old_summary = await summarize_text(old_text)
        merged = (SESSION_SUMMARY.get(session_id, "") + "\n" + old_summary).strip()
        if num_tokens_from_text(merged) > 600:
            merged = await summarize_text(merged)
        SESSION_SUMMARY[session_id] = merged
        SESSIONS[session_id] = kept

# ----- 스트리밍 콜백 -----
class QueueCallback(AsyncCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """OpenAI API가 토큰을 생성할 때마다 호출됨"""
        await self.queue.put(token)

    async def on_llm_end(self, *args, **kwargs) -> None:
        """모든 토큰 전송 후 호출"""
        await self.queue.put("[[END]]")

# ----- 라우팅 -----
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/stream")
async def stream(message: str, session_id: str = "") -> StreamingResponse:
    """클라이언트에서 /stream 호출 시, SSE로 토큰 실시간 전송"""
    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in SESSIONS:
        SESSIONS[session_id] = []

    await trim_context(session_id)

    messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    summary = SESSION_SUMMARY.get(session_id, "")
    if summary:
        messages.append(SystemMessage(content=f"[이전 요약]\n{summary}"))
    messages.extend(SESSIONS[session_id])
    messages.append(HumanMessage(content=message))

    queue: asyncio.Queue = asyncio.Queue()

    async def token_generator() -> AsyncGenerator[bytes, None]:
        """SSE로 토큰을 하나씩 전송"""
        if not API_KEY:
            # 💡 API_KEY 없을 때 Mock 토큰 전송
            mock_text = f"(Mock 응답) '{message}'에 대한 답변 예시입니다."
            for ch in mock_text:
                await asyncio.sleep(0.05)  # 타이핑 속도 흉내
                yield f"data: {ch}\n\n".encode("utf-8")
            yield b"data: [[END]]\n\n"
            return

        # 실제 OpenAI API 호출
        cb = QueueCallback(queue)
        llm = ChatOpenAI(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            streaming=True,
            callbacks=[cb],
            openai_api_key=API_KEY
        )

        asyncio.create_task(llm.apredict_messages(messages))
        while True:
            token = await queue.get()
            if token == "[[END]]":
                yield b"data: [[END]]\n\n"
                break
            chunk = token.replace("\n", "\\n")
            yield f"data: {chunk}\n\n".encode("utf-8")

    SESSIONS[session_id].append(HumanMessage(content=message))

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(token_generator(), headers=headers)




# uvicorn nenwsss:app --reload
#  http://127.0.0.1:8000


# fastapi
# uvicorn
# jinja2
# python-multipart
# langchain
# langchain-openai
# tiktoken
