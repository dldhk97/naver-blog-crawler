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
from article import Article

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

# 게시글 타입별 본문 지정. 본문만 선택할 수 있으면 본문 노드 반환.
def get_main_content(content):
    main = content.select('div.se-main-container')
    if main:
        return main[0]
    else:
        main = content.select('div.__se_component_area')
        if main:
            return main[0]
        else:
            return content

# 본문 텍스트 추출
def get_entire_body(content):
    result = str(content.get_text())

    # 개행문자 정리함. '\n ' -> '\n'
    result = re.sub("(\\n )" , "\n", result)
    # 개행문자 정리 2 '\n' 2번이상 반복 -> '\n'
    result = re.sub("(\\n){2,}" , "\n", result)
    # 개행문자 정리 3 ' ' 2번이상 반복 -> ' '
    result = re.sub("( ){2,}" , " ", result)
    # 개행문자 정리 4 특수공백문자 정리
    result = re.sub('\u200b' , "", result)

    return result

def get_images(content):
    result = []
    for node in content.find_all('img'):
        result.append(node)
    return result

def get_hyperlinks(content):
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

                    for link in get_blog_post_content_soup.select('iframe#mainFrame'):
                        real_blog_post_url = "http://blog.naver.com" + link.get('src')

                        get_real_blog_post_content_code = requests.get(real_blog_post_url)
                        get_real_blog_post_content_text = get_real_blog_post_content_code.text

                        get_real_blog_post_content_soup = BeautifulSoup(get_real_blog_post_content_text, 'lxml')

                        # 2년 전에는 태그ID가 postViewArea인 div 내에 컨텐츠가 있었는데, 
                        # 현재는 태그ID가 post-view + logNo 조합인 div 안에 컨텐츠가 있음.
                        contentTag = 'div#postViewArea'
                        logNo = ''
                        for s in real_blog_post_url.split('&'):
                            if s.startswith('logNo'):
                                logNo = s.split('=')[1]
                                contentTag = 'div#post-view' + logNo
                                break
                        
                        # blogId 구하기(부가적인거라 예외 잡혀도 무관)
                        blogId = 'Unknown'
                        try:
                            for s in real_blog_post_url.split('?'):
                                if s.startswith('blogId'):
                                    blogId = s.split('&')[0].split('=')[1]
                                    break;
                        except e as Exception:
                            print(e)

                        for blog_post_content in get_real_blog_post_content_soup.select(contentTag):
                            main_content = get_main_content(blog_post_content)

                            remove_html_tag = re.compile('<.*?>')

                            title = re.sub(remove_html_tag, '', response_body_dict['items'][j]['title'])
                            description = re.sub(remove_html_tag, '',
                                                           response_body_dict['items'][j]['description'])
                            date = datetime.datetime.strptime(response_body_dict['items'][j]['postdate'],
                                                                            "%Y%m%d").strftime("%y.%m.%d")
                            blogName = response_body_dict['items'][j]['bloggername']

                            body = get_entire_body(main_content)            # 본문 텍스트 추출
                            images = get_images(main_content)               # 이미지 목록 추출
                            hyperlinks = get_hyperlinks(main_content)       # 하이퍼링크 목록 추출
                            videos = get_videos(main_content)               # 비디오 목록 추출(유튜브 or 네이버TV)

                            currentArticle = Article(blogId, logNo, blog_post_url, title, description, date, blogName, images, hyperlinks, videos, body)

                            print(currentArticle)
                            print("-----------------------------------------------------------------------------------")
                except Exception as e:
                    print(e)
                    j += 1

    