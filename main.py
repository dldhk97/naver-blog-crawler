import os
import naverblogcrawler
import csv
from datetime import datetime

# 'UTF-8'이 아닌, 'MS949'로 할 경우 엑셀에서 바로 열 수 있지만, 특정 문자(\u2027)가 포함된 경우 오류가 납니다.
CSV_ENCODING_TYPE = 'utf-8'

def parse_and_save(search_word, max_count=None):
    blog_post_list = naverblogcrawler.naver_blog_crawling(search_word, 100, "sim", max_count)

    if blog_post_list:
        print("텍스트 파일로 저장합니다")
        save_as_csv(search_word, blog_post_list)
    return

def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

def save_as_csv(search_word, blog_post_list):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    save_path = os.getcwd() + '\\crawl\\'
    create_directory(save_path)
    file_name = now + '-' + search_word + '.csv'

    try:
        f = open(save_path + file_name, 'w', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)
        for blog_post in blog_post_list:
            try:
                renew_body = blog_post._body.replace('\n',' ')   # 바디에 개행문자가 있으면 csv파일이 제대로 생성 안됨...
                image_count = len(blog_post._images)
                hyperlink_count = len(blog_post._hyperlinks)
                video_count = len(blog_post._videos)

                wr.writerow([blog_post._blog_id, blog_post._log_no, blog_post._url, blog_post._title, renew_body, image_count, hyperlink_count, video_count])
                
                print(blog_post._url + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 게시물 저장 성공!')
        f.close
    except Exception as e:
        print("Failed to save text file : ")
        print(e)

    return
    

if __name__ == '__main__':
    parse_and_save("대구희망지원금 신청", 10)
    # parse_and_save("다운로드", 80)
    # parse_and_save("립버전", 80)