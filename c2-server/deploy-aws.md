# AWS 배포 가이드

## 방법 1: EC2 + Docker Compose (간단)

### 1. EC2 인스턴스 생성
- AMI: Ubuntu 22.04 LTS
- Instance Type: t2.medium 이상
- Storage: 20GB 이상
- Security Group: 포트 22, 8000 열기

### 2. SSH 접속 및 설정

```bash
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
sudo apt install docker.io docker-compose git -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# 재로그인
exit
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### 3. 코드 클론 및 실행

```bash
git clone https://github.com/HOHK0923/ReD-Chain.git
cd ReD-Chain/c2-server

# 환경 변수 설정
cp .env.example .env
nano .env

# 반드시 변경할 것:
# SECRET_KEY=your-random-secret-key-here
# API_KEY_SALT=your-random-salt-here

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. Security Group 설정

AWS Console → EC2 → Security Groups

**Inbound Rules:**
- SSH: Port 22 (당신의 IP만)
- Custom TCP: Port 8000 (0.0.0.0/0 또는 특정 IP)

### 5. 접속 확인

```bash
# 헬스 체크
curl http://your-ec2-ip:8000/health

# 브라우저에서
http://your-ec2-ip:8000/docs
```

---

## 방법 2: EC2 + RDS + ElastiCache (프로덕션)

### 1. RDS PostgreSQL 생성

```
- Engine: PostgreSQL 15
- Template: Free tier / Production
- DB Instance Identifier: redchain-db
- Master username: malchain
- Master password: (강력한 비밀번호 설정)
- VPC: EC2와 동일한 VPC
- Public access: No
- Security Group: PostgreSQL (5432) 허용
```

Security Group 설정:
- Type: PostgreSQL
- Port: 5432
- Source: EC2의 Security Group

### 2. ElastiCache Redis 생성

```
- Engine: Redis
- Name: redchain-cache
- Node type: cache.t3.micro
- VPC: EC2와 동일한 VPC
- Security Group: Redis (6379) 허용
```

Security Group 설정:
- Type: Custom TCP
- Port: 6379
- Source: EC2의 Security Group

### 3. EC2에서 환경 변수 수정

```bash
cd ReD-Chain/c2-server
nano .env
```

```ini
# RDS 엔드포인트 (AWS Console에서 확인)
DATABASE_URL=postgresql+asyncpg://malchain:your-password@redchain-db.xxxxx.ap-northeast-2.rds.amazonaws.com:5432/malchain

# ElastiCache 엔드포인트 (AWS Console에서 확인)
REDIS_URL=redis://redchain-cache.xxxxx.0001.apn2.cache.amazonaws.com:6379

SECRET_KEY=your-super-secret-key-change-this
API_KEY_SALT=your-salt-change-this
```

### 4. Docker Compose 수정 (외부 DB 사용)

```bash
nano docker-compose.yml
```

postgres와 redis 서비스 주석 처리하고 c2-server만 실행:

```yaml
version: '3.8'

services:
  c2-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      API_KEY_SALT: ${API_KEY_SALT}
    restart: always
```

### 5. 실행

```bash
docker-compose up -d
```

---

## 자동 재시작 설정

```bash
# systemd 서비스 생성
sudo nano /etc/systemd/system/redchain.service
```

```ini
[Unit]
Description=ReD-Chain C2 Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/ReD-Chain/c2-server
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable redchain
sudo systemctl start redchain

# 상태 확인
sudo systemctl status redchain
```

---

## HTTPS 설정 (프로덕션 권장)

### Nginx + Let's Encrypt 사용

```bash
# Nginx 설치
sudo apt install nginx certbot python3-certbot-nginx -y

# Nginx 설정
sudo nano /etc/nginx/sites-available/redchain
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/redchain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com
```

---

## 모니터링

### 로그 확인

```bash
# C2 서버 로그
docker-compose logs -f c2-server

# 실시간 모니터링
docker stats

# 디스크 사용량
df -h
```

### 기본 모니터링

```bash
# htop 설치
sudo apt install htop -y
htop
```

---

## 업데이트 방법

```bash
cd ReD-Chain
git pull origin main
cd c2-server
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 트러블슈팅

### 포트가 이미 사용 중인 경우

```bash
# 포트 사용 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### DB 연결 실패

```bash
# RDS Security Group 확인
# EC2에서 RDS 접속 테스트
telnet redchain-db.xxxxx.rds.amazonaws.com 5432
```

### Docker 메모리 부족

```bash
# Docker 정리
docker system prune -a

# 메모리 확인
free -h
```

---

## 비용 최적화

- **Free Tier 사용 시:**
  - EC2: t2.micro (1년 무료)
  - RDS: db.t3.micro (1년 무료, 750시간/월)
  - ElastiCache: cache.t2.micro (사용량 기준)

- **프로덕션:**
  - EC2: t2.medium 이상
  - RDS: db.t3.small 이상
  - Auto Scaling 설정

---

## 보안 체크리스트

- [ ] SSH 키 기반 인증만 허용
- [ ] Security Group 최소 권한 원칙
- [ ] RDS public access 비활성화
- [ ] 강력한 SECRET_KEY, API_KEY_SALT 사용
- [ ] HTTPS 적용 (프로덕션)
- [ ] 정기적인 백업 설정
- [ ] CloudWatch 알람 설정
- [ ] IAM Role 기반 권한 관리
