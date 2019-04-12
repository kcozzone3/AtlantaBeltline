from tkinter import *
import pymysql
import hashlib
from tkinter import messagebox
import random

class Beltline:

    def __init__(self):

        # database connection, not needed yet, will need upon adding SQL commands
        self.db = self.connect()
        self.cursor = self.db.cursor()

        #when we call init, we need to create the first window - login. We build the window and display it separately
        self.initLoginWindow()
        self.displayLoginWindow(self.loginWindow)

        #we make the login window the main loop (causing the program to actually start and run
        self.loginWindow.mainloop()



        #if the main loop closes, we exit the program
        sys.exit()


    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                                               LOGIN                                                            #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initLoginWindow(self):

        #this creates a new window (Tk())
        self.loginWindow = Tk()

        #hide the window using the withdraw method
        self.loginWindow.withdraw()

        #set the title for the window, along with a white background color
        self.loginWindow.title("Beltline Login")
        self.loginWindow.config(background='#ffffff')

        #show the window again
        self.loginWindow.deiconify()

    def displayLoginWindow(self, loginWindow):

        #login and password entry variables used for login input
        self.loginUsername = StringVar()
        self.loginPassword = StringVar()

        #create a label (text) on the login window with the text of login with certain other properties
        loginLabel = Label(loginWindow, text="Login", font="Helvetica", foreground='#000000', background='#ffffff')

        #we place this on the grid in 1,3 with some padding to make it look nice. Sticky determines where in the cell
        #it is placed
        loginLabel.grid(row=1, column=2, pady=(2,6), sticky=W)

        # create a username label and place in the grid
        usernameLabel = Label(loginWindow, text="Username", foreground='#000000', background='#ffffff')
        usernameLabel.grid(row=2, column=1, padx=(2,5), pady=(0,4), sticky=W)

        # create a username entry box, accounting for the inputted text to be the login username. We also set a width
        # for how many characters can be easily displayed
        usernameBox = Entry(loginWindow, textvariable=self.loginUsername, width=20)
        usernameBox.grid(row=2, column=2, padx=(0,2), pady=(0,4), sticky=E)

        # Password Label creation
        passwordLabel = Label(loginWindow, text="Password ", foreground='#000000', background='#ffffff')
        passwordLabel.grid(row=4, column=1, padx=(2,5), pady=(0,4), sticky=W)

        # Password Entry Box creation: difference to username is the show='*', which displays *** instead of abc
        passwordBox = Entry(loginWindow, show='*', textvariable=self.loginPassword, width=20)
        passwordBox.grid(row=4, column=2, padx=(0,2), pady=(0,4), sticky=E)

        # create buttons that as of now, do no logic checking, but simply move screens
        loginButton = Button(loginWindow, command=self.onLoginButtonClicked, text="Login", background='#4286f4')
        loginButton.grid(row=5,column=1,padx=(2,2),pady=(2,2), sticky=E)
        registerButton = Button(loginWindow, command=self.onRegisterButtonClicked, text="Register", background='#4286f4')
        registerButton.grid(row=5, column=2, padx=(2, 2), pady=(2, 2))

    def onRegisterButtonClicked(self):
        self.initRegistrationNavigationWindow()
        self.displayRegistrationNavigationWindow(self.registrationNavigationWindow)
        self.loginWindow.withdraw()

    def onLoginButtonClicked(self):
        self.username = self.loginUsername.get()
        self.password = self.loginPassword.get()

        if not self.username:
            messagebox.showwarning("Username Field Empty", "The username field is empty. Please try again.")
            return

        if not self.password:
            messagebox.showwarning("Password Field Empty", "The password field is empty. Please try again.")
            return

        hashedPassword = self.encrypt(self.password)


        usernameValid = self.cursor.execute("SELECT * FROM user where EXISTS (SELECT * FROM user where Username=%s)", self.username)

        if usernameValid == 0:
            messagebox.showwarning("Username Invalid", "This username is not registered in the system.")
            return

        passwordMatching = self.cursor.execute("SELECT * FROM user where EXISTS (SELECT * FROM user where (Username=%s and Password=%s))", (self.username, hashedPassword))

        if passwordMatching == 0:
            messagebox.showwarning("Invalid Login", "This username and password combination is not registered in the system.")
            return


        self.cursor.execute("SELECT status FROM user where Username=%s", self.username)
        accountStatus = self.cursor.fetchone()
        accountStatus = accountStatus.get('status').lower()

        if (accountStatus == "declined"):
            messagebox.showwarning("Banned Account", "Your account has been banned. Please contact an administrator.")
            return
        elif (accountStatus == "pending"):
            messagebox.showwarning("Pending Approval", "Your account is pending approval. Please be patient.")
            return

        isVisitor = self.cursor.execute("SELECT * FROM visitor where EXISTS (SELECT * FROM visitor where VisUsername=%s)", self.username)
        isEmployee = self.cursor.execute("SELECT * FROM employee where EXISTS (SELECT * FROM employee where EmpUsername=%s)", self.username)
        if isEmployee:
            isAdmin = self.cursor.execute("SELECT * FROM administrator where EXISTS (SELECT * FROM administrator where AdminUsername=%s)", self.username)
            isManager = self.cursor.execute("SELECT * FROM manager where EXISTS (SELECT * FROM manager where ManUsername=%s)", self.username)
            isStaff = self.cursor.execute("SELECT * FROM staff where EXISTS (SELECT * FROM staff where StaffUsername=%s)", self.username)

        if isVisitor:
            if isEmployee:
                if isAdmin:
                    messagebox.showwarning("Administrator-Visitor", "Admin-Visitor Functionality not added yet.")
                elif isManager:
                    messagebox.showwarning("Manager-Visitor", "Manager-Visitor Functionality not added yet.")
                elif isStaff:
                    messagebox.showwarning("Staff-Visitor", "Staff-Visitor Functionality not added yet.")
                else:
                    messagebox.showwarning("Uhhh", "You shouldn't be here (employee-visitor).")
            else:
                #Just a visitor
                self.initVisitorFunctionalityWindow()
                self.displayVisitorFunctionalityWindow(self.visitorFunctionalityWindow)
                self.loginWindow.withdraw()
        elif isEmployee:
            if isAdmin:
                messagebox.showwarning("Administrator", "Admin Functionality not added yet.")
            elif isManager:
                messagebox.showwarning("Manager", "Manager Functionality not added yet.")
            elif isStaff:
                messagebox.showwarning("Staff", "Staff Functionality not added yet.")
            else:
                messagebox.showwarning("Uhhh", "You shouldn't be here (employee).")
        else:
            #Just a user
            self.initUserFunctionalityWindow()
            self.displayUserFunctionalityWindow(self.userFunctionalityWindow)
            self.loginWindow.withdraw()


    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                                        PASSWORD HASHING                                                        #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#


    def encrypt(self, unhashed_string):
        hashed_string = hashlib.sha256(unhashed_string.encode()).hexdigest()
        return hashed_string

    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                                REGISTRATION  NAVIGATION                                                        #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initRegistrationNavigationWindow(self):
        self.registrationNavigationWindow = Toplevel()
        self.registrationNavigationWindow.title("Registration")
        self.registrationNavigationWindow.config(background='#ffffff')

    def displayRegistrationNavigationWindow(self, registrationNavigationWindow):
        registerLabel = Label(registrationNavigationWindow, text="Register Navigation", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E)


        userOnlyButton = Button(registrationNavigationWindow, command=self.onUserOnlyButtonClicked, text="User Only",
                                background='#4286f4')
        userOnlyButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)


        visitorOnlyButton = Button(registrationNavigationWindow, command=self.onVisitorOnlyButtonClicked,
                                   text="Visitor Only", background='#4286f4')
        visitorOnlyButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)


        employeeOnlyButton = Button(registrationNavigationWindow, command=self.onEmployeeOnlyButtonClicked,
                                    text="Employee Only", background='#4286f4')
        employeeOnlyButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)


        employeeVisitorButton = Button(registrationNavigationWindow, command=self.onEmployeeVisitorButtonClicked,
                                       text="Employee-Visitor", background='#4286f4')
        employeeVisitorButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)


        backButton = Button(registrationNavigationWindow, command=self.onRegistrationBackButtonClicked, text="Back",
                             background='#4286f4')
        backButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onUserOnlyButtonClicked(self):
        self.initUserOnlyRegistrationWindow()
        self.displayUserOnlyRegistrationWindow(self.userOnlyRegistrationWindow)
        self.registrationNavigationWindow.destroy()

    def onVisitorOnlyButtonClicked(self):
        self.initVisitorOnlyRegistrationWindow()
        self.displayVisitorOnlyRegistrationWindow(self.visitorOnlyRegistrationWindow)
        self.registrationNavigationWindow.destroy()

    def onEmployeeOnlyButtonClicked(self):
        self.initEmployeeOnlyRegistrationWindow()
        self.displayEmployeeOnlyRegistrationWindow(self.employeeOnlyRegistrationWindow)
        self.registrationNavigationWindow.destroy()

    def onEmployeeVisitorButtonClicked(self):
        self.initEmployeeVisitorRegistrationWindow()
        self.displayEmployeeVisitorRegistrationWindow(self.employeeVisitorRegistrationWindow)
        self.registrationNavigationWindow.destroy()

    def onRegistrationBackButtonClicked(self):
        self.registrationNavigationWindow.destroy()
        self.loginWindow.deiconify()

    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                                   USER ONLY REGISTRATION                                                       #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initUserOnlyRegistrationWindow(self):
        self.userOnlyRegistrationWindow = Toplevel()
        self.userOnlyRegistrationWindow.title("Registration -- User")
        self.userOnlyRegistrationWindow.config(background='#ffffff')

    def displayUserOnlyRegistrationWindow(self, userOnlyRegistrationWindow):
        self.registrationFirstName = StringVar()
        self.registrationLastName = StringVar()
        self.registrationUserName = StringVar()
        self.registrationPassword = StringVar()
        self.registrationConfirmPassword = StringVar()

        registerLabel = Label(userOnlyRegistrationWindow, text="User Only Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E, columnspan=2)

        firstNameLabel = Label(userOnlyRegistrationWindow, text = "First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2,5), pady=(0,4), sticky = W)

        firstNameBox = Entry(userOnlyRegistrationWindow, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(userOnlyRegistrationWindow, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2,5), pady=(0,4), sticky=W)

        lastNameBox = Entry(userOnlyRegistrationWindow, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(userOnlyRegistrationWindow, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(userOnlyRegistrationWindow, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(userOnlyRegistrationWindow, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2,5), pady=(0,4), sticky=W)

        passwordBox = Entry(userOnlyRegistrationWindow, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(userOnlyRegistrationWindow, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2,5), pady=(0,4), sticky=W)

        confirmPasswordBox = Entry(userOnlyRegistrationWindow, textvariable=self.registrationConfirmPassword, width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        #EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(userOnlyRegistrationWindow, command=self.onUserOnlyRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(userOnlyRegistrationWindow, command=self.onUserOnlyRegistrationRegisterButtonClicked, text="Register",
                            background='#4286f4')
        registerButton.grid(row=7, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onUserOnlyRegistrationBackButtonClicked(self):
        self.initRegistrationNavigationWindow()
        self.displayRegistrationNavigationWindow(self.registrationNavigationWindow)
        self.userOnlyRegistrationWindow.destroy()


    def onUserOnlyRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()

        if not firstName:
            firstName = ""
        if not lastName:
            lastName = ""

        if not username:
            messagebox.showwarning("Missing Username", "The username field is empty. Please try again.")
            return
        if not password:
            messagebox.showwarning("Missing Password", "The password field is empty. Please try again.")
            return
        if not confirmPassword:
            confirmPassword = ""

        if len(username) > 16:
            messagebox.showwarning("Username too long", "Usernames can have at maximum 16 letters.")
            return

        usernameExists = self.cursor.execute("SELECT * from user where Username=%s", username)
        if usernameExists:
            messagebox.showwarning("Username Already Taken", "This username already exists within the database.")
            return

        if len(password) < 8:
            messagebox.showwarning("Password Too Short", "Passwords must have at least 8 characters.")
            return

        if password != confirmPassword:
            messagebox.showwarning("Password Mismatch", "The password and the confirmed Password do not match.")
            return

        if len(firstName) > 32:
            messagebox.showwarning("First Name too long", "First names can only be 32 characters. Please abbreviate.")
            return
        if len(lastName) > 32:
            messagebox.showwarning("Last Name too long", "Last names can only be 32 characters. Please abbreviate.")
            return

        hashedPassword = self.encrypt(password)
        self.cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)", (username, hashedPassword, firstName, lastName, "Pending"))
        messagebox.showwarning("Registration Successful", "You are now registered. You will need to wait for administrator approval to login.")

        self.userOnlyRegistrationWindow.destroy()
        self.loginWindow.deiconify()


    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                                VISITOR ONLY REGISTRATION                                                       #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initVisitorOnlyRegistrationWindow(self):
        self.visitorOnlyRegistrationWindow = Toplevel()
        self.visitorOnlyRegistrationWindow.title("Registration -- Visitor")
        self.visitorOnlyRegistrationWindow.config(background='#ffffff')

    def displayVisitorOnlyRegistrationWindow(self, visitorOnlyRegistrationWindow):
        self.registrationFirstName = StringVar()
        self.registrationLastName = StringVar()
        self.registrationUserName = StringVar()
        self.registrationPassword = StringVar()
        self.registrationConfirmPassword = StringVar()

        registerLabel = Label(visitorOnlyRegistrationWindow, text="Visitor Only Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E, columnspan=2)

        firstNameLabel = Label(visitorOnlyRegistrationWindow, text = "First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2,5), pady=(0,4), sticky = W)

        firstNameBox = Entry(visitorOnlyRegistrationWindow, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(visitorOnlyRegistrationWindow, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2,5), pady=(0,4), sticky=W)

        lastNameBox = Entry(visitorOnlyRegistrationWindow, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(visitorOnlyRegistrationWindow, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(visitorOnlyRegistrationWindow, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(visitorOnlyRegistrationWindow, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(visitorOnlyRegistrationWindow, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(visitorOnlyRegistrationWindow, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(visitorOnlyRegistrationWindow, textvariable=self.registrationConfirmPassword, width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)



        #EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(visitorOnlyRegistrationWindow, command=self.onVisitorOnlyRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(visitorOnlyRegistrationWindow, command=self.onVisitorOnlyRegistrationRegisterButtonClicked, text="Register",
                            background='#4286f4')
        registerButton.grid(row=7, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onVisitorOnlyRegistrationBackButtonClicked(self):
        self.initRegistrationNavigationWindow()
        self.displayRegistrationNavigationWindow(self.registrationNavigationWindow)
        self.visitorOnlyRegistrationWindow.destroy()


    def onVisitorOnlyRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()

        if not firstName:
            firstName = ""
        if not lastName:
            lastName = ""

        if not username:
            messagebox.showwarning("Missing Username", "The username field is empty. Please try again.")
            return
        if not password:
            messagebox.showwarning("Missing Password", "The password field is empty. Please try again.")
            return
        if not confirmPassword:
            confirmPassword = ""

        if len(username) > 16:
            messagebox.showwarning("Username too long", "Usernames can have at maximum 16 letters.")
            return

        usernameExists = self.cursor.execute("SELECT * from user where Username=%s", username)
        if usernameExists:
            messagebox.showwarning("Username Already Taken", "This username already exists within the database.")
            return

        if len(password) < 8:
            messagebox.showwarning("Password Too Short", "Passwords must have at least 8 characters.")
            return

        if password != confirmPassword:
            messagebox.showwarning("Password Mismatch", "The password and the confirmed Password do not match.")
            return

        if len(firstName) > 32:
            messagebox.showwarning("First Name too long", "First names can only be 32 characters. Please abbreviate.")
            return
        if len(lastName) > 32:
            messagebox.showwarning("Last Name too long", "Last names can only be 32 characters. Please abbreviate.")
            return

        hashedPassword = self.encrypt(password)
        self.cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)", (username, hashedPassword, firstName, lastName, "Pending"))
        self.cursor.execute("INSERT into visitor values (%s)", username)
        messagebox.showwarning("Registration Successful", "You are now registered. You will need to wait for administrator approval to login.")

        self.visitorOnlyRegistrationWindow.destroy()
        self.loginWindow.deiconify()


    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                               EMPLOYEE ONLY REGISTRATION                                                       #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initEmployeeOnlyRegistrationWindow(self):
        self.employeeOnlyRegistrationWindow = Toplevel()
        self.employeeOnlyRegistrationWindow.title("Registration -- Employee")
        self.employeeOnlyRegistrationWindow.config(background='#ffffff')

    def displayEmployeeOnlyRegistrationWindow(self, employeeOnlyRegistrationWindow):
        self.registrationFirstName = StringVar()
        self.registrationLastName = StringVar()
        self.registrationUserName = StringVar()
        self.registrationPassword = StringVar()
        self.registrationConfirmPassword = StringVar()
        self.registrationEmployeeType = StringVar()
        self.registrationEmployeeType.set("")
        self.registrationState = StringVar()
        self.registrationState.set("")
        self.registrationPhone = StringVar()
        self.registrationAddress = StringVar()
        self.registrationCity = StringVar()
        self.registrationZIP = StringVar()

        self.states = ["AL", "AK", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
                       "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH",
                       "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA",
                       "VT", "WA", "WI", "WV", "WY", "other"]

        self.employeeType = ["Manager", "Staff"]

        registerLabel = Label(employeeOnlyRegistrationWindow, text="Employee Only Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E, columnspan=2)

        firstNameLabel = Label(employeeOnlyRegistrationWindow, text = "First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2,5), pady=(0,4), sticky = W)

        firstNameBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(employeeOnlyRegistrationWindow, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2,5), pady=(0,4), sticky=W)

        lastNameBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(employeeOnlyRegistrationWindow, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(employeeOnlyRegistrationWindow, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(employeeOnlyRegistrationWindow, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationConfirmPassword,
                                   width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        userTypeLabel = Label(employeeOnlyRegistrationWindow, text="Employee Type", background='#ffffff')
        userTypeLabel.grid(row=7, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        userTypeDropdown = OptionMenu(employeeOnlyRegistrationWindow, self.registrationEmployeeType, *self.employeeType)
        userTypeDropdown.grid(row=7, column=2, padx=(8, 5), pady=(0, 4), sticky=W)

        phoneLabel = Label(employeeOnlyRegistrationWindow, text="Phone", background='#ffffff')
        phoneLabel.grid(row=8, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        phoneBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationPhone, width=20)
        phoneBox.grid(row=8, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        addressLabel = Label(employeeOnlyRegistrationWindow, text="Address", background='#ffffff')
        addressLabel.grid(row=9, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        addressBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationAddress, width=20)
        addressBox.grid(row=9, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        cityLabel = Label(employeeOnlyRegistrationWindow, text="City", background='#ffffff')
        cityLabel.grid(row=10, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        cityBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationCity, width=20)
        cityBox.grid(row=10, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        stateLabel = Label(employeeOnlyRegistrationWindow, text="State", background='#ffffff')
        stateLabel.grid(row=11, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        stateDropdown = OptionMenu(employeeOnlyRegistrationWindow, self.registrationState, *self.states)
        stateDropdown.grid(row=11, column=2, padx=(8, 5), pady=(0, 4), sticky=W)

        zipLabel = Label(employeeOnlyRegistrationWindow, text="Zipcode", background='#ffffff')
        zipLabel.grid(row=12, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        zipBox = Entry(employeeOnlyRegistrationWindow, textvariable=self.registrationZIP, width=20)
        zipBox.grid(row=12, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        #EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(employeeOnlyRegistrationWindow, command=self.onEmployeeOnlyRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=13, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(employeeOnlyRegistrationWindow, command=self.onEmployeeOnlyRegistrationRegisterButtonClicked, text="Register",
                            background='#4286f4')
        registerButton.grid(row=13, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onEmployeeOnlyRegistrationBackButtonClicked(self):
        self.initRegistrationNavigationWindow()
        self.displayRegistrationNavigationWindow(self.registrationNavigationWindow)
        self.employeeOnlyRegistrationWindow.destroy()

    def onEmployeeOnlyRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()

        employeeType = self.registrationEmployeeType.get()
        state = self.registrationState.get()
        phone = self.registrationPhone.get()
        address = self.registrationAddress.get()
        city = self.registrationCity.get()
        zipcode = self.registrationZIP.get()

        if not firstName:
            firstName = ""
        if not lastName:
            lastName = ""
        if not state:
            state = ""
        if not address:
            address = ""
        if not city:
            city = ""
        if not zipcode:
            zipcode = ""
        if not confirmPassword:
            confirmPassword = ""


        if not username:
            messagebox.showwarning("Missing Username", "The username field is empty. Please try again.")
            return
        if not password:
            messagebox.showwarning("Missing Password", "The password field is empty. Please try again.")
            return
        if not employeeType:
            messagebox.showwarning("Missing Employee Type", "Please select an employee type.")
            return
        if not phone:
            messagebox.showwarning("Missing Phone Number", "Please enter a phone number in format xxxxxxxxxx")
            return


        if len(username) > 16:
            messagebox.showwarning("Username too long", "Usernames can have at maximum 16 letters.")
            return

        usernameExists = self.cursor.execute("SELECT * from user where Username=%s", username)
        if usernameExists:
            messagebox.showwarning("Username Already Taken", "This username already exists within the database.")
            return


        if len(password) < 8:
            messagebox.showwarning("Password Too Short", "Passwords must have at least 8 characters.")
            return

        if password != confirmPassword:
            messagebox.showwarning("Password Mismatch", "The password and the confirmed Password do not match.")
            return

        if len(firstName) > 32:
            messagebox.showwarning("First Name too long", "First names can only be 32 characters. Please abbreviate.")
            return
        if len(lastName) > 32:
            messagebox.showwarning("Last Name too long", "Last names can only be 32 characters. Please abbreviate.")
            return
        if len(address) > 64:
            messagebox.showwarning("Address too long", "Addresses are limited to 64 characters. Please abbreviate.")
            return
        if len(phone) > 10 or len(phone) < 10:
            messagebox.showwarning("Phone number incorrect", "Please enter a phone number in format xxxxxxxxxx")
            return
        if len(zipcode) > 5:
            messagebox.showwarning("Zipcode too long", "Please enter a zipcode in format xxxxx")
            return
        if zipcode != "":
            if len(zipcode) < 5:
                messagebox.showwarning("Zipcode too short", "Please enter a zipcode in format xxxxxx")
        if len(city) > 32:
            messagebox.showwarning("City name too long", "The city name is limited to 32 characters. Please abbreviate.")

        phoneExists = self.cursor.execute("SELECT * from employee where Phone=%s", phone)
        if phoneExists:
            messagebox.showwarning("Phone Already Registered", "This phone number is already registered.")

        empId = random.randint(1, 999999999)
        while self.cursor.execute("SELECT * from employee where EmployeeID=%s", empId):
            empId = random.randint(1, 999999999)


        hashedPassword = self.encrypt(password)
        self.cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)", (username, hashedPassword, firstName, lastName, "Pending"))
        self.cursor.execute("INSERT into employee values (%s, %s, %s, %s, %s, %s, %s)", (username, empId, phone, address, city, state, zipcode))

        if employeeType == "Manager":
            self.cursor.execute("INSERT into manager values (%s)", username)
        elif employeeType == "Staff":
            self.cursor.execute("INSERT into staff values (%s)", username)
        else:
            messagebox.showwarning("Uhh", "You shouldn't be here: employee-visitor")

        messagebox.showwarning("Registration Successful", "You are now registered. You will need to wait for administrator approval to login.")

        self.employeeOnlyRegistrationWindow.destroy()
        self.loginWindow.deiconify()


    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                            EMPLOYEE-VISITOR REGISTRATION                                                       #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initEmployeeVisitorRegistrationWindow(self):
        self.employeeVisitorRegistrationWindow = Toplevel()
        self.employeeVisitorRegistrationWindow.title("Registration -- Employee-Visitor")
        self.employeeVisitorRegistrationWindow.config(background='#ffffff')

    def displayEmployeeVisitorRegistrationWindow(self, employeeVisitorRegistrationWindow):
        self.registrationFirstName = StringVar()
        self.registrationLastName = StringVar()
        self.registrationUserName = StringVar()
        self.registrationPassword = StringVar()
        self.registrationConfirmPassword = StringVar()
        self.registrationEmployeeType = StringVar()
        self.registrationState = StringVar()
        self.registrationPhone = StringVar()
        self.registrationAddress = StringVar()
        self.registrationCity = StringVar()
        self.registrationZIP = StringVar()

        self.states = ["AL", "AK", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
                       "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH",
                       "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA",
                       "VT", "WA", "WI", "WV", "WY", "other"]

        self.employeeType = ["Manager", "Staff"]

        registerLabel = Label(employeeVisitorRegistrationWindow, text="Employee-Visitor Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E, columnspan=2)

        firstNameLabel = Label(employeeVisitorRegistrationWindow, text = "First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2,5), pady=(0,4), sticky = W)

        firstNameBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(employeeVisitorRegistrationWindow, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2,5), pady=(0,4), sticky=W)

        lastNameBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(employeeVisitorRegistrationWindow, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(employeeVisitorRegistrationWindow, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(employeeVisitorRegistrationWindow, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationConfirmPassword,
                                   width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        userTypeLabel = Label(employeeVisitorRegistrationWindow, text="Employee Type", background='#ffffff')
        userTypeLabel.grid(row=7, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        userTypeDropdown = OptionMenu(employeeVisitorRegistrationWindow, self.registrationEmployeeType, *self.employeeType)
        userTypeDropdown.grid(row=7, column=2, padx=(16, 5), pady=(0, 4), sticky=W)

        phoneLabel = Label(employeeVisitorRegistrationWindow, text="Phone", background='#ffffff')
        phoneLabel.grid(row=8, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        phoneBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationPhone, width=20)
        phoneBox.grid(row=8, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        addressLabel = Label(employeeVisitorRegistrationWindow, text="Address", background='#ffffff')
        addressLabel.grid(row=9, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        addressBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationAddress, width=20)
        addressBox.grid(row=9, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        cityLabel = Label(employeeVisitorRegistrationWindow, text="City", background='#ffffff')
        cityLabel.grid(row=10, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        cityBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationCity, width=20)
        cityBox.grid(row=10, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        stateLabel = Label(employeeVisitorRegistrationWindow, text="State", background='#ffffff')
        stateLabel.grid(row=11, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        stateDropdown = OptionMenu(employeeVisitorRegistrationWindow, self.registrationState, *self.states)
        stateDropdown.grid(row=11, column=2, padx=(16, 5), pady=(0, 4), sticky=W)

        zipLabel = Label(employeeVisitorRegistrationWindow, text="Zipcode", background='#ffffff')
        zipLabel.grid(row=12, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        zipBox = Entry(employeeVisitorRegistrationWindow, textvariable=self.registrationZIP, width=20)
        zipBox.grid(row=12, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        #EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(employeeVisitorRegistrationWindow, command=self.onEmployeeVisitorRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=13, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(employeeVisitorRegistrationWindow, command=self.onEmployeeVisitorRegistrationRegisterButtonClicked, text="Register",
                            background='#4286f4')
        registerButton.grid(row=13, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onEmployeeVisitorRegistrationBackButtonClicked(self):
        self.initRegistrationNavigationWindow()
        self.displayRegistrationNavigationWindow(self.registrationNavigationWindow)
        self.employeeVisitorRegistrationWindow.destroy()

    def onEmployeeVisitorRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()

        employeeType = self.registrationEmployeeType.get()
        state = self.registrationState.get()
        phone = self.registrationPhone.get()
        address = self.registrationAddress.get()
        city = self.registrationCity.get()
        zipcode = self.registrationZIP.get()

        if not firstName:
            firstName = ""
        if not lastName:
            lastName = ""
        if not state:
            state = ""
        if not address:
            address = ""
        if not city:
            city = ""
        if not zipcode:
            zipcode = ""
        if not confirmPassword:
            confirmPassword = ""


        if not username:
            messagebox.showwarning("Missing Username", "The username field is empty. Please try again.")
            return
        if not password:
            messagebox.showwarning("Missing Password", "The password field is empty. Please try again.")
            return
        if not employeeType:
            messagebox.showwarning("Missing Employee Type", "Please select an employee type.")
            return
        if not phone:
            messagebox.showwarning("Missing Phone Number", "Please enter a phone number in format xxxxxxxxxx")
            return


        if len(username) > 16:
            messagebox.showwarning("Username too long", "Usernames can have at maximum 16 letters.")
            return

        usernameExists = self.cursor.execute("SELECT * from user where Username=%s", username)
        if usernameExists:
            messagebox.showwarning("Username Already Taken", "This username already exists within the database.")
            return


        if len(password) < 8:
            messagebox.showwarning("Password Too Short", "Passwords must have at least 8 characters.")
            return

        if password != confirmPassword:
            messagebox.showwarning("Password Mismatch", "The password and the confirmed Password do not match.")
            return

        if len(firstName) > 32:
            messagebox.showwarning("First Name too long", "First names can only be 32 characters. Please abbreviate.")
            return
        if len(lastName) > 32:
            messagebox.showwarning("Last Name too long", "Last names can only be 32 characters. Please abbreviate.")
            return
        if len(address) > 64:
            messagebox.showwarning("Address too long", "Addresses are limited to 64 characters. Please abbreviate.")
            return
        if len(phone) > 10 or len(phone) < 10:
            messagebox.showwarning("Phone number incorrect", "Please enter a phone number in format xxxxxxxxxx")
            return
        if len(zipcode) > 5:
            messagebox.showwarning("Zipcode too long", "Please enter a zipcode in format xxxxx")
            return
        if zipcode != "":
            if len(zipcode) < 5:
                messagebox.showwarning("Zipcode too short", "Please enter a zipcode in format xxxxxx")
        if len(city) > 32:
            messagebox.showwarning("City name too long", "The city name is limited to 32 characters. Please abbreviate.")

        phoneExists = self.cursor.execute("SELECT * from employee where Phone=%s", phone)
        if phoneExists:
            messagebox.showwarning("Phone Already Registered", "This phone number is already registered.")

        empId = random.randint(1, 999999999)
        while self.cursor.execute("SELECT * from employee where EmployeeID=%s", empId):
            empId = random.randint(1, 999999999)


        hashedPassword = self.encrypt(password)
        self.cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)", (username, hashedPassword, firstName, lastName, "Pending"))
        self.cursor.execute("INSERT into employee values (%s, %s, %s, %s, %s, %s, %s)", (username, empId, phone, address, city, state, zipcode))
        self.cursor.execute("INSERT into visitor values (%s)", username)
        if employeeType == "Manager":
            self.cursor.execute("INSERT into manager values (%s)", username)
        elif employeeType == "Staff":
            self.cursor.execute("INSERT into staff values (%s)", username)
        else:
            messagebox.showwarning("Uhh", "You shouldn't be here: employee-visitor")

        messagebox.showwarning("Registration Successful", "You are now registered. You will need to wait for administrator approval to login.")

        self.employeeVisitorRegistrationWindow.destroy()
        self.loginWindow.deiconify()

    #----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                #
    #                               SPECIFIC USER NAVIGATION                                                         #
    #                                                                                                                #
    #----------------------------------------------------------------------------------------------------------------#

    def initUserFunctionalityWindow(self):
        self.userFunctionalityWindow = Toplevel()
        self.userFunctionalityWindow.title("Functionality -- User")
        self.userFunctionalityWindow.config(background='#ffffff')

    def displayUserFunctionalityWindow(self, userFunctionalityWindow):
        userLabel = Label(userFunctionalityWindow, text="User Functionality", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        userLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E)


        takeTransitButton = Button(userFunctionalityWindow, command=self.onTakeTransitButtonClicked, text="Take Transit",
                                background='#4286f4')
        takeTransitButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)

        transitHistoryButton = Button(userFunctionalityWindow, command=self.onTransitHistoryButtonClicked, text="Transit History",
                                   background='#4286f4')
        transitHistoryButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        userNavBackButton = Button(userFunctionalityWindow, command=self.onUserFunctionalityBackButtonClicked, text="Back",
                                   background='#4286f4')
        userNavBackButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onUserFunctionalityBackButtonClicked(self):
        self.userFunctionalityWindow.destroy()
        self.loginWindow.deiconify()

    # ----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                 #
    #                            VISITOR ONLY NAVIGATION                                                              #
    #                                                                                                                 #
    # ----------------------------------------------------------------------------------------------------------------#


    def initVisitorFunctionalityWindow(self):
        self.visitorFunctionalityWindow = Toplevel()
        self.visitorFunctionalityWindow.title("Functionality -- Visitor")
        self.visitorFunctionalityWindow.config(background='#ffffff')

    def displayVisitorFunctionalityWindow(self, visitorFunctionalityWindow):
        visitorFunctionalityLabel = Label(visitorFunctionalityWindow, text="Visitor Functionality", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        visitorFunctionalityLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky = W + E)


        exploreEventButton = Button(visitorFunctionalityWindow, command=self.onVisitorOnlyRegistrationRegisterButtonClicked, text="Explore Event",
                                background='#4286f4')
        exploreEventButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)

        exploreSiteButton = Button(visitorFunctionalityWindow, command=self.onVisitorOnlyRegistrationRegisterButtonClicked,
                                        text = "Explore Site", background='#4286f4')
        exploreSiteButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)

        viewVisitHistoryButton = Button(visitorFunctionalityWindow, command=self.onVisitorOnlyRegistrationRegisterButtonClicked, text="View Visit History",
                                background='#4286f4')
        viewVisitHistoryButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)

        takeTransitButton = Button(visitorFunctionalityWindow, command=self.onVisitorOnlyRegistrationRegisterButtonClicked,
                                        text = "Take Transit", background='#4286f4')
        takeTransitButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)

        viewTransitHistoryButton = Button(visitorFunctionalityWindow, command=self.onVisitorOnlyRegistrationRegisterButtonClicked,
                                        text = "View Transit History", background='#4286f4')
        viewTransitHistoryButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky= W + E)

        backButton = Button(visitorFunctionalityWindow, command=self.onVisitorFunctionalityBackButtonClicked, text="Back",
                             background='#4286f4')
        backButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onVisitorFunctionalityBackButtonClicked(self):
        self.visitorFunctionalityWindow.destroy()
        self.loginWindow.deiconify()


    # ----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                 #
    #                            GLOBAL NAVIGATION AFTER LOGIN                                                        #
    #                                                                                                                 #
    # ----------------------------------------------------------------------------------------------------------------#


    def onTakeTransitButtonClicked(self):
        return False

    def onTransitHistoryButtonClicked(self):
        return False

    # ----------------------------------------------------------------------------------------------------------------#
    #                                                                                                                 #
    #                            DATABASE CONNECTION IMPLEMENTATION                                                   #
    #                                                                                                                 #
    # ----------------------------------------------------------------------------------------------------------------#
    def connect(self):
        try:
            #this is Kyle's connection: if you are running into errors, comment it out and make a similar call to this method
            db = pymysql.connect(host='localhost',
                             user='root',
                             password='9A4q372X4m',
                             db='beltline',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
            return db
        except:
            messagebox.showwarning('Error!','Cannot connect. Please check your parameters on the connection call.')
            return False



if __name__ == '__main__':
    beltline = Beltline()
    beltline.db.close()
