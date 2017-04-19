import json
import sqlite3 as sq
from collections import OrderedDict
from flask import Flask, request, Response, redirect
from urllib.parse import urlparse
from user_agents import parse as parse_ua
from baseconv import base36

app = Flask(__name__)
HOST = 'http://localhost:5000'


def create_table():
    """ Initialize the DB """
    query = """
        create table urls (
            id integer primary key autoincrement,
            short text unique not null,
            default_url text not null,
            default_hits integer default 0,
            mobile_url text,
            mobile_hits integer default 0,
            tablet_url text,
            tablet_hits integer default 0,
            created datetime default current_timestamp
        );"""
    with sq.connect('getshorty.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except sq.OperationalError:
            print("Table already created")


def get_max_id():
    """
    Get the max id in the DB to be able to encode the next one.

    :returns: the value+1 of the last autoincremented id
    :raises OperationalError: raises an exception if there's a problem with the DB
    """
    query = """
        SELECT MAX(id) from urls;
        """
    with sq.connect('getshorty.sqlite3') as conn:
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            print('{}'.format(result))
            print(type(result))
            max_id = 0 if result[0] == None else result[0]
            return max_id + 1
        except sq.OperationalError:
            print("Error!")


def dict_factory(cursor, row):
    """Dictionary factory, uses OrderedDict to preserve the order of the parameters"""
    d = OrderedDict()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def hit(urlcode, target):
    """
    Sum +1 to the redirects/hits counter in the db

    :param urlcode: the shorten urlcode
    :param target: the target choosen for add 1 hit to the counter
    :returns: True if was succesful, otherwise False
    :raises OperationalError: raises an exception if there's a problem with the DB
    """
    column = dict(default='default_hits',
                  mobile='mobile_hits', tablet='tablet_hits')
    query = 'UPDATE urls SET {target_hits} = {target_hits} + 1 WHERE short = {urlcode};'.\
            format(target_hits=column[target], urlcode=urlcode)
    print(query)
    with sq.connect('getshorty.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return True
        except sq.OperationalError:
            print("ERROR")
            return False


def valid_url(url):
    """
    Validates that the url provided is in a valid format.

    :param url: an url
    :returns: True if it is a valid url, False otherwise
    :raises OperationalError: raises an exception if there's a problem with the DB
    """
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return True
    return False


@app.route('/api/1.0/create', methods=['POST'])
def create():
    """
    Endpoint to create a short url and optional specify some targets(mobile, tablet) 

    :param url: The default url to be shorten, target=Desktop/default  
    :param url-mobile: [Optional] The url to redirect if the client is a mobile device 
    :param url-tablet: [Optional] The url to redirect if the client is a tablet
    :returns: JSON, params = shorten, url , mobile, tablet
    :raises OperationalError: raises an exception if there's a problem with the DB
    """
    url, mobile_url, tablet_url = None, None, None
    errors = []
    params = request.get_json(force=True)
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
        if 'url-tablet' in params and params['url-tablet']:
            tablet_url = params['url-tablet']
            if not valid_url(params['url-tablet']):
                errors.append({'detail': 'Invalid url url-tablet'})
        if not errors:
            shorten = long_to_short(url, mobile_url, tablet_url)
            if not shorten:
                return Response(json.dumps(dict(errors='Server Error')), status=500, mimetype="application/json")
            response_data = OrderedDict(shorten="{0}/{1}".format(HOST, shorten),
                                        url="{}".format(url), mobile=mobile_url, tablet=tablet_url)
            return Response(json.dumps(response_data), status=201, mimetype="application/json")
    else:
        errors.append({'detail': 'Missing url parameter'})
    return Response(json.dumps(dict(errors=errors)), status=422, mimetype="application/json")


@app.route('/api/1.0/list', methods=['GET'])
def get_urls():
    """
    Lists all urls with the targets and redirects/hits counter

    :returns: JSON, all the data in the urls table
    :raises: raises an exception if there's a problem with the DB
    """
    query = 'SELECT * from urls;'
    with sq.connect('getshorty.sqlite3') as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                short = row['short']
                row['short'] = '{host}/{short}'.format(
                    host=HOST, short=row['short'])
            return Response(json.dumps(rows), status=200, mimetype="application/json")
        except:
            return Response(json.dumps(dict(errors='Server Error')), status=500, mimetype="application/json")


def long_to_short(url, url_mobile=None, url_tablet=None):
    """
    Create a code for the shortened url and inserts in the DB along with the targets 
    Uses base36 enconding so only numbers and lowercase characters for better usability

    :param url: The default url to be shorten, target=Desktop/default  
    :param url_mobile: [Optional] The url to redirect if the client is a mobile device 
    :param url_tablet: [Optional] The url to redirect if the client is a tablet
    :returns: String, base_id=the short code 
    :raises OperationalError: raises an exception if there's a problem with the DB
    """
    url_id = get_max_id()
    based_id = base36.encode(url_id)
    query = 'INSERT into urls(short,default_url,mobile_url,tablet_url) VALUES ("{short}","{url}","{mobile}","{tablet}");'.\
        format(short=based_id, url=url, mobile=url_mobile, tablet=url_tablet)
    with sq.connect('getshorty.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return based_id
        except sq.OperationalError:
            print("ERROR")
            return False


def short_to_long(urlcode):
    """
    Get the the long url, targets and data for the urlcode provided.

    :param urlcode: the code for the shorten url  
    :returns: sqlite.Row, DB row
    :raises: raises an exception if there's a problem with the DB
    """
    query = 'SELECT * from urls where short="{short}";'.format(short=urlcode)
    with sq.connect('getshorty.sqlite3') as conn:
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            row = cursor.fetchone()
            return row
        except:
            return False


@app.route('/<string:urlcode>', methods=['GET'])
def lookup(urlcode):
    """
    Endpoint that recieves the short url and redirects to the long url target
    Case insensitive for better usability 

    :param urlcode: The code of the short url  
    :returns: redirects to target
    """
    urlcode = urlcode.lower()
    result = short_to_long(urlcode)
    print(type(result))
    if result:
        url = result['default_url']
        target = 'default'
        ua = parse_ua(request.headers.get('User-Agent'))
        if result['mobile_url'] and ua.is_mobile:
            url = result['mobile_url']
            target = 'mobile'
        elif result['tablet_url'] and ua.is_tablet:
            url = result['tablet_url']
            target = 'tablet'
        hit(urlcode, target)
        return redirect(url)
        return Response(str(result['mobile_url ']))
    return Response("URL NOT FOUND", status=404)


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
