import pymysql
from datetime import datetime
from pprint import pprint

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
SELECT T.TransportType, T.Route, T.Price, C.SiteName, tmp.num_sites as NumSites
    FROM transit AS T JOIN connect AS C
                      ON (T.TransportType, T.Route) = (C.TransportType, C.Route)
                      JOIN (SELECT TransportType, Route, count(*) AS num_sites FROM connect GROUP BY TransportType, Route) AS tmp
                      ON (T.TransportType, T.Route) = (tmp.TransportType, tmp.Route);

CREATE VIEW emp_profile AS
SELECT E.EmpUsername, E.EmployeeID, E.Phone, Concat(E.Address, ', ', E.City, ' ', E.State, ', ', E.Zipcode) as Address
	FROM Employee as E;

CREATE VIEW user_type AS
SELECT Username, CASE WHEN EXISTS(SELECT * FROM manager WHERE ManUsername = u.Username) = 1 THEN 'Manager' collate utf8mb4_general_ci
				 WHEN EXISTS(SELECT * FROM staff WHERE StaffUsername = u.Username) = 1 THEN 'Staff' collate utf8mb4_general_ci
				 WHEN EXISTS(SELECT * FROM visitor WHERE VisUsername = u.Username) = 1 THEN 'Visitor' collate utf8mb4_general_ci
                             ELSE 'User' collate utf8mb4_general_ci
       END AS UserType
FROM User AS u WHERE NOT EXISTS(SELECT * FROM administrator WHERE AdminUsername = u.Username);

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


class TakeTransit:
    """(15) USER TAKE TRANSIT"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        """Returns a dict for col names, and a list of sites (for the Contain Site filter
        dropdown."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Route, TransportType, Price, NumSites as '# Connected Sites' "
                           "FROM transit_connect GROUP BY TransportType")  # Yes, inefficient since we're only
            transits = cursor.fetchall()                                   # displaying a blank table on loadup. But,
                                                                           # it still gets the col names :/
            for i in transits:
                for key in i:
                    i[key] = ""

            transits = {1: transits[1]}  # Returns just col names, as we have to load a blank table to start with.

            cursor.execute("SELECT Name FROM site")
            sites = [d['Name'] for d in cursor.fetchall()]

        return transits, sites

    def filter(self, p1=None, p2=None, site=None, transport_type=None, sort='TransportType'):
        """Given two prices, a transport type and site, return a list of tuples that represent the possible transits."""

        query = "SELECT Route, TransportType, Price, NumSites as '# Connected Sites' FROM transit_connect WHERE 1=1 "
        # 1=1 is there so I can add AND to every if statement and not have to check if there should be an
        # AND statement there
        if p1 and p2:
            query += f"AND Price BETWEEN {p1} AND {p2} "
        elif p1:
            query += f"AND Price >= {p1} "
        elif p2:
            query += f"AND Price <= {p2} "

        if transport_type:
            query += f"AND TransportType = '{transport_type}' "

        if site:
            query += f"AND SiteName = '{site}' "

        query += f'GROUP BY TransportType, Route ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            transits = cursor.fetchall()

        for i in transits:
            for key in i:
                i[key] = str(i[key])
        transits = {i+1: transits[i] for i in range(len(transits))}

        if transits == {}:
            transits = self.load()[0]
            # Why does .fetchall() return an empty tuple if there are no results? Why not an empty dict like any reasonable person would want

        return transits


    def submit(self, route, transport_type, date, username):
        """Given a route, transport_type, and date, submits an entry into the database. Returns 0 for a successful
        submission, -1 if the User attempts to take the same transport on the same day twice, and -2 if the inputted
        date is incorrect. """

        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM take WHERE Username = '{username}' AND Date = '{date}' AND Route = '{route}' "
                           f"AND TransportType = '{transport_type}'")
            if len(cursor.fetchall()) >= 1:
                # Create a window/popup alerting the user they cannot take the same transit twice
                return -1

            else:
                cursor.execute(f"INSERT INTO take VALUES ('{username}', '{transport_type}', '{route}', '{date}')")
                self.connection.commit()

        return 0


