from tkinter import *
from tkinter import messagebox

import pymysql
import Queries

import hashlib
import random
from datetime import datetime
from functools import partial
import re

from tkintertable import TableModel, TableCanvas


# PUT PASSWORD HERE
#######################################
MYSQL_PASSWORD = '9A4q372X4m'
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
        self.loginEmail = StringVar()
        self.loginPassword = StringVar()

        # create a label (text) on the login window with the text of login with certain other properties
        loginLabel = Label(self, text="Login", font="Helvetica", foreground='#000000', background='#ffffff')

        # we place this on the grid in 1,3 with some padding to make it look nice. Sticky determines where in the cell
        # it is placed
        loginLabel.grid(row=1, column=2, pady=(2, 6), sticky=W)

        # create a username label and place in the grid
        emailLabel = Label(self, text="Email", foreground='#000000', background='#ffffff')
        emailLabel.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        # create a username entry box, accounting for the inputted text to be the login username. We also set a width
        # for how many characters can be easily displayed
        emailBox = Entry(self, textvariable=self.loginEmail, width=20)
        emailBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

        # Password Label creation
        passwordLabel = Label(self, text="Password", foreground='#000000', background='#ffffff')
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
        self.email = self.loginEmail.get()
        self.password = self.loginPassword.get()

        if not self.email:
            messagebox.showwarning("Email Field Empty", "The email field is empty. Please try again.")
            return

        if not self.password:
            messagebox.showwarning("Password Field Empty", "The password field is empty. Please try again.")
            return

        hashedPassword = encrypt(self.password)
        usernameValid = cursor.execute("SELECT Username FROM user where Username = (SELECT Username FROM emails where Email=%s)",
                                          self.email)

        if usernameValid == 0:
            messagebox.showwarning("Email Invalid", "This email isn't registered in the system.")
            return
        else:
            results = cursor.fetchone()
            username = results['Username']
            print(results['Username'])


        passwordMatching = cursor.execute(
            "SELECT * FROM user where EXISTS (SELECT * FROM user where (Username=%s and Password=%s))",
            (username, hashedPassword))

        if passwordMatching == 0:
            messagebox.showwarning("Invalid Login",
                                   "This email and password combination is not registered in the system.")
            return

        cursor.execute("SELECT status FROM user where Username=%s", username)
        accountStatus = cursor.fetchone()
        accountStatus = accountStatus.get('status').lower()

        global identifier
        identifier = username

        if accountStatus == "declined":
            messagebox.showwarning("Banned Account", "Your account has been banned. Please contact an administrator.")
            return
        elif accountStatus == "pending":
            messagebox.showwarning("Pending Approval", "Your account is pending approval. Please be patient.")
            return

        isVisitor = cursor.execute("SELECT * FROM visitor where EXISTS (SELECT * FROM visitor where VisUsername=%s)",
                                      username)
        isEmployee = cursor.execute(
            "SELECT * FROM employee where EXISTS (SELECT * FROM employee where EmpUsername=%s)", username)
        if isEmployee:
            isAdmin = cursor.execute(
                "SELECT * FROM administrator where EXISTS (SELECT * FROM administrator where AdminUsername=%s)",
                username)
            isManager = cursor.execute(
                "SELECT * FROM manager where EXISTS (SELECT * FROM manager where ManUsername=%s)", username)
            isStaff = cursor.execute("SELECT * FROM staff where EXISTS (SELECT * FROM staff where StaffUsername=%s)",
                                        username)

        if isVisitor:
            if isEmployee:
                if isAdmin:
                    administratorVisitorFunctionalityWindow = AdministratorVisitorFunctionality(self)
                    self.withdraw()
                    administratorVisitorFunctionalityWindow.display()
                elif isManager:
                    managerVisitorFunctionalityWindow = ManagerVisitorFunctionality(self)
                    self.withdraw()
                    managerVisitorFunctionalityWindow.display()
                elif isStaff:
                    staffVisitorFunctionalityWindow = StaffVisitorFunctionality(self)
                    self.withdraw()
                    staffVisitorFunctionalityWindow.display()
                else:
                    messagebox.showwarning("Uhhh", "You shouldn't be here (employee-visitor).")
            else:
                # Just a visitor
                visitorFunctionalityWindow = VisitorFunctionality(self)
                self.withdraw()
                visitorFunctionalityWindow.display()

        elif isEmployee:
            if isAdmin:
                administratorFunctionalityWindow = AdministratorFunctionality(self)
                self.withdraw()
                administratorFunctionalityWindow.display()
            elif isManager:
                managerFunctionalityWindow = ManagerFunctionality(self)
                self.withdraw()
                managerFunctionalityWindow.display()
            elif isStaff:
                staffFunctionalityWindow = StaffFunctionality(self)
                self.withdraw()
                staffFunctionalityWindow.display()
            else:
                messagebox.showwarning("Uhhh", "You shouldn't be here (employee).")
        else:
            # Just a user
            userFunctionalityWindow = UserFunctionality(self)
            self.withdraw()
            userFunctionalityWindow.display()


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

        hasValidEmail=False

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
            hasValidEmail=True

        if hasValidEmail == False:
            messagebox.showwarning("Email not entered", "Please enter at least 1 email.")
            return

        hashedPassword = encrypt(password)
        cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)",
                          (username, hashedPassword, firstName, lastName, "Pending"))
        for email in emailList:
            cursor.execute("INSERT into emails values (%s, %s)", (username, email))
        db.commit()
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

        hasValidEmail=False

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
            hasValidEmail=True

        if hasValidEmail == False:
            messagebox.showwarning("Email not entered", "Please enter at least 1 email.")
            return

        hashedPassword = encrypt(password)
        cursor.execute("INSERT into user values (%s, %s, %s, %s, %s)",
                          (username, hashedPassword, firstName, lastName, "Pending"))
        cursor.execute("INSERT into visitor values (%s)", username)
        for email in emailList:
            cursor.execute("INSERT into emails values (%s, %s)", (username, email))
        db.commit()
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

        hasValidEmail=False

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
            hasValidEmail=True

        if hasValidEmail == False:
            messagebox.showwarning("Email not entered", "Please enter at least 1 email.")
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
        db.commit()

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

        hasValidEmail=False

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
            hasValidEmail=True

        if hasValidEmail == False:
            messagebox.showwarning("Email not entered", "Please enter at least 1 email.")
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
        db.commit()

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
        TransitHistoryWindow = TransitHistory(self)
        self.withdraw()
        TransitHistoryWindow.display()



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
                                        command=self.onVisitorFunctionalityVisitHistoryButtonButtonClicked,
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
        backButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onVisitorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()

    def onVisitorFunctionalityExploreEventButtonClicked(self):
        pass
        """
        def __init__(self, master):
            Toplevel.__init__(self)
            self.master = master
            self.title('ExploreEvent -- Visitor')
            self.config(background='#ffffff')
        def display(self):
            self.eventName = StringVar()
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
            """

        #TODO

    def onVisitorFunctionalityExploreSiteButtonClicked(self):
        pass
        #TODO

    def onVisitorFunctionalityVisitHistoryButtonButtonClicked(self):
        visitHistoryWindow = visitorVisitHistory(self)
        self.withdraw()
        visitHistoryWindow.display()

    def onTakeTransitButtonClicked(self):
        TakeTransitWindow = TakeTransit(self)
        self.withdraw()
        TakeTransitWindow.display()

    def onTransitHistoryButtonClicked(self):
        TransitHistoryWindow = TransitHistory(self)
        self.withdraw()
        TransitHistoryWindow.display()


