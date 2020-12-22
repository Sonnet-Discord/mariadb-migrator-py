import migration_libs.lib_sql_handler as lib_sql_handler
import migration_libs.lib_mdb_handler as lib_mdb_handler
from migration_libs.lib_loaders import generate_infractionid

import glob, getpass, mariadb, random, string, json

def initialize_login():
    print('Rhea to Sonnet Migrator\nMake sure you have a MariaDB server ready!')
    
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



def migrate():
    with lib_mdb_handler.db_handler() as mariadb
        for i in glob.glob("datastore/*.db"):
            with lib_sql_handler.db_handler(i) as sqlitedb:
            
                # Clean db
                mariadb.delete_table(f"{i[:-3]}_config")
                mariadb.delete_table(f"{i[:-3]}_infractions")
                mariadb.delete_table(f"{i[:-3]}_starboard")
                mariadb.delete_table(f"{i[:-3]}_mutes")
                
                # Make new tables
                mariadb.make_new_table(f"{i[:-3]}_config",[["property", tuple, 1], ["value", str]])
                fuckin_hell.make_new_table(f"{i[:-3]}_infractions", [
                ["infractionID", tuple, 1],
                ["userID", str],
                ["moderatorID", str],
                ["type", str],
                ["reason", str],
                ["timestamp", int(64)]
                ])
                mariadb.make_new_table(f"{i[:-3]}_starboard", [["messageID", tuple, 1]])
                mariadb.make_new_table(f"{i[:-3]}_mutes", [["infractionID", tuple, 1],["userID", str],["endMute",int(64)]])
            
                # Move data
                config = sqlitedb.grab_config()
                infractions = sqlitedb.grab_infractions()
                
                used = []
                for configuration in config:
                    mariadb.add_to_table(f"{i[:-3]}_config", [["property",configuration[0]],["value",configuration[1]]])
                for g in infractions:
                    new_id = generate_infractionid()
                    while (new_id in used):
                        new_id = generate_infractionid()
                    used.append(new_id)
                    mariadb.add_to_table(f"{i[:-3]}_infractions", [
                    ["infractionID", new_id],
                    ["userID", g[1]],
                    ["moderatorID", g[2]],
                    ["type", g[3]],
                    ["reason", g[4]],
                    ["timestamp", g[5]]])
    
    print("COMPLETED\n now copy the .login-info.txt file to your sonnet instance")



a = input("INITDB or MOVEDATA")
if a.lower() == 'initdb':
    initialize_login()
elif a.lower() == "movedata":
    migrate()
