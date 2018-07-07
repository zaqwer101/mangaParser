import requests
import os
from lxml import html
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter

manga_name = "guran-buru"


def getMangaUrls(list_of_urls):
    str = ""
    a = []
    _pages = list_of_urls.split("pages:")[1]
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

#########
# ATTENTION: Эту функцию я честно спиздил с гитхаба пользователя bradleyayers
#########
def fill_page_with_image(path, canvas):
    from PIL import Image

    page_width, page_height = canvas._pagesize

    image = Image.open(path)
    image_width, image_height = image.size

    orientation = 1

    # These are the possible values for the Orientation EXIF attribute:
    ORIENTATIONS = {
        1: "Horizontal (normal)",
        2: "Mirrored horizontal",
        3: "Rotated 180",
        4: "Mirrored vertical",
        5: "Mirrored horizontal then rotated 90 CCW",
        6: "Rotated 90 CW",
        7: "Mirrored horizontal then rotated 90 CW",
        8: "Rotated 90 CCW",
    }
    draw_width, draw_height = page_width, page_height
    if orientation == 1:
        canvas.setPageRotation(0)
    elif orientation == 3:
        canvas.setPageRotation(180)
    elif orientation == 6:
        image_width, image_height = image_height, image_width
        draw_width, draw_height = page_height, page_width
        canvas.setPageRotation(90)
    elif orientation == 8:
        image_width, image_height = image_height, image_width
        draw_width, draw_height = page_height, page_width
        canvas.setPageRotation(270)
    else:
        raise ValueError("Unsupported image orientation '%s'."
                         % ORIENTATIONS[orientation])

    if image_width > image_height:
        page_width, page_height = page_height, page_width  # flip width/height
        draw_width, draw_height = draw_height, draw_width
        canvas.setPageSize((page_width, page_height))

    canvas.drawImage(path, 0, 0, width=draw_width, height=draw_height,
                     preserveAspectRatio=True)


def downloadManga(manga_name):
    image_server_url = 'https://img2.mangalib.me'
    next = "initial value"
    current_url = "https://mangalib.me/" + manga_name + "/v1/c1/1"
    current_volume = 1
    current_dir = manga_name + "/" + manga_name + "[" + str(current_volume) + "]"
    current_chapter = "01"
    os.mkdir(manga_name)
    os.mkdir(manga_name + "/" + manga_name + "[" + str(current_volume) + "]")
    imagefile_names = []
    while next != '':
        r = requests.get(current_url)
        tree = html.fromstring(r.content)
        script_text = tree.xpath('/html/head/script')[0]
        content = script_text.text_content()
        a = content.split('\n')
        list_of_urls = a[3]
        next = a[5].split("'")[1]
        img_url = a[9].split("'")[1]

        print(img_url)
        files = getMangaUrls(list_of_urls)
        for i in range(len(files)):
            print(image_server_url + img_url + files[i])
            r = requests.get(image_server_url + img_url + files[i])
            ii = str(i + 1)
            if len(ii) == 1:
                ii = "0" + str(ii)
            open(current_dir + "/" + manga_name + "_v" + str(current_volume) + "_c" + str(
                current_chapter) + "_p" + ii + "." + files[i].split(".")[-1], "wb") \
                .write(r.content)
            imagefile_names.append(current_dir + "/" + manga_name + "_v" + str(current_volume) + "_c" + str(
                current_chapter) + "_p" + ii + "." + files[i].split(".")[-1])
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
    return imagefile_names


def createPDF(manga_name):
    volume_number = 1
    for volume_dir in os.listdir(manga_name):
        pdf = Canvas(manga_name + "_volume_" + str(volume_number) + ".pdf")
        for image_file in os.listdir(manga_name + "/" + volume_dir):
            file_path = manga_name + "/" + volume_dir + "/" + image_file
            fill_page_with_image(file_path, pdf)
            pdf.showPage()
        volume_number += 1
        pdf.save()


print(downloadManga("guran-buru"))
createPDF("guran-buru")