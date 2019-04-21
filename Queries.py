import pymysql
from datetime import datetime


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


    def submit(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(f"UPDATE user SET Status = 'Approved' WHERE Username = '{username}'")
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

        query = "SELECT Route, TransportType, Price, NumSites AS '# Connected Sites', " \
                "NumTaken as '# Transits Logged'  FROM transit_connect NATURAL JOIN " \
                "(SELECT TransportType, Route, COUNT(*) as NumTaken FROM take GROUP BY TransportType, Route) " \
                "as tmp WHERE 1=1 "
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


"""Screen 35"""
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
            sites = ['--ALL--'] + sites
            return sites

    def filter(self, name='--ALL--', openEveryday='--ALL--', startDate=None, endDate=None, visitRangea=None, visitRangeb=None, countRangea=None, countRangeb=None, includeVisited=False, sort="SiteName"):
        """Given all the filter requirement, return dict of all site details"""
        query = f"select SiteName, EventCount, sum(TotalVisits) as TotalVisits, sum(MyVisits) as MyVisits from OMG_view "

        if includeVisited:
            query += f"where MyVisits = 0 and MyVisits = 1 "
        else:
            query += f"where MyVisits = 0 "

        if name != '--ALL--':
            query += f"and SiteName = '{name}' "

        if openEveryday != '--ALL--':
            query += f"and OpenEveryday = '{openEveryday}' "
        elif openEveryday == '--ALL--':
            query += f"and OpenEveryday = 0 and OpenEveryday = 1 "

        if startDate:
            query += f"and Date >= '{startDate}' "
        
        if endDate:
            query += f"and Date <= '{endDate}' "

        if visitRangea:
            query += f"and TotalVisits >= '{visitRangea}' "

        if visitRangeb:
            query += f"and TotalVisits <= '{visitRangeb}' "

        if countRangea:
            query += f"and EventCount >= '{countRangea}' "

        if countRangeb:
            query += f"and EventCount <= '{countRangeb}' "

        query += f"group by SiteName "

        if sort:
            query += f"order by '{sort}';"


        with self.connection.cursor() as cursor:
            cursor.execute(query)
            siteDetails = cursor.fetchall()

        if siteDetails:
            for i in siteDetails:
                for key in i:
                    i[key] = str(i[key])
            siteDetails = {i+1: siteDetails[i] for i in range(len(siteDetails))}
        else:
            siteDetails = {}

        return siteDetails


"""Screen 38"""
class visitorVisitHistory:
    """(38) VISTOR VISIT HISTORY"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, username):
        """Given a username, return a list of sites and visit history"""
        with self.connection.cursor() as cursor:
            cursor.execute(f"select distinct SiteName from (select v.VisUsername, v.SiteName, v.EventName, v.Date, e.Price from VisitEvent as v " \
                           f"join Event as e where v.SiteName = e.SiteName and v.EventName=e.EventName and v.StartDate = e.StartDate and VisUsername = ' {username}' " \
                           f"union all select VisUsername, Sitename, ' ' as EventName, Date, 0 as Price from visitSite where VisUsername = '{username}') as siteTable;")
            sites = cursor.fetchall()
            sites = [i['SiteName']for i in sites]

            cursor.execute(f"select v.Date, v.EventName, v.SiteName, e.Price from VisitEvent as v join Event as e "\
                            f"where v.SiteName = e.SiteName and v.EventName=e.EventName and v.StartDate = e.StartDate and VisUsername = 'mary.smith' "\
                            f"union all select Date, ' ' as EventName, Sitename, 0 as Price from visitSite where VisUsername = 'mary.smith' order by Date;")
            history = cursor.fetchall()

            if history:
                for i in history:
                    for key in i:
                        i[key] = str(i[key])
                history = {i+1: history[i] for i in range(len(history))}
            else:
                history = {}

        return sites, history

    def filter(self, username, event=None, site=None, startDate=None, endDate=None, sort='Date'):
        """Given username or other filter requirements, return a list represents visit history"""
        query = f"select *  from (select v.VisUsername, v.SiteName, v.EventName, v.Date, e.Price from VisitEvent as v join Event as e "\
                f"where v.SiteName = e.SiteName and v.EventName=e.EventName and v.StartDate = e.StartDate "\
                f"union all select VisUsername, Sitename, ' ' as EventName, Date, 0 as Price from visitSite) as fullTable "\
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
            query += f"and EventName = '{event}' "

        # or order by EventName, SiteName, Price
        query += f"ORDER BY '{sort}';"

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            history = cursor.fetchall()

        if history:
            for i in history:
                for key in i:
                    i[key] = str(i[key])
            history = {i+1: history[i] for i in range(len(history))}
        else:
            history = {}

        return history


"""Scrren 30"""
class ViewDailyDetail:
    """(30) MANAGER DAILY DETAIL"""
    def __init__(self, connection):
        self.connection = connection

    def load(self, username, date, sort='EventName'):
        """Given username and date, return a dict of daily detail information of the event.
            Duplicate event names are returned b/c of staff name, have to parse in the frontend"""
        with self.connection.cursor() as cursor:
            cursor.execute(f"CREATE OR REPLACE VIEW `Staff_view` AS select StaffUsername, a.EventName, "\
                f"a.SiteName, a.StartDate from AssignTo as a join (select EventName, SiteName, "\
                f"StartDate from AssignTo where StaffUsername = '{username}') as b on "\
                f"a.EventName = b.EventName and  a.SiteName = b.SiteName and a.StartDate = b.StartDate;")
            self.connection.commit()

            cursor.execute(f"CREATE OR REPLACE VIEW `CountVis_view` AS select count(VisUsername) AS "\
                f"CountVis, EventName, SiteName, StartDate, Date from visitevent group by "
                f"EventName, startDate, SiteName, Date;")
            self.connection.commit()

            query = "select EventName, StaffUsername, CountVis, (CountVis * Price) as 'Revenue' from "\
            f"(select t1.EventName, t1.StaffUserName, t2.CountVis, t2.Date, t3.Price from Staff_view as "\
            f"t1 join CountVis_view as t2 on t1.EventName = t2.EventName and t1.SiteName = t2.SiteName and "\
            f"t1.StartDate = t2.StartDate join Event as t3 on t1.EventName = t3.EventName and t1.SiteName = "\
            f"t3.SiteName and t1.StartDate = t3.StartDate) as BigTable "

            query += f"where Date = '{date}' order by '{sort}';"
            cursor.execute(query)
            dailyDetails = cursor.fetchall()

            if dailyDetails:
                for i in dailyDetails:
                    for key in i:
                        i[key] = str(i[key])
                dailyDetails = {i+1: dailyDetails[i] for i in range(len(dailyDetails))}
            else:
                dailyDetails = {}
        return dailyDetails
