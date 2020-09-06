import json
import datetime
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup

class BlogPost:
    def __init__(self, blog_id, log_no, url, title, description, date, blog_name, images, hyperlinks, videos, body):
        self._blog_id = blog_id
        self._log_no = log_no
        self._url = url
        self._title = title
        self._description = description
        self._date = date
        self._blog_name = blog_name
        self._images = images
        self._hyperlinks = hyperlinks
        self._videos = videos
        self._body = body

    def __str__(self):
        s = "Blog ID : " + self._blog_id + "\n"
        s += "logNo : " + self._log_no + "\n"
        s += "포스팅 URL : " + self._url + "\n"
        s += "포스팅 제목 : " + self._title + "\n"
        s += "포스팅 설명 : " + self._description + "\n"
        s += "포스팅 날짜 : " + self._date + "\n"
        s += "블로그 이름 : " + self._blog_name + "\n"

        if self._images:
            s += "이미지 목록 : "
            for image in self._images:
                 s += image + "\n"

        if self._hyperlinks:
            s += "하이퍼링크 목록 : "
            for hyperlink in self._hyperlinks:
                s += hyperlink + "\n"

        if self._videos:
            s += "비디오 목록 : "
            for video in self._videos:
                s += video + "\n"

        s += "포스팅 내용 : " + self._body
        return s