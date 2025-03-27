# 🐍 Flask 

웹앱을 Flask로 제작

---

## 💡 주요 기능

- 🔐 회원가입 / 로그인 / 로그아웃
- 📝 게시글 작성, 수정, 삭제
- 🖼️ 이미지 업로드
- 💬 댓글 작성, 삭제
- ❤️ 좋아요 기능
- 🌓 다크모드 토글
- 📱 반응형 디자인 (인스타 스타일)

---

## 🛠 사용 기술

- Python 3.x
- Flask / Flask-Login / Flask-Migrate / SQLAlchemy
- SQLite (개발용 DB)
- Bootstrap 5
- Jinja2

---

## 🚀 실행 방법

```bash
# 가상환경 설정
python -m venv venv
source venv/Scripts/activate  # 윈도우
pip install -r requirements.txt

# DB 초기화
flask db upgrade

# 실행
python app.py
