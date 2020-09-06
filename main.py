import os
import NaverBlogCrawler
import csv
from datetime import datetime

# CSV 인코딩 타입. ms949 혹은 utf-8을 쓰시면 됩니다.
CSV_ENCODING_TYPE = 'ms949'

def parseAndSave(searchWord, maxCount=None):
    blogPostList = NaverBlogCrawler.naverBlogCrawling(searchWord, 100, "sim", maxCount)

    if blogPostList:
        print("텍스트 파일로 저장합니다")
        saveAsCsv(searchWord, blogPostList)
    return

def createDirectory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

def saveAsCsv(searchWord, blogPostList):
    # 저장할 csv 파일명 설정
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    savePath = os.getcwd() + '\\crawl\\'
    createDirectory(savePath)
    fileName = now + '-' + searchWord + '.csv'

    try:
        f = open(savePath + fileName, 'w', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)
        for currentBlogPost in blogPostList:
            try:
                newlineRemovedBody = currentBlogPost._body.replace('\n',' ') # 바디에 개행문자가 있으면 csv파일이 제대로 생성 안됨...
                imageCnt = len(currentBlogPost._images)
                hyperlinkCnt = len(currentBlogPost._hyperlinks)
                videoCnt = len(currentBlogPost._videos)

                wr.writerow([currentBlogPost._blogId, currentBlogPost._logNo, currentBlogPost._url, currentBlogPost._title, newlineRemovedBody, imageCnt, hyperlinkCnt, videoCnt])
                
                print(currentBlogPost._url + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 게시물 저장 성공!')
        f.close
    except Exception as e:
        print("Failed to save text file : ")
        print(e)

    return
    

if __name__ == '__main__':
    parseAndSave("대구 희망지원금", 10)
    # parseAndSave("다운로드", 80)
    # parseAndSave("립버전", 80)