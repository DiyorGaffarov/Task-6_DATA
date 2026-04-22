from flask import Flask, request, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "faker_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SQL Faker</title>
    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            margin: 0;
        }

        .container {
            width: 90%;
            margin: 30px auto;
        }

        .card {
            background: #1e293b;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 20px;
        }

        h1 {
            margin-bottom: 10px;
        }

        label {
            display: block;
            margin-top: 10px;
        }

        input, select {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border-radius: 8px;
            border: none;
        }

        button {
            margin-top: 15px;
            padding: 10px 15px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }

        .btn-primary {
            background: #7c3aed;
            color: white;
        }

        .btn-secondary {
            background: #334155;
            color: white;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 10px;
            border-bottom: 1px solid #334155;
            text-align: left;
        }

        th {
            background: #020617;
        }
    </style>
</head>
<body>

<div class="container">

<h1>SQL Faker Generator</h1>

<div class="card">
<form method="get">
{% if error %}
<div style="color: red; margin-bottom: 10px;">
    Error: {{ error }}
</div>
{% endif %}
<label>Locale</label>
<select name="locale">
    <option value="en_US" {% if locale == 'en_US' %}selected{% endif %}>
        English (United States)
    </option>

    <option value="de_DE" {% if locale == 'de_DE' %}selected{% endif %}>
        German (Germany)
    </option>
</select>

<label>Seed</label>
<input type="number" name="seed" value="{{ seed }}">

<label>Batch</label>
<input type="number" name="batch" value="{{ batch }}">

<label>Batch Size</label>
<input type="number" name="batch_size" value="{{ batch_size }}">

<button class="btn-primary" type="submit" name="action" value="generate">Generate</button>
<button class="btn-secondary" type="submit" name="action" value="next">Next Batch</button>

</form>
</div>

<div class="card">

<table>
<tr>
    <th>Item</th>
    <th>Name</th>
    <th>Gender</th>
    <th>Address</th>
    <th>Height</th>
    <th>Weight</th>
    <th>Eye Color</th>
    <th>Phone</th>
    <th>Email</th>
</tr>

{% for u in users %}
<tr>
    <td>{{ u.item }}</td>
    <td>{{ u.full_name }}</td>
    <td>{{ u.gender }}</td>
    <td>{{ u.address }}</td>
    <td>{{ u.height }}</td>
    <td>{{ u.weight }}</td>
    <td>{{ u.eye_color }}</td>
    <td>{{ u.phone }}</td>
    <td>{{ u.email }}</td>
</tr>
{% endfor %}

</table>

</div>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    locale = request.args.get("locale", "en_US")
    action = request.args.get("action", "")

    error = None
    users = []

    try:
        seed = int(request.args.get("seed", 123))
        batch = int(request.args.get("batch", 0))
        batch_size = int(request.args.get("batch_size", 10))

        if action == "next":
            batch += 1

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT * FROM faker_generate_users_batch(%s, %s, %s, %s)",
            (locale, seed, batch, batch_size)
        )

        users = cur.fetchall()

        cur.close()
        conn.close()

    except Exception as e:
        error = str(e)

    return render_template_string(
        HTML,
        users=users,
        locale=locale,
        seed=seed if 'seed' in locals() else 123,
        batch=batch if 'batch' in locals() else 0,
        batch_size=batch_size if 'batch_size' in locals() else 10,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)