class TransitHistory:
    """(16) USER TRANSIT HISTORY"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        """Given a username, returns a list of tuples that represents all of the transits a User has taken, and a list
        of sites for the Contain Site filter dropdown."""

        # DO NOT DELETE THIS COMMENT
        # SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'take';
        # Just in case the TAs get mean and delete every transit and ask us to load TransitHistory, this is the fix ^
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT Date, Route, TransportType, Price FROM transit_connect NATURAL JOIN take")
            transits = cursor.fetchall()


            for i in transits:
                for key in i:
                    i[key] = ""

            transits = {1: transits[0]}  # Returns just col names, as we have to load a blank table to start with.

            cursor.execute("SELECT Name FROM site")
            sites = [d['Name'] for d in cursor.fetchall()]

        return transits, sites


    def filter(self, username, d1=None, d2=None, transport_type=None, site=None, route=None, sort='Date'):
        """Given two days (as strings or datetime objects), a transport type, site, and route, return a list of tuples
        that represents all of the transits a User has taken."""

        query = f"SELECT Date, Route, TransportType, Price FROM transit_connect NATURAL JOIN take WHERE " \
                f"Username = '{username}' "
        if d1 and d2:
            query += f"AND Date BETWEEN '{d1}' AND '{d2}' "
        elif d1:
            query += f"AND Date >= '{d1}' "
        elif d2:
            query += f"AND Date <= '{d2}' "

        if transport_type:
            query += f"AND TransportType = '{transport_type}' "

        if site:
            query += f"AND SiteName = '{site}' "

        if route:
            query += f"AND Route = '{route}' "

        query += f'GROUP BY TransportType, Route, Date ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            transits = cursor.fetchall()

        for i in transits:
            for key in i:
                i[key] = str(i[key])
        transits = {i+1: transits[i] for i in range(len(transits))}

        if transits == {}:
            transits = self.load()[0]  # Why does .fetchall() return an empty tuple if there are no results?
        print(query)
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


class ManageProfile:
    """(17) EMPLOYEE MANAGE PROFILE"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, username):
        """Returns a first name, last name, site name, emp ID, phone number, address (as a concatenated string), and
        a list of emails."""
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT EmpUsername as 'Username', EmployeeID, Phone, Address, FirstName, LastName FROM "
                           f"emp_profile JOIN user ON EmpUsername = Username WHERE EmpUsername = '{username}'")
            username, empid, phone, address, fname, lname= cursor.fetchall()[0].values()

            cursor.execute(f"SELECT Email FROM emails WHERE Username = '{username}'")
            emails = [d['Email'] for d in cursor.fetchall()]

            cursor.execute(f"SELECT Name FROM Site WHERE ManUsername = '{username}'")
            site = cursor.fetchone()
            if site:
                site = site['Name']

            cursor.execute(f"SELECT Exists(SELECT VisUsername FROM visitor WHERE VisUsername = '{username}') as Vis")
            vis = cursor.fetchone()['Vis']
            if vis == 1:
                vis = True

            else:
                vis = False

            return fname, lname, empid, phone, address, emails, site, vis

    def submit(self, username, fname, lname, phone, emails, vis):

        with self.connection.cursor() as cursor:

            cursor.execute(f"SELECT Email FROM emails WHERE Username != '{username}'")
            all_emails = [d['Email'] for d in cursor.fetchall()]
            if any(i in all_emails for i in emails):
                return -1

            cursor.execute(f"DELETE FROM emails WHERE Username = '{username}'")
            self.connection.commit()

            for email in emails:
                cursor.execute(f"INSERT INTO emails VALUES ('{username}', '{email}')")
                self.connection.commit()

            cursor.execute(f"UPDATE user SET FirstName = '{fname}', LastName = '{lname}' WHERE Username = '{username}'")
            self.connection.commit()

            cursor.execute(f"UPDATE employee SET phone = '{phone}' WHERE EmpUsername = '{username}'")
            self.connection.commit()

            if vis and vis != self.get_vis(username):
                cursor.execute(f"INSERT INTO visitor VALUES ('{username}')")
                self.connection.commit()

            elif not vis and vis != self.get_vis(username):
                cursor.execute(f"DELETE FROM visitor WHERE VisUsername = '{username}'")
                self.connection.commit()

        return 0

    def get_vis(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT Exists(SELECT VisUsername FROM visitor WHERE VisUsername = '{username}') as Vis")
            vis = cursor.fetchone()['Vis']
            if vis == 1:
                vis = True

            else:
                vis = False

            return vis


class ManageUser:
    """(18) ADMIN MANAGE USER"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Username, COUNT(Email) AS 'Email Count', UserType, Status FROM user NATURAL JOIN emails "
                           "NATURAL JOIN user_type GROUP BY Username")
            users = cursor.fetchall()

            for i in users:
                for key in i:
                    i[key] = ""

            users = {1: users[1]}  # Returns just col names, as we have to load a blank table to start with.

        return users

    def filter(self, username=None, user_type=None, status=None, sort='Username'):

        query = "SELECT Username, COUNT(Email) AS 'Email Count', UserType, Status FROM user NATURAL JOIN emails " \
                "NATURAL JOIN user_type WHERE 1=1 "
        if username:
           query += f"AND Username = '{username}' "

        if user_type:
            query += f"AND UserType = '{user_type}' "

        if status:
            query += f"AND Status = '{status}' "

        query += f'GROUP BY Username ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            users = cursor.fetchall()

        for i in users:
            for key in i:
                i[key] = str(i[key])
        users = {i+1: users[i] for i in range(len(users))}

        if users == {}:
            users = self.load()
        print(users)
        return users


    def submit(self, username, status):
        with self.connection.cursor() as cursor:
            cursor.execute(f"UPDATE user SET Status = '{status}' WHERE Username = '{username}'")
            self.connection.commit()


class ManageSite:
    """(20) ADMIN EDIT SITE"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Name as SiteName, Manager, OpenEveryday FROM site AS s JOIN "
                           "(SELECT ManUsername, Concat(FirstName, ' ', LastName) as Manager FROM manager "
                           "JOIN user ON ManUsername = Username) as tmp ON tmp.ManUsername = s.ManUsername")
            sites = cursor.fetchall()

            for i in sites:
                for key in i:
                    i[key] = ""

            sites = {1: sites[1]}  # Returns just col names, as we have to load a blank table to start with.

            cursor.execute("SELECT DISTINCT ManUsername, FirstName, LastName FROM user JOIN manager ON Username = ManUsername")
            managers = [f"{d['FirstName']} {d['LastName']}" for d in cursor.fetchall()]

            cursor.execute("SELECT Name FROM site")
            sitenames = [d['Name'] for d in cursor.fetchall()]

        return sites, sitenames, managers

    def filter(self, site=None, manager=None, everyday=None, sort='SiteName'):

        query = "SELECT Name as SiteName, Manager, OpenEveryday FROM site AS s JOIN " \
                "(SELECT ManUsername, Concat(FirstName, ' ', LastName) as Manager FROM manager " \
                "JOIN user ON ManUsername = Username) as tmp ON tmp.ManUsername = s.ManUsername " \
                "WHERE 1=1 "
        if site:
           query += f"AND Name = '{site}' "

        if manager:
            query += f"AND Manager = '{manager}' "

        if everyday is not None:
            query += f"AND OpenEveryday = {everyday} "

        query += f'ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            sites = cursor.fetchall()

        for i in sites:
            for key in i:
                i[key] = str(i[key])
        sites = {i+1: sites[i] for i in range(len(sites))}
        print(sites)
        for d in sites.values():
            d['OpenEveryday'] = 'false' if d['OpenEveryday'] == '0' else 'true'

        if sites == {}:
            return self.load()[0]
        else:
            return sites

    def delete(self, sitename):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM site WHERE Name = '{sitename}'")
            self.connection.commit()


class EditSite:
    """(19) ADMIN MANAGE SITE"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, sitename):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Manager, Zipcode, OpenEveryday, Address FROM site AS s JOIN "
                           "(SELECT ManUsername, Concat(FirstName, ' ', LastName) as Manager FROM manager "
                           "JOIN user ON ManUsername = Username) as tmp ON tmp.ManUsername = s.ManUsername "
                           f"WHERE Name = '{sitename}'")
            site = cursor.fetchone()
            manager, zipcode, everyday, address = site['Manager'], site['Zipcode'], site['OpenEveryday'], site['Address']
            everyday = True if everyday == 1 else False

            cursor.execute("SELECT ManUsername, FirstName, LastName FROM user JOIN manager ON Username = ManUsername "
                           "WHERE ManUsername NOT IN (SELECT ManUsername FROM site)")
            managers = [f"{d['FirstName']} {d['LastName']}" for d in cursor.fetchall()]

            cursor.execute("SELECT Name FROM site")
            sitenames = [d['Name'] for d in cursor.fetchall()]

        return manager, managers, zipcode, address, everyday

    def update(self, sitename, address, zipcode, manager, everyday, original):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT ManUsername FROM user JOIN manager ON Username = ManUsername "
                                     f"WHERE Concat(FirstName, ' ', LastName) = '{manager}'")
            manager = cursor.fetchone()['ManUsername']
            if sitename == original:
                cursor.execute(f"UPDATE Site SET Address = '{address}', Zipcode = {zipcode}, ManUsername = '{manager}', "
                               f"OpenEveryday = {'true' if everyday else 'false'} WHERE Name = '{sitename}'")
                self.connection.commit()

            else:
                cursor.execute("SELECT Name FROM site")
                sites = [d['Name'] for d in cursor.fetchall()]

                if sitename in sites:
                    return -1

                else:
                    cursor.execute(f"UPDATE Site SET Address = '{address}', Zipcode = {zipcode}, "
                                   f"ManUsername = '{manager}', OpenEveryday = {'true' if everyday else 'false'}, "
                                   f"Name = '{sitename}' WHERE Name = '{original}'")
                    self.connection.commit()


class CreateSite:
    """(21) ADMIN CREATE SITE"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT FirstName, LastName FROM user JOIN manager ON Username = ManUsername "
                           "WHERE ManUsername NOT IN (SELECT ManUsername FROM site)")
            return [f"{d['FirstName']} {d['LastName']}" for d in cursor.fetchall()]

    def create(self, sitename, address, zipcode, manager, everyday):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT ManUsername FROM user JOIN manager ON Username = ManUsername "
                           f"WHERE Concat(FirstName, ' ', LastName) = '{manager}'")
            manager = cursor.fetchone()['ManUsername']

            cursor.execute("SELECT Name FROM site")
            sites = [d['Name'] for d in cursor.fetchall()]

            if sitename in sites:
                return -1

            else:
                cursor.execute(f"INSERT INTO Site VALUES ('{sitename}', '{address}', {zipcode}, "
                               f"{'true' if everyday else 'false'}, '{manager}')")
                self.connection.commit()


