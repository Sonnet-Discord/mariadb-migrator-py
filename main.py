import migration_libs.lib_sql_handler as lib_sql_handler
import migration_libs.lib_mdb_handler as lib_mdb_handler
from migration_libs.lib_loaders import generate_infractionid

import glob, getpass, mariadb, random, string, json

def initialize_login():
    print('Make sure you have a MariaDB server ready!')
    
    # Get root login
    host = input('MariaDB IP Address (127.0.0.1): ') or "127.0.0.1"
    port = input('MariaDB Service Port (3306): ') or "3306"
    db_name = input('MariaDB Database Name (sonnet): ') or "sonnet"
    username = input('MariaDB Username (root): ') or "root"
    password = getpass.getpass('MariaDB Password: ')

    newpass = "".join([random.choice(string.ascii_letters) for i in range(random.randint(30,35))])

    # Generate sonnet user
    tmp = {
        "server": host,
        "port": port,
        "db_name": db_name,
        "login": "sonnet_user",
        "password": newpass
    }
    
    root = {
        "server": host,
        "port": port,
        "db_name": db_name,
        "login": username,
        "password": password
    }
    
    with open(".login-info.txt","w") as login_file:
        login_file.write(json.dumps(tmp))
    
    
    with lib_mdb_handler.db_handler_minimal(root) as database:
        
        database.cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        database.cur.execute(f"USE {db_name};")
        print('Created database OK.')
        
        database.cur.execute(f"CREATE USER IF NOT EXISTS 'sonnet_user'@'127.0.0.1' IDENTIFIED BY '{newpass}'")
        print('User created OK.')
        
        database.cur.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO 'sonnet_user'@'127.0.0.1' WITH GRANT OPTION")
        print("User granted database permission OK.")
        database.cur.execute("FLUSH PRIVILEGES")
    print("COMPLETED")



def migrate(sqlite3_loc):
    with lib_mdb_handler.db_handler() as mariadbc:
        with lib_sql_handler.db_handler(sqlite3_loc) as sqlitedb:

            for i in sqlitedb.list_tables("%_config")[0]:
                mariadbc.make_new_table(i, [["property", tuple, 1], ["value", str]])
                for row in sqlitedb.fetch_table(i):
                    mariadbc.add_to_table(i, [["property", row[0]], ["value", row[1]]])

            for i in sqlitedb.list_tables("%_infractions")[0]:
                mariadbc.make_new_table(i, [
                ["infractionID", tuple, 1],
                ["userID", str],
                ["moderatorID", str],
                ["type", str],
                ["reason", str],
                ["timestamp", int(64)]
                ])
                for row in sqlitedb.fetch_table(i):
                    mariadbc.add_to_table(i, [
                    ["infractionID", row[0]],
                    ["userID", row[1]],
                    ["moderatorID", row[2]],
                    ["type", row[3]],
                    ["reason", row[4]],
                    ["timestamp", row[5]]
                    ])

            for i in sqlitedb.list_tables("%_starboard")[0]:
                mariadbc.make_new_table(i, [["messageID", tuple, 1]])
                for row in sqlitedb.fetch_table(i):
                    mariadbc.add_to_table(i, [["messageID", row[0]]])

            for i in sqlitedb.list_tables("%_mutes")[0]:
                mariadbc.make_new_table(i, [["infractionID", tuple, 1],["userID", str],["endMute",int(64)]])
                for row in sqlitedb.fetch_table(i):
                    mariadbc.add_to_table(i, [
                        ["infractionID", row[0]],
                        ["userID", row[1]],
                        ["endMute", row[2]]
                        ])

    print("COMPLETED\n now copy the .login-info.txt file to your sonnet instance")


a = input("INITDB or MOVEDATA: ")
if a.lower() == 'initdb':
    initialize_login()
elif a.lower() == "movedata":
    b = input("sqlite3 location: ")
    migrate(b)
else:
    print("invalid option, exiting")
