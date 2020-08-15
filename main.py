import os
import NaverBlogCrawler
from datetime import datetime

def parse_and_save(search_word, max_count=None):
    article_list = NaverBlogCrawler.naver_blog_crawling(search_word, 100, "sim", max_count)

    if article_list:
        print("텍스트 파일로 저장합니다")
        save_as_text(search_word, article_list)
    return

def createDirectory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise


def save_as_text(search_word, article_list):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    save_path = os.getcwd() + '\\crawl\\'
    createDirectory(save_path)
    file_name = now + '-' + search_word + '.txt'

    try:
        f = open(save_path + file_name, 'w', encoding='utf-8')
        for article in article_list:
            try:
                f.write(article.toCsvStyle())
                print(article._url + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 게시물 저장 성공!')
        f.close
    except Exception as e:
        print("Failed to save text file : ")
        print(e)

    

if __name__ == '__main__':
    parse_and_save("자기소개서 예시", 5)
    parse_and_save("다운로드", 5)