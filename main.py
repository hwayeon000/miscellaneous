from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import os
from typing import Optional
from dotenv import load_dotenv
import time
from collections import defaultdict

# 간단한 사용량 추적 (실제 서버에서는 데이터베이스 사용 권장)
usage_tracker = {
    'requests_today': 0,
    'last_reset': time.strftime('%Y-%m-%d'),
    'requests_this_minute': defaultdict(int)
}

# FastAPI 앱 초기화
app = FastAPI()

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

# Gemini API 설정
load_dotenv()
GEMINI_API_KEY = os.getenv('API_KEY')

# API 키 검증
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("⚠️ 경고: API 키를 설정해주세요!")
    print("환경변수 API_KEY를 설정하거나 .env 파일에 API_KEY=your_key_here 를 추가하세요.")
    print("Google AI Studio에서 API 키를 발급받을 수 있습니다: https://makersuite.google.com/app/apikey")
else:
    print(f"✅ API 키가 설정되었습니다: {GEMINI_API_KEY[:10]}...")

genai.configure(api_key=GEMINI_API_KEY)


# 사용 가능한 모델 확인 및 설정 (무료 사용량 최적화)
try:
    optimal_models = [
        ('gemini-1.5-flash', '일반 사용 - 10 RPM, 250 RPD'),
        ('gemini-1.5-flash-lite', '절약 모드 - 15 RPM, 1000 RPD'),  
        ('gemini-2.5-flash', '최신 버전 - 10 RPM'),
        ('gemini-1.0-pro', '기본 모델 - 안정적')
    ]
    
    model = None
    selected_model_info = None
    
    for model_name, description in optimal_models:
        try:
            model = genai.GenerativeModel(model_name)
            selected_model_info = description
            print(f"✅ 사용 중인 모델: {model_name} ({description})")
            break
        except Exception as e:
            print(f"❌ {model_name} 사용 불가")
            continue
    
    if model is None:
        print("⚠️ 기본 모델로 설정합니다...")
        model = genai.GenerativeModel('gemini-pro')
        selected_model_info = "기본 모델"
        
except Exception as e:
    print(f"모델 설정 중 오류: {e}")
    model = genai.GenerativeModel('gemini-pro')
    selected_model_info = "기본 모델"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/test-api")
async def test_api():
    """API 키 테스트 엔드포인트"""
    try:
        print("API 테스트 시작...")
        
        # 사용 가능한 모델 목록 확인
        models_info = []
        test_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-latest', 'gemini-1.0-pro']
        
        working_model = None
        for model_name in test_models:
            try:
                test_model = genai.GenerativeModel(model_name)
                response = test_model.generate_content("안녕")
                models_info.append({"model": model_name, "status": "작동", "response_length": len(response.text)})
                if working_model is None:
                    working_model = model_name
            except Exception as e:
                models_info.append({"model": model_name, "status": "오류", "error": str(e)[:100]})
        
        return {
            "status": "success" if working_model else "error",
            "working_model": working_model,
            "models_tested": models_info,
            "api_key_valid": working_model is not None
        }
    except Exception as e:
        print(f"API 테스트 실패: {str(e)}")
        return {
            "status": "error", 
            "api_key_valid": False,
            "error": str(e)
        }

@app.get("/list-models")
async def list_available_models():
    """사용 가능한 모델 목록 확인"""
    try:
        models = genai.list_models()
        model_list = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                model_list.append({
                    "name": m.name,
                    "display_name": getattr(m, 'display_name', 'N/A'),
                    "supported_methods": m.supported_generation_methods
                })
        return {"available_models": model_list}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask", response_class=HTMLResponse)