class AdministratorFunctionality(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Adminstrator-Only')
        self.config(background='#ffffff')

    def display(self):
        administratorFunctionalityLabel = Label(self, text="Administrator Functionality", font="Helvetica",foreground='#000000', background='#ffffff')
        administratorFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        adminmanageProfileButton = Button(self,command=self.onAdminManageProfileButtonClicked, text="Manage Profile",background='#4286f4')
        adminmanageProfileButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminmanageUserButton = Button(self,command=self.onAdminManageUserButtonClicked,text="Manage User", background='#4286f4')
        adminmanageUserButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminmanageTransitButton = Button(self,command=self.onAdminManageTransitButtonClicked,text="Manage Transit", background='#4286f4')
        adminmanageTransitButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminmanageSiteButton = Button(self, command=self.onAdminManageSiteButtonClicked,text="Manage Site", background='#4286f4')
        adminmanageSiteButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        admintakeTransitButton = Button(self,command=self.onAdminTakeTransitButtonClicked,text="Take Transit", background='#4286f4')
        admintakeTransitButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminviewTransitHistoryButton = Button(self,command=self.onAdminViewTransitHistoryButtonClicked,text="View Transit History", background='#4286f4')
        adminviewTransitHistoryButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        administratorBackButton = Button(self, command=self.onAdministratorFunctionalityBackButtonClicked,text="Back",background='#4286f4')
        administratorBackButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onAdminManageProfileButtonClicked(self):
        profileWindow = ManageProfile(self)
        profileWindow.display()
        self.withdraw()

    def onAdminManageUserButtonClicked(self):
        manageUserWindow = ManageUser(self)
        manageUserWindow.display()
        self.withdraw()

    def onAdminManageTransitButtonClicked(self):
        manageTransitWindow = ManageTransit(self)
        manageTransitWindow.display()
        self.withdraw()

    def onAdminManageSiteButtonClicked(self):
        manageSiteWindow = ManageSite(self)
        manageSiteWindow.display()
        self.withdraw()

    def onAdminTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onAdminViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onAdministratorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class AdministratorVisitorFunctionality(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Adminstrator-Visitor')
        self.config(background='#ffffff')

    def display(self):
        administratorVisitorFunctionalityLabel = Label(self, text="Administrator Visitor Functionality", font="Helvetica",foreground='#000000', background='#ffffff')
        administratorVisitorFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        adminVisitorManageProfileButton = Button(self,command=self.onAdminVisitorManageProfileButtonClicked, text="Manage Profile",background='#4286f4')
        adminVisitorManageProfileButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorManageUserButton = Button(self,command=self.onAdminVisitorManageUserButtonClicked, text="Manage User",background='#4286f4')
        adminVisitorManageUserButton.grid(row=2, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorManageTransitButton = Button(self,command=self.onAdminVisitorManageTransitButtonClicked,text="Manage Transit", background='#4286f4')
        adminVisitorManageTransitButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorTakeTransitButton = Button(self,command=self.onAdminVisitorTakeTransitButtonClicked,text="Take Transit", background='#4286f4')
        adminVisitorTakeTransitButton.grid(row=3, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorManageSiteButton = Button(self,command=self.onAdminVisitorManageSiteButtonClicked,text="Manage Site", background='#4286f4')
        adminVisitorManageSiteButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorExploreSiteButton = Button(self, command=self.onAdminVisitorExploreSiteButtonClicked,text="Explore Site", background='#4286f4')
        adminVisitorExploreSiteButton.grid(row=4, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorExploreEventButton = Button(self,command=self.onAdminVisitorExploreEventButtonClicked,text="Explore Event", background='#4286f4')
        adminVisitorExploreEventButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorViewVisitHistoryButton = Button(self,command=self.onAdminVisitorViewVisitHistoryButtonClicked,text="View Visit History", background='#4286f4')
        adminVisitorViewVisitHistoryButton.grid(row=5, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        adminVisitorViewTransitHistoryButton = Button(self,command=self.onAdminVisitorViewTransitHistoryButtonClicked,text="View Transit History", background='#4286f4')
        adminVisitorViewTransitHistoryButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        administratorBackButton = Button(self, command=self.onAdministratorFunctionalityBackButtonClicked,text="Back",background='#4286f4')
        administratorBackButton.grid(row=6, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onAdminVisitorManageProfileButtonClicked(self):
        profileWindow = ManageProfile(self)
        profileWindow.display()
        self.withdraw()

    def onAdminVisitorManageUserButtonClicked(self):
        manageUserWindow = ManageUser(self)
        manageUserWindow.display()
        self.withdraw()

    def onAdminVisitorTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onAdminVisitorManageTransitButtonClicked(self):
        manageTransitWindow = ManageTransit(self)
        manageTransitWindow.display()
        self.withdraw()

    def onAdminVisitorManageSiteButtonClicked(self):
        manageSiteWindow = ManageSite(self)
        manageSiteWindow.display()
        self.withdraw()


    def onAdminVisitorExploreSiteButtonClicked(self):
        pass

    def onAdminVisitorExploreEventButtonClicked(self):
        pass

    def onAdminVisitorViewVisitHistoryButtonClicked(self):
        pass

    def onAdminVisitorViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onAdministratorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class ManagerVisitorFunctionality(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Manager-Visitor')
        self.config(background='#ffffff')

    def display(self):
        managerVisitorFunctionalityLabel = Label(self, text="Manager Functionality", font="Helvetica",foreground='#000000', background='#ffffff')
        managerVisitorFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        managerVisitorManageProfileButton = Button(self,command=self.onManagerVisitorManageProfileButtonClicked, text="Manage Profile",background='#4286f4')
        managerVisitorManageProfileButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorManageEventButton = Button(self,command=self.onManagerVisitorManageEventButtonClicked,text="Manage Event", background='#4286f4')
        managerVisitorManageEventButton.grid(row=2, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorViewStaffButton = Button(self,command=self.onManagerVisitorViewStaffButtonClicked,text="View Staff", background='#4286f4')
        managerVisitorViewStaffButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorViewSiteReportButton = Button(self, command=self.onManagerVisitorViewSiteReportButtonClicked,text="View Site Report", background='#4286f4')
        managerVisitorViewSiteReportButton.grid(row=3, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorExploreSiteButton = Button(self,command=self.onManagerVisitorViewStaffButtonClicked,text="Explore Site", background='#4286f4')
        managerVisitorExploreSiteButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorExploreEventButton = Button(self, command=self.onManagerVisitorExploreEventButtonClicked,text="Explore Event", background='#4286f4')
        managerVisitorExploreEventButton.grid(row=4, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorTakeTransitButton = Button(self,command=self.onManagerVisitorTakeTransitButtonClicked,text="Take Transit", background='#4286f4')
        managerVisitorTakeTransitButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorViewTransitHistoryButton = Button(self,command=self.onManagerVisitorViewTransitHistoryButtonClicked,text="View Transit History", background='#4286f4')
        managerVisitorViewTransitHistoryButton.grid(row=5, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorViewVisitHistoryButton = Button(self,command=self.onManagerVisitorViewTransitHistoryButtonClicked,text="View Visit History", background='#4286f4')
        managerVisitorViewVisitHistoryButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerVisitorBackButton = Button(self, command=self.onManagerVisitorFunctionalityBackButtonClicked,text="Back",background='#4286f4')
        managerVisitorBackButton.grid(row=6, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onManagerVisitorManageProfileButtonClicked(self):
        profileWindow = ManageProfile(self)
        profileWindow.display()
        self.withdraw()

    def onManagerVisitorManageEventButtonClicked(self):
        pass

    def onManagerVisitorViewStaffButtonClicked(self):
        pass

    def onManagerVisitorViewSiteReportButtonClicked(self):
        pass

    def onManagerVisitorExploreSiteButtonClicked(self):
        pass

    def onManagerVisitorExploreEventButtonClicked(self):
        pass

    def onManagerVisitorTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onManagerVisitorViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onManagerVisitorViewVisitHistoryButtonClicked(self):
        pass

    def onManagerVisitorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class StaffVisitorFunctionality(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Staff-Visitor')
        self.config(background='#ffffff')

    def display(self):
        staffVisitorFunctionalityLabel = Label(self, text="Staff Functionality", font="Helvetica",foreground='#000000', background='#ffffff')
        staffVisitorFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        staffVisitorManageProfileButton = Button(self,command=self.onStaffVisitorManageProfileButtonClicked, text="Manage Profile",background='#4286f4')
        staffVisitorManageProfileButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorExploreEventButton = Button(self,command=self.onStaffVisitorExploreEventButtonClicked,text="Explore Event", background='#4286f4')
        staffVisitorExploreEventButton.grid(row=2, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorViewScheduleButton = Button(self,command=self.onStaffVisitorViewScheduleButtonClicked,text="View Schedule", background='#4286f4')
        staffVisitorViewScheduleButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorExploreSiteButton = Button(self,command=self.onStaffVisitorExploreSiteButtonClicked,text="Explore Site", background='#4286f4')
        staffVisitorExploreSiteButton.grid(row=3, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorTakeTransitButton = Button(self,command=self.onStaffVisitorTakeTransitButtonClicked,text="Take Transit", background='#4286f4')
        staffVisitorTakeTransitButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorViewVisitHistoryButton = Button(self,command=self.onStaffVisitorViewVisitHistoryButtonClicked,text="View Visit History", background='#4286f4')
        staffVisitorViewVisitHistoryButton.grid(row=4, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorViewTransitHistoryButton = Button(self,command=self.onStaffVisitorViewTransitHistoryButtonClicked,text="View Transit History", background='#4286f4')
        staffVisitorViewTransitHistoryButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffVisitorBackButton = Button(self, command=self.onStaffVisitorFunctionalityBackButtonClicked,text="Back",background='#4286f4')
        staffVisitorBackButton.grid(row=5, column=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onStaffVisitorManageProfileButtonClicked(self):
        pass

    def onStaffVisitorExploreEventButtonClicked(self):
        pass

    def onStaffVisitorViewScheduleButtonClicked(self):
        pass

    def onStaffVisitorExploreSiteButtonClicked(self):
        pass

    def onStaffVisitorTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onStaffVisitorViewVisitHistoryButtonClicked(self):
        pass

    def onStaffVisitorViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onStaffVisitorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class ManagerFunctionality(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Manager-Only')
        self.config(background='#ffffff')

    def display(self):
        managerFunctionalityLabel = Label(self, text="Manager Functionality", font="Helvetica",foreground='#000000', background='#ffffff')
        managerFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        managerManageProfileButton = Button(self,command=self.onManagerManageProfileButtonClicked, text="Manage Profile",background='#4286f4')
        managerManageProfileButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerManageEventButton = Button(self,command=self.onManagerManageEventButtonClicked,text="Manage Event", background='#4286f4')
        managerManageEventButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerViewStaffButton = Button(self,command=self.onManagerViewStaffButtonClicked,text="View Staff", background='#4286f4')
        managerViewStaffButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerViewSiteReportButton = Button(self, command=self.onManagerViewSiteReportButtonClicked,text="View Site Report", background='#4286f4')
        managerViewSiteReportButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerTakeTransitButton = Button(self,command=self.onManagerTakeTransitButtonClicked,text="Take Transit", background='#4286f4')
        managerTakeTransitButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerViewTransitHistoryButton = Button(self,command=self.onManagerViewTransitHistoryButtonClicked,text="View Transit History", background='#4286f4')
        managerViewTransitHistoryButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        managerBackButton = Button(self, command=self.onManagerFunctionalityBackButtonClicked,text="Back",background='#4286f4')
        managerBackButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onManagerManageProfileButtonClicked(self):
        profileWindow = ManageProfile(self)
        profileWindow.display()
        self.withdraw()

    def onManagerManageEventButtonClicked(self):
        pass

    def onManagerViewStaffButtonClicked(self):
        pass

    def onManagerViewSiteReportButtonClicked(self):
        pass

    def onManagerTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onManagerViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onManagerFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class StaffFunctionality(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Functionality -- Staff-Only')
        self.config(background='#ffffff')

    def display(self):
        staffFunctionalityLabel = Label(self, text="Staff Functionality", font="Helvetica",foreground='#000000', background='#ffffff')
        staffFunctionalityLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E)

        staffManageProfileButton = Button(self,command=self.onStaffManageProfileButtonClicked, text="Manage Profile",background='#4286f4')
        staffManageProfileButton.grid(row=2, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffViewScheduleButton = Button(self, command=self.onStaffViewScheduleButtonClicked,text="View Schedule", background='#4286f4')
        staffViewScheduleButton.grid(row=3, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffTakeTransitButton = Button(self,command=self.onStaffTakeTransitButtonClicked,text="Take Transit", background='#4286f4')
        staffTakeTransitButton.grid(row=4, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffViewTransitHistoryButton = Button(self,command=self.onStaffViewTransitHistoryButtonClicked,text="View Transit History", background='#4286f4')
        staffViewTransitHistoryButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        staffBackButton = Button(self, command=self.onStaffFunctionalityBackButtonClicked, text="Back",background='#4286f4')
        staffBackButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def onStaffManageProfileButtonClicked(self):
        profileWindow = ManageProfile(self)
        self.withdraw()
        profileWindow.display()

    def onStaffViewScheduleButtonClicked(self):
        scheduleWindow = staffViewSchedule(self)
        self.withdraw()
        scheduleWindow.display()

    def onStaffTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onStaffViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onStaffFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()



class TakeTransit(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Take Transit')
        self.config(background='#ffffff')
        self.SQL = Queries.TakeTransit(db)

    def display(self):
        transits, sitelist = self.SQL.load()

        self.route, self.p1, self.p2, self.tdate = StringVar(), StringVar(), StringVar(), StringVar()
        self.sites, self.ttype = StringVar(), StringVar()

        self.sites.set('Any')
        self.ttype.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=transits,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(transits), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(transits.values())[0]), height=25*7)
        #self.resultTable.grid(row=0, column=0, rowspan=10, sticky=W + E)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        siteLabel = Label(self, text="Contains Site", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=0, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        siteDropdown = OptionMenu(self, self.sites, *sitelist + ['Any'])
        siteDropdown.grid(row=0, column=3, padx=(2, 5), pady=(0, 4))

        ttypeLabel = Label(self, text="Transport Type", font="Helvetica", foreground='#000000', background='#ffffff')
        ttypeLabel.grid(row=1, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        ttypeDropdown = OptionMenu(self, self.ttype, *['MARTA', 'Bus', 'Bike', 'Any'])
        ttypeDropdown.grid(row=1, column=3, padx=(2, 5), pady=(0, 4))

        priceLabel = Label(self, text="Price Range", font="Helvetica", foreground='#000000', background='#ffffff')
        priceLabel.grid(row=2, column=2, padx=(2, 2), pady=(2, 2), sticky=W)
        p1Box = Entry(self, textvariable=self.p1,  width=5)
        p1Box.grid(row=2, column=3, padx=(2, 2), pady=(2, 2), sticky=W)
        p2Box = Entry(self, textvariable=self.p2,  width=5)
        p2Box.grid(row=2, column=3, padx=(2, 2), pady=(2, 2), sticky=E)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=3, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortType = partial(self.filter, 'TransportType')
        sortTypeButton = Button(self, command=sortType, text="Sort by Transit Type", background='#4286f4')
        sortTypeButton.grid(row=4, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortPrice = partial(self.filter, 'Price')
        sortPriceButton = Button(self, command=sortPrice, text="Sort by Price", background='#4286f4')
        sortPriceButton.grid(row=5, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortSites = partial(self.filter, 'NumSites')
        sortSitesButton = Button(self, command=sortSites, text="Sort by Number of Sites", background='#4286f4')
        sortSitesButton.grid(row=6, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        dateLabel = Label(self, text="Transit Date: ", font="Helvetica", foreground='#000000', background='#ffffff')
        dateLabel.grid(row=8, column=2, padx=(4, 4), pady=(2, 2), sticky=E)
        dateBox = Entry(self, textvariable=self.tdate, width=5)
        dateBox.grid(row=8, column=3, padx=(2, 2), pady=(2, 2), sticky=W+E)

        logButton = Button(self, command=self.take, text="Log Transit", background='#4286f4')
        logButton.grid(row=9, column=3, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)



    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Route'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        p1, p2, site, ttype = self.p1.get(), self.p2.get(), self.sites.get(), self.ttype.get()

        conv = {'': None, 'Any': None}
        p1, p2, site, ttype = conv.get(p1, p1), conv.get(p2, p2), conv.get(site, site), conv.get(ttype, ttype)

        if sort is None:
            sort = 'TransportType'
        transits = self.SQL.filter(p1, p2, site, ttype, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(transits)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()

    def take(self):
        row = self.resultTable.model.getData()[self.resultTable.getSelectedRow() + 1]
        route, ttype, date = row['Route'], row['TransportType'], self.tdate.get()

        if any([route == '', ttype == '']):
            messagebox.showwarning('Error', 'No transit selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        try:
            datetime.strptime(date, '%Y-%m-%d')
        except Exception as e:
            print(e)
            messagebox.showwarning('Error', 'Incorrect date format. Please enter YYYY-MM-DD')

            return

        if self.SQL.submit(route, ttype, date, identifier) == -1:
            messagebox.showwarning('Error', 'You may not take the same transit twice in one day.')

            return

        else:
            messagebox.showwarning('Success', 'Transit successfully logged.')


class TransitHistory(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Transit History')
        self.config(background='#ffffff')
        self.SQL = Queries.TransitHistory(db)

    def display(self):
        transits, sitelist = self.SQL.load()

        self.ttype, self.sites, self.d1, self.d2, self.route = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()

        self.sites.set('Any')
        self.ttype.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=transits,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(transits), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(transits.values())[0]), height=25*7)
        #self.resultTable.grid(row=0, column=0, rowspan=10, sticky=W + E)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=20, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        siteLabel = Label(self, text="Contains Site", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=1, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        siteDropdown = OptionMenu(self, self.sites, *sitelist + ['Any'])
        siteDropdown.grid(row=1, column=3, padx=(2, 5), pady=(0, 4))

        ttypeLabel = Label(self, text="Transport Type", font="Helvetica", foreground='#000000', background='#ffffff')
        ttypeLabel.grid(row=2, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        ttypeDropdown = OptionMenu(self, self.ttype, *['MARTA', 'Bus', 'Bike', 'Any'])
        ttypeDropdown.grid(row=2, column=3, padx=(2, 5), pady=(0, 4))

        routeLabel = Label(self, text="Route", font="Helvetica", foreground='#000000', background='#ffffff')
        routeLabel.grid(row=3, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        routeDropdown = Entry(self, textvariable=self.route, width=10)
        routeDropdown.grid(row=3, column=3, padx=(2, 5), pady=(0, 4))


        dateLabel = Label(self, text="Date Range", font="Helvetica", foreground='#000000', background='#ffffff')
        dateLabel.grid(row=4, column=2, padx=(2, 2), pady=(2, 2), sticky=W)
        d1Box = Entry(self, textvariable=self.d1,  width=5)
        d1Box.grid(row=4, column=3, padx=(2, 2), pady=(2, 2), sticky=W)
        d2Box = Entry(self, textvariable=self.d2,  width=5)
        d2Box.grid(row=4, column=3, padx=(2, 2), pady=(2, 2), sticky=E)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=5, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortType = partial(self.filter, 'TransportType')
        sortTypeButton = Button(self, command=sortType, text="Sort by Transit Type", background='#4286f4')
        sortTypeButton.grid(row=6, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortRoute = partial(self.filter, 'Route')
        sortRouteButton = Button(self, command=sortRoute, text="Sort by Route", background='#4286f4')
        sortRouteButton.grid(row=7, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortDate = partial(self.filter, 'Date')
        sortDateButton = Button(self, command=sortDate, text="Sort by Date", background='#4286f4')
        sortDateButton.grid(row=8, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortPrice = partial(self.filter, 'Price')
        sortPriceButton = Button(self, command=sortPrice, text="Sort by Price", background='#4286f4')
        sortPriceButton.grid(row=9, column=2, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)


    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Route'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        d1, d2, site, ttype, route = self.d1.get(), self.d2.get(), self.sites.get(), self.ttype.get(), self.route.get()

        conv = {'': None, 'Any': None}
        p1, p2, site, ttype = conv.get(d1, d1), conv.get(d2, d2), conv.get(site, site), conv.get(ttype, ttype)

        for d in [d1, d2]:
            if d:
                try:
                    datetime.strptime(d, '%Y-%m-%d')
                except Exception as e:
                    print(e)
                    messagebox.showwarning('Error', 'Incorrect date format. Please enter YYYY-MM-DD')

        if sort is None:
            sort = 'Date'
        transits = self.SQL.filter(identifier, d1, d2, ttype, site, route, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(transits)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()


class ManageProfile(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Manage Profile')
        self.config(background='#ffffff')
        self.SQL = Queries.ManageProfile(db)
        self.email_pattern = re.compile(r'\w+@\w+\.\w+')

    def display(self):
        fname, lname, empid, phone, address, emails, site, vis = self.SQL.load(identifier)

        self.fname, self.lname, self.phone, self.emails, self.vis = StringVar(), StringVar(), StringVar(), StringVar(), BooleanVar()
        self.fname.set(fname)
        self.lname.set(lname)
        self.phone.set(phone)
        self.emails.set(' '.join(emails))
        self.vis.set(vis)


        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        titleLabel = Label(self, text='Manage Profile', font='Helvetica 15', foreground='#000000', background='#ffffff')
        titleLabel.grid(row=0, column=3, padx=(4,4), pady=(2,2), sticky=W+E)

        fnameLabel = Label(self, text="First Name", font="Helvetica", foreground='#000000', background='#ffffff')
        fnameLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        fnameBox = Entry(self, textvariable=self.fname, width=10)
        fnameBox.grid(row=1, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        lnameLabel = Label(self, text="Last Name", font="Helvetica", foreground='#000000', background='#ffffff')
        lnameLabel.grid(row=1, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        lnameBox = Entry(self, textvariable=self.lname, width=10)
        lnameBox.grid(row=1, column=5, padx=(4, 4), pady=(0, 4))

        usernameLabel = Label(self, text="Username", font="Helvetica", foreground='#000000', background='#ffffff')
        usernameLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        usernameLabel2 = Label(self, text=identifier, font="Helvetica", foreground='#000000', background='#ffffff')
        usernameLabel2.grid(row=2, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        siteLabel = Label(self, text="Site Name", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=2, column=4, padx=(4, 4), pady=(2, 2), sticky=W)
        siteLabel2 = Label(self, text=site, font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel2.grid(row=2, column=5, padx=(4, 4), pady=(0, 4))

        empidLabel = Label(self, text="Employee ID", font="Helvetica", foreground='#000000', background='#ffffff')
        empidLabel.grid(row=3, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        empidLabel2 = Label(self, text=empid, font="Helvetica", foreground='#000000', background='#ffffff')
        empidLabel2.grid(row=3, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        phoneLabel = Label(self, text="Phone", font="Helvetica", foreground='#000000', background='#ffffff')
        phoneLabel.grid(row=3, column=4, padx=(4, 4), pady=(2, 2), sticky=W)
        phoneBox = Entry(self, textvariable=self.phone, width=10)
        phoneBox.grid(row=3, column=5, padx=(4, 4), pady=(0, 4))

        addrLabel = Label(self, text="Address", font="Helvetica", foreground='#000000', background='#ffffff')
        addrLabel.grid(row=4, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        addrLabel2 = Label(self, text=address, font="Helvetica", foreground='#000000', background='#ffffff')
        addrLabel2.grid(row=4, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        emailLabel = Label(self, text="Emails (Space Separated)", font="Helvetica", foreground='#000000', background='#ffffff')
        emailLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        emailBox = Entry(self, textvariable=self.emails, width=100)
        emailBox.grid(row=5, column=2, padx=(4, 4), pady=(0, 4))

        visCheckButton = Checkbutton(self, text='Visitor', variable=self.vis)
        visCheckButton.grid(row=6, column=3, padx=(4,4), pady=(4,4))

        updateButton = Button(self, command=self.update, text="Update", background='#4286f4')
        updateButton.grid(row=10, column=3, padx=(2, 2), pady=(2, 2), sticky=W + E)


    def update(self):
        fname, lname, phone, emails, vis = self.fname.get(), self.lname.get(), self.phone.get(), self.emails.get(), self.vis.get()

        if len(fname) > 32:
            messagebox.showwarning('Error', 'First name is too long.')
            return
        elif len(lname) > 32:
            messagebox.showwarning('Error', 'Last name is too long.')
            return
        elif len(phone) != 10 or phone.isdigit() is False:
            messagebox.showwarning('Error', 'Phone number is invalid. Make sure to input a ten digit integer.')
            return

        try:
            emails = emails.split(' ')
            for email in emails:
                if self.email_pattern.fullmatch(email) is None:
                    messagebox.showwarning('Error', 'One or more emails is not in a valid format.')
                    return
        except Exception as e:
            print(e)
            messagebox.showwarning('Error', 'The format of emails input is incorrect. Make sure to separate each email with a space.')
            return

        if any(len(email) > 32 for email in emails):
            messagebox.showwarning('Error', 'One or more of your emails is too long.')
            return

        if self.SQL.submit(identifier, fname, lname, phone, emails, vis) == -1:
            messagebox.showwarning('Error', 'One or more of your emails already exists in the database under other users.')
            return

        else:
            messagebox.showwarning('Success', 'Profile successfully updated.')
            return


    def back(self):
        if 'admin' in self.master.title().lower():  # If you uncheck Visitor, then you lose visitor functionality and vice versa
            if self.SQL.get_vis(identifier):
                adminVisFuncWin = AdministratorVisitorFunctionality(self.master.master)
                adminVisFuncWin.display()
                self.destroy()
                self.master.destroy()
            else:
                adminFuncWin = AdministratorFunctionality(self.master.master)
                adminFuncWin.display()
                self.master.destroy()
                self.destroy()

        elif 'man' in self.master.title().lower():
            if self.SQL.get_vis(identifier):
                manVisFuncWin = ManagerVisitorFunctionality(self.master.master)
                manVisFuncWin.display()
                self.master.destroy()
                self.destroy()
            else:
                manFuncWin = ManagerFunctionality(self.master.master)
                manFuncWin.display()
                self.master.destroy()
                self.destroy()

        else:
            if self.SQL.get_vis(identifier):
                staffVisFuncWin = StaffVisitorFunctionality(self.master.master)
                staffVisFuncWin.display()
                self.master.destroy()
                self.destroy()
            else:
                staffFuncWin = StaffFunctionality(self.master.master)
                staffFuncWin.display()
                self.master.destroy()
                self.destroy()


class ManageUser(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Manage User')
        self.config(background='#ffffff')
        self.SQL = Queries.ManageUser(db)

    def display(self):
        users = self.SQL.load()

        self.user_name, self.user_type, self.status, =  StringVar(), StringVar(), StringVar()

        self.user_type.set('Any')
        self.status.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=users,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(users), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(users.values())[0]), height=25*7)
        #self.resultTable.grid(row=0, column=0, rowspan=10, sticky=W + E)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=13, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        unameLabel = Label(self, text="Username", font="Helvetica", foreground='#000000', background='#ffffff')
        unameLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        unameBox = Entry(self, textvariable=self.user_name, width=10)
        unameBox.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        utypeLabel = Label(self, text="User Type", font="Helvetica", foreground='#000000', background='#ffffff')
        utypeLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        utypeDropdown = OptionMenu(self, self.user_type, *['User', 'Manager', 'Visitor', 'Staff', 'Any'])
        utypeDropdown.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        statusLabel = Label(self, text="Status", font="Helvetica", foreground='#000000', background='#ffffff')
        statusLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        statusDropdown = OptionMenu(self, self.status, *['Approved', 'Pending', 'Declined', 'Any'])
        statusDropdown.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=5, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortType = partial(self.filter, 'UserType')
        sortTypeButton = Button(self, command=sortType, text="Sort by User Type", background='#4286f4')
        sortTypeButton.grid(row=6, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortName = partial(self.filter, 'Username')
        sortNameButton = Button(self, command=sortName, text="Sort by Username", background='#4286f4')
        sortNameButton.grid(row=7, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortStatus = partial(self.filter, 'Status')
        sortStatusButton = Button(self, command=sortStatus, text="Sort by User Status", background='#4286f4')
        sortStatusButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortEmail = partial(self.filter, 'Count(Email)')
        sortEmailButton = Button(self, command=sortEmail, text="Sort by Email", background='#4286f4')
        sortEmailButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        approveButton = Button(self, command=self.approve, text="Approve", background='#4286f4')
        approveButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        approveButton = Button(self, command=self.deny, text="Deny", background='#4286f4')
        approveButton.grid(row=11, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)



    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Username'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        user_name, user_type, status = self.user_name.get(), self.user_type.get(), self.status.get()

        conv = {'': None, 'Any': None}
        user_name, user_type, status = conv.get(user_name, user_name), conv.get(user_type, user_type), conv.get(status, status)

        if sort is None:
            sort = 'UserName'
        transits = self.SQL.filter(user_name, user_type, status, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(transits)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()

    def approve(self):
        row = self.resultTable.model.getData()[self.resultTable.getSelectedRow() + 1]
        user_name, user_type, status = row['Username'], row['UserType'], row['Status']

        if any([user_name == '', user_type == '', status == '']):
            messagebox.showwarning('Error', 'No user selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        self.SQL.submit(user_name)
        self.resultTable.model.setValueAt('Approved', self.resultTable.getSelectedRow(), 3)
        self.resultTable.redraw()
        messagebox.showwarning('Success', 'Status successfully updated.')

    def deny(self):
        row = self.resultTable.model.getData()[self.resultTable.getSelectedRow() + 1]
        user_name, user_type, status = row['Username'], row['UserType'], row['Status']

        if any([user_name == '', user_type == '', status == '']):
            messagebox.showwarning('Error', 'No user selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return
        elif status == 'Approved':
            messagebox.showwarning('Error', 'Cannot decline an already approved user. Let the man be, pesky admin.')
            return

        self.SQL.submit(user_name)
        self.resultTable.model.setValueAt('Declined', self.resultTable.getSelectedRow(), 3)
        self.resultTable.redraw()

        messagebox.showwarning('Success', 'Status successfully updated.')


class ManageSite(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Manage Site')
        self.config(background='#ffffff')
        self.SQL = Queries.ManageSite(db)

    def display(self):
        sites, sitenames, managers = self.SQL.load()

        self.site, self.manager, self.everyday =  StringVar(), StringVar(), StringVar()

        self.site.set('Any')
        self.manager.set('Any')
        self.everyday.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=sites,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(sites), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(sites.values())[0]), height=25*7)
        #self.resultTable.grid(row=0, column=0, rowspan=10, sticky=W + E)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=13, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        siteLabel = Label(self, text="Site", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        siteDropdown = OptionMenu(self, self.site, *sitenames + ['Any'])
        siteDropdown.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        manLabel = Label(self, text="Manager", font="Helvetica", foreground='#000000', background='#ffffff')
        manLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        manDropdown = OptionMenu(self, self.manager, *managers + ['Any'])
        manDropdown.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        everydayLabel = Label(self, text="Open Everyday", font="Helvetica", foreground='#000000', background='#ffffff')
        everydayLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        everydayDropdown = OptionMenu(self, self.everyday, *['True', 'False', 'Any'])
        everydayDropdown.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=5, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortName = partial(self.filter, 'Name')
        sortNameButton = Button(self, command=sortName, text="Sort by Name", background='#4286f4')
        sortNameButton.grid(row=6, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortMan = partial(self.filter, 'Manager')
        sortManButton = Button(self, command=sortMan, text="Sort by Manager", background='#4286f4')
        sortManButton.grid(row=7, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortEveryday = partial(self.filter, 'OpenEveryday')
        sortStatusButton = Button(self, command=sortEveryday, text="Sort by Availability per Day", background='#4286f4')
        sortStatusButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        createButton = Button(self, command=self.create, text="Create", background='#4286f4')
        createButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        deleteButton = Button(self, command=self.delete, text="Delete", background='#4286f4')
        deleteButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        editButton = Button(self, command=self.edit, text="Edit", background='#4286f4')
        editButton.grid(row=11, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)


    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['SiteName'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        site, manager, everyday = self.site.get(), self.manager.get(), self.everyday.get()

        conv = {'': None, 'Any': None}
        site, manager, everyday = conv.get(site, site), conv.get(manager, manager), conv.get(everyday, everyday)

        if sort is None:
            sort = 'SiteName'
        sites = self.SQL.filter(site, manager, everyday, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(sites)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()



    def edit(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        sitename = row['SiteName']

        if sitename == '':
            messagebox.showwarning('Error', 'No site selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return


        editSiteWindow = EditSite(self)
        editSiteWindow.display(sitename)
        self.withdraw()

    def create(self):
        createSiteWindow = CreateSite(self)
        createSiteWindow.display()
        self.withdraw()

    def delete(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        sitename = row['SiteName']

        if sitename == '':
            messagebox.showwarning('Error', 'No site selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return


        self.SQL.delete(sitename)
        self.resultTable.deleteRow()
        self.resultTable.redrawTable()
        messagebox.showwarning('Success', 'Site successfully deleted.')


class EditSite(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Edit Site')
        self.config(background='#ffffff')
        self.SQL = Queries.EditSite(db)

    def display(self, sitename):
        manager, managers, zipcode, address, everyday = self.SQL.load(sitename)
        self.original_sitename = sitename

        self.sitename, self.zipcode, self.address, self.managers, self.everyday = StringVar(), StringVar(), StringVar(), StringVar(), BooleanVar()
        self.sitename.set(sitename)
        self.managers.set(manager)
        self.zipcode.set(zipcode)
        self.address.set(address)
        self.everyday.set(everyday)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        titleLabel = Label(self, text='Edit Site', font='Helvetica 15', foreground='#000000', background='#ffffff')
        titleLabel.grid(row=0, column=3, padx=(4,4), pady=(2,2), sticky=W+E)

        sitenameLabel = Label(self, text="Name", font="Helvetica", foreground='#000000', background='#ffffff')
        sitenameLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        sitenameBox = Entry(self, textvariable=self.sitename, width=50)
        sitenameBox.grid(row=1, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        zipLabel = Label(self, text="Zip Code", font="Helvetica", foreground='#000000', background='#ffffff')
        zipLabel.grid(row=1, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        zipBox = Entry(self, textvariable=self.zipcode, width=7)
        zipBox.grid(row=1, column=5, padx=(4, 4), pady=(0, 4))

        addressLabel = Label(self, text="Address", font="Helvetica", foreground='#000000', background='#ffffff')
        addressLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        addressBox = Entry(self, textvariable=self.address, width=50)
        addressBox.grid(row=2, column=2, padx=(4, 4), pady=(0, 4))

        manLabel = Label(self, text="Manager", font="Helvetica", foreground='#000000', background='#ffffff')
        manLabel.grid(row=2, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        manDropdown = OptionMenu(self, self.managers, *managers)
        manDropdown.grid(row=2, column=5, padx=(2, 5), pady=(0, 4), sticky=W)

        everydayCheckButton = Checkbutton(self, text='Open Everyday', variable=self.everyday)
        everydayCheckButton.grid(row=3, column=3, padx=(4,4), pady=(4,4))

        updateButton = Button(self, command=self.submit, text="Update", background='#4286f4')
        updateButton.grid(row=10, column=3, padx=(2, 2), pady=(2, 2), sticky=W + E)


    def submit(self):
        sitename, manager, zipcode, address, everyday = self.sitename.get(), self.managers.get(), self.zipcode.get(), self.address.get(), self.everyday.get()

        if sitename == '':
            messagebox.showwarning('Error', 'A site must have a name.')
            return
        if len(sitename) > 64:
            messagebox.showwarning('Error', 'Site name is too long.')
            return
        elif len(address) > 64:
            messagebox.showwarning('Error', 'Address is too long.')
            return
        elif len(zipcode) != 5 or zipcode.isdigit() is False:
            messagebox.showwarning('Error', 'Zipcode is invalid. Make sure to input a 5 digit integer.')
            return

        if sitename != self.original_sitename:
            if self.SQL.update(sitename, address, zipcode, manager, everyday, original=self.original_sitename) == -1:
                messagebox.showwarning('Error', 'The sitename already exists in the database.')
                return

            else:
                messagebox.showwarning('Success', 'Profile successfully updated.')
                return
        else:
            self.SQL.update(sitename, address, zipcode, manager, everyday, original=self.original_sitename)
            messagebox.showwarning('Success', 'Profile successfully updated.')
            return



    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()


class CreateSite(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Create Site')
        self.config(background='#ffffff')
        self.SQL = Queries.CreateSite(db)

    def display(self):
        managers = self.SQL.load()

        self.sitename, self.zipcode, self.address, self.managers, self.everyday = StringVar(), StringVar(), StringVar(), StringVar(), BooleanVar()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        titleLabel = Label(self, text='Create Site', font='Helvetica 15', foreground='#000000', background='#ffffff')
        titleLabel.grid(row=0, column=3, padx=(4,4), pady=(2,2), sticky=W+E)

        sitenameLabel = Label(self, text="Name", font="Helvetica", foreground='#000000', background='#ffffff')
        sitenameLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        sitenameBox = Entry(self, textvariable=self.sitename, width=50)
        sitenameBox.grid(row=1, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        zipLabel = Label(self, text="Zip Code", font="Helvetica", foreground='#000000', background='#ffffff')
        zipLabel.grid(row=1, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        zipBox = Entry(self, textvariable=self.zipcode, width=7)
        zipBox.grid(row=1, column=5, padx=(4, 4), pady=(0, 4))

        addressLabel = Label(self, text="Address", font="Helvetica", foreground='#000000', background='#ffffff')
        addressLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        addressBox = Entry(self, textvariable=self.address, width=50)
        addressBox.grid(row=2, column=2, padx=(4, 4), pady=(0, 4))

        manLabel = Label(self, text="Manager", font="Helvetica", foreground='#000000', background='#ffffff')
        manLabel.grid(row=2, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        manDropdown = OptionMenu(self, self.managers, *managers)
        manDropdown.grid(row=2, column=5, padx=(2, 5), pady=(0, 4), sticky=W)

        everydayCheckButton = Checkbutton(self, text='Open Everyday', variable=self.everyday)
        everydayCheckButton.grid(row=3, column=3, padx=(4,4), pady=(4,4))

        createButton = Button(self, command=self.create, text="Create", background='#4286f4')
        createButton.grid(row=10, column=3, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()

    def create(self):
        sitename, manager, zipcode, address, everyday = self.sitename.get(), self.managers.get(), self.zipcode.get(), self.address.get(), self.everyday.get()

        if sitename == '':
            messagebox.showwarning('Error', 'A site must have a name.')
            return
        if len(sitename) > 64:
            messagebox.showwarning('Error', 'Site name is too long.')
            return
        elif len(address) > 64:
            messagebox.showwarning('Error', 'Address is too long.')
            return
        elif len(zipcode) != 5 or zipcode.isdigit() is False:
            messagebox.showwarning('Error', 'Zipcode is invalid. Make sure to input a 5 digit integer.')
            return
        elif manager is None or manager == '':
            messagebox.showwarning('Error', 'You must input a manager.')
            return

        if self.SQL.create(sitename, address, zipcode, manager, everyday) == -1:
                messagebox.showwarning('Error', 'The sitename already exists in the database.')
                return

        else:
            messagebox.showwarning('Success', 'Profile successfully updated.')
            return


class ManageTransit(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Manage Site')
        self.config(background='#ffffff')
        self.SQL = Queries.ManageTransit(db)

    def display(self):
        transits, sitenames = self.SQL.load()

        self.site, self.ttype, self.route, self.p1, self.p2 = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()

        self.site.set('Any')
        self.ttype.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=transits,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(transits), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(transits.values())[0]), height=25*7)
        #self.resultTable.grid(row=0, column=0, rowspan=10, sticky=W + E)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=13, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        ttypeLabel = Label(self, text="Transport Type", font="Helvetica", foreground='#000000', background='#ffffff')
        ttypeLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        ttypeDropdown = OptionMenu(self, self.ttype, *['Any', 'MARTA', 'Bus', 'Bike'])
        ttypeDropdown.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        routeLabel = Label(self, text="Route", font="Helvetica", foreground='#000000', background='#ffffff')
        routeLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2))
        routeBox = Entry(self, textvariable=self.route, width=10)
        routeBox.grid(row=3, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        siteLabel = Label(self, text="Contain Site", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        siteDropdown = OptionMenu(self, self.site, *sitenames + ['Any'])
        siteDropdown.grid(row=4, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        priceLabel = Label(self, text="Price Range", font="Helvetica", foreground='#000000', background='#ffffff')
        priceLabel.grid(row=5, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        p1Box = Entry(self, textvariable=self.p1,  width=5)
        p1Box.grid(row=5, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        p2Box = Entry(self, textvariable=self.p2,  width=5)
        p2Box.grid(row=5, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=6, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortTtype = partial(self.filter, 'TransportType')
        sortTtypeButton = Button(self, command=sortTtype, text="Sort by Transport Type", background='#4286f4')
        sortTtypeButton.grid(row=7, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortPrice = partial(self.filter, 'Price')
        sortPriceButton = Button(self, command=sortPrice, text="Sort by Price", background='#4286f4')
        sortPriceButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        createButton = Button(self, command=self.create, text="Create", background='#4286f4')
        createButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        deleteButton = Button(self, command=self.delete, text="Delete", background='#4286f4')
        deleteButton.grid(row=11, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        editButton = Button(self, command=self.edit, text="Edit", background='#4286f4')
        editButton.grid(row=12, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)


    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Route'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        site, ttype, p1, p2, route = self.site.get(), self.ttype.get(), self.p1.get(), self.p2.get(), self.route.get()

        conv = {'': None, 'Any': None}
        site, ttype, p1, p2, route = conv.get(site, site), conv.get(ttype, ttype), conv.get(p1, p1), conv.get(p2, p2), conv.get(route, route)

        if sort is None:
            sort = 'TransportType'

        sites = self.SQL.filter(site, ttype, route, p1, p2, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(sites)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()

    def edit(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        ttype, route = row['TransportType'], row['Route']

        if any([ttype == '', route == '']):
            messagebox.showwarning('Error', 'No transit selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return


        editTransitWindow = EditTransit(self)
        editTransitWindow.display(ttype, route)
        self.withdraw()

    def create(self):
        createSiteWindow = CreateSite(self)
        createSiteWindow.display()
        self.withdraw()

    def delete(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        sitename = row['SiteName']

        if sitename == '':
            messagebox.showwarning('Error', 'No site selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return


        self.SQL.delete(sitename)
        self.resultTable.deleteRow()
        self.resultTable.redrawTable()
        messagebox.showwarning('Success', 'Site successfully deleted.')


class EditTransit(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Edit Transit')
        self.config(background='#ffffff')
        self.SQL = Queries.EditTransit(db)

    def display(self, ttype, route):
        price, connected_sites, other_sites = self.SQL.load(ttype, route)
        self.ttype = ttype
        self.original_route = route
        self.route, self.price = StringVar(), StringVar()
        self.route.set(route)
        self.price.set(price)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        titleLabel = Label(self, text='Edit Transit', font='Helvetica 15', foreground='#000000', background='#ffffff')
        titleLabel.grid(row=0, column=0, padx=(4,4), pady=(2,2), sticky=W+E)

        ttypeLabel = Label(self, text=f"Transport Type: {ttype}", font="Helvetica", foreground='#000000', background='#ffffff')
        ttypeLabel.grid(row=1, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        routeLabel = Label(self, text="Route", font="Helvetica", foreground='#000000', background='#ffffff')
        routeLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        routeBox = Entry(self, textvariable=self.route, width=7)
        routeBox.grid(row=2, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        priceLabel = Label(self, text="Price", font="Helvetica", foreground='#000000', background='#ffffff')
        priceLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        priceBox = Entry(self, textvariable=self.price, width=15)
        priceBox.grid(row=3, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        self.sitesList = Listbox(self, selectmode=MULTIPLE)  # Multiple means you may select multiple sites.
        self.sitesList.grid(row=4, column=0, padx=(4,4), pady=(0,4), columnspan=2, sticky=W+E)

        for i, site in enumerate(connected_sites + other_sites):
            self.sitesList.insert(i, site)
            if site in connected_sites:
                self.sitesList.selection_set(i)

        updateButton = Button(self, command=self.submit, text="Update", background='#4286f4')
        updateButton.grid(row=10, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)


    def submit(self):
        route, price, sites = self.route.get(), self.price.get(), self.sitesList.curselection()
        sites = [self.sitesList.get(i) for i in sites]
        if price == '':
            messagebox.showwarning('Error', 'You must have a price.')
            return
        elif route == '':
            messagebox.showwarning('Error', 'You must have a route.')
            return
        elif len(sites) < 2:
            messagebox.showwarning('Error', 'Each transit must be connected to at least two sites.')
            return
        try:
            price = float(price)
            if price > 9999999.99 or price < 0:
                messagebox.showwarning('Error', 'Price is too high, negative, or has too many decimals. '
                                                'It must be a 7 digit float, with two extra decimal places.')
                return
        except:
            messagebox.showwarning('Error', 'Price must be a float.')
            return

        if self.SQL.submit(self.ttype, route, price, sites, self.original_route) == -1:
            messagebox.showwarning('Error', 'Duplicate entry for row/col')
            return

        else:
            messagebox.showwarning('Success', 'Transit successfully updated')
            return



    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()


class CreateTransit(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Create Site')
        self.config(background='#ffffff')
        self.SQL = Queries.CreateSite(db)

    def display(self):
        managers = self.SQL.load()

        self.sitename, self.zipcode, self.address, self.managers, self.everyday = StringVar(), StringVar(), StringVar(), StringVar(), BooleanVar()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        titleLabel = Label(self, text='Edit Site', font='Helvetica 15', foreground='#000000', background='#ffffff')
        titleLabel.grid(row=0, column=3, padx=(4,4), pady=(2,2), sticky=W+E)

        sitenameLabel = Label(self, text="Name", font="Helvetica", foreground='#000000', background='#ffffff')
        sitenameLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        sitenameBox = Entry(self, textvariable=self.sitename, width=50)
        sitenameBox.grid(row=1, column=2, padx=(4, 4), pady=(0, 4), sticky=W)

        zipLabel = Label(self, text="Zip Code", font="Helvetica", foreground='#000000', background='#ffffff')
        zipLabel.grid(row=1, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        zipBox = Entry(self, textvariable=self.zipcode, width=7)
        zipBox.grid(row=1, column=5, padx=(4, 4), pady=(0, 4))

        addressLabel = Label(self, text="Address", font="Helvetica", foreground='#000000', background='#ffffff')
        addressLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=E)
        addressBox = Entry(self, textvariable=self.address, width=50)
        addressBox.grid(row=2, column=2, padx=(4, 4), pady=(0, 4))

        manLabel = Label(self, text="Manager", font="Helvetica", foreground='#000000', background='#ffffff')
        manLabel.grid(row=2, column=4, padx=(4, 4), pady=(2, 2), sticky=E)
        manDropdown = OptionMenu(self, self.managers, *managers)
        manDropdown.grid(row=2, column=5, padx=(2, 5), pady=(0, 4), sticky=W)

        everydayCheckButton = Checkbutton(self, text='Open Everyday', variable=self.everyday)
        everydayCheckButton.grid(row=3, column=3, padx=(4,4), pady=(4,4))

        createButton = Button(self, command=self.create, text="Create", background='#4286f4')
        createButton.grid(row=10, column=3, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()

    def create(self):
        sitename, manager, zipcode, address, everyday = self.sitename.get(), self.managers.get(), self.zipcode.get(), self.address.get(), self.everyday.get()

        if sitename == '':
            messagebox.showwarning('Error', 'A site must have a name.')
            return
        if len(sitename) > 64:
            messagebox.showwarning('Error', 'Site name is too long.')
            return
        elif len(address) > 64:
            messagebox.showwarning('Error', 'Address is too long.')
            return
        elif len(zipcode) != 5 or zipcode.isdigit() is False:
            messagebox.showwarning('Error', 'Zipcode is invalid. Make sure to input a 5 digit integer.')
            return
        elif manager is None or manager == '':
            messagebox.showwarning('Error', 'You must input a manager.')
            return

        if self.SQL.create(sitename, address, zipcode, manager, everyday) == -1:
                messagebox.showwarning('Error', 'The sitename already exists in the database.')
                return

        else:
            messagebox.showwarning('Success', 'Profile successfully updated.')
            return


class staffEventDetail(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Event Detail')
        self.config(background='#ffffff')

    def display(self):
        self.event = StringVar()
        self.site = StringVar()
        self.startDate = StringVar()
        self.endDate = StringVar()
        self.durationDays = StringVar()
        self.staffAssigned = StringVar()
        self.capacity = StringVar()
        self.price = StringVar()
        self.description = StringVar()
        eventName = "Arboretum Walking Tour"
        siteName = "Inman Park"
        start = "2019-02-08"
        titleLabel = Label(self, text="Event Detail", font="Helvetica", foreground='#000000', background='#ffffff')
        titleLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W + E, columnspan = 2)
        eventLabel = Label(self, text="Event", foreground='#000000', background='#ffffff')
        eventLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        siteLabel = Label(self, text="Site", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=3, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=4, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        durationDaysLabel = Label(self, text="Duration Days", foreground='#000000', background='#ffffff')
        durationDaysLabel.grid(row=6, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        staffAssignedLabel = Label(self, text="Staff Assigned", foreground='#000000', background='#ffffff')
        staffAssignedLabel.grid(row=7, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        capacityLabel = Label(self, text="Capacity", foreground='#000000', background='#ffffff')
        capacityLabel.grid(row=8, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        priceLabel = Label(self, text="Price", foreground='#000000', background='#ffffff')
        priceLabel.grid(row=9, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        descriptionLabel = Label(self, text="Description", foreground='#000000', background='#ffffff')
        descriptionLabel.grid(row=10, column=1, padx=(4, 4), pady=(2, 2), sticky=W)
        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=11, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)
        cursor.execute("SELECT * FROM event WHERE EventName = %s AND SiteName = %s AND %s BETWEEN StartDate AND EndDate", (eventName, siteName, start))
        result = cursor.fetchone()
        print(result)
        eventLabelData = Label(self, text=result.get("EventName"), foreground='#000000', background='#ffffff')
        eventLabelData.grid(row=2, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        siteLabelData = Label(self, text=result.get("SiteName"), foreground='#000000', background='#ffffff')
        siteLabelData.grid(row=3, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        startDateLabelData = Label(self, text=start, foreground='#000000', background='#ffffff')
        startDateLabelData.grid(row=4, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        endDateLabelData = Label(self, text=result.get("EndDate"), foreground='#000000', background='#ffffff')
        endDateLabelData.grid(row=5, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        durationDaysLabelData = Label(self, text="Duration Days", foreground='#000000', background='#ffffff')
        durationDaysLabelData.grid(row=6, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        staffAssignedLabelData = Label(self, text="Staff Assigned", foreground='#000000', background='#ffffff')
        staffAssignedLabelData.grid(row=7, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        capacityLabelData = Label(self, text=result.get("Capacity"), foreground='#000000', background='#ffffff')
        capacityLabelData.grid(row=8, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        priceLabelData = Label(self, text=result.get("Price"), foreground='#000000', background='#ffffff')
        priceLabelData.grid(row=9, column=2, padx=(4, 4), pady=(2, 2), sticky=W)
        descriptionLabelData = Text(self, height=4, width=15, wrap=WORD)
        self.description.set(result.get("Description"))
        descriptionLabelData.insert("1.0", self.description.get())
        descriptionLabelData.grid(row=10, column=2, padx=(4, 4), pady=(2, 2), sticky=W)

    def back(self):
        self.master.deiconify()
        self.destroy()

class staffViewSchedule(Toplevel):
    def __init__(self, master):
            Toplevel.__init__(self)
            self.master = master
            self.title('View Schedule')
            self.config(background='#ffffff')
            self.SQL = Queries.StaffViewSchedule(db)

    def display(self):
        self.eventName = StringVar()
        self.descriptionKeyword = StringVar()
        self.startDate = StringVar()
        self.endDate = StringVar()

        schedule = self.SQL.load()
        self.resultTable = TableCanvas(self, editable=True, data=schedule,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(schedule), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(schedule.values())[0]), height=25*7)
        #self.resultTable.grid(row=0, column=0, rowspan=10, sticky=W + E)
        self.resultTable.show()

        eventNameLabel = Label(self, text="Event Name", foreground='#000000', background='#ffffff')
        eventNameLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        descriptionKeywordLabel = Label(self, text="Description Keyword", foreground='#000000', background='#ffffff')
        descriptionKeywordLabel.grid(row=3, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=4, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        filterButton = Button(self, text="Filter", command=self.filter, background='#4286f4')
        filterButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W)

        viewEventButton = Button(self, text="View Event", background='#4286f4')
        viewEventButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        eventNameBox = Entry(self, textvariable=self.eventName, width=20)
        eventNameBox.grid(row=2, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        descriptionKeywordBox = Entry(self, textvariable=self.descriptionKeyword, width=20)
        descriptionKeywordBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        startDateBox = Entry(self, textvariable=self.startDate, width=20)
        startDateBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        endDateBox = Entry(self, textvariable=self.endDate, width=20)
        endDateBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['EventName'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        eName, keyword, sDate, eDate = self.eventName.get(), self.descriptionKeyword.get(), self.startDate.get(), self.endDate.get()

        conv = {'': None, 'Any': None}
        eName, keyword, sDate, eDate = conv.get(eName, eName), conv.get(keyword, keyword), conv.get(sDate, sDate), conv.get(eDate, eDate)

        if sort is None:
            sort = 'E.EventName'
        schedule = self.SQL.filter(identifier, eName, sDate, eDate, keyword, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(schedule)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorExploreEvent(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Explore Event')
        self.config(background='#ffffff')

    def display(self):
        self.eventName = StringVar()
        self.descriptionKeyword = StringVar()
        self.siteName = StringVar()
        self.startDate = StringVar()
        self.endDate = StringVar()
        eventNameLabel = Label(self, text="Event Name", foreground='#000000', background='#ffffff')
        eventNameLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        descriptionKeywordLabel = Label(self, text="Description Keyword", foreground='#000000', background='#ffffff')
        descriptionKeywordLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        siteNameLabel = Label(self, text="Site Name", foreground='#000000', background='#ffffff')
        siteNameLabel.grid(row=3, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=4, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        filterButton = Button(self, text="Filter", background='#4286f4')
        filterButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        eventDetailButton = Button(self, text="Event Detail", background='#4286f4')
        eventDetailButton.grid(row=7, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        eventNameBox = Entry(self, textvariable=self.eventName, width=20)
        eventNameBox.grid(row=1, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        descriptionKeywordBox = Entry(self, textvariable=self.descriptionKeyword, width=20)
        descriptionKeywordBox.grid(row=2, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        siteNameBox = Entry(self, textvariable=self.siteName, width=20)
        siteNameBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        startDateBox = Entry(self, textvariable=self.startDate, width=20)
        startDateBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        endDateBox = Entry(self, textvariable=self.endDate, width=20)
        endDateBox.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorEventDetail(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Event Detail')
        self.config(background='#ffffff')

    def display(self):
        pass

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorExploreSite(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Explore Site')
        self.config(background='#ffffff')

    def display(self):
        self.includeVisited = StringVar()
        self.siteName = StringVar()
        self.siteName.set("")
        self.siteList = []
        self.openEveryday = StringVar()
        self.openEveryday.set("")
        self.openEverydayList = ["Yes", "No"]
        self.startDate = StringVar()
        self.endDate = StringVar()
        self.totalVisitsRange1 = StringVar()
        self.totalVisitsRange2 = StringVar()
        self.eventCountRange1 = StringVar()
        self.eventCountRange2 = StringVar()
        siteLabel = Label(self, text="Site", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=1, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        openEverydayLabel = Label(self, text="Open Everyday", foreground='#000000', background='#ffffff')
        openEverydayLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=3, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=4, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        totalVisitsRangeLabel = Label(self, text="Total Visits Range", foreground='#000000', background='#ffffff')
        totalVisitsRangeLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        eventCountRangeLabel = Label(self, text="Event Count Range", foreground='#000000', background='#ffffff')
        eventCountRangeLabel.grid(row=6, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        includeVisitedCheckbutton = Checkbutton(self, variable=self.includeVisited, text="Include Visited", foreground='#000000', background='#ffffff')
        includeVisitedCheckbutton.grid(row=7, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        filterButton = Button(self, text="Filter", background='#4286f4')
        filterButton.grid(row=8, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        siteDetailButton = Button(self, text="Site Detail", background='#4286f4')
        siteDetailButton.grid(row=8, column=2, padx=(2, 2), pady=(2, 2), sticky=W)
        transitDetailButton = Button(self, text="Transit Detail", background='#4286f4')
        transitDetailButton.grid(row=8, column=3, padx=(2, 2), pady=(2, 2), sticky=W)
        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=9, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        siteNameDropdown = OptionMenu(self, self.siteName, *self.siteList)
        siteNameDropdown.grid(row=1, column=2, padx=(8, 5), pady=(0, 4), sticky=W)
        openEverydayDropdown = OptionMenu(self, self.openEveryday, *self.openEverydayList)
        openEverydayDropdown.grid(row=2, column=2, padx=(8, 5), pady=(0, 4), sticky=W)
        startDateBox = Entry(self, textvariable=self.startDate, width=20)
        startDateBox.grid(row=3, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        endDateBox = Entry(self, textvariable=self.endDate, width=20)
        endDateBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        totalVisitsRange1Box = Entry(self, textvariable=self.totalVisitsRange1, width=20)
        totalVisitsRange1Box.grid(row=5, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        totalVisitsRange2Box = Entry(self, textvariable=self.totalVisitsRange2, width=20)
        totalVisitsRange2Box.grid(row=5, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        eventCountRange1Box = Entry(self, textvariable=self.eventCountRange1, width=20)
        eventCountRange1Box.grid(row=6, column=2, padx=(0, 2), pady=(0, 4), sticky=E)
        eventCountRange2Box = Entry(self, textvariable=self.eventCountRange2, width=20)
        eventCountRange2Box.grid(row=6, column=3, padx=(0, 2), pady=(0, 4), sticky=E)

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorTransitDetail(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Transit Detail')
        self.config(background='#ffffff')

    def display(self):
        pass

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorSiteDetail(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Site Detail')
        self.config(background='#ffffff')

    def display(self):
        pass

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorVisitHistory(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Visit History')
        self.config(background='#ffffff')

    def display(self):
        pass

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

                             cursorclass=pymysql.cursors.DictCursor)

        global cursor
        cursor = db.cursor()

    except Exception as e:
        print(e)
        print('Error! Cannot connect. Please double check the password variable to your MySQL server at the top of '
              'this file.')
        sys.exit()

    print("Connected!")

    root = Tk()
    app = Beltline(root)
    root.mainloop()

    db.close()
    sys.exit()
