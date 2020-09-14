import psycopg2

connection = psycopg2.connect('dbname=example user=rachelleondiege')

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS table2;")
cursor.execute('''
   CREATE TABLE table2 (
    id INTEGER PRIMARY KEY,
    completed BOOLEAN NOT NULL DEFAULT False
  );
 ''')

SQL = 'INSERT INTO table2 (id, completed) VALUES (%(id)s, %(completed)s);'
data = {
  'id': 4,
  'completed' : False
}

cursor.execute('INSERT INTO table2 (id, completed) VALUES (1, true);')
cursor.execute('INSERT INTO table2 (id, completed) VALUES (%s, %s)', (2, True))
cursor.execute('INSERT INTO table2 (id, completed)' +
' VALUES (%(id)s, %(completed)s);', {
  'id': 3,
  'completed' : False
})

cursor.execute(SQL, data)

cursor.execute('SELECT * FROM table2')

result1 = cursor.fetchall()

for x in result1:
   print(x)
# print('fetchall tupal:', result1)

connection.commit()

connection.close
cursor.close