async def ask_gemini(request: Request, question: str = Form(...)):
    """Gemini API에 질문을 보내고 답변을 받는 엔드포인트 - 일반 텍스트"""
    try:
        # 사용량 체크 (간단한 제한)
        current_date = time.strftime('%Y-%m-%d')
        current_minute = time.strftime('%Y-%m-%d %H:%M')
        
        # 날짜가 바뀌면 리셋
        if usage_tracker['last_reset'] != current_date:
            usage_tracker['requests_today'] = 0
            usage_tracker['last_reset'] = current_date
            usage_tracker['requests_this_minute'].clear()
        
        # 분당 요청 수 체크 (Flash 기준 10RPM)
        if usage_tracker['requests_this_minute'][current_minute] >= 8:
            return templates.TemplateResponse("test.html", {
                "request": request,
                "question": question,
                "error": f"분당 요청 한도 초과입니다. 잠시 후 다시 시도해주세요. (현재: {usage_tracker['requests_this_minute'][current_minute]}/8)"
            })
        
        # 일일 요청 수 체크 (Flash 기준 250RPD)
        if usage_tracker['requests_today'] >= 200:
            return templates.TemplateResponse("test.html", {
                "request": request,
                "question": question,
                "error": f"일일 요청 한도 초과입니다. 내일 다시 시도해주세요. (현재: {usage_tracker['requests_today']}/200)"
            })

        if not question.strip():
            return templates.TemplateResponse("test.html", {
                "request": request,
                "error": "질문을 입력해주세요."
            })
        
        print(f"받은 질문: {question}")
        
        # API 키 유효성 확인
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            return templates.TemplateResponse("test.html", {
                "request": request,
                "question": question,
                "error": "API 키가 설정되지 않았습니다. 환경변수 API_KEY를 설정해주세요."
            })
        
        # 최적화된 모델 사용 (무료 할당량 고려)
        try:
            fresh_model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            try:
                fresh_model = genai.GenerativeModel('gemini-1.5-flash-lite')
            except:
                fresh_model = model
        
        print("API 호출 시작...")
        
        # 프롬프트 길이 체크 및 분할 처리
        prompt_length = len(question)
        print(f"프롬프트 길이: {prompt_length}자")
        
        if prompt_length > 3000:
            print("긴 프롬프트 감지 - 분할 처리 시작")
            
            # 프롬프트를 두 부분으로 나누기
            mid_point = len(question) // 2
            part1 = question[:mid_point]
            part2 = question[mid_point:]
            
            # 첫 번째 부분 처리
            response1 = fresh_model.generate_content(
                f"{part1}\n\n[이것은 첫 번째 부분입니다. 두 번째 부분이 이어집니다.]",
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=2048,
                    temperature=0.7,
                )
            )
            
            # 두 번째 부분 처리 (첫 번째 응답 포함)
            combined_prompt = f"이전 응답: {response1.text}\n\n이어서 처리할 내용: {part2}\n\n위 내용을 종합해서 최종 답변을 해주세요."
            
            response = fresh_model.generate_content(
                combined_prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=2048,
                    temperature=0.7,
                )
            )
        else:
            # 일반 처리
            max_tokens = 2048 if prompt_length > 2000 else 1024
            response = fresh_model.generate_content(
                question,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    stop_sequences=None,
                )
            )
        
        print("API 호출 완료")
        
        # 사용량 업데이트
        usage_tracker['requests_today'] += 1
        usage_tracker['requests_this_minute'][current_minute] += 1
        
        # 응답 확인
        if hasattr(response, 'text') and response.text:
            answer = response.text
            print(f"답변 길이: {len(answer)}")
        else:
            print("응답이 비어있음")
            answer = "답변을 생성할 수 없습니다."
        
        return templates.TemplateResponse("test.html", {
            "request": request,
            "question": question,
            "answer": answer,
            "usage_info": f"오늘 사용량: {usage_tracker['requests_today']}/200, 이번 분: {usage_tracker['requests_this_minute'][current_minute]}/8"
        })
    
    except Exception as e:
        print(f"상세 오류: {type(e).__name__}: {str(e)}")
        error_message = f"오류가 발생했습니다: {str(e)}"
        return templates.TemplateResponse("test.html", {
            "request": request,
            "question": question if 'question' in locals() else "",
            "error": error_message
        })