class ManageTransit:
    """(20) ADMIN MANAGE TRANSIT"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Route, TransportType, Price, NumSites AS '# Connected Sites', "
                           "NumTaken as '# Transits Logged'  FROM transit_connect NATURAL JOIN "
                           "(SELECT TransportType, Route, COUNT(*) as NumTaken FROM take GROUP BY TransportType, Route) "
                           "as tmp GROUP BY Route, TransportType")
            transits = cursor.fetchall()

            for i in transits:
                for key in i:
                    i[key] = ""

            transits = {1: transits[1]}  # Returns just col names, as we have to load a blank table to start with.

            cursor.execute("SELECT Name FROM site")
            sitenames = [d['Name'] for d in cursor.fetchall()]

        return transits, sitenames

    def filter(self, sitename=None, ttype=None, route=None, p1=None, p2=None, sort='TransportType'):

        query = "SELECT Route, TransportType, Price, NumSites AS '# Connected Sites', NumTaken as '# Transits Logged'  " \
                "FROM transit_connect NATURAL JOIN ((SELECT TransportType, Route, COUNT(*) as NumTaken FROM take " \
                "NATURAL JOIN transit Group By TransportType, Route) UNION (SELECT TransportType, Route, 0 " \
                "FROM transit WHERE (TransportType, Route) NOT IN (SELECT TransportType, Route FROM take) " \
                "GROUP BY TransportType, Route)) as tmp WHERE 1=1 "  # What a monster query.

        if sitename:
            query += f"AND SiteName = '{sitename}' "

        if ttype:
            query += f"AND TransportType = '{ttype}' "

        if route is not None:
            query += f"AND Route = '{route}' "

        if p1 and p2:
            query += f"AND Price BETWEEN {p1} AND {p2} "
        elif p1:
            query += f"AND Price >= {p1} "
        elif p2:
            query += f"AND Price <= {p2} "

        query += f'GROUP BY TransportType, Route ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            transits = cursor.fetchall()

        for i in transits:
            for key in i:
                i[key] = str(i[key])
        transits = {i+1: transits[i] for i in range(len(transits))}

        if transits == {}:
            return self.load()[0]
        else:
            return transits

    def delete(self, ttype, route):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM transit WHERE TransportType = '{ttype}' AND Route = '{route}'")
            self.connection.commit()


class EditTransit:
    """(23) ADMIN EDIT SITE"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, ttype, route):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT Price, SiteName FROM transit_connect WHERE TransportType = '{ttype}' AND Route = '{route}'")
            sites = cursor.fetchall()

            price = sites[0]['Price']
            connected_sites = [d['SiteName'] for d in sites]

            cursor.execute(f"SELECT SiteName FROM transit_connect WHERE SiteName NOT IN (SELECT SiteName "
                           f"FROM transit_connect WHERE TransportType = '{ttype}' AND Route = '{route}')")
            other_sites = [d['SiteName'] for d in cursor.fetchall()]



        return price, connected_sites, other_sites

    def submit(self, ttype, route, price, sites, original):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"DELETE FROM connect WHERE Route='{original}' AND TransportType='{ttype}'")
                for site in sites:
                    cursor.execute(f"INSERT INTO connect VALUES ('{site}', '{ttype}', '{original}')")

                cursor.execute(f"UPDATE transit SET Route='{route}', Price='{price}' WHERE TransportType='{ttype}' AND Route='{original}'")
                self.connection.commit()

            except Exception as e:
                print(e)
                return -1


