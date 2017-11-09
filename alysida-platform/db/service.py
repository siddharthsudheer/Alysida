#!/usr/bin/env python3
import sqlite3 as lite
import datetime as date

DB_PATH = "./db/my_dbs/"
DB_DOWNLOADS_PATH = DB_PATH + 'downloads/'


def query(dbs, user_query, in_downloads=False):
    try:
        dir_path = DB_DOWNLOADS_PATH if in_downloads else DB_PATH
        db_path = dir_path + dbs + '.db'
        conn = lite.connect(db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(user_query)
                col_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                final_rows = list(map(lambda x: x[0] if len(x) == 1 else x, rows))
                result = False if (len(final_rows) == 0) else {
                    'column_names': col_names, 'rows': final_rows}
                return result
        except lite.Error as e:
            print(e)
        finally:
            conn.close()
    except lite.OperationalError as e:
        print(e)

def post_many(dbs, user_query, ls):
    resp = False
    try:
        db_path = DB_PATH + dbs + '.db'
        conn = lite.connect(db_path)
        try:
            with conn:
                conn.executemany(user_query, ls)
                resp = True
        except lite.Error as e:
            conn.rollback()
            print(e)
    except lite.OperationalError as e:
        print(e)
    finally:
        conn.close()
    return resp


def post(dbs, user_query):
    resp = False
    try:
        db_path = DB_PATH + dbs + '.db'
        conn = lite.connect(db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(user_query)
                conn.commit()
                resp = True
        except lite.Error as e:
            conn.rollback()
            print(e)
    except lite.OperationalError as e:
        print(e)
    finally:
        conn.close()
    return resp


def insert_into(dbs, vals):
    def _peer_addresses(vals):
        return "INSERT INTO peer_addresses (IP) VALUES ('{}')".format(vals)

    def _main_chain(vals):
        return "INSERT INTO main_chain (NONCE, HASH, BLOCK_DATA, TIME_STAMP) VALUES {}".format(vals)

    def _unconfirmed_pool(vals):
        return "INSERT INTO unconfirmed_pool (HASH, TXN_DATA, TIME_STAMP) VALUES {}".format(vals)

    def _my_node_info(vals):
        return "INSERT INTO node_prefs (UUID, IP, PREFERENCES) VALUES {}".format(vals)

    options = {
        'peer_addresses': _peer_addresses(vals),
        'main_chain': _main_chain(vals),
        'unconfirmed_pool': _unconfirmed_pool(vals),
        'node_prefs': _my_node_info(vals)
    }

    return options[dbs]


def get_timestamp():
    timestamp_format = '%Y-%m-%d %H:%M:%S'
    timestamp = date.datetime.now()
    return timestamp.strftime(timestamp_format)


def get_size(dbs, sql_query, in_downloads=False):
    return query(dbs, sql_query, in_downloads=in_downloads)['rows'][0][0]


def compare_dbs(my_db, their_db):
    size_query = "SELECT COUNT(*) FROM {}".format(my_db)
    if get_size(my_db, size_query) > get_size(their_db, size_query, in_downloads=True):
        db1 = DB_PATH + my_db + '.db'
        db2 = DB_DOWNLOADS_PATH + their_db + '.db'
        print("My DB is authoritative.")
    else:
        db1 = DB_DOWNLOADS_PATH + their_db + '.db'
        db2 = DB_PATH + my_db + '.db'
        print("Their DB is authoritative.")

    try:
        conn = lite.connect(db1)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("ATTACH DATABASE '{}' AS db2".format(db2))
                sql_query = """
                    SELECT *
                    FROM peer_addresses as db1
                    WHERE db1.HASH NOT IN
                    (SELECT DISTINCT HASH FROM db2.peer_addresses) 
                """
                cursor.execute(sql_query)
                col_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = False if (len(rows) == 0) else {
                    'column_names': col_names, 'rows': rows}
                return result
        except lite.Error as e:
            print(e)
    except lite.OperationalError as e:
        print(e)
    finally:
        conn.close()
