import argparse
import re
import sqlite3

ap = argparse.ArgumentParser()
ap.add_argument("-d","--database",    required=True,help="Path to the SQLite database you wish to analyze.")
args = vars(ap.parse_args())

match_list  = []
regex_match = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

# connect to the database
db     = sqlite3.connect(args['database'])
cursor = db.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

tables = cursor.fetchall()

for table in tables:
    
    print "[*] Scanning table...%s" % table
    
    # now do a broad select for all records
    cursor.execute("SELECT * FROM %s" % table[0])

    rows = cursor.fetchall()
    
    for row in rows:
        
        for column in row:
            
            try:
                matches = regex_match.findall(column)
            except:
                continue
            
            for match in matches:
                
                if match not in match_list:
                    
                    match_list.append(match)
cursor.close()
db.close()
            
print "[*] Discovered %d matches." % len(match_list)

for match in match_list:
    print match