import mysql.connector
from mysql.connector import Error


mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "12345678",
    database = "SongToImageDB"
)

mycursor = mydb.cursor()

# mycursor.execute("ALTER TABLE Images ADD img LONGBLOB;")

def addUserInfo(id, name, email):
    mycursor = mydb.cursor()
    try:
        mycursor.execute("INSERT INTO Users (id, name, email) VALUES (%s,%s,%s)",(id, name,email))
        mydb.commit()
        print("Insertion successfull")
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

def addUserImg(id, name, user_id, img):
    mycursor = mydb.cursor()
    try:
        mycursor.execute("INSERT INTO Images (id, name,user_id,img) VALUES (%s,%s,%s,%s)", (id, name, user_id,img))
        mydb.commit()
        print("Insertion successfull")
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

def convert_data(data, file_name):
    # Convert binary format to images
    # or files data(with given file_name)
    with open(file_name, 'wb') as file:
        file.write(data)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def findImage(id):
    mycursor.execute("SELECT img, name FROM Images WHERE user_id = %s;", (id,))
    records = mycursor.fetchall()
    return records

def downloadImg(records):
    print(records)
    for i in records:
        convert_data(i[0], i[1] + ".png")

