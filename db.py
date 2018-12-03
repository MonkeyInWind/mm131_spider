import pymysql
import uuid
import time

connection = pymysql.connect(
            host = '127.0.0.1',
            port = 3306,
            user = 'root',
            password = '111111',
            database = 'img_spider',
            charset = 'utf8'
        )


def save_img_to_db(class_en, img_url, title_id):
    try:
        cid = str(uuid.uuid1())
        time_stamp = str(int(time.time()))
        with connection.cursor() as cursor:
            sql = "insert into `mm131` (`id`, `time_stamp`, `class_en`, `url`, `title_id`) values (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (cid, time_stamp, class_en, img_url, title_id))

        connection.commit()
        return None
    except Exception as e:
        print('save image to db error')
        print(e)
        return None
    #finally:
    #    connection.close()
    #    print ('save ' + class_en + ' success...')
    #    return None
def save_img_title(class_en, class_cn, title):
    try:
        cid = str(uuid.uuid1())
        time_stamp = str(int(time.time()))
        with connection.cursor() as cursor:
            sql = "insert into `mm131_titles` (`id`, `time_stamp`, `class_en`, `class_cn`, `title`) values (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (cid, time_stamp, class_en, class_cn, title))

        connection.commit()
        return cid
    except Exception as e:
        print('save ' + class_en + ' ' + title + ' error')
        print(e)
        return None
    #finally:
     #   connection.close()
