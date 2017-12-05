#!/usr/bin/env python3
import os
import json
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
                cursor.execute("PRAGMA foreign_keys = ON;")
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

def post_many(dbs, user_query, ls=None):
    try:
        db_path = DB_PATH + dbs + '.db'
        conn = lite.connect(db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                if ls == None:
                    cursor.executescript(user_query)
                else:
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
                cursor.execute("PRAGMA foreign_keys = ON;")
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
    if dbs == "peer_addresses": 
        return "INSERT INTO peer_addresses (IP, PUBLIC_KEY, REGISTRATION_STATUS) VALUES {}".format(vals)

    elif dbs == "main_chain":
        block_hash, nonce, time_stamp, txns = vals
        txn_inserts = list()
        main_chain = "INSERT INTO main_chain (BLOCK_NUM, BLOCK_HASH, NONCE, TIME_STAMP) VALUES (NULL,'{}',{},'{}');".format(block_hash, nonce, time_stamp)
        for txn in txns:
            ins_vals = (block_hash, txn['hash'], txn['txn_data']['sender'], txn['txn_data']['receiver'], txn['txn_data']['amount'], txn['time_stamp'])
            ins = "INSERT INTO confirmed_txns (BLOCK_HASH, TXN_HASH, sender, receiver, amount, TXN_TIME_STAMP) VALUES {};".format(ins_vals)
            txn_inserts.append(ins)
        confirmed_txns = '{}'.format(''.join(map(str, txn_inserts))) 
        final = main_chain + "\n" + confirmed_txns
        print(final)
        return final

    elif dbs == "unconfirmed_pool": 
        txn_hash, sender, recv, amt, time_stamp = vals
        transaction_recs = "INSERT INTO transaction_recs (HASH, sender, receiver, amount) VALUES {};".format((txn_hash, sender, recv, amt))
        unconfirmed_pool = "INSERT INTO unconfirmed_pool (HASH, TIME_STAMP) VALUES {};".format((txn_hash, time_stamp))
        final = transaction_recs + "\n" + unconfirmed_pool
        return final

    elif dbs == "node_prefs": 
        return "INSERT INTO node_prefs (UUID, IP, PREFERENCES) VALUES {}".format(vals)


def get_timestamp():
    timestamp_format = '%Y-%m-%d %H:%M:%S'
    timestamp = date.datetime.now()
    return timestamp.strftime(timestamp_format)


def add_new_peer_address(parsed, db_status):
        if db_status == 'acceptance-pending':
            peer_addrs = list(map(lambda x: (x[0],x[1]), parsed['ips']))
        else:
            peer_addrs = list(map(lambda x: (x,'unregistered'), parsed['ips']))
        
        multi_insert = "INSERT INTO peer_addresses (IP, PUBLIC_KEY, REGISTRATION_STATUS) VALUES (?, ?, '{}')".format(db_status)
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
            if db_status == 'acceptance-pending':
                just_ips = list(map(lambda x: x[0], parsed['ips']))
                peer_addrs_2 = str(tuple(just_ips)).replace(",)",")")
            else:
                peer_addrs_2 = str(tuple(parsed['ips'])).replace(",)",")")
            sql_query = "SELECT * FROM peer_addresses WHERE REGISTRATION_STATUS='registered' AND IP IN {}".format(peer_addrs_2)
            query_result = query("peer_addresses", sql_query)
            print(query_result)

            if query_result:
                final_msg = 'Success: Successfully Registered'
                final_status = falcon.HTTP_200
            else:
                final_msg = 'Success: Successfully Added'
                final_status = falcon.HTTP_201

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


def add_txn_to_db(txn_record_vals):
    insert_sql = insert_into("unconfirmed_pool", txn_record_vals)
    db_resp = post_many("unconfirmed_pool", insert_sql)

    if db_resp != True:
        final_title = 'Error'
        final_msg = db_resp
        resp_status = falcon.HTTP_400
    else:
        final_title = 'Success'
        final_msg = 'New transaction successfully added to DB.'
        resp_status = falcon.HTTP_201
    
    return (final_title, final_msg, resp_status)