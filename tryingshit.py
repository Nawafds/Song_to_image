import mysql.connector
from mysql.connector import Error

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "12345678",
    database = "Songs"
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE TABLE USER (ID int PRIMARY KEY, Image LONGBLOB);")

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



# aImg = convertToBinaryData("prototype/photos/havana.png")
# id = 2
#
# mycursor.execute("INSERT INTO USER (ID, Image) VALUES (%s,%s);", (id,aImg))
# mydb.commit()

mycursor.execute("SELECT * FROM USER WHERE ID = 1 ")

myresult = mycursor.fetchall()

for x in myresult:
  print(x[0])
  convert_data(x[1], "house.png")














