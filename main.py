import os
import naverblogcrawler
import csv
from datetime import datetime

# CSV 인코딩 타입은 ms949 or utf-8
CSV_ENCODING_TYPE = 'ms949'

def parse_and_save(search_word, max_count=None):
    blogpost_list = naverblogcrawler.naver_blog_crawling(search_word, 100, "sim", max_count)

    if blogpost_list:
        print("텍스트 파일로 저장합니다")
        save_as_csv(search_word, blogpost_list)
    return

def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

def save_as_csv(search_word, blogpost_list):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    save_path = os.getcwd() + '\\crawl\\'
    create_directory(save_path)
    file_name = now + '-' + search_word + '.csv'

    try:
        f = open(save_path + file_name, 'w', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)
        for blogpost in blogpost_list:
            try:
                renew_body = blogpost._body.replace('\n',' ')   # 바디에 개행문자가 있으면 csv파일이 제대로 생성 안됨...
                image_count = len(blogpost._images)
                hyperlink_count = len(blogpost._hyperlinks)
                video_count = len(blogpost._videos)

                wr.writerow([blogpost._blog_id, blogpost._log_no, blogpost._url, blogpost._title, renew_body, image_count, hyperlink_count, video_count])
                
                print(blogpost._url + ' 저장 완료')
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