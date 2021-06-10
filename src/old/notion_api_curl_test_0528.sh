####### table이 page 그 자체인 경우

# first: children list 호출

https://www.notion.so/niceguy1575/hi-265f9e4c179747628209a4509b600fea
https://www.notion.so/niceguy1575/cast-e8b0a509c0d94ea487a670ef31e840e7

curl 'https://api.notion.com/v1/pages/265f9e4c179747628209a4509b600fea' \
  -H 'Notion-Version: 2021-05-13' \
  -H "Authorization: Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi"

curl 'https://api.notion.com/v1/pages/e8b0a509c0d94ea487a670ef31e840e7' \
  -H 'Notion-Version: 2021-05-13' \
  -H "Authorization: Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi"


# second: page내 properties 호출
curl 'https://api.notion.com/v1/databases/29000bbca3e843b9854bf7eb75080efb' \
  -H 'Notion-Version: 2021-05-13' \
  -H "Authorization: Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi"



####### page 내 table 조회는?

https://www.notion.so/niceguy1575/hihi-7c63596ea9b54bb1b1cc2a344e1755f2

# page 내 모든 블록 아이디 조회
curl 'https://api.notion.com/v1/blocks/7c63596ea9b54bb1b1cc2a344e1755f2/children?page_size=100' \
  -H 'Notion-Version: 2021-05-13' \
  -H "Authorization: Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi"

# database_id 획득
# 이후 해당 database조회하여 속성값 도출
curl 'https://api.notion.com/v1/databases/74540bfd-a619-4109-9402-e85867d1f11c' \
  -H 'Notion-Version: 2021-05-13' \
  -H "Authorization: Bearer secret_pPWC3kHqaPaHTHaAANpHa1RXVzv8Z5akflOyJZX7mQi"