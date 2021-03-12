from flask import Flask
import config

app = Flask(__name__)

import views

if __name__ == '__main__':
    app.run()