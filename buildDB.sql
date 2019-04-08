
DROP DATABASE IF EXISTS Beltline;
CREATE DATABASE Beltline;
USE Beltline;

CREATE TABLE User
   	 ( Username varchar(16) NOT NULL,
   	   Password varchar(32) NOT NULL, 
        	   
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
      	EmployeeID int NOT NULL,
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
    
     


