from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import uvicorn
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 🔹 static 디렉토리 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# 샘플 데이터
sample_data = {
    'name': ['김철수', '이영희', '박지민'],
    'age': [25, 30, 28],
    'city': ['서울', '부산', '대전']
}

@app.get("/")
async def home(
    request: Request,
):
    return templates.TemplateResponse("test0605.html", {"request": request})

@app.get("/test")
async def home(
    request: Request,
    selected_status: Optional[str] = None, # 수면, 외출 필터링
    out_rest_reason: Optional[str] = None,
):
    print(selected_status)
    print(out_rest_reason)
    return templates.TemplateResponse("modal_test.html", {
        "request": request,
        "selected_status": selected_status or "all",  # None일 때 기본값
        "out_rest_reason": out_rest_reason or "all"
    })

@app.get("/download-excel")
async def download_excel():
    # DataFrame 생성
    df = pd.DataFrame(sample_data)
    
    # Excel 파일로 변환
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')
    
    # 파일 포인터를 처음으로 이동
    output.seek(0)
    
    # 스트리밍 응답으로 반환
    headers = {
        'Content-Disposition': 'attachment; filename="users.xlsx"'
    }
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers=headers
    )

# python test.py 로 실행 가능하도록
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8050)
# http://127.0.0.1:8050




# from flask import Flask, render_template
# from datetime import datetime

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('test0605.html', title='홍길동', heading='과일', content=datetime.now())

# if __name__ == '__main__':
#     app.run(debug=True)

