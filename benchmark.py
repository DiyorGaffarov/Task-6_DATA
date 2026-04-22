import time
import psycopg2
from psycopg2.extras import RealDictCursor


conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="faker_db",
    user="postgres",
    password="root"
)

cur = conn.cursor(cursor_factory=RealDictCursor)

locale = "en_US"
seed = 123
batch = 0
batch_size = 1000   # 🔥 change this

start = time.time()

cur.execute(
    "SELECT * FROM faker_generate_users_batch(%s, %s, %s, %s)",
    (locale, seed, batch, batch_size)
)

users = cur.fetchall()

end = time.time()

elapsed = end - start
count = len(users)

print(f"Generated users: {count}")
print(f"Time taken: {elapsed:.4f} seconds")
print(f"Speed: {count / elapsed:.2f} users/second")

cur.close()
conn.close()