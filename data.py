import sqlite3
connection = sqlite3.connect("data.db")
print(connection.total_changes)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS shuttles (id TEXT, name TEXT, lat TEXT, lon TEXT, heading TEXT, route TEXT, lastStop TEXT, lastUpdate TEXT)")

temp = [{"id":20989,"name":"#47","lat":41.309798,"lon":-72.923995,"heading":119,"route":14,"lastStop":41,"lastUpdate":1711504330}
,{"id":20990,"name":"#325","lat":41.302916,"lon":-72.93191,"heading":204,"route":7,"lastStop":10,"lastUpdate":1711504333}
,{"id":20991,"name":"#44","lat":41.309768,"lon":-72.926822,"heading":72,"route":13,"lastStop":53,"lastUpdate":1711504335}
,{"id":20993,"name":"#55","lat":41.299705,"lon":-72.929476,"heading":172,"route":14,"lastStop":9,"lastUpdate":1711504336}
,{"id":20994,"name":"#42","lat":41.303187,"lon":-72.934229,"heading":339,"route":13,"lastStop":43,"lastUpdate":1711504334}
,{"id":20995,"name":"#40","lat":41.307558,"lon":-72.928536,"heading":208,"route":14,"lastStop":98,"lastUpdate":1711504336}
,{"id":20996,"name":"#56","lat":41.304476,"lon":-72.930765,"heading":211,"route":13,"lastStop":38,"lastUpdate":1711504335}
,{"id":20997,"name":"#330","lat":41.305722,"lon":-72.931929,"heading":119,"route":10,"lastStop":127,"lastUpdate":1711504335}]

for element in temp:
    cursor.execute("INSERT INTO shuttles (id,name,lat,lon,heading,route,lastStop,lastUpdate) VALUES (?,?,?,?,?,?,?,?)", (element["id"], element["name"], element["lat"], element["lon"], element["heading"],element["route"],element["lastStop"],element["lastUpdate"]))

connection.commit()

cursor.execute("SELECT * FROM shuttles")
rows = cursor.fetchall()

for row in rows:
    print(row)

print(connection.total_changes)
