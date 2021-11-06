import time
import redis
from flask_bootstrap import Bootstrap
from flask import Flask, render_template_string, render_template, request
import logging

app = Flask(__name__, template_folder='templates')
cache = redis.Redis(host='redis', port=6379)
Bootstrap(app)

logging.basicConfig(filename='/var/log/app.log', level=logging.INFO, 
  format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/', methods = ['GET', 'POST'])
def enter():
    app.logger.info('Processing Default Request')
    count = get_hit_count()
    return render_template('index.html', count=count)

if __name__ == '__main__':
    app.run(debug=True)

