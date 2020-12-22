# -*- coding: utf-8 -*-

import requests
import json
import urllib2

from PIL import ImageFile
from flask import Flask, request, make_response, jsonify

ERROR_MESSAGE = '네트워크 접속에 문제가 발생하였습니다. 잠시 후 다시 시도해주세요.'
URL_OPEN_TIME_OUT = 10

app = Flask(__name__)

#----------------------------------------------------
# 제목 
#----------------------------------------------------
def get_title(answer):

    #--------------------------------
    # 영화가 있는지 검사
    #--------------------------------
    title = []
    index = answer.find(' 1. ')
    
    if index < 0:
        return answer, title
    
    title_string = answer[index + 1:]
    answer = answer[:index]

    #--------------------------------
    # 영화제목을 배열로 설정
    #--------------------------------
    number = 1
    
    while 1:
        number += 1
        search_string = ' %d. ' % number
        index = title_string.find(search_string)
        
        if index < 0:
            title.append(title_string[3:].strip())
            break;
        
        title.append(title_string[3:index].strip())
        title_string = title_string[index + 1:]
    
    return answer, title


#----------------------------------------------------
# Dialogflow에서 대답 구하기
#----------------------------------------------------
def get_answer(text, user_key):
    
    #--------------------------------
    # Dialogflow에 요청
    #--------------------------------
    data_send = { 
        'lang': 'ko',
        'query': text,
        'sessionId': user_key,
        'timezone': 'Asia/Seoul'
    }
    
    data_header = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer adfb4242e4a041...'	# Dialogflow의 Client access token 입력
    }
    
    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    
    res = requests.post(dialogflow_url,
                            data=json.dumps(data_send),
                            headers=data_header)

    #--------------------------------
    # 대답 처리하기
    #--------------------------------
    if res.status_code != requests.codes.ok:
        return ERROR_MESSAGE
    
    data_receive = res.json()
    answer = data_receive['result']['fulfillment']['speech'] 
    
    return answer



#----------------------------------------------------
# 영화 정보 처리
#----------------------------------------------------
def process_movie_info(movie_name):

    if movie_name == u'라라랜드':
        answer = '<Photo>https://img.movist.com/?img=/x00/04/84/38_p1.jpg</Photo>'
        ##answer += '긍정, 부정 의견 넣기'

    return answer


#----------------------------------------------------
# Dialogflow fullfillment 처리
#----------------------------------------------------
@app.route('/', methods=['POST'])
def webhook():

    #--------------------------------
    # 액션 정의
    #--------------------------------
    req = request.get_json(force=True)
    action = req['result']['action']

    #--------------------------------
    # 액션 처리
    #--------------------------------
    if action == 'movie_info':
        movie_name = req['result']['parameters']['review_type']
        answer = process_movie_info(movie_name)
    else:
        answer = 'error'

    res = {'speech': answer}
        
    return jsonify(res)



#----------------------------------------------------
# 카카오톡 키보드 처리
#----------------------------------------------------
@app.route("/keyboard")
def keyboard():

    res = {
        'type': 'buttons',
        'buttons': ['음성으로 분석하기']
        'buttons': ['텍스트로 분석하기']
    }

    return jsonify(res)



#----------------------------------------------------
# 카카오톡 메시지 처리
#----------------------------------------------------
@app.route('/message', methods=['POST'])
def message():

    #--------------------------------
    # 메시지 받기
    #--------------------------------
    req = request.get_json()
    user_key = req['user_key']
    content = req['content']
    
    if len(user_key) <= 0 or len(content) <= 0:
        answer = ERROR_MESSAGE

    #--------------------------------
    # 메시지 설정
    #--------------------------------
    res = {
        'message': {
            'text': answer
        }                    
    }

    #--------------------------------
    # 메뉴 버튼 설정
    #--------------------------------
    menu_button = get_menu_button(menu)
    
    if menu_button != None:
        res['keyboard'] = menu_button 

    return jsonify(res)



#----------------------------------------------------
# 메인 함수
#----------------------------------------------------
if __name__ == '__main__':

    app.run(host='0.0.0.0', port = 5110, threaded=True)    
    
