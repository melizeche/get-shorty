import os
import json
import config as cfg
import sqlite3 as sq
from getshorty import GetShorty
from urllib.parse import urlparse
from collections import OrderedDict
from user_agents import parse as parse_ua
from flask import Flask, request, Response, redirect

app = Flask('get-shorty')

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, cfg.DATABASE)))

sht = GetShorty(app.config['DATABASE'])


def init_db():
    """ Initialize the DB """
    with sq.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        try:
            with app.open_resource('schema.sql', mode='r') as f:
                cursor.executescript(f.read())
            conn.commit()
        except sq.OperationalError:
            print("Table already created")


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    print('Initializing database.')
    init_db()


def dict_factory(cursor, row):
    """Dictionary factory, uses OrderedDict to preserve the order of the parameters"""
    d = OrderedDict()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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
    if 'url' in params and params['url']:
        url = params['url']
        if not valid_url(url):
            errors.append(cfg.ERROR_URL)
        # Checks if the parameter exists and if isn't empty
        if 'url-mobile' in params and params['url-mobile']:
            mobile_url = params['url-mobile']
            if not valid_url(params['url-mobile']):
                errors.append(cfg.ERROR_MOBILE)
        if 'url-tablet' in params and params['url-tablet']:
            tablet_url = params['url-tablet']
            if not valid_url(params['url-tablet']):
                errors.append(cfg.ERROR_TABLET)
        if not errors:
            shorten = sht.long_to_short(url, mobile_url, tablet_url)
            if not shorten:
                return Response(json.dumps(dict(errors=cfg.ERROR_SERVER)), status=500, mimetype="application/json")
            response_data = OrderedDict(
                shorten="{0}/{1}".format(cfg.HOST, shorten))  # ,
            # url="{}".format(url), mobile=mobile_url, tablet=tablet_url)
            return Response(json.dumps(response_data), status=201, mimetype="application/json")
    else:
        errors.append(cfg.ERROR_MISSING)
    return Response(json.dumps(dict(errors=errors)), status=422, mimetype="application/json")


@app.route('/api/1.0/list', methods=['GET'])
def get_urls():
    """
    Lists all urls with the targets and redirects/hits counter

    :returns: JSON, all the data in the urls table
    :raises: raises an exception if there's a problem with the DB
    """
    query = 'SELECT * from urls;'
    with sq.connect(app.config['DATABASE']) as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                short = row['short']
                row['short'] = '{host}/{short}'.format(
                    host=cfg.HOST, short=row['short'])
            return Response(json.dumps(rows), status=200, mimetype="application/json")
        except:
            return Response(json.dumps(dict(errors=cfg.ERROR_SERVER)), status=500, mimetype="application/json")


@app.route('/<string:urlcode>', methods=['GET'])
def lookup(urlcode):
    """
    Endpoint that recieves the short url and redirects to the long url target
    Case insensitive for better usability

    :param urlcode: The code of the short url
    :returns: redirects to target
    """
    urlcode = urlcode.lower()
    result = sht.short_to_long(urlcode)
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
        sht.hit(urlcode, target)
        return redirect(url)
        return Response(str(result['mobile_url ']))
    return Response('{"error":"URL NOT FOUND"}', status=404, mimetype="application/json")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
