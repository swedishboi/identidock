from flask import Flask, Response, request
import requests
import hashlib
import redis

app = Flask(__name__)
cache = redis.StrictRedis(host='redis', port=6379, db=0)

default_name = 'Joe Bloggs'
salt = 'UNIQUE_SALT'

def get_page_for(name, hash):
    header = '<html><head><title>Identidock</title></head><body>'
    body = '''<form method="POST">
    Hello <input type="text" name="name" value="{0}">
    <input type="submit" value="submit">
    </form>
    <p>You look like a:
    <img src="/monster/{1}"/>
    '''.format(name, hash)
    footer = '</body></html>'

    return header + body + footer

def get_name_from_form():
    return request.form['name']

def hash_name(name):
    salted_name = name + salt
    return hashlib.sha256(salted_name.encode()).hexdigest()


@app.route('/', methods=['GET', 'POST'])
def home():
    name = default_name

    if request.method == 'POST':
        name = get_name_from_form()

    hash = hash_name(name)

    return get_page_for(name, hash)


@app.route('/monster/<name>')
def get_identicon(name):
    image = cache.get(name)

    if image is None:
        print('Cache miss ' + name, flush=True)
        r = requests.get('http://dnmonster:8080/monster/' + name + '?size=80')
        image = r.content
        cache.set(name, image)

    return Response(image, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
