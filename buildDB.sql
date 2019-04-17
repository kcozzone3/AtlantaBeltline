
DROP DATABASE IF EXISTS Beltline;
CREATE DATABASE Beltline;
USE Beltline;

CREATE TABLE User
   	 ( Username varchar(16) NOT NULL,
   	   Password varchar(64) NOT NULL, 
        	   
FirstName varchar(32),
      	LastName varchar(32),
      	Status varchar(16), 
      	PRIMARY KEY (Username)
	
   	 );

CREATE TABLE Emails
   	 ( Username varchar(16) NOT NULL,
      	Email varchar(32) NOT NULL,
     	 
      	PRIMARY KEY (Username, Email),
      	FOREIGN KEY (Username) REFERENCES User(Username)
      	
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE Visitor
   	 ( VisUsername varchar(16) NOT NULL,
     	 
      	PRIMARY KEY (VisUsername),
      	FOREIGN KEY (VisUsername) REFERENCES User(Username)
	
	ON UPDATE CASCADE
	ON DELETE CASCADE  
      	);
     	 
CREATE TABLE Employee
   	 ( EmpUsername varchar(16) NOT NULL,
      	EmployeeID char(9) NOT NULL,
      	Phone char(10) NOT NULL,
      	Address varchar(64),
      	City varchar(32),
      	State varchar(32),
      	Zipcode char(5),
        
	    UNIQUE EmployeeID (EmployeeID), 
	    UNIQUE Phone (Phone),
      	PRIMARY KEY (EmpUsername),
      	FOREIGN KEY (EmpUsername) REFERENCES User(Username)

	ON UPDATE CASCADE
            ON DELETE CASCADE

      	);


CREATE TABLE Administrator
   	 ( AdminUsername varchar(16) NOT NULL,
   	 
      	PRIMARY KEY (AdminUsername),
      	FOREIGN KEY (AdminUsername) REFERENCES Employee(EmpUsername)

	ON UPDATE CASCADE
	ON DELETE CASCADE
      	);
	

CREATE TABLE Manager
   	 ( ManUsername varchar(16) NOT NULL,
   	 
      	PRIMARY KEY (ManUsername),
      	FOREIGN KEY (ManUsername) REFERENCES Employee(EmpUsername)

ON UPDATE CASCADE
            ON DELETE CASCADE  
      	);
     	 
CREATE TABLE Staff
   	 ( StaffUsername varchar(16) NOT NULL,
   	 
   	 PRIMARY KEY (StaffUsername),
      	FOREIGN KEY (StaffUsername) REFERENCES Employee(EmpUsername)

	ON UPDATE CASCADE
            ON DELETE CASCADE
    	);
   	 
CREATE TABLE Transit
   	 ( TransportType varchar(16) NOT NULL,
      	Route varchar(32) NOT NULL,
      	Price decimal(9,2) NOT NULL,

      	PRIMARY KEY (TransportType, Route)

      	);
     	 
CREATE TABLE Site
   	 ( Name varchar(64) NOT NULL,
      	Address varchar(64) NOT NULL,
      	Zipcode int(5),
      	OpenEveryday bool NOT NULL,
      	ManUsername varchar(16) NOT NULL,
     	 
      	PRIMARY KEY (Name),
      	FOREIGN KEY (ManUsername) REFERENCES Manager(ManUsername)
	
	ON DELETE RESTRICT 
	ON UPDATE CASCADE
      	);

CREATE TABLE Event   
   	 ( SiteName varchar(64) NOT NULL,
      	EventName varchar(64) NOT NULL, 
      	StartDate date NOT NULL,
      	EndDate date NOT NULL,
      	Price decimal(9,2) NOT NULL,
     	Capacity int,
      	MinStaffReq int NOT NULL,
     	Description varchar(800) NOT NULL,

      	PRIMARY KEY (SiteName, EventName, StartDate),
      	FOREIGN KEY (SiteName) REFERENCES Site(Name)
     	 
      	ON DELETE CASCADE
	ON UPDATE CASCADE
      	);

CREATE TABLE Take
   	 ( Username varchar(16) NOT NULL,
      	TransportType varchar(16) NOT NULL,
      	Route varchar(32) NOT NULL,
      	Date date NOT NULL,
     	 
      	PRIMARY KEY (Username, TransportType, Route, Date),
      	FOREIGN KEY (Username) REFERENCES User(Username)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
      	FOREIGN KEY (TransportType, Route) REFERENCES Transit(TransportType, Route)
	ON UPDATE CASCADE
	ON DELETE RESTRICT
      	);
     	 

CREATE TABLE AssignTo
   	 ( StaffUsername varchar(16) NOT NULL,
      	SiteName varchar(64) NOT NULL,
      	EventName varchar(64) NOT NULL,
      	StartDate date NOT NULL,
     	 
      	PRIMARY KEY (StaffUsername, SiteName, EventName, StartDate),
      	FOREIGN KEY (StaffUsername) REFERENCES Staff(StaffUsername)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
      	FOREIGN KEY (SiteName, EventName, StartDate) REFERENCES Event(SiteName,  EventName, StartDate)
	ON UPDATE CASCADE
	ON DELETE CASCADE
      	);
     	 
CREATE TABLE VisitSite
   	 ( VisUsername varchar(16) NOT NULL,
      	SiteName varchar(64) NOT NULL,
      	Date date NOT NULL,
     	
      	PRIMARY KEY (VisUsername, SiteName, Date),
      	FOREIGN KEY (VisUsername) REFERENCES Visitor(VisUsername)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
      	FOREIGN KEY (SiteName) REFERENCES Site(Name)
	ON UPDATE CASCADE
	ON DELETE CASCADE
      	);

CREATE TABLE VisitEvent
   	 ( VisUsername varchar(16) NOT NULL,
      	SiteName varchar(64) NOT NULL,
      	EventName varchar(64) NOT NULL,
      	StartDate date NOT NULL,
      	Date date NOT NULL,
     	 
      	PRIMARY KEY (VisUsername, SiteName, EventName, StartDate, Date),
      	FOREIGN KEY (VisUsername) REFERENCES Visitor(VisUsername)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
      	FOREIGN KEY (SiteName, EventName, StartDate) REFERENCES Event(SiteName, EventName, StartDate)
	ON UPDATE CASCADE
	ON DELETE CASCADE
      	);

CREATE TABLE Connect
   	 ( SiteName varchar(64) NOT NULL,
      	TransportType varchar(16) NOT NULL,
      	Route varchar(32) NOT NULL,
     	 
      	PRIMARY KEY (SiteName, TransportType, Route),
      	FOREIGN KEY (SiteName) REFERENCES Site(Name)
	ON DELETE CASCADE
	ON UPDATE CASCADE,
      	FOREIGN KEY (TransportType, Route) REFERENCES Transit(TransportType, Route)
	ON DELETE RESTRICT
	ON UPDATE CASCADE

      	);

CREATE VIEW transit_connect AS
SELECT T.TransportType, T.Route, T.Price, C.SiteName, tmp.num_sites as NumSites
    FROM transit AS T JOIN connect AS C 
                      ON (T.TransportType, T.Route) = (C.TransportType, C.Route) 
                      JOIN (SELECT TransportType, Route, count(*) AS num_sites FROM connect GROUP BY TransportType, Route) AS tmp 
                      ON (T.TransportType, T.Route) = (tmp.TransportType, tmp.Route);
                      
CREATE VIEW emp_profile AS
SELECT E.EmpUsername, E.EmployeeID, E.Phone, Concat(E.Address, ', ', E.City, ' ', E.State, ', ', E.Zipcode) as Address
	FROM Employee as E;

CREATE VIEW user_type AS  -- https://stackoverflow.com/questions/63447/how-do-i-perform-an-if-then-in-an-sql-select <--- NEAT!!! Also, weird collate errors for some reason :/
SELECT Username, CASE WHEN EXISTS(SELECT * FROM manager WHERE ManUsername = u.Username) = 1 THEN 'Manager' collate utf8mb4_general_ci
				 WHEN EXISTS(SELECT * FROM staff WHERE StaffUsername = u.Username) = 1 THEN 'Staff' collate utf8mb4_general_ci
				 WHEN EXISTS(SELECT * FROM visitor WHERE VisUsername = u.Username) = 1 THEN 'Visitor' collate utf8mb4_general_ci
                             ELSE 'User' collate utf8mb4_general_ci
       END AS UserType
FROM User AS u WHERE NOT EXISTS(SELECT * FROM administrator WHERE AdminUsername = u.Username);

