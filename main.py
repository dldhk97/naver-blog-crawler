import NaverBlogCrawler

if __name__ == '__main__':
    article_list = NaverBlogCrawler.naver_blog_crawling("라이젠 4500U", 100, "sim")
    if article_list:
        # save as txt
        print("텍스트 파일로 저장합니다")
