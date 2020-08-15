import os
import NaverBlogCrawler
import csv
from datetime import datetime

def parse_and_save(search_word, max_count=None):
    article_list = NaverBlogCrawler.naver_blog_crawling(search_word, 100, "sim", max_count)

    if article_list:
        print("텍스트 파일로 저장합니다")
        save_as_csv(search_word, article_list)
    return

def createDirectory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

def save_as_csv(search_word, article_list):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    save_path = os.getcwd() + '\\crawl\\'
    createDirectory(save_path)
    file_name = now + '-' + search_word + '.csv'

    try:
        f = open(save_path + file_name, 'w', encoding='utf-8')
        wr = csv.writer(f)
        for article in article_list:
            try:
                renew_body = article._body.replace('\n',' ') # 바디에 개행문자가 있으면 csv파일이 제대로 생성 안됨...
                image_count = len(article._images)
                hyperlink_count = len(article._hyperlinks)
                video_count = len(article._videos)

                wr.writerow([article._blogId, article._logNo, article._url, article._title, renew_body, image_count, hyperlink_count, video_count])
                
                print(article._url + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 게시물 저장 성공!')
        f.close
    except Exception as e:
        print("Failed to save text file : ")
        print(e)

    return
    

if __name__ == '__main__':
    parse_and_save("자기소개서 예시", 80)
    parse_and_save("다운로드", 80)
    parse_and_save("립버전", 80)