import json
import datetime
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup

class Article:
    def __init__(self, blogId, logNo, url, title, description, date, blogName, images, hyperlinks, videos, body):
        self._blogId = blogId
        self._logNo = logNo
        self._url = url
        self._title = title
        self._description = description
        self._date = date
        self._blogName = blogName
        self._images = images
        self._hyperlinks = hyperlinks
        self._videos = videos
        self._body = body

    def __str__(self):
        s = "Blog ID : " + self._blogId + "\n"
        s += "logNo : " + self._logNo + "\n"
        s += "포스팅 URL : " + self._url + "\n"
        s += "포스팅 제목 : " + self._title + "\n"
        s += "포스팅 설명 : " + self._description + "\n"
        s += "포스팅 날짜 : " + self._date + "\n"
        s += "블로그 이름 : " + self._blogName + "\n"

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
    
    # def toCsvStyle(self):
    #     s = self._blogId + "\t"
    #     s += self._logNo + "\t"
    #     s += self._url + "\t"
    #     s += self._title + "\t"
    #     s += self._description + "\t"
    #     s += self._date + "\t"
    #     s += self._blogName + "\t"

    #     if self._images:
    #         for image in self._images:
    #              s += image + "\n"
    #     s += '\t'
    #     if self._hyperlinks:
    #         for hyperlink in self._hyperlinks:
    #             s += hyperlink + "\n"
    #     s += '\t'
    #     if self._videos:
    #         for video in self._videos:
    #             s += video + "\n"
    #     s += '\t'
    #     s += self._body
    #     return s
