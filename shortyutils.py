from baseconv import base36
import sqlite3 as sq


class GetShorty:

    def __init__(self, database):
        self.DB = database

    def get_max_id(self):
        """
        Get the max id in the DB to be able to encode the next one.

        :returns: the value+1 of the last autoincremented id
        :raises OperationalError: raises an exception if there's a problem with the DB
        """

        query = """
            SELECT MAX(id) from urls;
            """
        with sq.connect(self.DB) as conn:
            conn.row_factory = sq.Row
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                max_id = 0 if result[0] == None else result[0]
                return max_id + 1
            except sq.OperationalError:
                print("Error!")

    def hit(self, urlcode, target):
        """
        Sum +1 to the redirects/hits counter in the db

        :param urlcode: the shorten urlcode
        :param target: the target choosen for add 1 hit to the counter
        :returns: True if was succesful, otherwise False
        :raises OperationalError: raises an exception if there's a problem with the DB
        """
        column = dict(default='default_hits',
                      mobile='mobile_hits', tablet='tablet_hits')
        query = 'UPDATE urls SET {target_hits} = {target_hits} + 1 WHERE short = "{urlcode}";'.\
            format(target_hits=column[target], urlcode=urlcode)
        with sq.connect(self.DB) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                return True
            except sq.OperationalError:
                print("ERROR")
                return False

    def long_to_short(self, url, url_mobile=None, url_tablet=None):
        """
        Create a code for the shortened url and inserts in the DB along with the targets 
        Uses base36 enconding so only numbers and lowercase characters for better usability

        :param url: The default url to be shorten, target=Desktop/default  
        :param url_mobile: [Optional] The url to redirect if the client is a mobile device 
        :param url_tablet: [Optional] The url to redirect if the client is a tablet
        :returns: String, base_id=the short code 
        :raises OperationalError: raises an exception if there's a problem with the DB
        """
        url_id = self.get_max_id()
        try:
            based_id = base36.encode(url_id)
        except ValueError:
            return False

        query = 'INSERT into urls(short,default_url,mobile_url,tablet_url) VALUES ("{short}","{url}","{mobile}","{tablet}");'.\
            format(short=based_id, url=url,
                   mobile=url_mobile, tablet=url_tablet)
        with sq.connect(self.DB) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                return based_id
            except sq.OperationalError:
                print("ERROR")
                return False

    def short_to_long(self, urlcode):
        """
        Get the the long url, targets and data for the urlcode provided.

        :param urlcode: the code for the shorten url
        :returns: sqlite.Row, DB row
        :raises: raises an exception if there's a problem with the DB
        """
        query = 'SELECT * from urls where short="{short}";'.format(
            short=urlcode)
        with sq.connect(self.DB) as conn:
            conn.row_factory = sq.Row
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                return row
            except:
                return False
