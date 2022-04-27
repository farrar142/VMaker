# setup

## 실행

0. ffmpeg 설치
1. vm.exe 경로를 환경변수에 등록.
2. setup.py 실행하여 필요한 모듈 등록
3. cmd 혹은 exe파일로 vm.exe 실행
4. settings.json 을 vm.exe 실행 경로에 저장.

## settings.json 설정

### 예시

```json
{
  "filesPath": "./origin",
  "resultPath": "./result",
  "resultFile": "result.mp4",
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

filesPath : 수정 할 파일이 있는 경로입니다.
resultPath : 결과 파일이 저장될 경로입니다.
resultFile : 결과 파일의 이름입니다.
files : 병합/수정 할 파일들을 적습니다.
remove : 동영상에서 제거할 구간을 적습니다 단위는 초입니다.
aremove : 동영상에서 음소거할 구간을 적습니다 단위는 초입니다.
fadein : 페이드인 시간입니다.
fadeout : 페이드아웃 시간입니다.
youtube : settings.json 파일에 해당 항목이 있을 시 유튜브로 업로드를 시도합니다. youtube api에서 지원하는 oauth2.json파일이 있어야 합니다.

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
