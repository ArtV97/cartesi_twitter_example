import sqlite3
from sqlite3 import Error
from hashlib import sha256

DATABASE_PATH = "./"

#######################################################
### :desc: create a database connection to the SQLite
###        database specified by db_file.
### :param db_file: database file
### :return: Connection object or None
#######################################################
def create_connection(db_file):
    conn = None
    db_file = DATABASE_PATH + "/" + db_file
    try:
        conn = sqlite3.connect(db_file)
        create_database(db_file, conn)
        return conn
    except Error as e:
        print(e)

    return conn


#######################################################
### :desc: create database and database file if it not
###        exists.
### :param database: file
### :param conn: Connection object
### :return: None
#######################################################
def create_database(database, conn = None):
    # TABLES SQL
    user_table = """ CREATE TABLE IF NOT EXISTS user (
                                username VARCHAR(20),
                                password VARCHAR(64) NOT NULL,
                                join_date DATE NOT NULL,

                                CONSTRAINT PK_user PRIMARY KEY (username)
                            ); """


    tweet_table = """ CREATE TABLE IF NOT EXISTS tweet (
                                tweet_id INTEGER,
                                username VARCHAR(20) NOT NULL,
                                msg VARCHAR(280) NOT NULL,
                                timestamp DATE NOT NULL,
                                likes INTEGER DEFAULT 0,
                                retweets INTEGER DEFAULT 0,
                                replies INTEGER DEFAULT 0,

                                CONSTRAINT PK_tweet PRIMARY KEY (tweet_id),
                                CONSTRAINT FK_tweet_user FOREIGN KEY (username) REFERENCES user(username)
                            ); """


    like_table = """ CREATE TABLE IF NOT EXISTS like (
                                tweet_id INTEGER NOT NULL,
                                username VARCHAR(20) NOT NULL,

                                CONSTRAINT PK_like PRIMARY KEY (tweet_id, username),
                                CONSTRAINT FK0_like_tweet FOREIGN KEY (tweet_id) REFERENCES tweet(tweet_id),
                                CONSTRAINT FK1_like_user FOREIGN KEY (username) REFERENCES user(username)
                            ); """


    # retweets are tweets too
    retweet_table = """ CREATE TABLE IF NOT EXISTS retweet (
                                retweet_id INTEGER NOT NULL,
                                tweet_id INTEGER NOT NULL,

                                CONSTRAINT PK_retweet PRIMARY KEY (retweet_id, tweet_id),
                                CONSTRAINT FK0_retweet_tweet FOREIGN KEY (retweet_id) REFERENCES tweet(tweet_id),
                                CONSTRAINT FK1_retweet_tweet FOREIGN KEY (tweet_id) REFERENCES tweet(tweet_id)
                            ); """   


    # replies are "tweets" too
    reply_table = """ CREATE TABLE IF NOT EXISTS reply (
                                reply_id INTEGER NOT NULL,
                                tweet_id INTEGER NOT NULL,

                                CONSTRAINT PK_reply PRIMARY KEY (reply_id, tweet_id),
                                CONSTRAINT FK0_reply_tweet FOREIGN KEY (reply_id) REFERENCES tweet(tweet_id),
                                CONSTRAINT FK1_reply_tweet FOREIGN KEY (tweet_id) REFERENCES tweet(tweet_id)
                            ); """


    # TRIGGERS SQL
    like_upd_trigger = ''' CREATE TRIGGER IF NOT EXISTS like_update
        AFTER INSERT ON like
        BEGIN
            UPDATE tweet SET likes = likes + 1 WHERE tweet.tweet_id = NEW.tweet_id;
        END;
    '''

    like_del_trigger = ''' CREATE TRIGGER IF NOT EXISTS like_delete
        AFTER DELETE ON like
        BEGIN
            UPDATE tweet SET likes = likes - 1 WHERE tweet.tweet_id = OLD.tweet_id;
        END;
    '''

    retweet_upd_trigger = ''' CREATE TRIGGER IF NOT EXISTS retweet_update
        AFTER INSERT ON retweet
        BEGIN
            UPDATE tweet SET retweets = retweets + 1 WHERE tweet.tweet_id = NEW.tweet_id;
        END;
    '''

    retweet_del_trigger = ''' CREATE TRIGGER IF NOT EXISTS retweet_delete
        AFTER DELETE ON retweet
        BEGIN
            UPDATE tweet SET retweets = retweets - 1 WHERE tweet.tweet_id = OLD.tweet_id;
        END;
    '''

    reply_upd_trigger = ''' CREATE TRIGGER IF NOT EXISTS reply_update
        AFTER INSERT ON reply
        BEGIN
            UPDATE tweet SET replies = replies + 1 WHERE tweet.tweet_id = NEW.tweet_id;
        END;
    '''

    reply_del_trigger = ''' CREATE TRIGGER IF NOT EXISTS reply_delete
        AFTER DELETE ON reply
        BEGIN
            UPDATE tweet SET replies = replies - 1 WHERE tweet.tweet_id = OLD.tweet_id;
        END;
    '''

    close_at_end = False
    # create a database connection
    if conn is None:
        conn = create_connection(database)
        close_at_end = True

    # create tables
    if conn is not None:
        cur = conn.cursor()

        # CREATE TABLES
        cur.execute(user_table)
        cur.execute(tweet_table)
        cur.execute(like_table)
        cur.execute(retweet_table)
        cur.execute(reply_table)

        # CREATE TRIGGERS
        cur.execute(like_upd_trigger)
        cur.execute(like_del_trigger)
        cur.execute(retweet_upd_trigger)
        cur.execute(retweet_del_trigger)
        cur.execute(reply_upd_trigger)
        cur.execute(reply_del_trigger)

        if close_at_end: conn.close()
    else:
        print("Error! cannot create the database connection.")