class CreateTransit:
    """(24) ADMIN CREATE TRANSIT"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Name FROM site")

            sites = [d['Name'] for d in cursor.fetchall()]
            return sites

    def create(self, ttype, route, price, sites):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT TransportType, Route FROM transit")
            transits = [(d['TransportType'], d['Route']) for d in cursor.fetchall()]

            if (ttype, route) in transits:
                return -1

            else:
                cursor.execute(f"INSERT INTO transit VALUES ('{ttype}', '{route}', {price})")
                self.connection.commit()
                for site in sites:
                    cursor.execute(f"INSERT INTO connect VALUES ('{site}', '{ttype}', '{route}')")
                    self.connection.commit()


class ManageEvent:
    """(25) MANAGER MANAGE EVENT"""

    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT EventName, SiteName, StartDate, StaffCount, Duration, Visits, Revenue FROM manage_event")
            events = cursor.fetchall()

            for i in events:
                for key in i:
                    i[key] = ""

            events = {1: events[1]}  # Returns just col names, as we have to load a blank table to start with.

        return events

    def filter(self, manager, name=None, keyword=None, d1=None, d2=None, dur1=None, dur2=None, vis1=None, vis2=None, rev1=None, rev2=None, sort='EventName'):

        query = f"SELECT EventName, SiteName, StartDate, StaffCount, Duration, Visits, Revenue FROM manage_event WHERE ManUsername = '{manager}' "

        if name:
            query += f"AND EventName LIKE '%{name}%' "

        if keyword:
            query += f"AND Description LIKE '%{keyword}%' "

        if d1 and d2:
            query += f"AND StartDate IN (SELECT StartDate FROM event WHERE StartDate BETWEEN {d1} AND {d2}) "
        elif d1:
            query += f"AND StartDate IN (SELECT StartDate FROM event WHERE StartDate >= {d1}) "
        elif d2:
            f"AND StartDate IN (SELECT StartDate FROM event WHERE StartDate <= {d2}) "

        if dur1 and dur2:
            query += f"AND Duration BETWEEN {dur1} AND {dur2} "
        elif dur1:
            query += f"AND Duration >= {dur1} "
        elif dur2:
            f"AND Duration <= {dur2} "

        if vis1 and vis2:
            query += f"AND Visits BETWEEN {vis1} AND {vis2} "
        elif vis1:
            query += f"AND Visits >= {vis1} "
        elif vis2:
            f"AND Visits <= {vis2} "

        if rev1 and rev2:
            query += f"AND Revenue BETWEEN {rev1} AND {rev2} "
        elif rev1:
            query += f"AND Revenue >= {rev1} "
        elif rev2:
            f"AND Revenue <= {rev2} "

        query += f'GROUP BY EventName, SiteName, StartDate ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            events = cursor.fetchall()

        for i in events:
            for key in i:
                i[key] = str(i[key])
        events = {i + 1: events[i] for i in range(len(events))}

        if events == {}:
            return self.load()
        else:
            return events

    def delete(self, eventname, sitename, startdate):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM event WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}'")


class EditEvent:
    """(26) MANAGER EDIT EVENT"""

    def __init__(self, connection):
        self.connection = connection

    def load(self, manager,  eventname, sitename, startdate):
        with self.connection.cursor() as cursor:

            cursor.execute("SELECT Price, EndDate, MinStaffReq, Capacity, Description FROM manage_event WHERE "
                           f"ManUsername = '{manager}' AND EventName = '{eventname}' AND StartDate = '{startdate}'")
            event = cursor.fetchone()
            price, enddate, minstaffreq, cap, desc = event['Price'], event['EndDate'], event['MinStaffReq'], event['Capacity'], event['Description']

            cursor.execute(f"Select DISTINCT(CONCAT(FirstName, ' ', LastName, ' (', StaffUsername, ')')) AS StaffName FROM assignto JOIN user ON StaffUsername = Username "
                           f"WHERE SiteName = '{sitename}' AND EventName = '{eventname}' AND StartDate = '{startdate}'")
            cur_staff = [d['StaffName'] for d in cursor.fetchall()]

            cursor.execute(f"""
                            SELECT Distinct(CONCAT(FirstName, ' ', Lastname, ' (', StaffUsername, ')')) AS StaffName FROM assignto JOIN user ON StaffUsername = Username
                            WHERE StaffUsername NOT IN (SELECT StaffUsername from assignto NATURAL JOIN event WHERE SiteName = '{sitename}' AND EventName = '{eventname}' AND StartDate = '{startdate}')
                            AND StaffUsername NOT IN (SELECT StaffUsername FROM assignto NATURAL JOIN event WHERE StaffUsername = ANY(SELECT StaffUsername FROM assignto WHERE StartDate BETWEEN '{startdate}' AND '{enddate}'))
                            AND StaffUsername NOT IN (SELECT StaffUsername FROM assignto NATURAL JOIN event WHERE StaffUsername = ANY(SELECT StaffUsername FROM assignto NATURAL JOIN event WHERE EndDate BETWEEN '{startdate}' AND '{enddate}'));
                            """)
            avail_staff = [d['StaffName'] for d in cursor.fetchall()]

            cursor.execute(f"""
                        SELECT gen_date AS Date, IFNULL(DailyVisits, 0) AS DailyVisits, IFNULL(DailyRevenue, 0) AS DailyRevenue FROM
                        (SELECT Date, COUNT(VisUsername) AS DailyVisits, COUNT(VisUsername) * Price AS DailyRevenue
                        FROM visitevent
                        NATURAL JOIN
                        event
                        WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}' GROUP BY Date) AS calc

                        RIGHT JOIN
                        dates_view
                        ON gen_date = Date
                        WHERE gen_date BETWEEN '{startdate}' AND '{enddate}'
                        """)
            dailies = cursor.fetchall()

            for i in dailies:
                for key in i:
                    i[key] = ""

            dailies = {1: dailies[0]}  # Returns just col names, as we have to load a blank table to start with.

        return price, enddate, minstaffreq, cap, cur_staff, avail_staff, desc, dailies

    def filter(self, manager, eventname, sitename, startdate, rev1=None, rev2=None, vis1=None, vis2=None, sort='Date'):
        print(rev2)
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT EndDate FROM event WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}'")
            enddate = cursor.fetchone()['EndDate']

        query = f"""
                        SELECT gen_date AS Date, IFNULL(DailyVisits, 0) AS DailyVisits, IFNULL(DailyRevenue, 0) AS DailyRevenue FROM
                        (SELECT Date, COUNT(VisUsername) AS DailyVisits, COUNT(VisUsername) * Price AS DailyRevenue
                        FROM visitevent
                        NATURAL JOIN
                        event
                        WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}' GROUP BY Date) AS calc

                        RIGHT JOIN
                        dates_view
                        ON gen_date = Date
                        WHERE gen_date BETWEEN '{startdate}' AND '{enddate} '
                """

        if vis1 and vis2:
            query += f"AND IFNULL(DailyVisits, 0) BETWEEN {vis1} AND {vis2} "
        elif vis1:
            query += f"AND IFNULL(DailyVisits, 0) >= {vis1} "
        elif vis2:
            query += f"AND IFNULL(DailyVisits, 0) <= {vis2} "

        if rev1 and rev2:
            query += f"AND IFNULL(DailyRevenue, 0) BETWEEN {rev1} AND {rev2} "
        elif rev1:
            query += f"AND IFNULL(DailyRevenue, 0) >= {rev1} "
        elif rev2:
            query += f"AND IFNULL(DailyRevenue, 0) <= {rev2} "

        query += f"ORDER BY {sort} DESC"

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            dailies = cursor.fetchall()

        for i in dailies:
            for key in i:
                i[key] = str(i[key])
        dailies = {i+1: dailies[i] for i in range(len(dailies))}

        if dailies == {}:
            return self.load(manager, eventname, sitename, startdate)[-1]
        else:
            return dailies

    def submit(self, eventname, sitename, startdate, desc, staff):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM assignto WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}'")
            self.connection.commit()
            for i in staff:
                print(i[i.find('(')+1:i.find(')')])
                cursor.execute(f"INSERT INTO assignto VALUES ('{i[i.find('(')+1:i.find('}')]}', '{sitename}', '{eventname}', '{startdate}')")
                self.connection.commit()

            cursor.execute(f'UPDATE event SET Description = "{desc}" WHERE EventName = "{eventname}" AND SiteName = "{sitename}" AND StartDate = "{startdate}"')
            self.connection.commit()


class CreateEvent:
    """(27) MANAGER CREATE EVENT"""

    def __init__(self, connection):
        self.connection = connection

    def load(self):
        pass

    def get_staff(self, d1, d2):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT Distinct(CONCAT(FirstName, ' ', Lastname, ' (', StaffUsername, ')')) AS StaffName FROM assignto JOIN user ON StaffUsername = Username "
                           f"WHERE StaffUsername NOT IN (SELECT StaffUsername FROM assignto NATURAL JOIN event WHERE StaffUsername = ANY(SELECT StaffUsername FROM assignto WHERE StartDate BETWEEN '{d1}' AND '{d2}')) "
                           f"AND StaffUsername NOT IN (SELECT StaffUsername FROM assignto NATURAL JOIN event WHERE StaffUsername = ANY(SELECT StaffUsername FROM assignto NATURAL JOIN event WHERE EndDate BETWEEN '{d1}' AND '{d2}'))")
            return [d['StaffName'] for d in cursor.fetchall()]

    def create(self, manager, eventname, price, cap, minstaff, d1, d2, desc, staff):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT Name FROM site WHERE ManUsername = '{manager}'")
                sitename = cursor.fetchone()['Name']

                cursor.execute(f"INSERT INTO event VALUES ('{sitename}', '{eventname}', '{d1}', '{d2}', {price}, {cap}, {minstaff}, '{desc}')")

                for i in staff:
                    cursor.execute(f"INSERT INTO assignto VALUES ('{i[i.find('(')+1:i.find('}')]}', '{sitename}', '{eventname}', '{d1}')")

                self.connection.commit()

            except:
                return -1


class ManageStaff:
    """(28) MANAGER MANAGE STAFF"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT CONCAT(FirstName, ' ', LastName) AS Name, COUNT(*) As NumShifts FROM "
                           f"assignto JOIN user on assignto.StaffUsername = user.Username GROUP BY Name")
            staff = cursor.fetchall()

            for i in staff:
                for key in i:
                    i[key] = ""

            staff = {1: staff[1]}  # Returns just col names, as we have to load a blank table to start with.

            cursor.execute(f"SELECT DISTINCT(Name) FROM site")
            sites = cursor.fetchall()
            sites = [d['Name'] for d in sites]

        return staff, sites

    def filter(self, site=None, fname=None, lname=None, d1=None, d2=None, sort='Name'):
        query = "SELECT CONCAT(FirstName, ' ', LastName) AS Name, COUNT(*) As NumShifts FROM " \
                "assignto JOIN user on assignto.StaffUsername = user.Username WHERE 1=1 "

        if site:
            query += f"AND SiteName = '{site}'"
        if fname:
            query += f"AND FirstName LIKE '%{fname}%' "
        if lname:
            query += f"AND LastName LIKE '%{lname}%' "
        if d1 and d2:
            query += f"AND StartDate BETWEEN '{d1}' AND '{d2}' "
        elif d1:
            query += f"AND StartDate >= '{d1}' "
        elif d2:
            query += f"AND StartDate <= '{d2}' "

        query += f"GROUP BY Name ORDER BY {sort}"
        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            staff = cursor.fetchall()

        for i in staff:
            for key in i:
                i[key] = str(i[key])
        staff = {i + 1: staff[i] for i in range(len(staff))}

        if staff == {}:
            return self.load()[0]
        else:
            return staff


