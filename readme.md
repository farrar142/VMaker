# setup

## 실행

1. vm.exe 경로를 환경변수에 등록.
2. cmd 혹은 exe파일로 vm.exe 실행
3. settings.json 을 vm.exe 실행 경로에 저장.

## settings.json 설정

### 예시

```json
{
  "filesPath": "./origin",
  "resultPath": "./result",
  "files": {
    "01.mp4": {
      "remove": ["~3", "10~15", "~5"],
      "fadein": 3,
      "fadeout": 3
    },
    "02.mp4": {
      "aremove": ["~3", "10~15", "~5"],
      "fadein": 3,
      "fadeout": 3
    }
  },
  "youtube": {
    "title": "sandring",
    "description": "password",
    "keywords": "test,YoutubeAPI",
    "category": "22",
    "privacyStatus": "private"
  }
}
```

## Youtube API 설정

1. (가이드 링크)[https://kminito.tistory.com/5]
2. client_secrets.json 을 vm.exe 실행 경로에 저장.

## 개발설정

### 필요 모듈 심볼릭링크 설정.

1. cmd를 관리자 권한으로 실행
1. setup.py 실행

### 서드파티 라이브러리 설치.

1. pip install -r req.txt
2. PyToYou/setup.py 관리자 권한으로 실행.
