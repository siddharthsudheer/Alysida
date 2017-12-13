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
        db_path =  dir_path + dbs + '.db'
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
    timestamp_format = '%Y-%m-%d %H:%M:%S.%f'
    timestamp = date.datetime.now()
    return timestamp.strftime(timestamp_format)

def add_new_peer_address(parsed, adding_status):
    # When you manually add peers or
    # discover peers the adding_status is 
    # 'unregistered'
    peer = parsed
    peer['status'] = adding_status
    
    #check if already in DB:
    exist_query = "SELECT * FROM peer_addresses WHERE IP = '{}'".format(peer['ip'])
    exist_result = query("peer_addresses", exist_query)

    # they dont exist regardless
    # of adding_status
    if not exist_result:
        vals = "('{}', '{}', '{}')".format(peer['ip'], peer['pub_key'], peer['status'])
        sql = insert_into("peer_addresses", vals)
        db_resp = post("peer_addresses", sql)

        if db_resp:
            return ({"title": "Success: Successfully Added"}, falcon.HTTP_201, )
        else:
            return ({"title": "Failed: Something went wrong"}, falcon.HTTP_500)
    
    else:
        if adding_status == 'unregistered':
            return ({"title": "Success: Successfully Added"}, falcon.HTTP_201)
        else:
            #check if they were approved as 'registered' or not
            db_ip, db_pk, db_stat = exist_result['rows'][0]
            if db_stat == "registered":
                return ({"title": "Success: Successfully Registered"}, falcon.HTTP_201)

            elif db_stat == "unregistered":
                update_query = """
                UPDATE peer_addresses 
                SET PUBLIC_KEY = '{}', REGISTRATION_STATUS = 'acceptance-pending' 
                WHERE REGISTRATION_STATUS = 'unregistered' AND IP = '{}'""".format(peer['pub_key'], str(db_ip))
                db_resp = post("peer_addresses", update_query)
                return ({"title": "Success: Successfully Added"}, falcon.HTTP_201)
            
            elif db_stat == "acceptance-pending":
                return ({"title": "Wait: Yet to be accepted."}, falcon.HTTP_201)

            else:
                return ("Unauthorized", falcon.HTTP_401)


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

# def get_size(dbs, sql_query, in_downloads=False):
#     result = query(dbs, sql_query, in_downloads=in_downloads)
#     final = 0 if not result else result['rows'][0]
#     return final

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


