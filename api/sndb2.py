import urllib.request

opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

urllib.request.urlretrieve("https://www.bigw.com.au/medias/sys_master/images/images/h06/h56/11957876031518.jpg", "00000001.jpg")