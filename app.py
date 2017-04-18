import json
import sqlite3 as sq
from flask import Flask, request, Response, jsonify, redirect
from urllib.parse import urlparse
from user_agents import parse as parse_ua
from baseconv import base36

app = Flask(__name__)
HOST = 'http://localhost:5000'


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
            max_id = 0 if result[0] == None else result[0]
            print(max_id)
            print(type(max_id))
            return max_id + 1
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
            shorten = long_to_short(url, mobile_url, tablet_url)
            if not shorten:
                return Response(json.dumps(dict(errors='Server Error')), status=500, mimetype="application/json")
            response_data = dict(shorten="{0}/{1}".format(HOST, shorten),
                                 url="{}".format(url), mobile=mobile_url, tablet=tablet_url)
            return Response(json.dumps(response_data), status=201, mimetype="application/json")
    else:
        errors.append({'detail': 'Missing url parameter'})
    return Response(json.dumps(dict(errors=errors)), status=422, mimetype="application/json")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/api/1.0/list', methods=['GET'])
def get_urls():
    query = 'SELECT * from urls;'
    print(query)
    with sq.connect('getshorty.sqlite3') as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            print("AAAAAA")
            for row in rows:
                short = row['short']
                row['short'] = '{host}/{short}'.format(host=HOST,short=row['short'])
            return Response(json.dumps(rows), status=200, mimetype="application/json")
        except:
            return Response(json.dumps(dict(errors='Server Error')), status=500, mimetype="application/json")


def long_to_short(url, url_mobile=None, url_tablet=None):
    url_id = get_max_id()
    print(url_id)
    based_id = base36.encode(url_id)
    print(based_id)
    query = 'INSERT into urls(short,default_url,mobile_url,tablet_url) VALUES ("{short}","{url}","{mobile}","{tablet}");'.\
        format(short=based_id, url=url, mobile=url_mobile, tablet=url_tablet)
    print(query)
    with sq.connect('getshorty.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return based_id
        except sq.OperationalError:
            print("ERROR")
            return False


def short_to_long(urlcode):
    query = 'SELECT * from urls where short="{short}";'.format(short=urlcode)
    print(query)
    with sq.connect('getshorty.sqlite3') as conn:
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        # try:
        cursor.execute(query)
        row = cursor.fetchone()
        print("AAAAAA")
        #print(row)
        return row
        # except:
        #     print("ERROR")


@app.route('/<string:urlcode>', methods=['GET'])
def lookup(urlcode):
    print(urlcode)
    result = short_to_long(urlcode)
    print(type(result))
    if result:
        url = result['default_url']
        ua = parse_ua(request.headers.get('User-Agent'))
        print(ua, ua.is_mobile, ua.is_tablet)
        print(result.keys())
        print(result['mobile_url'])
        print('true' if 'mobile_url' in result else 'false')
        if result['mobile_url'] and ua.is_mobile:
            url = result['mobile_url']
        elif result['tablet_url'] and ua.is_tablet:
            url = result['tablet_url']
        print(url)
        return redirect(url)
        return Response(str(result['mobile_url ']))
    return Response("URL NOT FOUND", status=404)


if __name__ == '__main__':
    create_table()
    # print(get_max_id())
    app.run(debug=True)
