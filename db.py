import pymysql
import uuid
import time

connection = pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = '111111',
            db = 'img_spider',
            charset = 'utf8mb4',
            cursorclass = pymysql.cursors.DictCursor
        )

def save_title(title, img_id, class_en):


def save_img(class_cn, class_en, img_url):
    try:
        id = models.UUIDField(primary_key = True, default = uuid.uuid1(), editable = False, null = False)
        time_stamp = str(int(time.time()))
        with connection.cursor() as cursor:
            sql = "insert into 'mm131' ('id', 'time_stamp')"