###################################################################
#                                                                 #
#                            INSERTS                              #
#                                                                 #
###################################################################
def create_user(conn, username, password, join_date):
    password = sha256(password.encode()).hexdigest()

    sql = ''' INSERT INTO user(username, password, join_date)
            VALUES(?, ?, ?) '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (username, password, join_date))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False
    
    return True


def create_tweet(conn, username, msg, timestamp):
    sql = ''' INSERT INTO tweet(username, msg, timestamp)
            VALUES(?, ?, ?) '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (username, msg, timestamp))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False
    
    # return lastrowid which is the most recent tweet_id
    return cur.lastrowid


def create_like(conn, tweet_id, username):
    sql = ''' INSERT INTO like(tweet_id, username)
            VALUES(?, ?) '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (tweet_id, username))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False
    
    return True


def create_retweet(conn, retweet_id, tweet_id):
    sql = ''' INSERT INTO retweet(retweet_id, tweet_id)
            VALUES(?, ?) '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (retweet_id, tweet_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False
    
    return True


def create_reply(conn, reply_id, tweet_id):
    sql = ''' INSERT INTO reply(reply_id, tweet_id)
            VALUES(?, ?) '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (reply_id, tweet_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False
    
    return True


def generate_retweet(conn, tweet_id, username, timestamp, quote=""):
    try:
        # the reply is a tweet too
        reply_id = create_tweet(conn, username, quote, timestamp)
        create_retweet(conn, reply_id, tweet_id)
    except Error as e:
        print(e)
        return False
    
    return True



def generate_reply(conn, tweet_id, username, timestamp, msg):
    try:
        # the reply is a tweet too
        reply_id = create_tweet(conn, username, msg, timestamp)
        create_reply(conn, reply_id, tweet_id)
    except Error as e:
        print(e)
        return False
    
    return True


###################################################################
#                                                                 #
#                            QUERIES                              #
#                                                                 #
###################################################################
def get_users(conn):
    sql = ''' SELECT * FROM user '''
    cur = conn.cursor()

    try:
        cur.execute(sql)
    except:
        return False
    
    return cur.fetchall()


def get_tweets(conn):
    sql = ''' SELECT * FROM tweet '''
    cur = conn.cursor()

    try:
        cur.execute(sql)
    except:
        return False
    
    return cur.fetchall()


def get_likes(conn):
    sql = ''' SELECT * FROM like '''
    cur = conn.cursor()

    try:
        cur.execute(sql)
    except:
        return False
    
    return cur.fetchall()


def get_retweets(conn):
    sql = ''' SELECT * FROM retweet '''
    cur = conn.cursor()

    try:
        cur.execute(sql)
    except:
        return False
    
    return cur.fetchall()


def get_replies(conn):
    sql = ''' SELECT * FROM reply '''
    cur = conn.cursor()

    try:
        cur.execute(sql)
    except:
        return False
    
    return cur.fetchall()
  

def get_user_tweets(conn, username):
    sql = ''' SELECT * FROM tweet WHERE username = ? '''
    cur = conn.cursor()

    try:
        cur.execute(sql, (username,))
    except:
        return False
    
    return cur.fetchall()


# Get likes of a given tweet
def get_tweet_likes(conn, tweet_id):
    sql = ''' SELECT username FROM like WHERE tweet_id = ? '''

    cur = conn.cursor()

    try:
        cur.execute(sql, (tweet_id,))
    except Exception as e:
        print(e)
        return False
    
    return list(map(lambda x: x[0], cur.fetchall()))


# Get retweets of a given tweet
def get_tweet_retweets(conn, tweet_id):
    sql = ''' SELECT * FROM tweet WHERE tweet_id IN
            (SELECT retweet_id FROM retweet WHERE retweet.tweet_id = ?) '''

    cur = conn.cursor()

    try:
        cur.execute(sql, (tweet_id,))
    except Exception as e:
        print(e)
        return False
    
    return cur.fetchall()


# Get replies of a given tweet
def get_tweet_replies(conn, tweet_id):
    sql = ''' SELECT * FROM tweet WHERE tweet_id IN
            (SELECT reply_id FROM reply WHERE reply.tweet_id = ?) '''

    cur = conn.cursor()

    try:
        cur.execute(sql, (tweet_id,))
    except Exception as e:
        print(e)
        return False
    
    return cur.fetchall()


def get_user_tweets(conn, username):
    sql = ''' SELECT * FROM tweet WHERE username = ? '''

    cur = conn.cursor()

    try:
        cur.execute(sql, (username,))
    except Exception as e:
        print(e)
        return False
    
    return cur.fetchall()


###################################################################
#                                                                 #
#                              AUX                                #
#                                                                 #
###################################################################
def user_login(conn, username, password):
    sql = ''' SELECT * FROM user WHERE username = ? AND password = ? '''
    cur = conn.cursor()

    password = sha256(password.encode()).hexdigest()
    try:
        cur.execute(sql, (username, password))
    except:
        return False
    
    return cur.fetchone()


if __name__ == "__main__":
    create_database("twitter.db")
    
    conn = create_connection("twitter.db")
    
    # create users
    create_user(conn, "User 1", "1234", "11/16/2022 12:10:13")
    create_user(conn, "User 2", "1234", "11/16/2022 12:11:13")
    create_user(conn, "User 3", "1234", "11/16/2022 12:12:13")
    create_user(conn, "User 4", "1234", "11/16/2022 12:13:13")
    create_user(conn, "User 5", "1234", "11/16/2022 12:14:13")

    # create tweets
    create_tweet(conn, "User 1", "Tweet Test 1", "11/16/2022 12:10:13")
    create_tweet(conn, "User 1", "Tweet Test 2", "11/16/2022 12:10:16")
    create_tweet(conn, "User 2", "Tweet Test 3", "11/16/2022 12:10:19")
    create_tweet(conn, "User 3", "Tweet Test 4", "11/16/2022 12:10:22")
    create_tweet(conn, "User 4", "Tweet Test 5", "11/16/2022 12:10:25")
    create_tweet(conn, "User 4", "Tweet Test 6", "11/16/2022 12:10:28")
    create_tweet(conn, "User 5", "Tweet Test 7", "11/16/2022 12:10:31")

    # create likes
    create_like(conn, 2, "User 1") # User 1 liked tweet 2
    create_like(conn, 2, "User 3") # User 1 liked tweet 2
    create_like(conn, 2, "User 5") # User 1 liked tweet 2
    create_like(conn, 1, "User 2") # User 1 liked tweet 2
    create_like(conn, 3, "User 4") # User 1 liked tweet 3

    # create retweets
    generate_retweet(conn, 3, "User 4", "11/16/2022 18:37:13", "User 4 quoted tweet 3 in his retweet")
    generate_retweet(conn, 2, "User 1", "11/16/2022 18:38:13")
    generate_retweet(conn, 4, "User 5", "11/16/2022 18:39:13", "User 5 quoted tweet 4 in his retweet")

    # create replies
    generate_reply(conn, 1, "User 2", "11/16/2022 12:11:13", "User 2 Replying Tweet 1")
    generate_reply(conn, 4, "User 1", "11/16/2022 12:11:22", "User 1 Replying Tweet 4")
    generate_reply(conn, 4, "User 3", "11/16/2022 12:12:22", "User 3 Replying Tweet 4")
    generate_reply(conn, 2, "User 5", "11/16/2022 12:15:16", "User 5 Replying Tweet 2")
    generate_reply(conn, 6, "User 4", "11/16/2022 12:16:28", "User 4 Replying Tweet 6")

    conn.close()