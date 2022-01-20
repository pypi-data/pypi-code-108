from flask import Flask
import asyncio 
import random

app = Flask(__name__)

async def long_task():
    await asyncio.sleep(3)
    random_number = random.randint(1, 100)
    with open('/tmp/random.txt', 'w') as f:
        f.write(str(random_number))
    print("long task")

@app.route("/hello")
async def hello():
    task = await asyncio.create_task(long_task())
    return 'world'



if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
