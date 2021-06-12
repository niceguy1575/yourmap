# where are you? in yourmap!

## Overview

회사, 모임 등 조직이라는 공동체를 이루는 모두는 도대체 어디서 살고 있을까요? 🤷🏻‍♀️

궁금해서 조직원의 위치 조사까지 다 마쳤습니다. 그런데 이걸 어떻게 한눈에 볼 수 있죠?

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 👉 우리 조직원이 사는 곳을 노션에서 지도로 확인할 수 있습니다!

결국 `yourmap`은 이런 질문에 답해주고 싶었습니다.

> 🤔 가깝고도 먼 우리 사이... 아무리 같은 서울 하늘아래라지만, 우리 팀원들은 도대체 어디서 살고 있는걸까?
 
 
## Result

<div>
    <a href="https://plotly.com/~niceguy1575/32/?share_key=R0pz3e7CrJBD4pSKM2azV6" target="_blank" title="yourmap_ver_openmate_0612" style="display: block; text-align: center;"><img src="https://plotly.com/~niceguy1575/32.png?share_key=R0pz3e7CrJBD4pSKM2azV6" alt="yourmap_ver_openmate_0612" style="max-width: 100%;width: 600px;"  width="600" onerror="this.onerror=null;this.src='https://plotly.com/404.png';" /></a>

### 👇 details ...

https://plotly.com/~niceguy1575/32/


 
## Structure
 yourmap은 다음과 같은 구조를 가지고 있는 프로그램입니다.
 

 
1.  노션에서 팀원 위치 DB를 구축합니다.
2. 시도/시군구 단위의 주소를 정제하여 좌표화 시킵니다.
3. Python에서 지도를 그리고, Chart-Studio에서 web embeding을 시킵니다.

## 진행사항
현재까지 진행되고 있는 개발 진행 상황 (100%)

	1. 개발 크루 모집 완료(suyo)
	2. 기능 개발 (100%)
		*  notion API 데이터 수집 기능 (100%)
		*  시도/시군구 형상정보 가공 (100%)
		*  위치정보 데이터 시각화 (100%)
		*  Chart-Studio 연계 (100%)
	3. 위치정보 주소정제 (100%)
	4. URL return 및 notion embedding(100%)
	5. 중복 좌표지역 Jittering (100%)
	6. 모듈화 (100%)
		=> Class화 시킬것. 현재 일부만 구현됨.

## Issue
1. Chart-Studio 연동 시 500kb 이상의 지도는 생성되지 못함

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 👉 100개 이상의 Point 시각화에는 무리가 없을 것으로 보임.

## 참고
1. 행정동 형상정보 획득

[https://www.juso.go.kr/addrlink/devLayerRequestList.do](https://www.juso.go.kr/addrlink/devLayerRequestList.do)

2.  python을 이용한 노션 웹페이지 시각화

[https://data101.oopy.io/good-place-to-live-alone?fbclid=IwAR2iPqJs_DeND8iPl2TMO2D-cr7b6M3WS-t8nKU7BktzCpz5_ZA2rD28uS0](https://data101.oopy.io/good-place-to-live-alone?fbclid=IwAR2iPqJs_DeND8iPl2TMO2D-cr7b6M3WS-t8nKU7BktzCpz5_ZA2rD28uS0)
[https://data101.oopy.io/plolty-tutorial-guide-in-korean](https://data101.oopy.io/plolty-tutorial-guide-in-korean)