class SiteReport:
    """(29) MANAGER SITE REPORT"""
    def __init__(self, connection):
        self.connection = connection

    def load(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
f"""
SELECT Date AS Date, IFNULL(EventCount, 0) AS EventCount, IFNULL(StaffCount, 0) AS StaffCount, IFNULL(TotalVisits, 0) AS TotalVisits, IFNULL(TotalRevenue, 0) AS TotalRevenue from
(SELECT gen_date AS Date, Count(*) AS EventCount FROM event RIGHT JOIN dates_view ON gen_date BETWEEN StartDate AND EndDate WHERE StartDate BETWEEN '1111-11-11' AND '1111-11-11' AND SiteName = 'Lizard' GROUP BY Date) AS EC
NATURAL JOIN
(SELECT gen_date AS Date, Count(*) AS StaffCount FROM assignto NATURAL JOIN event RIGHT JOIN dates_view ON gen_date BETWEEN StartDate AND EndDate WHERE StartDate BETWEEN '1111-11-11' AND '1111-11-11' AND SiteName = 'Lizard' GROUP BY Date) AS SC
NATURAL JOIN
(SELECT gen_date AS Date, IFNULL(ETotal, 0) + IFNULL(STotal, 0) AS TotalVisits FROM dates_view LEFT JOIN (SELECT Date, COUNT(VisUsername) AS ETotal FROM visitevent WHERE Date BETWEEN '1111-11-11' AND '1111-11-11' AND SiteName = 'Lizard' GROUP BY Date) AS E ON gen_date = Date
NATURAL LEFT JOIN (SELECT Date, COUNT(VisUsername) AS STotal FROM visitsite WHERE Date BETWEEN '1111-11-11' AND '1111-11-11' AND SiteName = 'Lizard' GROUP BY Date) AS S) AS TV
NATURAL LEFT JOIN
(SELECT Date, Q.Total AS TotalRevenue FROM (SELECT Date, Price * Count(VisUsername) AS Total FROM event NATURAL JOIN visitevent WHERE Date BETWEEN '1111-11-11' AND '1111-11-11' AND SiteName = 'Lizard' GROUP BY Date) AS Q) AS TR WHERE 1=1
""")
            dailies = cursor.fetchall()
            for i in dailies:
                for key in i:
                    i[key] = ""

        return {1: {'Date': '', 'EventCount': '', 'StaffCount': '', 'TotalVisits': '', 'TotalRevenue': ''}}

    def filter(self, manager, startdate, enddate, e1, e2, s1, s2, rev1, rev2, vis1, vis2, sort='Date'):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT Name FROM site WHERE ManUsername = '{manager}'")
            try:
                sitename = cursor.fetchone()['Name']
            except:  # If the manager has no site assigned.
                return self.load()

        query = f"""
SELECT gen_date AS Date, EventCount, StaffCount, TotalVisits, TotalRevenue from
(SELECT gen_date, IFNULL(StaffCount, 0) AS StaffCount FROM (SELECT gen_date FROM dates_view WHERE gen_date  BETWEEN '{startdate}' AND '{enddate}') AS D2 LEFT JOIN (SELECT gen_date AS Date, Count(*) AS StaffCount FROM assignto NATURAL JOIN event RIGHT JOIN dates_view ON gen_date BETWEEN StartDate AND EndDate WHERE StartDate BETWEEN '{startdate}' AND '{enddate}' AND SiteName = '{sitename}' GROUP BY Date) AS SC1 ON Date = gen_date) AS SC
NATURAL JOIN
(SELECT gen_date, IFNULL(EventCount, 0) AS EventCount FROM (SELECT gen_date FROM dates_view WHERE gen_date BETWEEN '{startdate}' AND '{enddate}') AS D1 LEFT JOIN (SELECT gen_date AS Date, Count(*) AS EventCount FROM event RIGHT JOIN dates_view ON gen_date BETWEEN StartDate AND EndDate WHERE StartDate BETWEEN '{startdate}' AND '{enddate}' AND SiteName = '{sitename}' GROUP BY Date) AS EC1 On Date = gen_date) AS EC
NATURAL JOIN
(SELECT gen_date, ETot + STot AS TotalVisits FROM
	(SELECT gen_date, IFNULL(ETotal, 0) AS ETot FROM dates_view LEFT JOIN (SELECT Date, COUNT(VisUsername) AS ETotal FROM visitevent WHERE Date BETWEEN '{startdate}' AND '{enddate}' AND SiteName = '{sitename}' GROUP BY Date) AS E ON gen_date = Date WHERE gen_date BETWEEN '{startdate}' AND '{enddate}') AS E
	NATURAL JOIN
	(SELECT gen_date, IFNULL(STotal, 0) AS STot FROM dates_view LEFT JOIN (SELECT Date, COUNT(VisUsername) AS STotal FROM visitsite WHERE Date BETWEEN '{startdate}' AND '{enddate}' AND SiteName = '{sitename}' GROUP BY Date) AS S ON gen_date = Date WHERE gen_date BETWEEN '{startdate}' AND '{enddate}') AS S) AS VTot
NATURAL JOIN
(SELECT gen_date, IFNULL(TotalRevenue, 0) AS TotalRevenue FROM (SELECT gen_date FROM dates_view WHERE gen_date  BETWEEN '{startdate}' AND '{enddate}') AS D4 LEFT JOIN (SELECT Date, Price * Count(VisUsername) AS TotalRevenue FROM event NATURAL JOIN visitevent WHERE Date BETWEEN '{startdate}' AND '{enddate}' AND SiteName = '{sitename}' GROUP BY Date) AS TR1 ON Date = gen_date) AS RTot
WHERE 1=1
"""
        if e1 and e2:
            query += f"AND EventCount BETWEEN {e1} AND {e2} "
        elif e1:
            query += f"AND EventCount >= {e1} "
        elif e2:
            query += f"AND EventCount <= {e2} "

        if s1 and s2:
            query += f"AND StaffCount BETWEEN {s1} AND {s2} "
        elif s1:
            query += f"AND StaffCount >= {s1} "
        elif s2:
            query += f"AND StaffCount <= {s2} "

        if vis1 and vis2:
            query += f"AND TotalVisits BETWEEN {vis1} AND {vis2} "
        elif vis1:
            query += f"AND TotalVisits >= {vis1} "
        elif vis2:
            f"AND Visits <= {vis2} "

        if rev1 and rev2:
            query += f"AND TotalRevenue BETWEEN {rev1} AND {rev2} "
        elif rev1:
            query += f"AND TotalRevenue >= {rev1} "
        elif rev2:
            f"AND TotalRevenue <= {rev2} "

        query += f"ORDER BY {sort}"
        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            dailies = cursor.fetchall()

        for i in dailies:
            for key in i:
                i[key] = str(i[key])
        dailies = {i + 1: dailies[i] for i in range(len(dailies))}

        if dailies == {}:
            return self.load()
        else:
            return dailies