@app.post("/ask-file", response_class=HTMLResponse)
async def ask_file(request: Request, file: UploadFile = File(...)):
    """파일 업로드로 질문하기 - 한글 인코딩 지원"""
    try:
        # 파일 검증
        if not file.filename.endswith(('.txt', '.md')):
            return templates.TemplateResponse("test.html", {
                "request": request,
                "error": "txt 또는 md 파일만 업로드 가능합니다."
            })
        
        # 파일 읽기 - 여러 인코딩 시도
        content = await file.read()
        question = None
        
        # 한국어 파일을 위한 다양한 인코딩 시도
        encodings_to_try = [
            'utf-8',           # 표준 유니코드
            'utf-8-sig',       # BOM이 있는 UTF-8
            'cp949',           # 한국어 Windows 기본
            'euc-kr',          # 한국어 리눅스/유닉스
            'ascii',           # 영어만
            'latin1'           # 마지막 수단
        ]
        
        for encoding in encodings_to_try:
            try:
                question = content.decode(encoding)
                print(f"✅ 파일을 {encoding} 인코딩으로 성공적으로 읽었습니다.")
                print(f"파일에서 읽은 질문 길이: {len(question)}자")
                break
            except UnicodeDecodeError as e:
                print(f"❌ {encoding} 인코딩 실패: {str(e)}")
                continue
        
        if question is None:
            return templates.TemplateResponse("test.html", {
                "request": request,
                "error": "파일의 인코딩을 인식할 수 없습니다. UTF-8, EUC-KR, CP949 중 하나로 저장해주세요."
            })
        
        # 빈 내용 체크
        if not question.strip():
            return templates.TemplateResponse("test.html", {
                "request": request,
                "error": "파일 내용이 비어있습니다."
            })
        
        # ask_gemini 함수의 로직을 재사용
        return await ask_gemini(request, question)
    
    except Exception as e:
        print(f"파일 처리 오류: {str(e)}")
        return templates.TemplateResponse("test.html", {
            "request": request,
            "error": f"파일 처리 중 오류가 발생했습니다: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    
    # templates 디렉토리 생성 (없는 경우)
    os.makedirs("templates", exist_ok=True)
    
    print("FastAPI 서버를 시작합니다...")
    print("브라우저에서 http://127.0.0.1:8050 으로 접속하세요.")
    print("\n📝 API 키 설정 방법:")
    print("1. Google AI Studio에서 API 키 발급: https://makersuite.google.com/app/apikey")
    print("2. 환경변수 설정:")
    print("   Windows: set API_KEY=your_api_key_here")
    print("   Mac/Linux: export API_KEY=your_api_key_here")
    print("3. 또는 .env 파일에 API_KEY=your_api_key_here 추가")
    
    uvicorn.run(app, host="0.0.0.0", port=8050)


# pip install fastapi uvicorn jinja2 python-multipart google-generativeai
# # pip install google-generativeai
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# # ----- 환경변수 로드 -----
# load_dotenv()
# API_KEY = os.getenv('API_KEY')  # .env에 저장된 API_KEY 불러오기

# genai.configure(api_key=API_KEY)

# model = genai.GenerativeModel('gemini-1.5-flash')

# response = model.generate_content("너 한글 잘해? 오늘 날씨 알려줘.", stream=True)

text = '''
[역할]
당신은 학생의 주간 출결 데이터를 기반으로 습관 진단 및 행동 개선 전략을 제안하는 출결 분석 전문가입니다.
[분석 목표]
1. 출석 계획과 실제 출결 간 일치도 분석 → 루틴 유지력 진단
2. 출석 시간 vs 계획 시간 차이 정량 분석 → 루틴 안정성 평가
3. 지각/조퇴 사유, 요일별 반복성 분석 → 패턴 진단 및 원인 파악
4. 출석률 및 정상 출석일 수 기반 평가 → 루틴 지속 가능성 판단
5. 즉시 개선할 행동 습관 or 환경 조정 방안 제시 → 실질적 행동 전략 제안
[제약사항]
- 시사점은 전체 구성을 문장 4줄로만 구성하고, 한 문장 당 글자 수는 85자 이내로 한다.
- “지각하지 말자”, “출석률을 높이자” 같은 형식적 문장 금지
- 반드시 데이터 기반 분석*포함 (출석 시간, 지각/조퇴 사유, 요일별 반복 등)
- 문제 원인을 루틴/컨디션/환경(교통 등)과 연결 → 행동 교정 or 환경 조정 방식으로 제안
- 결석/지각/조퇴 발생일은 반드시 원인 진단 + 개선 방향 포함
[출력 형식 예시]
종합 요약 인사이트
- 월요일과 금요일은 출석 시간이 계획과 거의 일치해 루틴 유지가 잘 되고 있음
- 화·목 늦잠으로 지각이 발생해 수면 관리와 알람 강화가 필요함.
- 월·수·금 외부 약속으로 조퇴가 반복되어 일정 조정과 보충 계획이 필요함.
- 수요일에 회복 시간을 고려해 전날(화요일) 일정 조정 또는 교통 대안 확보가 필요함
- 출석률은 75%로 유지 중이나, 주중 중반 리듬을 정비하지 않으면 전체 주간 루틴 붕괴 우려가 있음
- 화~수는 피로도 또는 환경 요인(버스 지연, 컨디션 저하 등)으로 출결 패턴 붕괴가 반복되는 구조. 월요일과 금요일은 출석 시간이 계획과 거의 일치해 루틴 유지가 잘 되고 있음
'''



# for chunk in response:
#     print(chunk.text, end='', flush=True)