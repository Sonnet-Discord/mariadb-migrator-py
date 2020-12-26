import migration_libs.lib_sql_handler as lib_sql_handler
from migration_libs.lib_loaders import generate_infractionid

import glob, random, string, json

def migrate(dbloc):
    with lib_sql_handler.db_handler(dbloc) as mariadbc:
        for i in glob.glob("datastore/*.db"):
            with lib_sql_handler.db_handler(i) as sqlitedb:

                i = i.split("/")[1]

                # Make new tables
                mariadbc.make_new_table(f"{i[:-3]}_config",[["property", tuple, 1], ["value", str]])
                mariadbc.make_new_table(f"{i[:-3]}_infractions", [
                ["infractionID", tuple, 1],
                ["userID", str],
                ["moderatorID", str],
                ["type", str],
                ["reason", str],
                ["timestamp", int(64)]
                ])
                mariadbc.make_new_table(f"{i[:-3]}_starboard", [["messageID", tuple, 1]])
                mariadbc.make_new_table(f"{i[:-3]}_mutes", [["infractionID", tuple, 1],["userID", str],["endMute",int(64)]])
            
                # Move data
                config = sqlitedb.grab_config()
                infractions = sqlitedb.grab_infractions()
                
                used = []
                for configuration in config:
                    mariadbc.add_to_table(f"{i[:-3]}_config", [["property",configuration[0]],["value",configuration[1]]])
                for g in infractions:
                    new_id = generate_infractionid()
                    while (new_id in used):
                        new_id = generate_infractionid()
                    used.append(new_id)
                    mariadbc.add_to_table(f"{i[:-3]}_infractions", [
                    ["infractionID", new_id],
                    ["userID", g[1]],
                    ["moderatorID", g[2]],
                    ["type", g[3]],
                    ["reason", g[4]],
                    ["timestamp", g[5]]])
    
    print("COMPLETED")



a = input("sqlite3 location: ")
migrate(a)