class DailyDetail:
    """(30) MANAGER DAILY DETAIl"""
    def __init__(self, connection):
        self.connection = connection

    def filter(self, manager, date, sort='EventName'):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT Name FROM site WHERE ManUsername = '{manager}'")
            try:
                sitename = cursor.fetchone()['Name']
            except:  # If the manager has no site assigned.
                return {1: {'EventName': '', 'StaffNames': '', 'NumVisits': '', 'Revenue': ''}}

        query = f"""
                SELECT EventName, StaffNames, NumVisits, Revenue FROM(
                    (SELECT EventName, IFNULL(NumVisits, 0) AS NumVisits, IFNULL(NumVisits * Price, 0) AS Revenue FROM (SELECT EventName, StartDate, Price FROM event WHERE '2019-10-10' BETWEEN StartDate and EndDate AND SiteName = 'Piedmont Park') A NATURAL LEFT JOIN (SELECT EventName, COUNT(VisUsername) AS NumVisits FROM visitevent WHERE Date = '2019-10-10' AND SiteName = 'Piedmont Park' GROUP BY EventName) B) AS C
                NATURAL JOIN
                    (SELECT EventName, GROUP_CONCAT(CONCAT(FirstName, ' ', LastName) ORDER BY FirstName ASC) AS StaffNames FROM event NATURAL JOIN assignto JOIN user ON Username = StaffUsername WHERE  '{date}' BETWEEN StartDate AND EndDate AND SiteName = '{sitename}' GROUP BY EventName) AS D)
                ORDER BY {sort}

                """
        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            events = cursor.fetchall()

        for i in events:
            for key in i:
                i[key] = str(i[key])
        events = {i + 1: events[i] for i in range(len(events))}

        if events == {}:
            return {1: {'EventName': '', 'StaffNames': '', 'NumVisits': '', 'Revenue': '', 'TotalRevenue': ''}}
        else:
            return events


class ViewSchedule:
    """(31) STAFF VIEW SCHEDULE"""
    def __init__(self, connection):
        self.connection = connection

    def filter(self, staff, eventname=None, keyword=None, startdate=None, enddate=None, sort='EventName'):
        query = f"SELECT EventName, SiteName, StartDate, EndDate, Count(StaffUsername) AS StaffCount FROM event NATURAL JOIN assignto " \
                f"WHERE StaffUsername = '{staff}' "

        if eventname:
            query += f"AND EventName LIKE '%{eventname}%' "
        if keyword:
            query += f"AND Description LIKE '%{keyword}%' "
        if startdate:
            query += f"AND EndDate >= '{startdate}' "
        if enddate:
            query += f"AND StartDate <= '{enddate}' "

        query += f"GROUP BY EventName, SiteName, StartDate ORDER BY {sort}"

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            events = cursor.fetchall()

        for i in events:
            for key in i:
                i[key] = str(i[key])
        events = {i + 1: events[i] for i in range(len(events))}

        if events == {}:
            return {1: {'EventName': '', 'SiteName': '', 'StartDate': '', 'EndDate': '', 'StaffCount': ''}}
        else:
            return events


