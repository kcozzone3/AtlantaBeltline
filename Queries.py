import pymysql
from datetime import datetime

connection = pymysql.connect(host='localhost',
                             user=user,
                             password=password,
                             db='beltline',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

"""
 __      ___                   
 \ \    / (_)                  
  \ \  / / _  _____      _____ 
   \ \/ / | |/ _ \ \ /\ / / __|
    \  /  | |  __/\ V  V /\__ \
     \/   |_|\___| \_/\_/ |___/

Some views that will make later queries easier. Put these at the bottom of buildDB.sql
"""

"""
This looks like a mess, admittedly. And there's probably a better way to do it.
This view (transit_connect) basically holds all of the transits that a user may take.
It joins the transit table and connect table, and then joins to a temporary table that 
calculates the number of connected sites (which is necessary according to the PDF). 

Also, I rename some of the columns in this view because it might save us a few lines of Python later when we have to 
display each column.

CREATE VIEW transit_connect AS
SELECT T.TransportType, T.Route, T.Price, C.SiteName, tmp.num_sites as "# Connected Sites"
    FROM transit AS T JOIN connect AS C 
                      ON (T.TransportType, T.Route) = (C.TransportType, C.Route) 

                      JOIN (SELECT TransportType, Route, count(*) AS num_sites FROM connect GROUP BY TransportType, Route) AS tmp 
                      ON (T.TransportType, T.Route) = (tmp.TransportType, tmp.Route);
"""

"""
  _    _                 ______                _   _                   _ _ _         
 | |  | |               |  ____|              | | (_)                 | (_) |        
 | |  | |___  ___ _ __  | |__ _   _ _ __   ___| |_ _  ___  _ __   __ _| |_| |_ _   _ 
 | |  | / __|/ _ \ '__| |  __| | | | '_ \ / __| __| |/ _ \| '_ \ / _` | | | __| | | |
 | |__| \__ \  __/ |    | |  | |_| | | | | (__| |_| | (_) | | | | (_| | | | |_| |_| |
  \____/|___/\___|_|    |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|\__,_|_|_|\__|\__, |
                                                                                __/ |
                                                                               |___/ 
"""

"""(15) USER TAKE TRANSIT"""
with connection.cursor() as cursor:
    # On load, we will retrieve all transits
    cursor.execute("SELECT * FROM transit_connect GROUP BY TransportType")
    transits = cursor.fetchall()  # fetchall() returns all tuples from the query, specifically as a list of dicts.

    # We also need to grab a list of all the available sites for the "Contain Site"
    cursor.execute("SELECT UNIQUE SiteName FROM transit_connect")
    sites = cursor.fetchall()

    # Then, we'd display all of the info inside the transits variable and populate the containSiteDropdown with the
    # stuff inside the sites variable.

with connection.cursor() as cursor:
    # The user may input items to filter, namely ContainSite, Price Range A and B, and Transport Type
    # We might imagine that, in our onTakeTransitFilter() function that is called after a button press, we
    # would run the following code:

    p1, p2, transport_type, site = priceBox1.get(), priceBox2.get(), transportTypeDropdown.get(), containSiteDropdown.get()
    cursor.execute(f"SELECT * FROM transit_connect WHERE SiteName = {site} AND "
                   f"Price BETWEEN {p1} AND {p2} AND TransportType = {transport_type} GROUP BY TransportType, Route")
    transits = cursor.fetchall()

    # Then, we'd display this new info as we did before.

with connection.cursor() as cursor:
    # Finally, we'd submit an entry to the database. But, remember, a User is not allowed to take the same transit
    # twice in the same day. Also, we'd need to make sure that Route and Transit Date are entered, and that the
    # Transit Date is a valid date.

    route, date = routeButton.get(), transitDateBox.get()
    route, transport_type = route[0], route[1] # Here I'm assuming that the routeButton will return a list of values
                                               # but I may be wrong. If I'm correct, the first and second elements
                                               # of that list should bRoute and Transit Type (as indicated in the picture).


    try:
        datetime.strptime(date, '%Y-%m-%d')

    except:
        # If this throws an error (incorrect date format), then we'd make an error window/popup to alert the User.
        pass

    cursor.execute(f"SELECT * FROM take WHERE Username = {username} AND Date = {date}")  # Where username is the login id that is in use.
    if len(cursor.fetchall()) >= 1:
        # Create a window/popup alerting the user they cannot take the same transit twice
        break

    else:
        cursor.execute(f"INSERT INTO take VALUES ({username}, {transport_type}, {route}, {date})")
        connection.commit()





