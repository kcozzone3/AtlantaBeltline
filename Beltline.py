from tkinter import *
from tkinter import messagebox

import pymysql
import Queries

import hashlib
import random
from datetime import datetime


# PUT PASSWORD HERE
#######################################
MYSQL_PASSWORD = 'YOUR PASSWORD HERE'
#######################################


class Beltline(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        self.root.title("Atlanta Beltine DB Application")
        self.root.withdraw()

        loginWindow = Login(self.root)
        loginWindow.display()


class Login(Toplevel):
    def __init__(self, master_window):
        Toplevel.__init__(self)
        self.master = master_window
        self.title('Beltline Login')
        self.config(background='#ffffff')

    def display(self):
        self.loginUsername = StringVar()
        self.loginPassword = StringVar()

        # create a label (text) on the login window with the text of login with certain other properties
        loginLabel = Label(self, text="Login", font="Helvetica", foreground='#000000', background='#ffffff')

        # we place this on the grid in 1,3 with some padding to make it look nice. Sticky determines where in the cell
        # it is placed
        loginLabel.grid(row=1, column=2, pady=(2, 6), sticky=W)

        # create a username label and place in the grid
        usernameLabel = Label(self, text="Username", foreground='#000000', background='#ffffff')
        usernameLabel.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        # create a username entry box, accounting for the inputted text to be the login username. We also set a width
        # for how many characters can be easily displayed
        usernameBox = Entry(self, textvariable=self.loginUsername, width=20)
        usernameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        # Password Label creation
        passwordLabel = Label(self, text="Password ", foreground='#000000', background='#ffffff')
        passwordLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        # Password Entry Box creation: difference to username is the show='*', which displays *** instead of abc
        passwordBox = Entry(self, show='*', textvariable=self.loginPassword, width=20)
        passwordBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        # create buttons that as of now, do no logic checking, but simply move screens
        loginButton = Button(self, command=self.onLoginButtonClicked, text="Login", background='#4286f4')
        loginButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=E)
        registerButton = Button(self, command=self.onRegisterButtonClicked, text="Register",
                                background='#4286f4')
        registerButton.grid(row=5, column=2, padx=(2, 2), pady=(2, 2))

    def onRegisterButtonClicked(self):
        registerWindow = RegistrationNav(self)
        self.withdraw()
        registerWindow.display()

    def onLoginButtonClicked(self):
        self.username = self.loginUsername.get()
        self.password = self.loginPassword.get()

        if not self.username:
            messagebox.showwarning("Username Field Empty", "The username field is empty. Please try again.")
            return

        if not self.password:
            messagebox.showwarning("Password Field Empty", "The password field is empty. Please try again.")
            return

        hashedPassword = encrypt(self.password)
        usernameValid = cursor.execute("SELECT * FROM user where EXISTS (SELECT * FROM user where Username=%s)",
                                          self.username)

        if usernameValid == 0:
            messagebox.showwarning("Username Invalid", "This username is not registered in the system.")
            return

        passwordMatching = cursor.execute(
            "SELECT * FROM user where EXISTS (SELECT * FROM user where (Username=%s and Password=%s))",
            (self.username, hashedPassword))

        if passwordMatching == 0:
            messagebox.showwarning("Invalid Login",
                                   "This username and password combination is not registered in the system.")
            return

        cursor.execute("SELECT status FROM user where Username=%s", self.username)
        accountStatus = cursor.fetchone()
        accountStatus = accountStatus.get('status').lower()

        if accountStatus == "declined":
            messagebox.showwarning("Banned Account", "Your account has been banned. Please contact an administrator.")
            return
        elif accountStatus == "pending":
            messagebox.showwarning("Pending Approval", "Your account is pending approval. Please be patient.")
            return

        isVisitor = cursor.execute("SELECT * FROM visitor where EXISTS (SELECT * FROM visitor where VisUsername=%s)",
                                      self.username)
        isEmployee = cursor.execute(
            "SELECT * FROM employee where EXISTS (SELECT * FROM employee where EmpUsername=%s)", self.username)
        if isEmployee:
            isAdmin = cursor.execute(
                "SELECT * FROM administrator where EXISTS (SELECT * FROM administrator where AdminUsername=%s)",
                self.username)
            isManager = cursor.execute(
                "SELECT * FROM manager where EXISTS (SELECT * FROM manager where ManUsername=%s)", self.username)
            isStaff = cursor.execute("SELECT * FROM staff where EXISTS (SELECT * FROM staff where StaffUsername=%s)",
                                        self.username)

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
                # Just a visitor
                visitorFunctionalityWindow = VisitorFunctionality(self)
                self.withdraw()
                visitorFunctionalityWindow.display()

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
            # Just a user
            userFunctionalityWindow = UserFunctionality(self)
            self.withdraw()
            userFunctionalityWindow.deiconify()


