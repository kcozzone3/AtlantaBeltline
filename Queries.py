import pymysql
from datetime import datetime

# Sample connection object we'd create inside Beltline.py after the user logs in.
# connection = pymysql.connect(host='localhost',
#                              user=user,
#                              password=password,
#                              db='beltline',
#                              charset='utf8mb4',
#                              cursorclass=pymysql.cursors.DictCursor)

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

class UserTakeTransit:
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        """Returns a list of tuples that represents all transits, and a list of sites (for the Contain Site filter
        dropdown."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM transit_connect GROUP BY TransportType")
            transits = cursor.fetchall()
            transits = [tuple(d.values()) for d in transits]

            cursor.execute("SELECT DISTINCT SiteName FROM transit_connect")
            sites = [i for d in cursor.fetchall() for i in list(d.values())]

        return transits, sites

    def filter(self, p1=None, p2=None, transport_type=None, site=None):
        """Given two prices, a transport type and site, return a list of tuples that represent the possible transits."""
        # We can imagine that we'd get the parameters like thus (inside Beltline.py):
        # p1, p2, transport_type, site = priceBox1.get(), priceBox2.get(), transportTypeDropdown.get(), containSiteDropdown.get()

        query = "SELECT * FROM transit_connect "

        if not any([p1, p2, transport_type, site]): #If no filter params are given
            return self.load()
        else:
            query += "WHERE 1=1 " #1=1 is there so I can add AND to every if statement and
                                  #not have to check if there should be an AND statement there
        if p1 and p2:
            query += f"AND Price BETWEEN {p1} AND {p2} "
        elif p1:
            query += f"AND Price >= {p1} "
        elif p2:
            query += f"AND Price <= {p2} "

        if transport_type :
            query += f"AND TransportType = {transport_type} "

        if site:
            query += f"AND SiteName = {site} "

        with self.connection.cursor() as cursor:
            cursor.execute(query + "GROUP BY TransportType, Route")
            transits = cursor.fetchall()
            transits = [tuple(d.values()) for d in transits]

        return transits


    def submit(self, route, transport_type, date):
        """Given a route, transport_type, and date, submits an entry into the database. Returns 0 for a successful
        submission, -1 if the User attempts to take the same transport on the same day twice, and -2 if the inputted
        date is incorrect. """

        try:
            datetime.strptime(date, '%Y-%m-%d')
        except:
            # If this throws an error (incorrect date format), then we'd make an error window/popup to alert the User.
            return -2

        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM take WHERE Username = {username} AND Date = {date}")
            if len(cursor.fetchall()) >= 1:
                # Create a window/popup alerting the user they cannot take the same transit twice
                return -1

            else:
                cursor.execute(f"INSERT INTO take VALUES ({username}, {transport_type}, {route}, {date})")
                connection.commit()

        return 0



"""(16) USER TRANSIT HISTORY"""
class UserTransitHistory:
    def __init__(self, connection):
        self.connection = connection

    def load(self, username):
        """Given a username, returns a list of tuples that represents all of the transits a User has taken, and a list
        of sites for the Contain Site filter dropdown."""

        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM take WHERE Username = {username}")
            transits = cursor.fetchall()
            transits = [tuple(d.values()) for d in transits]


            cursor.execute("SELECT DISTINCT SiteName FROM transit_connect")
            sites = [i for d in cursor.fetchall() for i in list(d.values())]

        return transits, sites


    def filter(self, username, d1=None, d2=None, transport_type=None, site=None, route=None):
        """Given two days (as strings or datetime objects), a transport type, site, and route, return a list of tuples
        that represents all of the transits a User has taken."""
        #We can imagine that we'd get the parameters like the following:
        #d1, d2, transport_type, site, route = dateBox1.get(), dateBox2.get(), transportTypeDropdown.get(), \
        #                                      containSiteDropdown.get(), routeBox.get()

        if type(d1) == str:  # Converts datetime object to string, just in case we ever pass in a datetime object.
            d1 = d1.strftime('%Y-%m-%d')
            d2 = d2.strftime('%Y-%m-%d')

        query = f"SELECT * FROM take WHERE Username = {username} "
        if d1 and d2:
            query += f"AND Date BETWEEN {d1} AND {d2} "
        elif d1:
            query += f"AND Date >= {d1} "
        elif d2:
            query += f"AND Date <= {d2} "

        if transport_type:
            query += f"AND TransportType = {transport_type} "

        if site:
            query += f"AND SiteName = {site} "

        if route:
            query += f"AND Route = {route}"

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            transits = cursor.fetchall()
            transits = [tuple(d.values()) for d in transits]

        return transits




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

