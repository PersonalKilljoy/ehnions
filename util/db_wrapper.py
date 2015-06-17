import MySQLdb  # apt-get install python-MySQLdb

# Simple mysql wrapper
# Should be used with 'with' keyword to ensure proper initialization and closure of database


class DataBs:
    def __init__(self):
        try:
            sslopts = {'cert': '/opt/mysql/newcerts/client-cert.pem', 'key': '/opt/mysql/newcerts/client-key.pem'}
            self.dbconnection = MySQLdb.connect(user='mysql', passwd='TOPKEK', db='scandb', unix_socket='/var/run/mysqld/mysqld.sock', ssl=sslopts)
            self.dbcursor = self.dbconnection.cursor()
        except Exception as e:
            if self.dbcursor is not None:
                self.dbcursor.close()
            if self.dbconnection is not None:
                self.dbconnection.close()
            raise e

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.dbconnection.commit()
        self.dbcursor.close()
        self.dbconnection.close()

    def add_onion(self, data):
        add_onion = """INSERT INTO tblCollectedOnions
                                        (onion_addr, source)
                                        VALUES(%s, %s)"""
        self.dbcursor.execute(add_onion, data)
        self.dbconnection.commit()

    def select_scannable(self):
        query = ("SELECT DISTINCT tco.onion_addr from tblCollectedOnions AS tco WHERE tco.onion_addr NOT IN (SELECT DISTINCT tos.onion_addr FROM tblOnionScan AS tos) ORDER BY tco.onion_addr")
        self.dbcursor.execute(query)
        return self.dbcursor.fetchall()

    def add_onion_scan(self, data):
        add_onionscan = """INSERT INTO tblOnionScan
                                        (onion_addr, working, contents,title,sha1_hash)
                                        VALUES(%s, %s, %s,%s,%s)"""
        self.dbcursor.execute(add_onionscan, data)
        self.dbconnection.commit()