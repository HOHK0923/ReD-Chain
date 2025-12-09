# EC2 빠른 배포 가이드

## 1. EC2 접속

```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

## 2. 프로젝트 업데이트

```bash
cd ReD-Chain

# 최신 코드 받기
git pull origin main

# 또는 처음이면 클론
# git clone https://github.com/HOHK0923/ReD-Chain.git
# cd ReD-Chain
```

## 3. 웹 대시보드 빌드

```bash
cd web-dashboard

# Node.js 설치 (처음만)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 의존성 설치
npm install

# 빌드 (dist 폴더 생성)
npm run build

# 확인
ls dist/
# index.html 파일이 있어야 함
```

## 4. C2 서버 실행

```bash
cd ../c2-server

# Python 패키지 설치 (처음만)
pip3 install -r requirements.txt

# 기존 프로세스 종료
pkill -f main_standalone.py

# 새로 실행
nohup python3 main_standalone.py > c2.log 2>&1 &

# 로그 확인
tail -f c2.log
```

## 5. Security Group 설정

```
AWS Console → EC2 → Security Groups → 인바운드 규칙
포트 8000 추가:
- Type: Custom TCP
- Port: 8000
- Source: 0.0.0.0/0 (또는 내 IP만)
```

## 6. 접속 테스트

```bash
# EC2에서 테스트
curl http://localhost:8000/

# 아이패드/PC에서 접속
# http://your-ec2-public-ip:8000/
```

## 문제 해결

### 포트가 이미 사용중
```bash
lsof -ti:8000 | xargs kill -9
```

### 빌드 파일이 안보임
```bash
cd web-dashboard
ls dist/
# 없으면 다시 빌드
npm run build
```

### 서버 재시작
```bash
cd c2-server
pkill -f main_standalone.py
nohup python3 main_standalone.py > c2.log 2>&1 &
```

## 완료!

이제 `http://your-ec2-ip:8000` 으로 접속하면 웹 대시보드가 나옵니다!