class RegistrationNav(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Registration Navigation')
        self.config(background='#ffffff')

    def display(self):
        registerLabel = Label(self, text="Register Navigation", font="Helvetica", foreground='#000000',
                              background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        userOnlyButton = Button(self, command=self.onUserOnlyButtonClicked, text="User Only", background='#4286f4')
        userOnlyButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        visitorOnlyButton = Button(self, command=self.onVisitorOnlyButtonClicked, text="Visitor Only",
                                   background='#4286f4')
        visitorOnlyButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        employeeOnlyButton = Button(self, command=self.onEmployeeOnlyButtonClicked, text="Employee Only",
                                    background='#4286f4')
        employeeOnlyButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        employeeVisitorButton = Button(self, command=self.onEmployeeVisitorButtonClicked, text="Employee-Visitor",
                                       background='#4286f4')
        employeeVisitorButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        backButton = Button(self, command=self.onRegistrationBackButtonClicked, text="Back", background='#4286f4')
        backButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onUserOnlyButtonClicked(self):
        userRegistrationWindow = UserRegistration(self)
        self.withdraw()
        userRegistrationWindow.display()

    def onVisitorOnlyButtonClicked(self):
        visitorRegistrationWindow = VisitorRegistration(self)
        self.withdraw()
        visitorRegistrationWindow.display()

    def onEmployeeOnlyButtonClicked(self):
        employeeRegistrationWindow = EmployeeRegistration(self)
        self.withdraw()
        employeeRegistrationWindow.display()

    def onEmployeeVisitorButtonClicked(self):
        employeeVisitorRegistration = EmployeeVisitorRegistration(self)
        self.withdraw()
        employeeVisitorRegistration.display()

    def onRegistrationBackButtonClicked(self):
        self.destroy()
        self.master.deiconify()


class UserRegistration(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Registration -- User')
        self.config(background='#ffffff')

    def display(self):
        self.registrationFirstName = StringVar()
        self.registrationLastName = StringVar()
        self.registrationUserName = StringVar()
        self.registrationPassword = StringVar()
        self.registrationConfirmPassword = StringVar()

        registerLabel = Label(self, text="User Only Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E, columnspan=2)

        firstNameLabel = Label(self, text="First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        firstNameBox = Entry(self, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(self, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        lastNameBox = Entry(self, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(self, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(self, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(self, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(self, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(self, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(self, textvariable=self.registrationConfirmPassword, width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        emailLabel = Label(self, text="Email(s)", background='#ffffff')
        emailLabel.grid(row=7, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        self.emailBox = Text(self, height=4, width=15, wrap=WORD)
        self.emailBox.grid(row=7, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        self.emailBox.insert("1.0",
                             "Enter emails with 1 comma in between.\nEx: exampleOne@yahoo.com,example2@yahoo.com")

        # EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(self, command=self.onUserOnlyRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(self, command=self.onUserOnlyRegistrationRegisterButtonClicked, text="Register",
                                background='#4286f4')
        registerButton.grid(row=8, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onUserOnlyRegistrationBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onUserOnlyRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()
        emailString = self.emailBox.get("1.0", "end-1c")

        if not firstName:
            messagebox.showwarning("Missing First Name", "The first name field is empty. Please try again.")
            return
        if not lastName:
            messagebox.showwarning("Missing Last Name", "The last name field is empty. Please try again.")
            return

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

        usernameExists = cursor.execute("SELECT * from user where Username=%s", username)
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

        emailList = []
        while len(emailString) > 0:
            commaIndex = emailString.find(',')
            if commaIndex > -1:
                emailList.append(emailString[0:commaIndex])
                emailString = emailString[commaIndex + 1:]
            else:
                emailList.append(emailString[0:])
                emailString = ""
        for email in emailList:
            curEmail = email
            if curEmail.find('\n') > -1:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. You have an enter character somewhere.")
                return
            atLocation = curEmail.find('@')
            if atLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the @ character.")
                return
            beforeAt = email[0:atLocation]
            afterAt = email[atLocation + 1:]
            periodLocation = afterAt.find('.')
            if periodLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the . character.")
                return
            beforePeriodAfterAt = afterAt[0:periodLocation]
            afterPeriod = afterAt[periodLocation + 1:]
            if not beforeAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not beforePeriodAfterAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not afterPeriod.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            emailExists = cursor.execute("SELECT * from emails where Email=%s", curEmail)
            if emailExists:
                messagebox.showwarning("Email Already Taken",
                                       "An email you entered already exists within the database.")
                return

        hashedPassword = encrypt(password)
        cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)",
                          (username, hashedPassword, firstName, lastName, "Pending"))
        for email in emailList:
            cursor.execute("INSERT into emails values (%s, %s)", (username, email))
        messagebox.showwarning("Registration Successful",
                               "You are now registered. You will need to wait for administrator approval to login.")

        self.destroy()
        self.master.deiconify()


class VisitorRegistration(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Registration -- Visitor')
        self.config(background='#ffffff')

    def display(self):
        self.registrationFirstName = StringVar()
        self.registrationLastName = StringVar()
        self.registrationUserName = StringVar()
        self.registrationPassword = StringVar()
        self.registrationConfirmPassword = StringVar()

        registerLabel = Label(self, text="Visitor Only Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E, columnspan=2)

        firstNameLabel = Label(self, text="First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        firstNameBox = Entry(self, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(self, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        lastNameBox = Entry(self, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(self, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(self, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(self, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(self, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(self, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(self, textvariable=self.registrationConfirmPassword, width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        emailLabel = Label(self, text="Email(s)", background='#ffffff')
        emailLabel.grid(row=7, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        self.emailBox = Text(self, height=4, width=15, wrap=WORD)
        self.emailBox.grid(row=7, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        self.emailBox.insert("1.0",
                             "Enter emails with 1 comma in between.\nEx: exampleOne@yahoo.com,example2@yahoo.com")

        # EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(self, command=self.onVisitorOnlyRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(self, command=self.onVisitorOnlyRegistrationRegisterButtonClicked, text="Register",
                                background='#4286f4')
        registerButton.grid(row=8, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onVisitorOnlyRegistrationBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onVisitorOnlyRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()
        emailString = self.emailBox.get("1.0", "end-1c")

        if not firstName:
            messagebox.showwarning("Missing First Name", "The first name field is empty. Please try again.")
            return
        if not lastName:
            messagebox.showwarning("Missing Last Name", "The last name field is empty. Please try again.")
            return

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

        usernameExists = cursor.execute("SELECT * from user where Username=%s", username)
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

        emailList = []
        while len(emailString) > 0:
            commaIndex = emailString.find(',')
            if commaIndex > -1:
                emailList.append(emailString[0:commaIndex])
                emailString = emailString[commaIndex + 1:]
            else:
                emailList.append(emailString[0:])
                emailString = ""
        for email in emailList:
            curEmail = email
            if curEmail.find('\n') > -1:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. You have an enter character somewhere.")
                return
            atLocation = curEmail.find('@')
            if atLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the @ character.")
                return
            beforeAt = email[0:atLocation]
            afterAt = email[atLocation + 1:]
            periodLocation = afterAt.find('.')
            if periodLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the . character.")
                return
            beforePeriodAfterAt = afterAt[0:periodLocation]
            afterPeriod = afterAt[periodLocation + 1:]
            if not beforeAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not beforePeriodAfterAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not afterPeriod.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            emailExists = cursor.execute("SELECT * from emails where Email=%s", curEmail)
            if emailExists:
                messagebox.showwarning("Email Already Taken",
                                       "An email you entered already exists within the database.")
                return

        hashedPassword = encrypt(password)
        cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)",
                          (username, hashedPassword, firstName, lastName, "Pending"))
        cursor.execute("INSERT into visitor values (%s)", username)
        for email in emailList:
            cursor.execute("INSERT into emails values (%s, %s)", (username, email))
        messagebox.showwarning("Registration Successful",
                               "You are now registered. You will need to wait for administrator approval to login.")

        self.self.destroy()
        self.loginWindow.deiconify()


class EmployeeRegistration(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Registration -- Employee')
        self.config(background='#ffffff')

    def display(self):
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

        registerLabel = Label(self, text="Employee Only Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E, columnspan=2)

        firstNameLabel = Label(self, text="First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        firstNameBox = Entry(self, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(self, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        lastNameBox = Entry(self, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(self, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(self, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(self, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(self, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(self, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(self, textvariable=self.registrationConfirmPassword,
                                   width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        userTypeLabel = Label(self, text="Employee Type", background='#ffffff')
        userTypeLabel.grid(row=7, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        userTypeDropdown = OptionMenu(self, self.registrationEmployeeType, *self.employeeType)
        userTypeDropdown.grid(row=7, column=2, padx=(8, 5), pady=(0, 4), sticky=W)

        phoneLabel = Label(self, text="Phone", background='#ffffff')
        phoneLabel.grid(row=8, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        phoneBox = Entry(self, textvariable=self.registrationPhone, width=20)
        phoneBox.grid(row=8, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        addressLabel = Label(self, text="Address", background='#ffffff')
        addressLabel.grid(row=9, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        addressBox = Entry(self, textvariable=self.registrationAddress, width=20)
        addressBox.grid(row=9, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        cityLabel = Label(self, text="City", background='#ffffff')
        cityLabel.grid(row=10, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        cityBox = Entry(self, textvariable=self.registrationCity, width=20)
        cityBox.grid(row=10, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        stateLabel = Label(self, text="State", background='#ffffff')
        stateLabel.grid(row=11, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        stateDropdown = OptionMenu(self, self.registrationState, *self.states)
        stateDropdown.grid(row=11, column=2, padx=(8, 5), pady=(0, 4), sticky=W)

        zipLabel = Label(self, text="Zipcode", background='#ffffff')
        zipLabel.grid(row=12, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        zipBox = Entry(self, textvariable=self.registrationZIP, width=20)
        zipBox.grid(row=12, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        emailLabel = Label(self, text="Email(s)", background='#ffffff')
        emailLabel.grid(row=13, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        self.emailBox = Text(self, height=4, width=15, wrap=WORD)
        self.emailBox.grid(row=13, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        self.emailBox.insert("1.0",
                             "Enter emails with 1 comma in between.\nEx: exampleOne@yahoo.com,example2@yahoo.com")

        # EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(self, command=self.onEmployeeOnlyRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=14, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(self, command=self.onEmployeeOnlyRegistrationRegisterButtonClicked, text="Register",
                                background='#4286f4')
        registerButton.grid(row=14, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onEmployeeOnlyRegistrationBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onEmployeeOnlyRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()
        emailString = self.emailBox.get("1.0", "end-1c")

        employeeType = self.registrationEmployeeType.get()
        state = self.registrationState.get()
        phone = self.registrationPhone.get()
        address = self.registrationAddress.get()
        city = self.registrationCity.get()
        zipcode = self.registrationZIP.get()

        if not firstName:
            messagebox.showwarning("Missing First Name", "The first name field is empty. Please try again.")
            return
        if not lastName:
            messagebox.showwarning("Missing Last Name", "The last name field is empty. Please try again.")
            return
        if not state:
            messagebox.showwarning("Missing State", "The state field is empty. Please try again.")
            return
        if not address:
            messagebox.showwarning("Missing Address", "The address field is empty. Please try again.")
            return
        if not city:
            messagebox.showwarning("Missing City", "The city field is empty. Please try again.")
            return
        if not zipcode:
            messagebox.showwarning("Missing Zipcode", "The zipcode field is empty. Please try again.")
            return
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

        usernameExists = cursor.execute("SELECT * from user where Username=%s", username)
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
            messagebox.showwarning("City name too long",
                                   "The city name is limited to 32 characters. Please abbreviate.")

        phoneExists = cursor.execute("SELECT * from employee where Phone=%s", phone)
        if phoneExists:
            messagebox.showwarning("Phone Already Registered", "This phone number is already registered.")
            return

        empId = random.randint(1, 999999999)
        while cursor.execute("SELECT * from employee where EmployeeID=%s", empId):
            empId = random.randint(1, 999999999)

        emailList = []
        while len(emailString) > 0:
            commaIndex = emailString.find(',')
            if commaIndex > -1:
                emailList.append(emailString[0:commaIndex])
                emailString = emailString[commaIndex + 1:]
            else:
                emailList.append(emailString[0:])
                emailString = ""
        for email in emailList:
            curEmail = email
            if curEmail.find('\n') > -1:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. You have an enter character somewhere.")
                return
            atLocation = curEmail.find('@')
            if atLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the @ character.")
                return
            beforeAt = email[0:atLocation]
            afterAt = email[atLocation + 1:]
            periodLocation = afterAt.find('.')
            if periodLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the . character.")
                return
            beforePeriodAfterAt = afterAt[0:periodLocation]
            afterPeriod = afterAt[periodLocation + 1:]
            if not beforeAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not beforePeriodAfterAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not afterPeriod.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            emailExists = cursor.execute("SELECT * from emails where Email=%s", curEmail)
            if emailExists:
                messagebox.showwarning("Email Already Taken",
                                       "An email you entered already exists within the database.")
                return

        hashedPassword = encrypt(password)
        cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)",
                          (username, hashedPassword, firstName, lastName, "Pending"))
        cursor.execute("INSERT into employee values (%s, %s, %s, %s, %s, %s, %s)",
                          (username, empId, phone, address, city, state, zipcode))

        if employeeType == "Manager":
            cursor.execute("INSERT into manager values (%s)", username)
        elif employeeType == "Staff":
            cursor.execute("INSERT into staff values (%s)", username)
        else:
            messagebox.showwarning("Uhh", "You shouldn't be here: employee")

        for email in emailList:
            cursor.execute("INSERT into emails values (%s, %s)", (username, email))

        messagebox.showwarning("Registration Successful",
                               "You are now registered. You will need to wait for administrator approval to login.")

        self.master.deiconify()
        self.destroy()


class EmployeeVisitorRegistration(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Registration -- Employee Visitor')
        self.config(background='#ffffff')

    def display(self):
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

        registerLabel = Label(self, text="Employee-Visitor Registration", font="Helvetica",
                              foreground='#000000', background='#ffffff')
        registerLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E, columnspan=2)

        firstNameLabel = Label(self, text="First Name", background='#ffffff')
        firstNameLabel.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        firstNameBox = Entry(self, textvariable=self.registrationFirstName, width=20)
        firstNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        lastNameLabel = Label(self, text="Last Name", background='#ffffff')
        lastNameLabel.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        lastNameBox = Entry(self, textvariable=self.registrationLastName, width=20)
        lastNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        usernameLabel = Label(self, text="Username", background='#ffffff')
        usernameLabel.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        usernameBox = Entry(self, textvariable=self.registrationUserName, width=20)
        usernameBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        passwordLabel = Label(self, text="Password", background='#ffffff')
        passwordLabel.grid(row=5, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        passwordBox = Entry(self, textvariable=self.registrationPassword, width=20)
        passwordBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        confirmPasswordLabel = Label(self, text="Confirm Password", background='#ffffff')
        confirmPasswordLabel.grid(row=6, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        confirmPasswordBox = Entry(self, textvariable=self.registrationConfirmPassword,
                                   width=20)
        confirmPasswordBox.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        userTypeLabel = Label(self, text="Employee Type", background='#ffffff')
        userTypeLabel.grid(row=7, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        userTypeDropdown = OptionMenu(self, self.registrationEmployeeType, *self.employeeType)
        userTypeDropdown.grid(row=7, column=2, padx=(16, 5), pady=(0, 4), sticky=W)

        phoneLabel = Label(self, text="Phone", background='#ffffff')
        phoneLabel.grid(row=8, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        phoneBox = Entry(self, textvariable=self.registrationPhone, width=20)
        phoneBox.grid(row=8, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        addressLabel = Label(self, text="Address", background='#ffffff')
        addressLabel.grid(row=9, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        addressBox = Entry(self, textvariable=self.registrationAddress, width=20)
        addressBox.grid(row=9, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        cityLabel = Label(self, text="City", background='#ffffff')
        cityLabel.grid(row=10, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        cityBox = Entry(self, textvariable=self.registrationCity, width=20)
        cityBox.grid(row=10, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        stateLabel = Label(self, text="State", background='#ffffff')
        stateLabel.grid(row=11, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        stateDropdown = OptionMenu(self, self.registrationState, *self.states)
        stateDropdown.grid(row=11, column=2, padx=(16, 5), pady=(0, 4), sticky=W)

        zipLabel = Label(self, text="Zipcode", background='#ffffff')
        zipLabel.grid(row=12, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        zipBox = Entry(self, textvariable=self.registrationZIP, width=20)
        zipBox.grid(row=12, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        emailLabel = Label(self, text="Email(s)", background='#ffffff')
        emailLabel.grid(row=13, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        self.emailBox = Text(self, height=4, width=15, wrap=WORD)
        self.emailBox.grid(row=13, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        self.emailBox.insert("1.0",
                             "Enter emails with 1 comma in between.\nEx: exampleOne@yahoo.com,example2@yahoo.com")

        # EMAIL NOT CURRENTLY IMPLEMENTED

        backButton = Button(self, command=self.onEmployeeVisitorRegistrationBackButtonClicked, text="Back",
                            background='#4286f4')
        backButton.grid(row=14, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        registerButton = Button(self, command=self.onEmployeeVisitorRegistrationRegisterButtonClicked, text="Register",
                                background='#4286f4')
        registerButton.grid(row=14, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onEmployeeVisitorRegistrationBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onEmployeeVisitorRegistrationRegisterButtonClicked(self):
        firstName = self.registrationFirstName.get()
        lastName = self.registrationLastName.get()
        username = self.registrationUserName.get()
        password = self.registrationPassword.get()
        confirmPassword = self.registrationConfirmPassword.get()
        emailString = self.emailBox.get("1.0", "end-1c")

        employeeType = self.registrationEmployeeType.get()
        state = self.registrationState.get()
        phone = self.registrationPhone.get()
        address = self.registrationAddress.get()
        city = self.registrationCity.get()
        zipcode = self.registrationZIP.get()

        if not firstName:
            messagebox.showwarning("Missing First Name", "The first name field is empty. Please try again.")
            return
        if not lastName:
            messagebox.showwarning("Missing Last Name", "The last name field is empty. Please try again.")
            return
        if not state:
            messagebox.showwarning("Missing State", "The state field is empty. Please try again.")
            return
        if not address:
            messagebox.showwarning("Missing Address", "The address field is empty. Please try again.")
            return
        if not city:
            messagebox.showwarning("Missing City", "The city field is empty. Please try again.")
            return
        if not zipcode:
            messagebox.showwarning("Missing Zipcode", "The zipcode field is empty. Please try again.")
            return
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

        usernameExists = cursor.execute("SELECT * from user where Username=%s", username)
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
            messagebox.showwarning("City name too long",
                                   "The city name is limited to 32 characters. Please abbreviate.")

        phoneExists = cursor.execute("SELECT * from employee where Phone=%s", phone)
        if phoneExists:
            messagebox.showwarning("Phone Already Registered", "This phone number is already registered.")
            return

        empId = random.randint(1, 999999999)
        while cursor.execute("SELECT * from employee where EmployeeID=%s", empId):
            empId = random.randint(1, 999999999)

        emailList = []
        while len(emailString) > 0:
            commaIndex = emailString.find(',')
            if commaIndex > -1:
                emailList.append(emailString[0:commaIndex])
                emailString = emailString[commaIndex + 1:]
            else:
                emailList.append(emailString[0:])
                emailString = ""
        for email in emailList:
            curEmail = email
            if curEmail.find('\n') > -1:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. You have an enter character somewhere.")
                return
            atLocation = curEmail.find('@')
            if atLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the @ character.")
                return
            beforeAt = email[0:atLocation]
            afterAt = email[atLocation + 1:]
            periodLocation = afterAt.find('.')
            if periodLocation < 0:
                messagebox.showwarning("Email Error",
                                       "The format of your email(s) is wrong. Some email(s) is missing the . character.")
                return
            beforePeriodAfterAt = afterAt[0:periodLocation]
            afterPeriod = afterAt[periodLocation + 1:]
            if not beforeAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not beforePeriodAfterAt.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            if not afterPeriod.isalnum():
                messagebox.showwarning("Email Error", "The format of your email(s) is wrong.")
                return
            emailExists = cursor.execute("SELECT * from emails where Email=%s", curEmail)
            if emailExists:
                messagebox.showwarning("Email Already Taken",
                                       "An email you entered already exists within the database.")
                return

        hashedPassword = encrypt(password)
        cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)",
                          (username, hashedPassword, firstName, lastName, "Pending"))
        cursor.execute("INSERT into employee values (%s, %s, %s, %s, %s, %s, %s)",
                          (username, empId, phone, address, city, state, zipcode))
        cursor.execute("INSERT into visitor values (%s)", username)
        if employeeType == "Manager":
            cursor.execute("INSERT into manager values (%s)", username)
        elif employeeType == "Staff":
            cursor.execute("INSERT into staff values (%s)", username)
        else:
            messagebox.showwarning("Uhh", "You shouldn't be here: employee-visitor")

        for email in emailList:
            cursor.execute("INSERT into emails values (%s, %s)", (username, email))

        messagebox.showwarning("Registration Successful",
                               "You are now registered. You will need to wait for administrator approval to login.")

        self.master.deiconify()
        self.destroy()


class UserFunctionality(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- User')
        self.config(background='#ffffff')

    def display(self):
        userLabel = Label(self, text="User Functionality", font="Helvetica",
                          foreground='#000000', background='#ffffff')
        userLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        takeTransitButton = Button(self, command=self.onTakeTransitButtonClicked, text="Take Transit",
                                   background='#4286f4')
        takeTransitButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        transitHistoryButton = Button(self, command=self.onTransitHistoryButtonClicked, text="Transit History",
                                      background='#4286f4')
        transitHistoryButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        userNavBackButton = Button(self, command=self.onUserFunctionalityBackButtonClicked, text="Back",
                                   background='#4286f4')
        userNavBackButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onUserFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onTakeTransitButtonClicked(self):
        TakeTransitWindow = TakeTransit(self)
        self.withdraw()
        TakeTransitWindow.display()

    def onTransitHistoryButtonClicked(self):
        pass
        # TODO


class VisitorFunctionality(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Visitor')
        self.config(background='#ffffff')

    def display(self):
        visitorFunctionalityLabel = Label(self, text="Visitor Functionality", font="Helvetica",
                                          foreground='#000000', background='#ffffff')
        visitorFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        exploreEventButton = Button(self,
                                    command=self.onVisitorFunctionalityExploreEventButtonClicked, text="Explore Event",
                                    background='#4286f4')
        exploreEventButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        exploreSiteButton = Button(self,
                                   command=self.onVisitorFunctionalityExploreSiteButtonClicked,
                                   text="Explore Site", background='#4286f4')
        exploreSiteButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        viewVisitHistoryButton = Button(self,
                                        command=self.onVisitorFunctionalityViewHistoryButtonButtonClicked,
                                        text="View Visit History", background='#4286f4')
        viewVisitHistoryButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        takeTransitButton = Button(self, command=self.onTakeTransitButtonClicked,
                                   text="Take Transit", background='#4286f4')
        takeTransitButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        viewTransitHistoryButton = Button(self,
                                          command=self.onTransitHistoryButtonClicked,
                                          text="View Transit History", background='#4286f4')
        viewTransitHistoryButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        backButton = Button(self, command=self.onVisitorFunctionalityBackButtonClicked,
                            text="Back",
                            background='#4286f4')
        backButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onVisitorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onVisitorFunctionalityExploreEventButtonClicked(self):
        pass
        #TODO

    def onVisitorFunctionalityExploreSiteButtonClicked(self):
        pass
        #TODO

    def onVisitorFunctionalityViewHistoryButtonButtonClicked(self):
        pass
        #TODO

    def onTakeTransitButtonClicked(self):
        TakeTransitWindow = TakeTransit(self)
        self.withdraw()
        TakeTransitWindow.display()

    def onTransitHistoryButtonClicked(self):
        pass
        # TODO


class TakeTransit(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Take Transit')
        self.config(background='#ffffff')
        self.SQL = Queries.TakeTransit(db)

    def display(self):
        transits, sites = self.SQL.load()

        self.route, self.d1, self.d2 = StringVar(), StringVar(), StringVar()
        self.sites, self.ttype = StringVar(), StringVar()


        takeTransitLabel = Label(self, text="Take Transit", font="Helvetica", foreground='#000000', background='#ffffff')
        takeTransitLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        takeTransitLabel = Label(self, text="Take Transit", font="Helvetica", foreground='#000000', background='#ffffff')
        takeTransitLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        siteDropdown = OptionMenu(self, self.sites, *sites + ['All'])

    def back(self):
        self.master.deiconify()
        self.destroy()


def encrypt(unhashed_string):
    return hashlib.sha256(unhashed_string.encode()).hexdigest()


if __name__ == '__main__':
    try:
        print("Connecting to DB")
        global db  # Makes the connection accessible from all scopes

        db = pymysql.connect(host='localhost',
                             user='root',
                             password=MYSQL_PASSWORD,
                             db='beltline',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

        global cursor
        cursor = db.cursor()

    except Exception as e:
        print(e)
        print('Error! Cannot connect. Please double check the password variable to your MySQL server at the top of '
              'the file.')
        sys.exit()

    print("Connected!")

    root = Tk()
    app = Beltline(root)
    root.mainloop()

    db.close()
    sys.exit()
