import mysql.connector

def mysql_connect(host: str, user: str, password: str, database: str):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor()
    return cursor, connection

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://chat.openai.com", "https://0d94-112-154-110-15.ngrok-free.app"],
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True
)

from fastapi import Request
import json

@app.post('/api/query')
async def query(request: Request):
    print("request body:", json.dumps(request.json(), indent=4))
    try:
        body = await request.json()
        cursor, connection = mysql_connect(
            body.get('host'),
            body.get('user'),
            body.get('password'),
            body.get('database')
        )
        query = body.get('query')
        cursor.execute(query)
        query_result = cursor.fetchall()

        # Normalize and prepare the result
        result = []
        column_names = [column[0] for column in cursor.description]
        for row in query_result:
            row_dict = {}
            for i in range(len(column_names)):
                row_dict[column_names[i]] = row[i]
            result.append(row_dict)

        cursor.close()
        connection.close()
        return {'result': result}
    except Exception as e:
        return {'error': e.msg}

import os
from fastapi.responses import FileResponse

@app.get('/openapi.json')
def get_openapi():
    file_path = os.path.join(os.getcwd(), 'openapi.json')
    return FileResponse(file_path, media_type='application/json')

if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=4000)
