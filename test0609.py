print("hello")
# import pandas as pd

# # CSV 파일 불러오기 (인코딩 설정으로 한글 깨짐 방지)
# # 보통 한글 윈도우에서 생성된 파일은 cp949 또는 euc-kr 인코딩일 확률이 높습니다.
# df = pd.read_csv('./data/국민건강보험공단_특정 상병 및 수가코드 그룹별 진료환자 정보E_20231231.csv', 
#                  encoding='cp949')
#                 #  encoding='utf-8')

# # 상위 5개 데이터 보여주기
# print(df.head())

def create_html_template():
    """HTML 템플릿 파일 생성"""
    html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>책 검색 및 목차 관리</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .search-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .search-form {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .search-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .search-input:focus {
            border-color: #3498db;
            outline: none;
        }
        
        .search-btn {
            padding: 15px 30px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        .search-btn:hover {
            background-color: #2980b9;
        }
        
        .search-btn:disabled {
            background-color: #95a5a6;
            cursor: not-allowed;
        }
        
        .search-results {
            margin-top: 20px;
        }
        
        .book-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
        }
        
        .book-header {
            display: flex;
            align-items: flex-start;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .book-thumbnail {
            width: 120px;
            height: 150px;
            object-fit: cover;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .book-info {
            flex: 1;
        }
        
        .book-title {
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .book-meta {
            color: #666;
            margin-bottom: 5px;
        }
        
        .book-description {
            color: #555;
            margin-top: 10px;
            max-height: 100px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .table-of-contents {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        
        .toc-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .toc-item {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        
        .toc-item:last-child {
            border-bottom: none;
        }
        
        .save-btn, .delete-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
            margin-top: 10px;
        }
        
        .save-btn {
            background-color: #27ae60;
            color: white;
        }
        
        .save-btn:hover {
            background-color: #229954;
        }
        
        .delete-btn {
            background-color: #e74c3c;
            color: white;
        }
        
        .delete-btn:hover {
            background-color: #c0392b;
        }
        
        .saved-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 20px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .message {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .error {
            background-color: #fee;
            color: #c33;
            border: 1px solid #fcc;
        }
        
        .success {
            background-color: #efe;
            color: #363;
            border: 1px solid #cfc;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .no-results {
            text-align: center;
            color: #666;
            padding: 40px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .stats {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 책 검색 및 목차 관리</h1>
        
        <!-- 검색 섹션 -->
        <div class="search-section">
            <h2 class="section-title">책 검색</h2>
            <form class="search-form" onsubmit="searchBooks(event)">
                <input type="text" class="search-input" id="searchInput" 
                       placeholder="검색할 책 제목을 입력하세요..." required>
                <button type="submit" class="search-btn" id="searchBtn">검색</button>
            </form>
            
            <div id="message"></div>
            <div id="searchResults" class="search-results"></div>
        </div>
        
        <!-- 저장된 책 섹션 -->
        <div class="saved-section">
            <div class="stats">
                <h2 class="section-title" style="margin: 0; border: none; padding: 0;">저장된 책 목록</h2>
                <span>총 {{ saved_books|length }}권</span>
            </div>
            
            {% if saved_books %}
                {% for book in saved_books %}
                <div class="book-item" id="saved-book-{{ book.id }}">
                    <div class="book-header">
                        {% if book.thumbnail %}
                        <img src="{{ book.thumbnail }}" alt="책 표지" class="book-thumbnail" 
                             onerror="this.style.display='none'">
                        {% endif %}
                        <div class="book-info">
                            <div class="book-title">{{ book.title }}</div>
                            <div class="book-meta">저자: {{ book.authors | join(', ') }}</div>
                            <div class="book-meta">출판사: {{ book.publisher }}</div>
                            <div class="book-meta">출간일: {{ book.publishedDate }}</div>
                            {% if book.pageCount != 'Unknown' %}
                            <div class="book-meta">페이지 수: {{ book.pageCount }}쪽</div>
                            {% endif %}
                            <div class="book-meta">저장일: {{ book.search_date }}</div>
                            
                            {% if book.description and book.description != 'No description' %}
                            <div class="book-description">{{ book.description[:200] }}{% if book.description|length > 200 %}...{% endif %}</div>
                            {% endif %}
                            
                            <button class="delete-btn" onclick="deleteSavedBook('{{ book.id }}')">삭제</button>
                        </div>
                    </div>
                    
                    {% if book.table_of_contents %}
                    <div class="table-of-contents">
                        <div class="toc-title">📋 목차 정보</div>
                        {% for toc_item in book.table_of_contents %}
                        <div class="toc-item">{{ toc_item }}</div>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <div class="no-results">
                    아직 저장된 책이 없습니다.<br>
                    위에서 책을 검색하고 저장해보세요!
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        async function searchBooks(event) {
            event.preventDefault();
            
            const searchInput = document.getElementById('searchInput');
            const searchBtn = document.getElementById('searchBtn');
            const messageDiv = document.getElementById('message');
            const resultsDiv = document.getElementById('searchResults');
            
            const title = searchInput.value.trim();
            
            if (!title) {
                showMessage('책 제목을 입력해주세요.', 'error');
                return;
            }
            
            // 로딩 상태
            searchBtn.disabled = true;
            searchBtn.textContent = '검색중...';
            messageDiv.innerHTML = '';
            resultsDiv.innerHTML = '<div class="loading">검색중입니다...</div>';
            
            try {
                const formData = new FormData();
                formData.append('title', title);
                
                const response = await fetch('/search', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showMessage(data.error, 'error');
                    resultsDiv.innerHTML = '';
                } else {
                    displaySearchResults(data.books);
                    showMessage(`${data.books.length}권의 책을 찾았습니다.`, 'success');
                }
                
            } catch (error) {
                console.error('검색 오류:', error);
                showMessage('검색 중 오류가 발생했습니다.', 'error');
                resultsDiv.innerHTML = '';
            } finally {
                searchBtn.disabled = false;
                searchBtn.textContent = '검색';
            }
        }
        
        function displaySearchResults(books) {
            const resultsDiv = document.getElementById('searchResults');
            
            if (books.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">검색 결과가 없습니다.</div>';
                return;
            }
            
            let html = '';
            books.forEach(book => {
                html += `
                    <div class="book-item">
                        <div class="book-header">
                            ${book.thumbnail ? `<img src="${book.thumbnail}" alt="책 표지" class="book-thumbnail" onerror="this.style.display='none'">` : ''}
                            <div class="book-info">
                                <div class="book-title">${book.title}</div>
                                <div class="book-meta">저자: ${book.authors.join(', ')}</div>
                                <div class="book-meta">출판사: ${book.publisher}</div>
                                <div class="book-meta">출간일: ${book.publishedDate}</div>
                                ${book.pageCount !== 'Unknown' ? `<div class="book-meta">페이지 수: ${book.pageCount}쪽</div>` : ''}
                                ${book.categories.length > 0 ? `<div class="book-meta">카테고리: ${book.categories.join(', ')}</div>` : ''}
                                
                                ${book.description && book.description !== 'No description' ? 
                                    `<div class="book-description">${book.description.substring(0, 200)}${book.description.length > 200 ? '...' : ''}</div>` : ''}
                                
                                <button class="save-btn" onclick="saveBook('${book.id}')">저장</button>
                            </div>
                        </div>
                        
                        ${book.table_of_contents && book.table_of_contents.length > 0 ? `
                        <div class="table-of-contents">
                            <div class="toc-title">📋 목차 정보</div>
                            ${book.table_of_contents.map(item => `<div class="toc-item">${item}</div>`).join('')}
                        </div>
                        ` : ''}
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
        
        async function saveBook(bookId) {
            const searchResults = document.getElementById('searchResults');
            const bookElements = searchResults.querySelectorAll('.book-item');
            
            let bookData = null;
            
            // 현재 검색 결과에서 해당 책 찾기 (전역 변수 대신 DOM에서 추출)
            // 실제로는 검색 결과를 전역 변수로 저장하거나 다른 방법 사용
            // 여기서는 간단히 구현
            
            try {
                // 책 저장을 위해 다시 검색 (실제로는 더 효율적인 방법 사용)
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({id: bookId}) // 임시로 ID만 전송
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, 'success');
                    // 페이지 새로고침하여 저장된 책 목록 업데이트
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showMessage(data.message, 'error');
                }
                
            } catch (error) {
                console.error('저장 오류:', error);
                showMessage('책 저장 중 오류가 발생했습니다.', 'error');
            }
        }
        
        async function deleteSavedBook(bookId) {
            if (!confirm('정말로 이 책을 삭제하시겠습니까?')) {
                return;
            }
            
            try {
                const response = await fetch(`/delete/${bookId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, 'success');
                    // DOM에서 해당 책 제거
                    const bookElement = document.getElementById(`saved-book-${bookId}`);
                    if (bookElement) {
                        bookElement.remove();
                    }
                    
                    // 저장된 책이 없으면 메시지 표시
                    const remainingBooks = document.querySelectorAll('[id^="saved-book-"]');
                    if (remainingBooks.length === 0) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    }
                } else {
                    showMessage('삭제 중 오류가 발생했습니다.', 'error');
                }
                
            } catch (error) {
                console.error('삭제 오류:', error);
                showMessage('삭제 중 오류가 발생했습니다.', 'error');
            }
        }
        
        function showMessage(message, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
            
            // 3초 후 메시지 자동 삭제
            setTimeout(() => {
                messageDiv.innerHTML = '';
            }, 3000);
        }
        
        // 전역 변수로 검색 결과 저장
        let currentSearchResults = [];
        
        // saveBook 함수 수정
        window.saveBook = async function(bookId) {
            const bookData = currentSearchResults.find(book => book.id === bookId);
            
            if (!bookData) {
                showMessage('책 정보를 찾을 수 없습니다.', 'error');
                return;
            }
            
            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(bookData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showMessage(data.message, 'error');
                }
                
            } catch (error) {
                console.error('저장 오류:', error);
                showMessage('책 저장 중 오류가 발생했습니다.', 'error');
            }
        };
        
        // displaySearchResults 함수 수정하여 검색 결과 저장
        function displaySearchResults(books) {
            currentSearchResults = books; // 전역 변수에 저장
            
            const resultsDiv = document.getElementById('searchResults');
            
            if (books.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">검색 결과가 없습니다.</div>';
                return;
            }
            
            let html = '';
            books.forEach(book => {
                html += `
                    <div class="book-item">
                        <div class="book-header">
                            ${book.thumbnail ? `<img src="${book.thumbnail}" alt="책 표지" class="book-thumbnail" onerror="this.style.display='none'">` : ''}
                            <div class="book-info">
                                <div class="book-title">${book.title}</div>
                                <div class="book-meta">저자: ${book.authors.join(', ')}</div>
                                <div class="book-meta">출판사: ${book.publisher}</div>
                                <div class="book-meta">출간일: ${book.publishedDate}</div>
                                ${book.pageCount !== 'Unknown' ? `<div class="book-meta">페이지 수: ${book.pageCount}쪽</div>` : ''}
                                ${book.categories.length > 0 ? `<div class="book-meta">카테고리: ${book.categories.join(', ')}</div>` : ''}
                                
                                ${book.description && book.description !== 'No description' ? 
                                    `<div class="book-description">${book.description.substring(0, 200)}${book.description.length > 200 ? '...' : ''}</div>` : ''}
                                
                                <button class="save-btn" onclick="saveBook('${book.id}')">저장</button>
                            </div>
                        </div>
                        
                        ${book.table_of_contents && book.table_of_contents.length > 0 ? `
                        <div class="table-of-contents">
                            <div class="toc-title">📋 목차 정보</div>
                            ${book.table_of_contents.map(item => `<div class="toc-item">${item}</div>`).join('')}
                        </div>
                        ` : ''}
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>'''
    
    try:
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("HTML 템플릿 파일이 생성되었습니다.")
    except Exception as e:
        print(f"템플릿 파일 생성 오류: {e}")

from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

class BookSearcher:
    def __init__(self):
        self.books_data = []
        self.data_file = 'books_data.json'
        self.load_data()
    
    def search_book(self, title):
        """Google Books API를 사용하여 책 검색"""
        try:
            # Google Books API 엔드포인트
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': f'intitle:{title}',
                'maxResults': 5,
                'langRestrict': 'ko'  # 한국어 우선
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            books = []
            
            if 'items' in data:
                for item in data['items']:
                    volume_info = item.get('volumeInfo', {})
                    
                    # 책 기본 정보 추출
                    book_info = {
                        'id': item.get('id'),
                        'title': volume_info.get('title', 'Unknown'),
                        'authors': volume_info.get('authors', ['Unknown']),
                        'publisher': volume_info.get('publisher', 'Unknown'),
                        'publishedDate': volume_info.get('publishedDate', 'Unknown'),
                        'description': volume_info.get('description', 'No description'),
                        'pageCount': volume_info.get('pageCount', 'Unknown'),
                        'categories': volume_info.get('categories', []),
                        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        'table_of_contents': self.extract_table_of_contents(volume_info),
                        'search_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    books.append(book_info)
            
            return books
            
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return []
        except Exception as e:
            print(f"검색 오류: {e}")
            return []
    
    def extract_table_of_contents(self, volume_info):
        """책 정보에서 목차 정보 추출 (제한적)"""
        # Google Books API는 목차를 직접 제공하지 않으므로,
        # 설명이나 다른 필드에서 목차 관련 정보를 추출 시도
        description = volume_info.get('description', '')
        
        # 간단한 목차 패턴 매칭
        toc_keywords = ['목차', '차례', '구성', 'Contents', 'Chapter']
        table_of_contents = []
        
        # 설명에서 목차 관련 내용 찾기
        if any(keyword in description for keyword in toc_keywords):
            lines = description.split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line for keyword in toc_keywords):
                    # 목차 관련 라인들 추출
                    if len(line) > 10 and len(line) < 100:
                        table_of_contents.append(line)
        
        # 목차를 찾지 못한 경우 카테고리를 목차로 사용
        if not table_of_contents and volume_info.get('categories'):
            table_of_contents = [f"주제: {', '.join(volume_info['categories'])}"]
        
        return table_of_contents if table_of_contents else ["목차 정보를 찾을 수 없습니다."]
    
    def save_book(self, book_data):
        """검색된 책 정보를 저장"""
        # 중복 체크 (같은 ID의 책이 이미 있는지 확인)
        existing_ids = [book.get('id') for book in self.books_data]
        if book_data.get('id') not in existing_ids:
            self.books_data.append(book_data)
            self.save_data()
            return True
        return False
    
    def save_data(self):
        """데이터를 JSON 파일에 저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"데이터 저장 오류: {e}")
    
    def load_data(self):
        """저장된 데이터를 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.books_data = json.load(f)
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            self.books_data = []
    
    def get_saved_books(self):
        """저장된 책 목록 반환"""
        return self.books_data
    
    def delete_book(self, book_id):
        """책 삭제"""
        self.books_data = [book for book in self.books_data if book.get('id') != book_id]
        self.save_data()

# BookSearcher 인스턴스 생성
book_searcher = BookSearcher()

@app.route('/')
def index():
    """메인 페이지"""
    saved_books = book_searcher.get_saved_books()
    return render_template('index.html', saved_books=saved_books)

@app.route('/search', methods=['POST'])
def search_books():
    """책 검색 API"""
    title = request.form.get('title', '').strip()
    
    if not title:
        return jsonify({'error': '책 제목을 입력해주세요.'})
    
    books = book_searcher.search_book(title)
    
    if not books:
        return jsonify({'error': '검색 결과를 찾을 수 없습니다.'})
    
    return jsonify({'books': books})

@app.route('/save', methods=['POST'])
def save_book():
    """책 정보 저장 API"""
    book_data = request.json
    
    if book_searcher.save_book(book_data):
        return jsonify({'success': True, 'message': '책이 저장되었습니다.'})
    else:
        return jsonify({'success': False, 'message': '이미 저장된 책입니다.'})

@app.route('/delete/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """책 삭제 API"""
    book_searcher.delete_book(book_id)
    return jsonify({'success': True, 'message': '책이 삭제되었습니다.'})

if __name__ == '__main__':
    # templates 디렉토리가 없으면 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # HTML 템플릿 파일 생성
    create_html_template()
    
    print("서버가 시작됩니다...")
    print("브라우저에서 http://localhost:5000 으로 접속하세요.")
    app.run(debug=True, host='0.0.0.0', port=5000)
