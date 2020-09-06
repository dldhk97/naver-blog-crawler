import re
import json
import math
import datetime
import requests
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup
from Constants import NaverAPI
from BlogPost import BlogPost

NAVER_CLIENT_ID = NaverAPI.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = NaverAPI.NAVER_CLIENT_SECRET


def naverBlogCrawling(searchWord, displayCnt, sortType, maxCnt=None):
    searchResultBlogPageCnt = getBlogSearchResultPaginationCnt(searchWord, displayCnt)
    return getBlogPost(searchWord, displayCnt, searchResultBlogPageCnt, sortType, maxCnt)


def getBlogSearchResultPaginationCnt(searchWord, displayCnt):
    encodedSearchWord = urllib.parse.quote(searchWord)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encodedSearchWord
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)

    response = urllib.request.urlopen(request)
    responseCode = response.getcode()

    if responseCode is 200:
        responseBody = response.read()
        responseBodyDict = json.loads(responseBody.decode('utf-8'))

        if responseBodyDict['total'] == 0:
            blogPaginationCnt = 0
        else:
            blogPaginationTotalCnt = math.ceil(responseBodyDict['total'] / int(displayCnt))

            if blogPaginationTotalCnt >= 1000:
                blogPaginationCnt = 1000
            else:
                blogPaginationCnt = blogPaginationTotalCnt

            print("키워드 " + searchWord + "에 해당하는 포스팅 수 : " + str(responseBodyDict['total']))
            print("키워드 " + searchWord + "에 해당하는 블로그 실제 페이징 수 : " + str(blogPaginationTotalCnt))
            print("키워드 " + searchWord + "에 해당하는 블로그 처리할 수 있는 페이징 수 : " + str(blogPaginationCnt))

        return blogPaginationCnt

# 게시글 타입별 본문 지정. 본문만 선택할 수 있으면 본문 노드 반환.
def getMainContent(content):
    main = content.select('div.se-main-container')
    if main:
        return main[0]
    else:
        main = content.select('div.__se_component_area')
        if main:
            return main[0]
        else:
            return content

# 블로그 URL에서 logNo 추출
def getLogNo(url):
    try:
        for s in url.split('&'):
            if s.startswith('logNo'):
                return s.split('=')[1]
    except Exception as e:
        print(e)
    return None

# 블로그 URL에서 blogId 추출
def getBlogId(url):
    for s in url.split('?'):
        if s.startswith('blogId'):
            return s.split('&')[0].split('=')[1]
    return 'Unknown'

# 본문 텍스트 추출
def getEntireBody(content):
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

# 노드에 data-lazy-src가 있으면 반환, 없으면 src를 반환
def getImgSrc(node):
    if node.has_attr('data-lazy-src'):
        return node['data-lazy-src']
    elif node.has_attr('src'):
        return node['src']
    return 'Image parse failed!'

# 이미지 src 목록을 반환
def getImages(content):
    result = []
    for node in content.find_all('img'):
        src = getImgSrc(node)
        result.append(src)
    return result

# 하이퍼링크 목록을 반환
def getHyperlinks(content):
    result = []
    for node in content.find_all('a', href=True):
        if node['href'] != '#':
            hyperlink = node['href']
            result.append(hyperlink)
    return result


def getVideos(content):
    # 유튜브 추출
    result = []
    for node in content.find_all('iframe'):
        if 'www.youtube.com' in node['src']:
            src = node['src']
            result.append(src)

    # 네이버 TV or 비디오 추출
    for node in content.find_all('video'):
        if node['src']:
            src = node['src']
            result.append(src)
    return result

def getBlogPost(searchWord, displayCnt, searchResultBlogPageCnt, sortType, maxCnt=None):
    encodedSearchBlogKeyword = urllib.parse.quote(searchWord)

    for i in range(1, searchResultBlogPageCnt + 1):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encodedSearchBlogKeyword + "&display=" + str(
            displayCnt) + "&start=" + str(i) + "&sort=" + sortType

        request = urllib.request.Request(url)

        request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)

        response = urllib.request.urlopen(request)
        responseCode = response.getcode()

        if responseCode is 200:
            responseBody = response.read()
            responseBodyDict = json.loads(responseBody.decode('utf-8'))

            blogPostList = []

            if maxCnt is None:
                maxCnt = len(responseBodyDict['items'])

            for j in range(1, maxCnt + 1):
                try:
                    blogPostUrl = responseBodyDict['items'][j]['link'].replace("amp;", "")

                    # 네이버 블로그인 경우만 처리함.
                    if 'blog.naver.com' in blogPostUrl:
                        getBlogPostContentCode = requests.get(blogPostUrl)
                        getBlogPostContentText = getBlogPostContentCode.text

                        getBlogPostContentSoup = BeautifulSoup(getBlogPostContentText, 'lxml')

                        for link in getBlogPostContentSoup.select('iframe#mainFrame'):
                            realBlogPostUrl = "http://blog.naver.com" + link.get('src')

                            getRealBlogPostContentCode = requests.get(realBlogPostUrl)
                            getRealBlogPostContentText = getRealBlogPostContentCode.text

                            getRealBlogPostContentSoup = BeautifulSoup(getRealBlogPostContentText, 'lxml')

                            # 2년 전에는 태그ID가 postViewArea인 div 내에 컨텐츠가 있었는데, 
                            # 현재는 태그ID가 post-view + logNo 조합인 div 안에 컨텐츠가 있음.
                            logNo = getLogNo(realBlogPostUrl)
                            if logNo:
                                bodyIdentifier = 'div#post-view' + logNo
                            else:
                                bodyIdentifier = 'div#postViewArea'
                            
                            # blogId 구하기(blogId + logNo로 URL이 없어도 만들어낼 수 있어서 추출하여 저장함)
                            blogId = getBlogId(realBlogPostUrl)

                            for blogPostContent in getRealBlogPostContentSoup.select(bodyIdentifier):
                                mainContent = getMainContent(blogPostContent)

                                removeHtmlTag = re.compile('<.*?>')

                                title = re.sub(removeHtmlTag, '', responseBodyDict['items'][j]['title'])
                                description = re.sub(removeHtmlTag, '',
                                                            responseBodyDict['items'][j]['description'])
                                date = datetime.datetime.strptime(responseBodyDict['items'][j]['postdate'],
                                                                                "%Y%m%d").strftime("%y.%m.%d")
                                blogName = responseBodyDict['items'][j]['bloggername']

                                body = getEntireBody(mainContent)            # 본문 텍스트 추출
                                images = getImages(mainContent)               # 이미지 목록 추출
                                hyperlinks = getHyperlinks(mainContent)       # 하이퍼링크 목록 추출
                                videos = getVideos(mainContent)               # 비디오 목록 추출(유튜브 or 네이버TV)

                                currentBlogPost = BlogPost(blogId, logNo, blogPostUrl, title, description, date, blogName, images, hyperlinks, videos, body)
                                blogPostList.append(currentBlogPost)

                                # print(currentBlogPost)
                                print(blogPostUrl + ' 파싱완료 (' + str(j) + '/' + str(maxCnt) + ')')
                    else:
                        print(blogPostUrl + ' 는 네이버 블로그가 아니라 패스합니다')
                except Exception as e:
                    print('파싱 도중 에러발생 : ')
                    print(e)
                    j += 1
            
            # 파싱 완료 시 게시물 목록이 있으면 반환
            print("파싱 완료!")
            if blogPostList:
                return blogPostList

    