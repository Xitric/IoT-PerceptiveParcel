import mysql.connector as db
import os


def __connect(database: str):
    host = os.environ['PP_DATABASE_HOST']
    user = os.environ['PP_DATABASE_USER']
    password = os.environ['PP_DATABASE_PASSWORD']
    return db.connect(host=host, user=user, passwd=password, db=database)


def get_route(package_id: str):
    try:
        connection = __connect('location_db')

        query = "SELECT timestamp, latitude, longitude, accuracy FROM geolocation WHERE package_id = %s ORDER BY timestamp"
        data = (package_id,)

        cursor = connection.cursor()
        cursor.execute(query, data)
        
        # Unfortunately, list comprehension did not work
        points = []
        for (timestamp, latitude, longitude, accuracy) in cursor:
            points.append((timestamp, latitude, longitude, accuracy))
        return points

    except db.Error as e:
        print("Error reading route from database", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Database connection closed")


def insert_location(package_id: str, timestamp: int, latitude: float, longitude: float, accuracy: int):
    try:
        connection = __connect('location_db')

        query = "INSERT INTO geolocation VALUES (%s,%s,%s,%s,%s)"
        data = (package_id, timestamp, latitude, longitude, accuracy)

        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()

    except db.Error as e:
        print("Error inserting location", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Database connection closed")


def insert_temperature_exceeding(package_id: str, timestamp: int, temperature: float):
    try:
        connection = __connect('location_db')

        query = "INSERT INTO temperature VALUES (%s,%s,%s)"
        data = (package_id, timestamp, temperature)

        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()

    except db.Error as e:
        print("Error inserting temperature", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Database connection closed")


def insert_humidity_exceeding(package_id: str, timestamp: int, humidity: float):
    try:
        connection = __connect('location_db')

        query = "INSERT INTO humidity VALUES (%s,%s,%s)"
        data = (package_id, timestamp, humidity)

        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()

    except db.Error as e:
        print("Error inserting humidity", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Database connection closed")