import mysql.connector
from mysql.connector import Error


def insert_location(package_id: str, timestamp: int, latitude: float, longitude: float, accuracy: int):
    print("insert_location called")

    try:
        connection = mysql.connector.connect(host='localhost', user='root', passwd='fg7ioh3bycw4io8euil', db='location_db')

        sql_insert_query = "INSERT INTO geolocation VALUES (%s,%s,%s,%s,%s)"
        data = (package_id, timestamp, latitude, longitude, accuracy)

        cursor = connection.cursor()
        cursor.execute(sql_insert_query, data)
        connection.commit()

    except Error as e:
        print("Error inserting location", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Connection closed")


def insert_temperature_exceeding(package_id: str, timestamp: int, temperature: float):
    print("insert_temperature_exceeding called")
    print(package_id, timestamp, temperature)
    try:
        connection = mysql.connector.connect(host='localhost', user='root', passwd='fg7ioh3bycw4io8euil', db='location_db')

        sql_insert_query = "INSERT INTO temperature VALUES (%s,%s,%s)"
        data = (package_id, timestamp, temperature)

        cursor = connection.cursor()
        cursor.execute(sql_insert_query, data)
        connection.commit()

    except Error as e:
        print("Error inserting temperature", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Connection closed")


def insert_humidity_exceeding(package_id: str, timestamp: int, humidity: float):
    print("insert_humidity_exceeding called")
    print(package_id, timestamp, humidity)
    try:
        connection = mysql.connector.connect(host='localhost', user='root', passwd='fg7ioh3bycw4io8euil', db='location_db')

        sql_insert_query = "INSERT INTO humidity VALUES (%s,%s,%s)"
        data = (package_id, timestamp, humidity)

        cursor = connection.cursor()
        cursor.execute(sql_insert_query, data)
        connection.commit()

    except Error as e:
        print("Error inserting humidity", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Connection closed")
