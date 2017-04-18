import json
import sqlite3 as sq
from flask import Flask, request, Response, jsonify
from urllib.parse import urlparse
from user_agents import parse as parse_ua
from baseconv import base36

app = Flask(__name__)


def create_table():
    query = """
        create table urls (
            id integer primary key autoincrement,
            short text unique not null,
            default_url text not null,
            mobile_url text,
            tablet_url text,
            created datetime default current_timestamp
        );"""
    with sq.connect('getshorty.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except sq.OperationalError:
            print("Table already created")


def get_max_id():
    query = """
        SELECT MAX(id) from urls;
        """
    with sq.connect('getshorty.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            print(result)
            print(type(result))
            if result==None:
                max_id=0
            print(max_id)
            print(type(max_id))
        except sq.OperationalError:
            print("Error!")


def valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return True
    return False


@app.route('/api/1.0/create', methods=['POST'])
def test():
    url, mobile_url, tablet_url = None, None, None
    errors = []
    params = request.get_json(force=True)
    # ua = request.headers.get('User-Agent')
    # print(ua)
    print(params)
    if 'url' in params and params['url']:
        url = params['url']
        if not valid_url(url):
            errors.append(
                {'detail': 'Invalid url, make sure to add the protocol e.g. http://'})
        if 'url-mobile' in params and params['url-mobile']:
            mobile_url = params['url-mobile']
            if not valid_url(params['url-mobile']):
                errors.append({'detail': 'Invalid url url-mobile'})
            print(mobile_url)
        if 'url-tablet' in params and params['url-tablet']:
            tablet_url = params['url-tablet']
            if not valid_url(params['url-tablet']):
                errors.append({'detail': 'Invalid url url-tablet'})
            print(tablet_url)
        print(url, mobile_url, tablet_url)
        if not errors:
            return Response("{0} {1} {2}".format(url, mobile_url, tablet_url), status=201)
    else:
        errors.append({'detail': 'Missing url parameter'})
    return Response(json.dumps(dict(errors=errors)), status=422, mimetype="application/json")


def get_urls():
    pass


def long_to_short(url):

    pass


def short_to_long(urlcode):
    pass

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
