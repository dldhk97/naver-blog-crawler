import re
import json
import math
import datetime
import requests
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup
from constants import NaverAPI

naver_client_id = NaverAPI.NAVER_CLIENT_ID
naver_client_secret = NaverAPI.NAVER_CLIENT_SECRET


def naver_blog_crawling(search_blog_keyword, display_count, sort_type):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_keyword
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", naver_client_id)
    request.add_header("X-Naver-Client-Secret", naver_client_secret)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()

    if response_code is 200:
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode('utf-8'))

        if response_body_dict['total'] == 0:
            blog_pagination_count = 0
        else:
            blog_pagination_total_count = math.ceil(response_body_dict['total'] / int(display_count))

            if blog_pagination_total_count >= 1000:
                blog_pagination_count = 1000
            else:
                blog_pagination_count = blog_pagination_total_count

            print("키워드 " + search_blog_keyword + "에 해당하는 포스팅 수 : " + str(response_body_dict['total']))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 실제 페이징 수 : " + str(blog_pagination_total_count))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 처리할 수 있는 페이징 수 : " + str(blog_pagination_count))

        return blog_pagination_count

def get_img_src(node):
    if node.has_attr('data-lazy-src'):
        return node['data-lazy-src']
    elif node.has_attr('src'):
        return node['src']
    return 'Image parse failed!'

# 게시글 타입별 본문 지정. 본문만 선택할 수 있으면 본문 노드 반환.
def get_main_content(content):
    main = content.select('div.se-main-container')
    if main:
        main = main[0]
    else:
        main = content.select('div.__se_component_area')
        if main:
            main = main[0]
        else:
            main = content
    return main

def get_texts(content):
    result = str(content.get_text())

    # 개행문자 정리함. '\n ' -> '\n'
    result = re.sub("(\\n )" , "\n", result)
    # 개행문자 정리 2 '\n' 2번이상 반복 -> '\n'
    result = re.sub("(\\n){2,}" , "\n", result)
    # 개행문자 정리 3 ' ' 2번이상 반복 -> ' '
    result = re.sub("( ){2,}" , " ", result)

    return result

def get_images(content):
    result = []
    for node in content.find_all('img'):
        result.append(node)
    return result

def get_hrefs(content):
    result = []
    for node in content.find_all('a', href=True):
        if node['href'] != '#':
            result.append(node)
    return result

def get_videos(content):
    # 유튜브 추출
    result = []
    for node in content.find_all('iframe'):
        if 'www.youtube.com' in node['src']:
            result.append(node)

    # 네이버 TV or 비디오 추출
    for node in content.find_all('video'):
        if node['src']:
            result.append(node)
    return result

def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type):
    encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)

    for i in range(1, search_result_blog_page_count + 1):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
            display_count) + "&start=" + str(i) + "&sort=" + sort_type

        request = urllib.request.Request(url)

        request.add_header("X-Naver-Client-Id", naver_client_id)
        request.add_header("X-Naver-Client-Secret", naver_client_secret)

        response = urllib.request.urlopen(request)
        response_code = response.getcode()

        if response_code is 200:
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode('utf-8'))

            for j in range(0, len(response_body_dict['items'])):
                try:
                    blog_post_url = response_body_dict['items'][j]['link'].replace("amp;", "")

                    get_blog_post_content_code = requests.get(blog_post_url)
                    get_blog_post_content_text = get_blog_post_content_code.text

                    get_blog_post_content_soup = BeautifulSoup(get_blog_post_content_text, 'lxml')

                    for link in get_blog_post_content_soup.select('iframe#mainFrame'):          # 2년 전에는 mainFrame의 태그가 frame이었는듯, 현재 iframe으로 변경됨.
                        real_blog_post_url = "http://blog.naver.com" + link.get('src')

                        get_real_blog_post_content_code = requests.get(real_blog_post_url)
                        get_real_blog_post_content_text = get_real_blog_post_content_code.text

                        get_real_blog_post_content_soup = BeautifulSoup(get_real_blog_post_content_text, 'lxml')

                        # 2년 전에는 태그ID가 postViewArea인 div 내에 컨텐츠가 있었는데, 
                        # 현재는 태그ID가 post-view + logNo 조합인 div 안에 컨텐츠가 있음.
                        contentTagID = 'div#postViewArea'
                        logNo = 'div#postViewArea'
                        for s in real_blog_post_url.split('&'):
                            if s.startswith('logNo'):
                                logNo = s.split('=')[1]
                                break
                        
                        contentTagID = 'div#post-view' + logNo

                        print('Debug:url : ' + blog_post_url)

                        for blog_post_content in get_real_blog_post_content_soup.select(contentTagID):
                            main_content = get_main_content(blog_post_content)

                            remove_html_tag = re.compile('<.*?>')

                            blog_post_title = re.sub(remove_html_tag, '', response_body_dict['items'][j]['title'])
                            blog_post_description = re.sub(remove_html_tag, '',
                                                           response_body_dict['items'][j]['description'])
                            blog_post_postdate = datetime.datetime.strptime(response_body_dict['items'][j]['postdate'],
                                                                            "%Y%m%d").strftime("%y.%m.%d")
                            blog_post_blogger_name = response_body_dict['items'][j]['bloggername']
                            blog_post_full_contents = get_texts(main_content)

                            # 이미지 목록 추출
                            images = get_images(main_content)

                            # 하이퍼링크 목록 추출
                            hrefs = get_hrefs(main_content)

                            # 비디오 목록 추출(미완성)
                            videos = get_videos(main_content)

                            print("포스팅 URL : " + blog_post_url)
                            print("포스팅 제목 : " + blog_post_title)
                            print("포스팅 설명 : " + blog_post_description)
                            print("포스팅 날짜 : " + blog_post_postdate)
                            print("블로거 이름 : " + blog_post_blogger_name)

                            if images:
                                print("이미지 목록 : ")
                                for image in images:
                                    print(get_img_src(image))

                            if hrefs:
                                print("하이퍼링크 목록 : ")
                                for href in hrefs:
                                    print(href['href'])

                            if videos:
                                print("비디오 목록 : ")
                                for video in videos:
                                    print(video['src'])

                            print("포스팅 내용 : " + blog_post_full_contents)
                            print("-----------------------------------------------------------------------------------")
                except Exception as e:
                    print(e)
                    j += 1

    