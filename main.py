import requests
import os
from lxml import html

manga_name = "guran-buru"


def getImageUrls(pages):
    str = ""
    a = []
    _pages = pages.split("pages:")[1]
    recording = False
    for i in range(len(_pages)):
        if _pages[i] == '}':
            recording = False
            str = str.split(":")[1]
            str = str.split(",")[0]
            a.append(str.split("\"")[1])

        if recording:
            str += _pages[i]

        if _pages[i] == '{':
            recording = True
            str = ""

    return a


image_server_url = 'https://img2.mangalib.me'
next = "initial value"
current_url = "https://mangalib.me/" + manga_name + "/v1/c1/1"
current_volume = 1
current_dir = manga_name + "/" + manga_name + "[" + str(current_volume) + "]"
current_chapter = "01"
os.mkdir(manga_name)
os.mkdir(manga_name + "/" + manga_name + "[" + str(current_volume) + "]")

while next != '':
    r = requests.get(current_url)
    tree = html.fromstring(r.content)
    script_text = tree.xpath('/html/head/script')[0]
    content = script_text.text_content()
    a = content.split('\n')
    pages = a[3]
    next = a[5].split("'")[1]
    img_url = a[9].split("'")[1]

    print(img_url)
    files = getImageUrls(pages)
    for i in range(len(files)):
        print(image_server_url + img_url + files[i])
        r = requests.get(image_server_url + img_url + files[i])
        ii = str(i + 1)
        if len(ii) == 1:
            ii = "0" + str(ii)
        open(current_dir + "/" + manga_name + "_v" + str(current_volume) + "_c" + str(current_chapter) + "_p" + ii + "." + files[i].split(".")[-1], "wb") \
            .write(r.content)

    new_current_volume = img_url.split('/')[4].split('-')[0]
    if new_current_volume != str(current_volume):
        os.mkdir(manga_name + "/" + manga_name + "[" + str(new_current_volume) + "]")
        current_volume = new_current_volume
        current_dir = manga_name + "/" + manga_name + "[" + str(current_volume) + "]"

    current_url = next
    current_chapter = int(current_chapter) + 1
    if len(str(current_chapter)) < 2:
        current_chapter = "0" + str(current_chapter)
    current_chapter = str(current_chapter)
    print(current_chapter)
