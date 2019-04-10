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
""" """SCREENS 15-16"""

"""(15) USER TAKE TRANSIT"""
# On load of this screen, we will retrieve all transits
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM transit_connect GROUP BY TransportType")
    transits = cursor.fetchall()  # fetchall() returns all tuples from the query, specifically as a list of dicts.
    transits = [tuple(d.values()) for d in transits] # Converts list of dicts into list of list of tuples. If it's
                                                     # better as a list of dicts then just ignore this line.

    # We also need to grab a list of all the available sites for the "Contain Site" dropdown
    cursor.execute("SELECT DISTINCT SiteName FROM transit_connect")
    sites = list(cursor.fetchall()[0].values())

# Then, we'd display all of the info inside the transits variable and populate the containSiteDropdown with the
# stuff inside the sites variable.

# The user may input items to filter, namely ContainSite, Price Range A and B, and Transport Type.
# We might imagine that, in our onTakeTransitFilter() function that is called after a button press, we
# would run the following code:
with connection.cursor() as cursor:
    p1, p2, transport_type, site = priceBox1.get(), priceBox2.get(), transportTypeDropdown.get(), containSiteDropdown.get()
    cursor.execute(f"SELECT * FROM transit_connect WHERE SiteName = {site} AND "
                   f"Price BETWEEN {p1} AND {p2} AND TransportType = {transport_type} GROUP BY TransportType, Route")
    transits = cursor.fetchall()
    transits = [tuple(d.values()) for d in transits]

# Then, we'd display this new info as we did before.

# Finally, the User may submit an entry to the database. But, remember, a User is not allowed to take the same transit
# twice in the same day. Also, we'd need to make sure that Route and Transit Date are entered, and that the
# Transit Date is a valid date. We'd run this code in our onTakeTransit() function that is called after a button press:
with connection.cursor() as cursor:
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




"""(16) USER TRANSIT HISTORY"""
# On load, we will retrieve all transits the user has taken
with connection.cursor() as cursor:
    cursor.execute(f"SELECT * FROM take WHERE Username = {username}")  # Where username is the login id that is in use.
    transits = cursor.fetchall()
    transits = []

    # We also need to grab a list of all the available sites for the "Contain Site" dropdown
    cursor.execute("SELECT DISTINCT SiteName FROM transit_connect")
    sites = list(cursor.fetchall()[0].values())

# Then, we'd display all of the info inside the transits variable and populate the containSiteDropdown with the
# stuff inside the sites variable.

# The user may input items to filter, namely ContainSite, Price Range A and B, and Transport Type
# We might imagine that, in our onTakeTransitFilter() function that is called after a button press, we
# would run the following code:
with connection.cursor() as cursor:
    d1, d2, transport_type, site, route = dateBox1.get(), dateBox2.get(), transportTypeDropdown.get(), \
                                          containSiteDropdown.get(), routeBox.get()

    cursor.execute(f"SELECT * FROM take WHERE Username = {username} AND SiteName = {site} AND "
                   f"Date BETWEEN {d1} AND {d2} AND TransportType = {transport_type} AND Route = {route}")
    transits = cursor.fetchall()

# Then, we'd display this new info as we did before.



"""
  ______                 _                         ______                _   _                   _ _ _         
 |  ____|               | |                       |  ____|              | | (_)                 | (_) |        
 | |__   _ __ ___  _ __ | | ___  _   _  ___  ___  | |__ _   _ _ __   ___| |_ _  ___  _ __   __ _| |_| |_ _   _ 
 |  __| | '_ ` _ \| '_ \| |/ _ \| | | |/ _ \/ _ \ |  __| | | | '_ \ / __| __| |/ _ \| '_ \ / _` | | | __| | | |
 | |____| | | | | | |_) | | (_) | |_| |  __/  __/ | |  | |_| | | | | (__| |_| | (_) | | | | (_| | | | |_| |_| |
 |______|_| |_| |_| .__/|_|\___/ \__, |\___|\___| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|\__,_|_|_|\__|\__, |
                  | |             __/ |                                                                   __/ |
                  |_|            |___/                                                                   |___/ 
"""
"""(17) EMPLOYEE MANAGE PROFILE"""

# On load, we will retrieve all data and populate all entries for their profile
with connection.cursor() as cursor:
    cursor.execute(f"SELECT FirstName, LastName, EmpUsername, Phone, Address, City, State, Zipcode "
                   f"FROM employee JOIN user ON EmpUsername = Username WHERE EmpUsername = {username}")
    fname, lname, username, phone, street, city, state, zipcode = cursor.fetchall()[0].values()

    address = f"{street}, {city}, {state}, {zipcode}"

    cursor.execute(f"SELECT Email FROM email WHERE Username = {username}")
    emails = [email for d in cursor.fetchall() for email in d.values()]

    cursor.execute(f"SELECT * FROM manager WHERE ManUsername = {username}") # Get's the site if they're a manager
    if cursor.fetchall():
        cursor.execute(f"SELECT Name FROM site WHERE ManUsername = {username}")
        site = cursor.fetchall()[0]['Name']

    cursor.execute(f"SELECT * FROM visitor WHERE VisUsername = {username}")
    if cursor.fetchall():
        visitor = True
    else:
        visitor = False

# Now we have address, visitor True/False, the Site (if they're a manager), name/phone/ID to display.