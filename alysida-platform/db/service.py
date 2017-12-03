#!/usr/bin/env python3
import os
import sqlite3 as lite
import datetime as date
import falcon

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
                resp = False if (len(final_rows) == 0) else {
                    'column_names': col_names, 'rows': final_rows}
        except lite.Error as e:
            print(e)
            resp = e
    except lite.OperationalError as e:
        print(e)
        resp = e
    finally:
        return resp

def post_many(dbs, user_query, ls):
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
            resp = e
    except lite.OperationalError as e:
        print(e)
        resp = e
    finally:
        conn.close()
    return resp


def post(dbs, user_query):
    # resp = False
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
            resp = e
    except lite.OperationalError as e:
        print(e)
        resp = e
    finally:
        conn.close()
    return resp


def insert_into(dbs, vals):
    def _peer_addresses(vals):
        return "INSERT INTO peer_addresses (IP, REGISTRATION_STATUS) VALUES {}".format(vals)

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

def add_new_peer_address(parsed, db_status):
        peer_addrs = list(map(lambda x: (x,), parsed['ips']))
        multi_insert = "INSERT INTO peer_addresses (IP, REGISTRATION_STATUS) VALUES (?, '{}')".format(db_status)
        db_resp = post_many("peer_addresses", multi_insert, peer_addrs)
        
        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
            final_status = falcon.HTTP_500

            msg = {
                'Title': final_title,
                'Message': final_msg
            }
        else:
            # Checking if they already registered earlier but haven't been
            # notified that they were accepted.
            # peer_addrs_2 = tuple(parsed['ips'])
            peer_addrs_2 = str(tuple(parsed['ips'])).replace(",)",")")
            sql_query = "SELECT * FROM peer_addresses WHERE REGISTRATION_STATUS='registered' AND IP IN {}".format(peer_addrs_2)
            query_result = query("peer_addresses", sql_query)

            final_msg = 'Success: Successfully Added'
            final_status = falcon.HTTP_201
            if query_result:
                final_msg = 'Success: Successfully Registered'
                final_status = falcon.HTTP_200
            
            msg = {
                'title': final_msg
            }
        return (msg, final_status)

def get_size(dbs, sql_query, in_downloads=False):
    result = query(dbs, sql_query, in_downloads=in_downloads)
    final = 0 if not result else result['rows'][0]
    return final

# def compare_dbs(my_db, their_db, on_column):
#     size_query = "SELECT COUNT(*) FROM {}".format(my_db)
#     if get_size(my_db, size_query) > get_size(their_db.replace(".db",""), size_query, in_downloads=True):
#         db1 = DB_PATH + my_db + '.db'
#         db2 = DB_DOWNLOADS_PATH + their_db
#         print("My DB is authoritative.")
#     else:
#         db1 = DB_DOWNLOADS_PATH + their_db
#         db2 = DB_PATH + my_db + '.db'
#         print("Their DB is authoritative.")

#     try:
#         conn = lite.connect(db1)
#         try:
#             with conn:
#                 cursor = conn.cursor()
#                 cursor.execute("ATTACH DATABASE '{}' AS db2".format(db2))
#                 sql_query = """
#                     SELECT *
#                     FROM {db_name} as db1
#                     WHERE db1.{column_name} NOT IN
#                     (SELECT DISTINCT {column_name} FROM db2.{db_name}) 
#                 """.format(db_name="peer_addresses", column_name=on_column)
#                 cursor.execute(sql_query)
#                 col_names = [desc[0] for desc in cursor.description]
#                 rows = cursor.fetchall()
#                 result = False if (len(rows) == 0) else {'column_names': col_names, 'rows': rows}
#                 return result
#         except lite.Error as e:
#             print(e)
#     except lite.OperationalError as e:
#         print(e)
#     finally:
#         conn.close()

def ip_db_diff(my_db, their_db):
    my_db_path = DB_PATH + my_db + '.db'
    their_db_path = DB_DOWNLOADS_PATH + their_db
    my_ip = str(query("node_prefs", "SELECT IP FROM node_prefs")['rows'][0])
    try:
        conn = lite.connect(their_db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("ATTACH DATABASE '{}' AS my_db".format(my_db_path))
                sql_query = """
                    SELECT IP
                    FROM peer_addresses as peer
                    WHERE (REGISTRATION_STATUS='registered' OR REGISTRATION_STATUS='registration-pending')
                        AND (
                            IP NOT IN (SELECT IP FROM my_db.peer_addresses)
                            AND
                            IP != '{my_ip_addr}'
                        )
                """.format(my_ip_addr=my_ip)
                cursor.execute(sql_query)
                col_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = False if (len(rows) == 0) else {'column_names': col_names, 'rows': rows}
                return result
        except lite.Error as e:
            print(e)
    except lite.OperationalError as e:
        print(e)
    finally:
        conn.close()
        os.remove(their_db_path)
