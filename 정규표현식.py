'[abc]' # : a,b,c중에 하나 있으면 매치. a -> a매치됨. before -> b매치됨. dude -> 매치안됨.
'[a-c]' # : a,b,c
'[0-5]' # : 0 ~ 5
'[A-Z]' # : A ~ Z
'[a-zA-Z]' # : 모든 알파벳
'[0-9]' # : 모든 숫자
'[가-힣]' # : 모든 한글
'[^0-9]' # 숫자가 아닌 모든 문자(특수문자, 공백, 알파벳 등)
#'\d' : '[0-9]'
# '\D' : '[^0-9]'
# '\s' : 화이트스페이스(공백 만드는 \n\t\r\f\v) 문자와 매치
# '\S' : 공백 아닌 모든 문자.
# '\w' : 문자 + 숫자
# '\W' : 문자+숫자 아닌 모든 문자
# 'a.b' : a + 모든문자 + b
# 'ca*t' : a가 0번 이상 반복
# 'ca+t' : a가 1번 이상 반복
# 'ca{2,5}t' : a가 2~5번 반복
# 'ab?c' : a + b가 있거나 없거나 + c
# 'a|b' : a 또는 b와 매치
# '\A' : 문자열 처음과 매칭. ^과 동일한데 multiline사용할때에도 문자열 처음만 매칭됨.
# '\Z' : 문자열 끝과 매칭 &과동일.
# '\b' : 단어 구분자. 보통 화이트스페이스와 매칭. r꼭 붙여야 인식함. 아니면 백스페이스로 인식.
# '\B' : 화이트스페이스 아닌 단어와 매칭
# '(ABC)' : ABC문자열그룹과 매칭

import re
p = re.compile('[a-z]+') # 정규표현식 [a-z]+ : 반복되는 알파벳이 컴파일된 패턴객체 p생성. 이걸로 검색가능.

m = p.match('python') # 처음부터 정규식와 매치되는지 조사. match객체
s = p.search('3 python') # 전체를 검색해서 정규식과 매치되는지 조사. 3있어도 매치됨. match객체
f = p.findall('Life is too short') # 정규식과 매치되는 모든 문자열을 리스트로 반환.
i = p.finditer('Life is too short') # iterator로 반환. match객체

p = re.compile('blue|white|red')
b = p.sub('colour', 'blue socks and red shoes') # 매칭되는 문자열을 colour로 교체
p = re.compile(r"(?P<name>\w+)\s+(?P<phone>\d+[-]\d+[-]\d+)") # ()로 그루핑. (?P<name>)하면 그룹에 name이라는 이름 붙힐수 있음.
print(p.sub("\g<2> \g<1>", "park 010-1234-1234")) # \g<번호/이름>으로 그룹 호출 가능

# match 객체 매서드
m.group() # 매치된 문자열 반환.
s.start() # 시작위치 반환.
m.end() # 끝위치 반환.
s.span() # (시작위치, 끝위치) 튜플 반환

p = re.match('[a-z]+', 'python') # 이렇게 한번에도 가능. p객체 한번만 쓸때는 이렇게.

p = re.compile('a.b', re.DOTALL) # \n도 포함해서 .검색 .은 \n을 제외한 모든문자와 매치 re.S로도 씀
p = re.compile('[a-z]+', re.IGNORECASE) # 대소문자 무시. re.I로도 씀
p = re.compile(r"^python\s\w+", re.MULTILINE) 
# ^는 문자열 처음에 매치되는지. &는 문자열 마지막에 매치되는지 인데 multiline, re.M을 쓰면
# 각 줄마다 이렇게 시작하는지 확인해줌.
data = """python one
life is too short
python two
you need python
python three"""
print(p.findall(data))

email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') # 파이썬문자열변환, 정규식 처리 과정에서 \을 두번 날리기때문에 생으로 . 하려면 \\.해야됨 \ 하려면 \\\\ rString쓰면 한번 날아가는것만 고려하면 됨
email_pattern = re.compile(r"""
    ^                       # 문자열의 시작
    [a-zA-Z0-9._%+-]+       # 사용자명: 영문자, 숫자, 특수문자
    @                       # @ 기호
    [a-zA-Z0-9.-]+          # 도메인명: 영문자, 숫자, 점, 하이픈
    \.                      # 점(.)
    [a-zA-Z]{2,}            # 최상위 도메인: 영문자 2자 이상
    $                       # 문자열의 끝
""", re.VERBOSE) # re.V를 쓰면 주석이랑 화이트스페이스 제거됨. 설명용.

p = re.compile(r"(\w+)\s+\d+[-]\d+[-]\d+") # ()로 그루핑. (?P<name>\w+)로 하면 그룹에 name이라는 이름 붙힐수 있음.
m = p.search("park 010-1234-1234")
print(m.group(1)) # group(0)은 전체. group(1)은 첫번째 그룹.

p = re.compile(r'(?P<word>\b\w+)\s+(?P=word)') # word그룹 재참조. 앞에 \b\w+가 똑같이 뒤에 나오는지 확인.
p.search('Paris in the the spring').group()

# 전방탐색 : 조건만 확인하고 결과에선 제외하고 싶을때
p = re.compile(".+(?=:)") # :이 뒤에 있는지 확인. ?= 대신 ?! 쓰면 :이 없는 문자열 매칭
m = p.search("http://google.com") # http만 반환