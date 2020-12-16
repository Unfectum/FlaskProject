from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route('/api/v1/hello-world-<numb>')
def my_endpoint(numb):
    return f'Hello World {numb}'


serve(app)  # WAITRESS!

# http://localhost:8080/api/v1/hello-world-11