class StaffEventDetail:
    """(30) MANAGER DAILY DETAIl"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, eventname, sitename, startdate):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT EndDate, DateDiff(EndDate, StartDate) + 1 AS Duration, Capacity, Price, Description "
                           f"FROM event WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}'")
            details = cursor.fetchone()

            enddate, duration, cap, price, desc = details['EndDate'], details['Duration'], details['Capacity'], details['Price'], details['Description']

            cursor.execute(f"SELECT GROUP_CONCAT(CONCAT(FirstName, ' ', LastName) ORDER BY FirstName ASC) AS StaffNames FROM assignto JOIN user ON StaffUsername = Username WHERE "
                           f"EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}'")
            staffnames = cursor.fetchone()['StaffNames']

        return enddate, duration, cap, price, desc, staffnames


class visitorExploreEvent:
    """(33) Visitor Explore Event"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, identifier):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT EventName, SiteName, StartDate, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate))")
            events = cursor.fetchall()

            for i in events:
                for key in i:
                    i[key] = ""

            events = {1: events[1]}  # Returns just col names, as we have to load a blank table to start with.

            cursor.execute("SELECT EventName, SiteName, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1 ")
            eventNames = [f"{d['EventName']}" for d in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT Name FROM site WHERE 1=1 ")
            siteNames = [f"{d['Name']}" for d in cursor.fetchall()]

            cursor.execute("SELECT EventName, SiteName, StartDate, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1 ")
            startDates = [f"{d['StartDate']}" for d in cursor.fetchall()]

            cursor.execute("SELECT EventName, SiteName, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1 ")
            ticketPrices = [f"{d['Price']}" for d in cursor.fetchall()]

            cursor.execute("SELECT EventName, SiteName, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1 ")
            ticketRemainings = [f"{d['TicketsRemaining']}" for d in cursor.fetchall()]

            cursor.execute("SELECT EventName, SiteName, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1 ")
            totalVisits = [f"{d['TotalNumVisits']}" for d in cursor.fetchall()]

            cursor.execute("SELECT EventName, SiteName, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT EventName, SiteName, StartDate, Price, Capacity FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1 ")
            myVisits = [f"{d['MyVisits']}" for d in cursor.fetchall()]

        return events, eventNames, siteNames, startDates, ticketPrices, ticketRemainings, totalVisits, myVisits

    def filter(self, identifier, event=None, site=None, keyword=None, startDate=None, endDate=None, TVR1=None, TVR2=None, TPR1=None, TPR2=None, includeVisited=None, includeSoldOut=None, sort='EventName'):

        query = "SELECT EventName, SiteName, StartDate, Price, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ((SELECT * FROM event) AS e LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \""+identifier+"\" GROUP BY EventName, SiteName, StartDate) AS myve ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)) WHERE 1=1"

        if event is not None:
           query += f" AND EventName = '{event}' "

        if site is not None:
           query += f" AND SiteName = '{site}' "

        if keyword is not None:
           query += f" AND Description LIKE '%{keyword}%' "

        if startDate is not None and endDate is not None:
           query += f" AND startDate BETWEEN '{startDate}' AND '{endDate}' "
           query += f" AND endDate BETWEEN '{startDate}' AND '{endDate}' "
        elif startDate is not None:
           query += f" AND startDate >= '{startDate}' "
        elif endDate is not None:
           query += f" AND endDate <= '{endDate}' "

        if TVR1 is not None:
           query += f" AND IFNULL(TotalVisits, 0) >= '{TVR1}' "

        if TVR2 is not None:
           query += f" AND IFNULL(TotalVisits, 0) <= '{TVR2}' "

        if TPR1 is not None:
           query += f" AND Price >= '{TPR1}' "

        if TPR2 is not None:
           query += f" AND Price <= '{site}' "

        if includeVisited is not '1':
           query += f" AND IFNULL(MyCount, 0) = 0 "

        if includeSoldOut is not '1':
           query += f" AND (Capacity - IFNULL(TotalVisits, 0)) > 0 "

        query += f' ORDER BY {sort} DESC'

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            events = cursor.fetchall()

        for i in events:
            for key in i:
                i[key] = str(i[key])
        events = {i+1: events[i] for i in range(len(events))}
        print(events)
        # for d in events.values():
        #     d['OpenEveryday'] = 'false' if d['OpenEveryday'] == '0' else 'true'

        if events == {}:
            return self.load(identifier)[0]
        else:
            return events


class visitorEventDetail:
    """(34) Visitor Event Detail"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, identifier, eventname, sitename, startdate):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT EventName, SiteName, Price, Description, StartDate, EndDate, (Capacity - IFNULL(TotalVisits, 0)) AS TicketsRemaining, IFNULL(TotalVisits, 0) AS TotalNumVisits, IFNULL(MyCount, 0) AS MyVisits FROM ("
                            "(SELECT * FROM event) AS e "
                            "LEFT JOIN (SELECT EventName AS veEventName, SiteName AS veSiteName, StartDate AS veStartDate, COUNT(*) AS TotalVisits "
                            "FROM visitevent GROUP BY EventName, SiteName, StartDate) AS ve "
                            "ON (e.EventName = ve.veEventName AND e.SiteName = ve.veSiteName AND e.StartDate = ve.veStartDate) "
                            "LEFT JOIN (SELECT EventName AS MYEventName, SiteName AS MYSiteName, StartDate AS MYStartDate, COUNT(*) AS MyCount FROM visitevent WHERE visUsername = \"" + identifier + "\" "
                            "GROUP BY EventName, SiteName, StartDate) AS myve "
                            "ON (e.EventName = myve.MYEventName AND e.SiteName = myve.MYSiteName AND e.StartDate = myve.MYStartDate)"
                            ")"
                            f"WHERE EventName = '{eventname}' AND SiteName = '{sitename}' AND StartDate = '{startdate}'")
            event = cursor.fetchone()
            eventName, siteName, startDate, endDate, ticketPrice, ticketsRemaining, description = event['EventName'], event['SiteName'], event['StartDate'], event['EndDate'], event['Price'], event['TicketsRemaining'], event['Description']
        return eventName, siteName, startDate, endDate, ticketPrice, ticketsRemaining, description

class visitorTransitDetail:
    def __init__(self, connection):
        self.connection = connection

    def load(self, sitename):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT c.Route, c.TransportType, Price, cc.NumConnectedSites FROM ("
                            "(SELECT Route, TransportType FROM connect WHERE SiteName = \'" +sitename+ "\') AS c "
                            "JOIN (SELECT * FROM transit) AS t "
                            "ON (t.Route = c.Route AND t.TransportType = c.TransportType) "
                            "JOIN (SELECT COUNT(*) AS NumConnectedSites, Route, TransportType FROM connect GROUP BY Route, TransportType) AS cc "
                            "ON (c.Route = cc.Route AND c.TransportType = cc.TransportType)"
                            ")")
            routes = cursor.fetchall()

            for i in routes:
                for key in i:
                    i[key] = ""

            routes = {1: routes[1]}

            cursor.execute("SELECT c.Route, c.TransportType, Price, cc.NumConnectedSites FROM ("
                            "(SELECT Route, TransportType FROM connect WHERE SiteName = \'" +sitename+ "\') AS c "
                            "JOIN (SELECT * FROM transit) AS t "
                            "ON (t.Route = c.Route AND t.TransportType = c.TransportType) "
                            "JOIN (SELECT COUNT(*) AS NumConnectedSites, Route, TransportType FROM connect GROUP BY Route, TransportType) AS cc "
                            "ON (c.Route = cc.Route AND c.TransportType = cc.TransportType)"
                            ")")
            transportTypes = [f"{d['TransportType']}" for d in cursor.fetchall()]
        return routes, transportTypes

    def filter(self, transporttype):
        query = ("SELECT c.Route, c.TransportType, Price, cc.NumConnectedSites FROM ("
                "(SELECT Route, TransportType FROM connect WHERE SiteName = \'" +sitename+ "\') AS c "
                "JOIN (SELECT * FROM transit) AS t "
                "ON (t.Route = c.Route AND t.TransportType = c.TransportType) "
                "JOIN (SELECT COUNT(*) AS NumConnectedSites, Route, TransportType FROM connect GROUP BY Route, TransportType) AS cc "
                "ON (c.Route = cc.Route AND c.TransportType = cc.TransportType)"
                ")")
        query += "WHERE TransportType = \'" +transporttype+ "\'"

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            routes = cursor.fetchall()

        for i in routes:
            for key in i:
                i[key] = str(i[key])
        routes = {i+1: routes[i] for i in range(len(routes))}

        return routes

class VisitorExploreSite:
    """(35) VISITOR EXPLORE SITE"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, username):
        """Given username, create all the views"""
        with self.connection.cursor() as cursor:
            cursor.execute(f"CREATE OR REPLACE VIEW `SiteTotal_view` AS select SiteName, EventName, "\
                f"Date, TotalVisits, OpenEveryday from ((select SiteName, ' ' as EventName, "\
                f"Date, Count(*) as TotalVisits from visitSite group by SiteName, EventName, "\
                f"Date union all select SiteName, EventName, Date, Count(*) as TotalVisits from "\
                f"visitEvent group by SiteName, EventName, Date) as T join (select Name, OpenEveryday "\
                f"from Site) as s on s.Name = T.SiteName);")
            self.connection.commit()

            cursor.execute(f"CREATE OR REPLACE VIEW `SiteVis_view` AS select SiteName, EventName, Date, MyVisits, "\
                f"OpenEveryday from ((select SiteName, ' ' as EventName, Date, Count(*) as MyVisits from "\
                f"visitSite where VisUsername = '{username}' group by SiteName, EventName, Date union all "\
                f"select SiteName, EventName, Date, Count(*) as MyVisits from visitEvent where VisUsername "
                f"= '{username}' group by SiteName, EventName, Date) as T1 join (select Name, OpenEveryday "\
                "from Site) as s1 on s1.Name = T1.SiteName );")
            self.connection.commit()

            cursor.execute(f"CREATE OR REPLACE VIEW `OMG_view` AS select m1.SiteName, m1.Date, m1.TotalVisits, "\
                f"m1.MyVisits, m1.OpenEveryday, m2.EventCount from (SELECT f1.SiteName, f1.EventName, f1.Date, "\
                f"f1.TotalVisits, f1.OpenEveryday, IFNULL(f2.MyVisits, 0) as MyVisits FROM SiteTotal_View as f1 "\
                f"LEFT JOIN SiteVis_View as f2 ON f1.SiteName = f2.SiteName and f1.EventName = f2.EventName and "\
                f"f1.Date = f2.Date) as m1 left join (select SiteName, count(EventName) as EventCount from (SELECT "\
                f"f1.SiteName, f1.EventName, f1.Date, f1.TotalVisits, f1.OpenEveryday, IFNULL(f2.MyVisits, 0) as "\
                f"MyVisits FROM SiteTotal_View as f1 LEFT JOIN SiteVis_View as f2 ON f1.SiteName = f2.SiteName and "\
                "f1.EventName = f2.EventName and f1.Date = f2.Date) as blah where EventName <> ' ' group by SiteName) "\
                f"as m2 on m1.SiteName = m2.SiteName;")
            self.connection.commit()

            cursor.execute(f"select Name from Site;")
            sites = cursor.fetchall()
            sites = [i['Name']for i in sites]
            sites = ['Any'] + sites
            return sites

    def filter(self, name=None, openEveryday=None, startDate=None, endDate=None, visitRangea=None, visitRangeb=None, countRangea=None, countRangeb=None, includeVisited=None, sort="SiteName"):
        """Given all the filter requirement, return dict of all site details"""
        query = f"select SiteName, EventCount, sum(TotalVisits) as TotalVisits, sum(MyVisits) as MyVisits from OMG_view "

        if includeVisited == '1':
            query += f"where (MyVisits = 0 OR MyVisits = 1) "
        else:
            query += f"where MyVisits = 0 "

        if name:
            query += f"and SiteName = '{name}' "

        if openEveryday:
            query += f"and OpenEveryday = {openEveryday} "

        if startDate:
            query += f"and Date >= '{startDate}' "

        if endDate:
            query += f"and Date <= '{endDate}' "

        query += f"group by SiteName HAVING SUM(EventCount) >= 0 "

        if visitRangea:
            query += f"and SUM(TotalVisits) >= {visitRangea} "

        if visitRangeb:
            query += f"and SUM(TotalVisits) <= {visitRangeb} "

        if countRangea:
            query += f"and SUM(EventCount) >= {countRangea} "

        if countRangeb:
            query += f"and SUM(EventCount) <= {countRangeb} "

        query += f"order by {sort}"

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            siteDetails = cursor.fetchall()


        if siteDetails:
            for i in siteDetails:
                for key in i:
                    i[key] = str(i[key])
            siteDetails = {i+1: siteDetails[i] for i in range(len(siteDetails))}
        else:
            siteDetails = {1:{"SiteName":"","EventCount":"","TotalVisits":"","MyVisits":""}}

        return siteDetails



class visitorSiteDetail:
    """(37) Visitor Site Detail"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, sitename):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT Name, OpenEveryday, Address FROM site WHERE Name = \'" +sitename+ "\'")
            site = cursor.fetchone()
            siteName, openEveryday, address = site["Name"], site["OpenEveryday"], site["Address"]
            if(openEveryday == "0"):
                openEveryday = "No"
            else:
                openEveryday = "Yes"
            return siteName, openEveryday, address


class VisitHistory:
    """(38) VISTOR VISIT HISTORY"""

    def __init__(self, connection):
        self.connection = connection

    def load(self, username):
        """Given a username, return a list of sites and visit history"""
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT Name AS SiteName FROM site")
            sites = cursor.fetchall()
            sites = [i['SiteName'] for i in sites]

            history = {1: {'Date': '', 'EventName': '', 'SiteName': '', 'Price': ''}}
        return sites, history

    def filter(self, username, startDate=None, endDate=None, event=None, site=None, sort='Date'):
        """Given username or other filter requirements, return a dict represents visit history"""
        query = f"select Date, EventName, SiteName, Price from (select v.VisUsername, v.SiteName, v.EventName, v.Date, e.Price from VisitEvent as v join Event as e " \
            f"where v.SiteName = e.SiteName and v.EventName=e.EventName and v.StartDate = e.StartDate " \
            f"union all select VisUsername, Sitename, ' ' as EventName, Date, 0 as Price from visitSite) as fullTable " \
            f"where VisUsername = '{username}' "

        if startDate and endDate:
            query += f"and Date >= '{startDate}' and Date <= '{endDate}' "
        elif startDate:
            query += f"and Date >= '{startDate}' "
        elif endDate:
            query += f"and Date <= '{endDate}' "

        if site:
            query += f"and SiteName = '{site}' "

        if event:
            query += f"and EventName LIKE '%{event}%' "

        # or order by EventName, SiteName, Price
        query += f"ORDER BY {sort};"

        with self.connection.cursor() as cursor:
            print(query)
            cursor.execute(query)
            history = cursor.fetchall()
        pprint(history)
        for i in history:
            for key in i:
                i[key] = str(i[key])
        pprint(history)
        history = {i + 1: history[i] for i in range(len(history))}
        pprint(history)
        if history == {}:
            return self.load(username)[1]
        else:
            return history
