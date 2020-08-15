import NaverBlogCrawler

def parse_and_save(search_word):
    article_list = NaverBlogCrawler.naver_blog_crawling(search_word, 100, "sim")

    if article_list:
        print("텍스트 파일로 저장합니다")
        saveAsText(article_list)
    return

def saveAsText(article_list):
    return

if __name__ == '__main__':
    parse_and_save("자기소개서 예시")