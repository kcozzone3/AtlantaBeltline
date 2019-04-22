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
MYSQL_PASSWORD = 'Gwhiteley99'
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
        exploreEventWindow = visitorExploreEvent(self)
        exploreEventWindow.display()
        self.withdraw()


    def onVisitorFunctionalityExploreSiteButtonClicked(self):
        ExploreSiteWindow = visitorExploreSite(self)
        ExploreSiteWindow.display()
        self.withdraw()

    def onVisitorFunctionalityVisitHistoryButtonButtonClicked(self):
        visitHistoryWindow = VisitHistory(self)
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
        ExploreSiteWindow = visitorExploreSite(self)
        ExploreSiteWindow.display()
        self.withdraw()

    def onAdminVisitorExploreEventButtonClicked(self):
        exploreEventWindow = visitorExploreEvent(self)
        exploreEventWindow.display()
        self.withdraw()

    def onAdminVisitorViewVisitHistoryButtonClicked(self):
        visitHistoryWindow = VisitHistory(self)
        self.withdraw()
        visitHistoryWindow.display()

    def onAdminVisitorViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onAdministratorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class ManagerVisitorFunctionality(Toplevel):
    def __init__(self, master):
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
        manageEventWindow = ManageEvent(self)
        manageEventWindow.display()
        self.withdraw()

    def onManagerVisitorViewStaffButtonClicked(self):
        viewStaffWindow = ManageStaff(self)
        viewStaffWindow.display()
        self.withdraw()

    def onManagerVisitorViewSiteReportButtonClicked(self):
        siteReportWindow = SiteReport(self)
        siteReportWindow.display()
        self.withdraw()

    def onManagerVisitorExploreSiteButtonClicked(self):
        ExploreSiteWindow = visitorExploreSite(self)
        ExploreSiteWindow.display()
        self.withdraw()

    def onManagerVisitorExploreEventButtonClicked(self):
        exploreEventWindow = visitorExploreEvent(self)
        exploreEventWindow.display()
        self.withdraw()

    def onManagerVisitorTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onManagerVisitorViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onManagerVisitorViewVisitHistoryButtonClicked(self):
        visitHistoryWindow = VisitHistory(self)
        self.withdraw()
        visitHistoryWindow.display()

    def onManagerVisitorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class StaffVisitorFunctionality(Toplevel):
    def __init__(self, master):
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
        profileWindow = ManageProfile(self)
        profileWindow.display()
        self.withdraw()

    def onStaffVisitorExploreEventButtonClicked(self):
        exploreEventWindow = visitorExploreEvent(self)
        exploreEventWindow.display()
        self.withdraw()

    def onStaffVisitorViewScheduleButtonClicked(self):
        viewScheduleWindow = StaffViewSchedule(self)
        viewScheduleWindow.display()
        self.withdraw()

    def onStaffVisitorExploreSiteButtonClicked(self):
        ExploreSiteWindow = visitorExploreSite(self)
        ExploreSiteWindow.display()
        self.withdraw()

    def onStaffVisitorTakeTransitButtonClicked(self):
        takeTransitWindow = TakeTransit(self)
        takeTransitWindow.display()
        self.withdraw()

    def onStaffVisitorViewVisitHistoryButtonClicked(self):
        visitHistoryWindow = VisitHistory(self)
        self.withdraw()
        visitHistoryWindow.display()

    def onStaffVisitorViewTransitHistoryButtonClicked(self):
        transitHistoryWindow = TransitHistory(self)
        transitHistoryWindow.display()
        self.withdraw()

    def onStaffVisitorFunctionalityBackButtonClicked(self):
        self.master.deiconify()
        self.destroy()


class ManagerFunctionality(Toplevel):
    def __init__(self, master):
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
        manageEventWindow = ManageEvent(self)
        manageEventWindow.display()
        self.withdraw()

    def onManagerViewStaffButtonClicked(self):
        viewStaffWindow = ManageStaff(self)
        viewStaffWindow.display()
        self.withdraw()

    def onManagerViewSiteReportButtonClicked(self):
        siteReportWindow = SiteReport(self)
        siteReportWindow.display()
        self.withdraw()

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
        viewScheduleWindow = StaffViewSchedule(self)
        viewScheduleWindow.display()
        self.withdraw()

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

        self.SQL.submit(user_name, 'Approved')
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

        self.SQL.submit(user_name, 'Declined')
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
        self.title('Manage Transit')
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
        createTransitWindow = CreateTransit(self)
        createTransitWindow.display()
        self.withdraw()

    def delete(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        ttype, route = row['TransportType'], row['Route']

        if route == '':
            messagebox.showwarning('Error', 'No transit selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        self.SQL.delete(ttype, route)
        self.resultTable.deleteRow()
        self.resultTable.redrawTable()
        messagebox.showwarning('Success', 'Transit successfully deleted.')


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
            messagebox.showwarning('Error', 'That Route/Transit combination already exist')
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
        self.title('Create Transit')
        self.config(background='#ffffff')
        self.SQL = Queries.CreateTransit(db)

    def display(self):
        sites = self.SQL.load()
        self.ttype, self.route, self.price, self.connected_sites = StringVar(), StringVar(), StringVar(), StringVar()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        titleLabel = Label(self, text='Create Transit', font='Helvetica 15', foreground='#000000', background='#ffffff')
        titleLabel.grid(row=0, column=0, padx=(4,4), pady=(2,2), sticky=W+E)

        ttypeLabel = Label(self, text=f"Transport Type", font="Helvetica", foreground='#000000', background='#ffffff')
        ttypeLabel.grid(row=1, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        utypeDropdown = OptionMenu(self, self.ttype, *['MARTA', 'Bus', 'Bike'])
        utypeDropdown.grid(row=1, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

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

        for i, site in enumerate(sites):
            self.sitesList.insert(i, site)

        createButton = Button(self, command=self.submit, text="Create", background='#4286f4')
        createButton.grid(row=10, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)


    def submit(self):
        ttype, route, price, sites = self.ttype.get(), self.route.get(), self.price.get(), self.sitesList.curselection()
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
                messagebox.showwarning('Error', 'Price is too long, negative, or has too many decimals. '
                                                'It must be a 7 digit float, with two extra decimal places.')
                return
        except:
            messagebox.showwarning('Error', 'Price must be a float.')
            return

        if self.SQL.create(ttype, route, price, sites) == -1:
            messagebox.showwarning('Error', 'That transit type/route combination already exists.')
            return

        else:
            messagebox.showwarning('Success', 'Transit successfully created')
            return



    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()  # Refreshes by removing all widgets and then reloading them.
        self.master.display()
        self.master.deiconify()
        self.destroy()


class ManageEvent(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Manage Event')
        self.config(background='#ffffff')
        self.SQL = Queries.ManageEvent(db)

    def display(self):
        events = self.SQL.load()

        self.name, self.keyword, self.d1, self.d2, self.dur1 = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
        self.dur2, self.vis1, self.vis2, self.rev1, self.rev2 = StringVar(), StringVar(), StringVar(),  StringVar(), StringVar()

        self.resultTable = TableCanvas(self, editable=True, data=events,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(events), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(events.values())[0]), height=25*7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=20, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        nameLabel = Label(self, text="Name", font="Helvetica", foreground='#000000', background='#ffffff')
        nameLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        nameBox = Entry(self, textvariable=self.name, width=10)
        nameBox.grid(row=2, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        keywordLabel = Label(self, text="Description Keyword", font="Helvetica", foreground='#000000', background='#ffffff')
        keywordLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2))
        keywordBox = Entry(self, textvariable=self.keyword, width=10)
        keywordBox.grid(row=3, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        d1Label = Label(self, text="Start Date", font="Helvetica", foreground='#000000', background='#ffffff')
        d1Label.grid(row=4, column=0, padx=(4, 4), pady=(2, 2))
        d1Box = Entry(self, textvariable=self.d1, width=10)
        d1Box.grid(row=4, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        d2Label = Label(self, text="End Date", font="Helvetica", foreground='#000000', background='#ffffff')
        d2Label.grid(row=5, column=0, padx=(4, 4), pady=(2, 2))
        d2Box = Entry(self, textvariable=self.d2, width=10)
        d2Box.grid(row=5, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        durLabel = Label(self, text="Duration Range", font="Helvetica", foreground='#000000', background='#ffffff')
        durLabel.grid(row=6, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        dur1Box = Entry(self, textvariable=self.dur1,  width=5)
        dur1Box.grid(row=6, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        dur2Box = Entry(self, textvariable=self.dur2,  width=5)
        dur2Box.grid(row=6, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        revLabel = Label(self, text="Revenue Range", font="Helvetica", foreground='#000000', background='#ffffff')
        revLabel.grid(row=7, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        rev1Box = Entry(self, textvariable=self.rev1,  width=5)
        rev1Box.grid(row=7, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        rev2Box = Entry(self, textvariable=self.rev2,  width=5)
        rev2Box.grid(row=7, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        visLabel = Label(self, text="Visit Range", font="Helvetica", foreground='#000000', background='#ffffff')
        visLabel.grid(row=8, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        vis1Box = Entry(self, textvariable=self.vis1, width=5)
        vis1Box.grid(row=8, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        vis2Box = Entry(self, textvariable=self.vis2, width=5)
        vis2Box.grid(row=8, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortName = partial(self.filter, 'EventName')
        sortTtypeButton = Button(self, command=sortName, text="Sort by Name", background='#4286f4')
        sortTtypeButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortStaff = partial(self.filter, 'StaffCount')
        sortStaffButton = Button(self, command=sortStaff, text="Sort by Staff Count", background='#4286f4')
        sortStaffButton.grid(row=11, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortDur = partial(self.filter, 'Duration')
        sortDurButton = Button(self, command=sortDur, text="Sort by Duration", background='#4286f4')
        sortDurButton.grid(row=12, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortVisits = partial(self.filter, 'Visits')
        sortVisitsButton = Button(self, command=sortVisits, text="Sort by Visits", background='#4286f4')
        sortVisitsButton.grid(row=13, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortRev = partial(self.filter, 'Revenue')
        sortRevButton = Button(self, command=sortRev, text="Sort by Revenue", background='#4286f4')
        sortRevButton.grid(row=14, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        createButton = Button(self, command=self.create, text="Create", background='#4286f4')
        createButton.grid(row=15, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        deleteButton = Button(self, command=self.delete, text="Delete", background='#4286f4')
        deleteButton.grid(row=16, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        editButton = Button(self, command=self.edit, text="Edit/View", background='#4286f4')
        editButton.grid(row=17, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['EventName'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        name, keyword, d1, d2, dur1 = self.name.get(), self.keyword.get(), self.d1.get(), self.d2.get(), self.dur1.get()
        dur2, vis1, vis2, rev1, rev2 = self.dur2.get(), self.vis1.get(), self.vis2.get(), self.rev1.get(), self.rev2.get()

        conv = {'': None, 'Any': None}
        filts = [conv.get(v,v) for v in [name, keyword, d1, d2, dur1, dur2, vis1, vis2, rev1, rev2]]

        if sort is None:
            sort = 'EventName'

        if d1:
            try:
                datetime.strptime(d1, '%Y-%m-%d')
            except Exception as e:
                print(e)
                messagebox.showwarning('Error', 'Incorrect date format. Please enter YYYY-MM-DD')
                return

        if d2:
            try:
                datetime.strptime(d2, '%Y-%m-%d')
            except Exception as e:
                print(e)
                messagebox.showwarning('Error', 'Incorrect date format. Please enter YYYY-MM-DD')
                return
        if dur1 and not dur1.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if dur2 and not dur2.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if rev1 and not rev1.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if rev2 and not rev2.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if vis1 and not vis1.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if vis2 and not vis2.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return

        events = self.SQL.filter(identifier, *filts + [sort])

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(events)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()

    def edit(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        eventname, sitename, startdate = row['EventName'], row['SiteName'], row['StartDate']

        if eventname == '':
            messagebox.showwarning('Error', 'No event selected. Make sure to click on the non-empty '
                                            'row number to select which event you are editing.')
            return

        editEventWindow = EditEvent(self)
        editEventWindow.display(eventname, sitename, startdate)
        self.withdraw()

    def create(self):
        createEventWindow = CreateEvent(self)
        createEventWindow.display()
        self.withdraw()

    def delete(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        eventname, sitename, startdate = row['EventName'], row['SiteName'], row['StartDate']

        if eventname == '':
            messagebox.showwarning('Error', 'No event selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        self.SQL.delete(eventname, sitename, startdate)
        self.resultTable.deleteRow()
        self.resultTable.redrawTable()
        messagebox.showwarning('Success', 'Event successfully deleted.')


class EditEvent(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Edit Event')
        self.config(background='#ffffff')
        self.SQL = Queries.EditEvent(db)

    def display(self, eventname, sitename, startdate):
        price, enddate, minstaffreq, cap, cur_staff, avail_staff, desc, dailies = self.SQL.load(identifier, eventname, sitename, startdate)
        self.staff, self.desc, self.vis1, self.vis2, self.rev1, self.rev2 = StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(),
        self.desc.set(desc)
        self.eventname, self.sitename, self.startdate = eventname, sitename, startdate

        self.resultTable = TableCanvas(self, editable=True, data=dailies,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(dailies), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150 * len(list(dailies.values())[0]), height=25 * 7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=25, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        eventnameLabel = Label(self, text=f"Name: {eventname}", font="Helvetica", foreground='#000000', background='#ffffff')
        eventnameLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        priceLabel = Label(self, text=f"Price: ${price}", font="Helvetica", foreground='#000000', background='#ffffff')
        priceLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        startdateLabel = Label(self, text=f"Start Date: {startdate}", font="Helvetica", foreground='#000000', background='#ffffff')
        startdateLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        enddateLabel = Label(self, text=f"End Date: {enddate}", font="Helvetica", foreground='#000000', background='#ffffff')
        enddateLabel.grid(row=5, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        minStaffLabel = Label(self, text=f"Min Staff Required: {minstaffreq}", font="Helvetica", foreground='#000000', background='#ffffff')
        minStaffLabel.grid(row=6, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        capacityLabel = Label(self, text=f"Capacity: {cap}", font="Helvetica", foreground='#000000', background='#ffffff')
        capacityLabel.grid(row=7, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        descLabel = Label(self, text="Description", font="Helvetica", foreground='#000000', background='#ffffff')
        descLabel.grid(row=8, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        descBox = Entry(self, textvariable=self.desc, width=100)
        descBox.grid(row=8, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        visLabel = Label(self, text="Daily Visit Range", font="Helvetica", foreground='#000000', background='#ffffff')
        visLabel.grid(row=9, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        vis1Box = Entry(self, textvariable=self.vis1, width=5)
        vis1Box.grid(row=9, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        vis2Box = Entry(self, textvariable=self.vis2, width=5)
        vis2Box.grid(row=9, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        revLabel = Label(self, text="Daily Revenue Range", font="Helvetica", foreground='#000000', background='#ffffff')
        revLabel.grid(row=10, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        rev1Box = Entry(self, textvariable=self.rev1,  width=5)
        rev1Box.grid(row=10, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        rev2Box = Entry(self, textvariable=self.rev2,  width=5)
        rev2Box.grid(row=10, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        self.staffList = Listbox(self, selectmode=MULTIPLE)  # Multiple means you may select multiple sites.
        self.staffList.grid(row=11, column=0, padx=(4,4), pady=(0,4), columnspan=2, sticky=W+E)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=12, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortVisits = partial(self.filter, 'DailyVisits')
        sortVisitsButton = Button(self, command=sortVisits, text="Sort by Visits", background='#4286f4')
        sortVisitsButton.grid(row=13, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortRev = partial(self.filter, 'DailyRevenue')
        sortRevButton = Button(self, command=sortRev, text="Sort by Revenue", background='#4286f4')
        sortRevButton.grid(row=14, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortDate = partial(self.filter, 'Date')
        sortDateButton = Button(self, command=sortDate, text="Sort by Date", background='#4286f4')
        sortDateButton.grid(row=15, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        updateButton = Button(self, command=partial(self.submit, minstaffreq), text="Update", background='#4286f4')
        updateButton.grid(row=16, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        for i, staffmember in enumerate(cur_staff + avail_staff):
            self.staffList.insert(i, staffmember)
            if staffmember in cur_staff:
                self.staffList.selection_set(i)

    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Date'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        rev1, rev2, vis1, vis2 = self.rev1.get(), self.rev2.get(), self.vis1.get(), self.vis2.get()

        conv = {'': None, 'Any': None}
        rev1, rev2, vis1, vis2 = conv.get(rev1, rev1), conv.get(rev2, rev2), conv.get(vis1, vis1), conv.get(vis2,vis2)

        if sort is None:
            sort = 'Date'

        if rev1 and not rev1.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if rev2 and not rev2.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if vis1 and not vis1.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        if vis2 and not vis2.isdigit():
            messagebox.showwarning('Error', 'Duration, Visits, and Revenue must be numbers')
            return
        print(rev2)
        dailies = self.SQL.filter(identifier, self.eventname, self.sitename, self.startdate, rev1, rev2, vis1, vis2, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(dailies)
        self.resultTable.redraw()

    def submit(self, minstaff):
        desc, staff = self.desc.get(), self.staffList.curselection()
        staff = [self.staffList.get(i) for i in staff]
        if desc == '':
            messagebox.showwarning('Error', 'You must have a description.')
            return
        elif len(staff) < minstaff:
            messagebox.showwarning('Error', 'You need more staff')
            return

        self.SQL.submit(self.eventname, self.sitename, self.startdate, desc, staff)
        messagebox.showwarning('Success', 'Event successfully updated.')

    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()


class CreateEvent(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Create Transit')
        self.config(background='#ffffff')
        self.SQL = Queries.CreateEvent(db)

    def display(self):
        self.eventname, self.price, self.cap, self.minstaff, self.d1, self.d2, self.desc = StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=25, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        eventnameLabel = Label(self, text=f"Name", font="Helvetica", foreground='#000000', background='#ffffff')
        eventnameLabel.grid(row=1, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        eventnameBox = Entry(self, textvariable=self.eventname, width=100)
        eventnameBox.grid(row=1, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        priceLabel = Label(self, text=f"Price", font="Helvetica", foreground='#000000', background='#ffffff')
        priceLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        priceBox = Entry(self, textvariable=self.price, width=100)
        priceBox.grid(row=2, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        capLabel = Label(self, text=f"Capacity", font="Helvetica", foreground='#000000', background='#ffffff')
        capLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        capBox = Entry(self, textvariable=self.cap, width=100)
        capBox.grid(row=3, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        minStaffLabel = Label(self, text=f"Min Staff Required", font="Helvetica", foreground='#000000', background='#ffffff')
        minStaffLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        minstaffBox = Entry(self, textvariable=self.minstaff, width=100)
        minstaffBox.grid(row=4, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        d1Label = Label(self, text=f"Start Date", font="Helvetica", foreground='#000000', background='#ffffff')
        d1Label.grid(row=5, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        d1Box = Entry(self, textvariable=self.d1, width=100)
        d1Box.grid(row=5, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        d2Label = Label(self, text=f"End Date", font="Helvetica", foreground='#000000', background='#ffffff')
        d2Label.grid(row=6, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        d2Box = Entry(self, textvariable=self.d2, width=100)
        d2Box.grid(row=6, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        descLabel = Label(self, text=f"Description", font="Helvetica", foreground='#000000', background='#ffffff')
        descLabel.grid(row=7, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        descBox = Entry(self, textvariable=self.desc, width=100)
        descBox.grid(row=7, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        self.staffList = Listbox(self, selectmode=MULTIPLE)  # Multiple means you may select multiple sites.
        self.staffList.grid(row=8, column=0, padx=(4, 4), pady=(0, 4), columnspan=2, sticky=W + E)

        getStaffButton = Button(self, command=self.getstaff, text="Get possible staff members", background='#4286f4')
        getStaffButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        createButton = Button(self, command=self.submit, text="Create", background='#4286f4')
        createButton.grid(row=11, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def getstaff(self):
        d1, d2 = self.d1.get(), self.d2.get()

        if any([d1 == '', d2 == '']):
            messagebox.showwarning('Error', 'You must input both dates first.')
            return

        try:
            datetime.strptime(d1, '%Y-%m-%d')
            datetime.strptime(d2, '%Y-%m-%d')
        except Exception as e:
            print(e)
            messagebox.showwarning('Error', 'Incorrect date format. Please enter YYYY-MM-DD')

        staff = self.SQL.get_staff(d1, d2)
        self.staffList.delete(0, END)
        for i, staffmember in enumerate(staff):
            self.staffList.insert(i, staffmember)


    def submit(self):
        eventname, price, cap, minstaff, d1, d2, desc, staff = self.eventname.get(), self.price.get(), self.cap.get(), self.minstaff.get(), self.d1.get(), self.d2.get(), self.desc.get(), self.staffList.curselection()
        staff = [self.staffList.get(i) for i in staff]

        if any([price == '', cap == '', minstaff == '', d1 == '', d2 == '', desc == '', staff == '']):
            messagebox.showwarning('Error', 'All fields are required.')
            return
        elif any([not cap.isdigit(), not minstaff.isdigit()]):
            messagebox.showwarning('Error', 'Capacity and Min Staff must be ints')
            return
        elif len(staff) < int(minstaff):
            messagebox.showwarning('Error', 'You need more staff.')
            return

        try:
            price = float(price)
            if price > 9999999.99 or price < 0:
                messagebox.showwarning('Error', 'Price is too long, negative, or has too many decimals. '
                                                'It must be a 7 digit float, with two extra decimal places.')
                return
        except:
            messagebox.showwarning('Error', 'Price must be a float.')
            return

        if self.SQL.create(identifier, eventname, price, cap, minstaff, d1, d2, desc, staff) == -1:
            messagebox.showwarning('Error', 'That event already exists.')
            return

        else:
            messagebox.showwarning('Success', 'Event successfully created')
            return



    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()  # Refreshes by removing all widgets and then reloading them.
        self.master.display()
        self.master.deiconify()
        self.destroy()


class ManageStaff(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Manage Staff')
        self.config(background='#ffffff')
        self.SQL = Queries.ManageStaff(db)

    def display(self):
        staff, sites = self.SQL.load()

        self.site, self.fname, self.lname, self.d1, self.d2 = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()

        self.site.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=staff,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(staff), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(staff.values())[0]), height=25*7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=13, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        siteLabel = Label(self, text="Site", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        siteDropdown = OptionMenu(self, self.site, *sites + ['Any'])
        siteDropdown.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        fnameLabel = Label(self, text="First Name", font="Helvetica", foreground='#000000', background='#ffffff')
        fnameLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2))
        fnameBox = Entry(self, textvariable=self.fname, width=10)
        fnameBox.grid(row=3, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        lnameLabel = Label(self, text="Last Name", font="Helvetica", foreground='#000000', background='#ffffff')
        lnameLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2))
        lnameBox = Entry(self, textvariable=self.lname, width=10)
        lnameBox.grid(row=4, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        d1Label = Label(self, text="Start Date", font="Helvetica", foreground='#000000', background='#ffffff')
        d1Label.grid(row=5, column=0, padx=(4, 4), pady=(2, 2))
        d1Box = Entry(self, textvariable=self.d1, width=10)
        d1Box.grid(row=5, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        d2Label = Label(self, text="End Date", font="Helvetica", foreground='#000000', background='#ffffff')
        d2Label.grid(row=6, column=0, padx=(4, 4), pady=(2, 2))
        d2Box = Entry(self, textvariable=self.d2, width=10)
        d2Box.grid(row=6, column=1, padx=(4, 4), pady=(0, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=7, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortType = partial(self.filter, 'Name')
        sortTypeButton = Button(self, command=sortType, text="Sort by Name", background='#4286f4')
        sortTypeButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortName = partial(self.filter, 'NumShifts')
        sortNameButton = Button(self, command=sortName, text="Sort by # Of Event Shifts", background='#4286f4')
        sortNameButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Name'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        site, fname, lname, d1, d2 = self.site.get(), self.fname.get(), self.lname.get(), self.d1.get(), self.d2.get()

        conv = {'': None, 'Any': None}
        site, fname, lname, d1, d2 = conv.get(site, site), conv.get(fname, fname), conv.get(lname, lname), conv.get(d1, d1), conv.get(d2, d2)

        if sort is None:
            sort = 'Name'
        staff = self.SQL.filter(site, fname, lname, d1, d2, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(staff)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()


class SiteReport(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Site Report')
        self.config(background='#ffffff')
        self.SQL = Queries.SiteReport(db)

    def display(self):
        dailies = self.SQL.load()

        self.startdate, self.enddate, self.e1, self.e2, self.s1, self.s2, self.vis1, self.vis2, self.rev1, self.rev2 = StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()

        self.resultTable = TableCanvas(self, editable=True, data=dailies,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(dailies), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(dailies.values())[0]), height=25*7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=20, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        startLabel = Label(self, text="StartDate", font="Helvetica", foreground='#000000', background='#ffffff')
        startLabel.grid(row=2, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        startBox = Entry(self, textvariable=self.startdate, width=5)
        startBox.grid(row=2, column=0, padx=(4, 4), pady=(4, 4), sticky=E)

        endLabel = Label(self, text="End Date", font="Helvetica", foreground='#000000', background='#ffffff')
        endLabel.grid(row=3, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        endBox = Entry(self, textvariable=self.enddate, width=5)
        endBox.grid(row=3, column=0, padx=(4, 4), pady=(4, 4), sticky=E)

        e1Label = Label(self, text="Event Count", font="Helvetica", foreground='#000000', background='#ffffff')
        e1Label.grid(row=4, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        e1Box = Entry(self, textvariable=self.e1, width=5)
        e1Box.grid(row=4, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        e2Box = Entry(self, textvariable=self.e2, width=5)
        e2Box.grid(row=4, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        s1Label = Label(self, text="Staff Count", font="Helvetica", foreground='#000000', background='#ffffff')
        s1Label.grid(row=5, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        s1Box = Entry(self, textvariable=self.s1, width=5)
        s1Box.grid(row=5, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        s2Box = Entry(self, textvariable=self.s2, width=5)
        s2Box.grid(row=5, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        revLabel = Label(self, text="Revenue Range", font="Helvetica", foreground='#000000', background='#ffffff')
        revLabel.grid(row=6, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        rev1Box = Entry(self, textvariable=self.rev1,  width=5)
        rev1Box.grid(row=6, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        rev2Box = Entry(self, textvariable=self.rev2,  width=5)
        rev2Box.grid(row=6, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        visLabel = Label(self, text="Visit Range", font="Helvetica", foreground='#000000', background='#ffffff')
        visLabel.grid(row=7, column=0, padx=(2, 2), pady=(2, 2), sticky=W)
        vis1Box = Entry(self, textvariable=self.vis1, width=5)
        vis1Box.grid(row=7, column=0, padx=(4, 4), pady=(4, 4), sticky=E)
        vis2Box = Entry(self, textvariable=self.vis2, width=5)
        vis2Box.grid(row=7, column=1, padx=(4, 4), pady=(4, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortDate = partial(self.filter, 'Date')
        sortDateButton = Button(self, command=sortDate, text="Sort by Date", background='#4286f4')
        sortDateButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortEvents = partial(self.filter, 'EventCount')
        sortNameButton = Button(self, command=sortEvents, text="Sort by Event Count", background='#4286f4')
        sortNameButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortStaff = partial(self.filter, 'StaffCount')
        sortManButton = Button(self, command=sortStaff, text="Sort by StaffCount", background='#4286f4')
        sortManButton.grid(row=11, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortVisits = partial(self.filter, 'TotalVisits')
        sortVisitsButton = Button(self, command=sortVisits, text="Sort by Visits", background='#4286f4')
        sortVisitsButton.grid(row=12, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortRev = partial(self.filter, 'TotalRevenue')
        sortRevButton = Button(self, command=sortRev, text="Sort by Revenue", background='#4286f4')
        sortRevButton.grid(row=13, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        detailButton = Button(self, command=self.detail, text="Daily Detail", background='#4286f4')
        detailButton.grid(row=14, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

    def detail(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        date = row['Date']

        if date == '':
            messagebox.showwarning('Error', 'No day selected. Make sure to click on the non-empty '
                                            'row number to select which date you are detailing.')
            return

        dailyDetailWindow = DailyDetail(self)
        dailyDetailWindow.display(date)
        self.withdraw()

    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Date'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        startdate, enddate, e1, e2, s1, s2, rev1, rev2, vis1, vis2 = self.startdate.get(), self.enddate.get(), self.e1.get(), self.e2.get(), self.s1.get(), self.s2.get(), self.rev1.get(), self.rev2.get(), self.vis1.get(), self.vis2.get()

        try:
            datetime.strptime(startdate, '%Y-%m-%d')
            datetime.strptime(enddate, '%Y-%m-%d')
        except Exception as e:
            print(e)
            messagebox.showwarning('Error', 'You must input a start and end date, please enter YYYY-MM-DD')
            return

        converted = []
        conv = {'': None, 'Any': None}
        for i in [e1, e2, s1, s2, rev1, rev2, vis1, vis2]:
            converted.append(conv.get(i, i))

        e1, e2, s1, s2, rev1, rev2, vis1, vis2 = converted

        if e1 and not e1.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if e2 and not e2.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if s1 and not s1.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if s2 and not s2.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if vis1 and not vis1.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if vis2 and not vis2.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if rev1 and not rev1.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return
        if rev2 and not rev2.isdigit():
            messagebox.showwarning('Error', 'All ranges must be numbers')
            return

        if sort is None:
            sort = 'Date'

        dailies = self.SQL.filter(identifier, startdate, enddate, e1, e2, s1, s2, rev1, rev2, vis1, vis2, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(dailies)
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


class DailyDetail(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Daily Detail')
        self.config(background='#ffffff')
        self.SQL = Queries.DailyDetail(db)

    def display(self, date):
        self.date = date
        events = self.SQL.filter(identifier, date)

        self.resultTable = TableCanvas(self, editable=True, data=events,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(events), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150 * len(list(events.values())[0]), height=25 * 7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=25, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortEvent = partial(self.filter, 'EventName')
        sortEventButton = Button(self, command=sortEvent, text="Sort by Event", background='#4286f4')
        sortEventButton.grid(row=13, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortRev = partial(self.filter, 'Revenue')
        sortRevButton = Button(self, command=sortRev, text="Sort by Revenue", background='#4286f4')
        sortRevButton.grid(row=14, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortVisits = partial(self.filter, 'NumVisits')
        sortVisitsButton = Button(self, command=sortVisits, text="Sort by Visits", background='#4286f4')
        sortVisitsButton.grid(row=15, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortStaff = partial(self.filter, 'StaffNames')
        sortVisitsButton = Button(self, command=sortStaff, text="Sort by Staff", background='#4286f4')
        sortVisitsButton.grid(row=16, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def filter(self, sort):

        dailies = self.SQL.filter(identifier, self.date, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(dailies)
        self.resultTable.redraw()


    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()


class StaffViewSchedule(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Staff View Schedule')
        self.config(background='#ffffff')
        self.SQL = Queries.ViewSchedule(db)

    def display(self):
        self.eventname, self.keyword, self.startdate, self.enddate = StringVar(), StringVar(), StringVar(), StringVar()

        self.resultTable = TableCanvas(self, editable=True, data={1: {'EventName': '', 'SiteName': '', 'StartDate': '', 'EndDate': '', 'StaffCount': ''}},
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       thefont=('Helvetica', 10), autoresizecols=1, rows=5,
                                       width=150*5, height=25*7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=25, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        eventNameLabel = Label(self, text="Event Name", foreground='#000000', background='#ffffff')
        eventNameLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        eventNameBox = Entry(self, textvariable=self.eventname, width=20)
        eventNameBox.grid(row=2, column=1, padx=(0, 2), pady=(0, 4), sticky=W)

        keywordLabel = Label(self, text="Description Keyword", foreground='#000000', background='#ffffff')
        keywordLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        keywordBox = Entry(self, textvariable=self.keyword, width=20)
        keywordBox.grid(row=4, column=1, padx=(0, 2), pady=(0, 4), sticky=W)

        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=5, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        startDateBox = Entry(self, textvariable=self.startdate, width=20)
        startDateBox.grid(row=5, column=1, padx=(0, 2), pady=(0, 4), sticky=W)

        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=6, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        endDateBox = Entry(self, textvariable=self.enddate, width=20)
        endDateBox.grid(row=6, column=1, padx=(0, 2), pady=(0, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=7, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        sortEvent = partial(self.filter, 'EventName')
        sortDateButton = Button(self, command=sortEvent, text="Sort Event", background='#4286f4')
        sortDateButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        sortSite = partial(self.filter, 'SiteName')
        sortSiteButton = Button(self, command=sortSite, text="Sort Site", background='#4286f4')
        sortSiteButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        sortStart = partial(self.filter, 'StartDate')
        sortDateButton = Button(self, command=sortStart, text="Sort Start Date", background='#4286f4')
        sortDateButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        sortEnd = partial(self.filter, 'EndDate')
        sortEndButton = Button(self, command=sortEnd, text="Sort End Date", background='#4286f4')
        sortEndButton.grid(row=11, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        sortStaff = partial(self.filter, 'StaffCount')
        sortStaffButton = Button(self, command=sortStaff, text="Sort Staff Count", background='#4286f4')
        sortStaffButton.grid(row=12, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

        viewEventButton = Button(self, command=self.view_event, text="View Event", background='#4286f4')
        viewEventButton.grid(row=13, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W+E)

    def filter(self, sort='EventName'):
        eventname, keyword, startdate, enddate = self.eventname.get(), self.keyword.get(), self.startdate.get(), self.enddate.get()

        converted = []
        conv = {'': None, 'Any': None}
        for i in [eventname, keyword, startdate, enddate]:
            converted.append(conv.get(i, i))
        eventname, keyword, startdate, enddate = converted

        if startdate:
            try:
                datetime.strptime(startdate, '%Y-%m-%d')
            except Exception as e:
                print(e)
                messagebox.showwarning('Error', 'Please enter YYYY-MM-DD')
                return
        if enddate:
            try:
                datetime.strptime(enddate, '%Y-%m-%d')
            except Exception as e:
                print(e)
                messagebox.showwarning('Error', 'YPlease enter YYYY-MM-DD')
                return

        events = self.SQL.filter(identifier, eventname, keyword, startdate, enddate, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(events)
        self.resultTable.redraw()

    def view_event(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        eventname, sitename, startdate = row['EventName'], row['SiteName'], row['StartDate']

        if eventname == '':
            messagebox.showwarning('Error', 'No event selected. Make sure to click on the non-empty '
                                            'row number to select which event you are detailing.')
            return

        staffEventDetailWindow = StaffEventDetail(self)
        staffEventDetailWindow.display(eventname, sitename, startdate)
        self.withdraw()

    def back(self):
        self.master.deiconify()
        self.destroy()


class StaffEventDetail(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Event Detail')
        self.config(background='#ffffff')
        self.SQL = Queries.StaffEventDetail(db)

    def display(self, eventname, sitename, startdate):
        enddate, duration, cap, price, desc, staffnames = self.SQL.load(eventname, sitename, startdate)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=25, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        eventNameLabel = Label(self, text=f"Event: {eventname}", foreground='#000000', background='#ffffff')
        eventNameLabel.grid(row=1, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        siteNameLabel = Label(self, text=f"Site: {sitename}", foreground='#000000', background='#ffffff')
        siteNameLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        startLabel = Label(self, text=f"Startdate: {startdate}", foreground='#000000', background='#ffffff')
        startLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        endLabel = Label(self, text=f"Enddate: {enddate}", foreground='#000000', background='#ffffff')
        endLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        pLabel = Label(self, text=f"Price: {price}", foreground='#000000', background='#ffffff')
        pLabel.grid(row=5, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        durLabel = Label(self, text=f"Duration: {duration}", foreground='#000000', background='#ffffff')
        durLabel.grid(row=6, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        capLabel = Label(self, text=f"Capacity: {cap}", foreground='#000000', background='#ffffff')
        capLabel.grid(row=7, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        staffLabel = Label(self, text=f"Staff: {staffnames}", foreground='#000000', background='#ffffff')
        staffLabel.grid(row=8, column=0, padx=(4, 4), pady=(2, 2), sticky=E)

        descLabel = Label(self, text=f"Description: {desc}", foreground='#000000', background='#ffffff', wraplength=500)
        descLabel.grid(row=9, column=0, columnspan=1, rowspan=5, padx=(4, 4), pady=(2, 2))

    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.display()  # Refreshes
        self.master.deiconify()
        self.destroy()


class visitorExploreEvent(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Explore Event')
        self.config(background='#ffffff')
        self.SQL = Queries.visitorExploreEvent(db)

    def display(self):
        events, eventNames, siteNames, startDates, ticketPrices, ticketRemainings, totalVisits, myVisits = self.SQL.load(identifier)

        self.eventName = StringVar()
        self.descriptionKeyword = StringVar()
        self.siteName = StringVar()
        self.siteName.set("Any")
        self.startDate = StringVar()
        self.endDate = StringVar()
        self.TVR1 = StringVar()
        self.TVR2 = StringVar()
        self.TPR1 = StringVar()
        self.TPR2 = StringVar()
        self.TPR2 = StringVar()
        self.includeVisited = StringVar()
        self.includeVisited.set("0")
        self.includeSoldOut = StringVar()
        self.includeSoldOut.set("0")

        self.resultTable = TableCanvas(self, editable=True, data=events,
                                        read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                        rows=len(events), thefont=('Helvetica', 10), autoresizecols=1,
                                        width=150*len(list(events.values())[0]), height=25*7)
        self.resultTable.grid(row=1, column=1, rowspan=10, sticky=W + E)
        self.resultTable.show()

        sortEventName = partial(self.filter, 'EventName')
        sortEventNameButton = Button(self, command=sortEventName, text="Sort by Event Name", background='#4286f4')
        sortEventNameButton.grid(row=16, column=1, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)
        sortSiteName = partial(self.filter, 'SiteName')
        sortSiteNameButton = Button(self, command=sortSiteName, text="Sort by Site Name", background='#4286f4')
        sortSiteNameButton.grid(row=17, column=1, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)
        sortTicketPrice = partial(self.filter, 'Price')
        sortTicketPriceButton = Button(self, command=sortTicketPrice, text="Sort by Ticket Price", background='#4286f4')
        sortTicketPriceButton.grid(row=18, column=1, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)
        sortTicketRemaining = partial(self.filter, 'TicketsRemaining')
        sortTicketRemainingButton = Button(self, command=sortTicketRemaining, text="Sort by Ticket Remaining", background='#4286f4')
        sortTicketRemainingButton.grid(row=19, column=1, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)
        sortTotalVisits = partial(self.filter, 'TotalNumVisits')
        sortTotalVisitsButton = Button(self, command=sortTotalVisits, text="Sort by Total Visits", background='#4286f4')
        sortTotalVisitsButton.grid(row=20, column=1, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)
        sortMyVisits = partial(self.filter, 'MyVisits')
        sortMyVisitsButton = Button(self, command=sortMyVisits, text="Sort by My Visits", background='#4286f4')
        sortMyVisitsButton.grid(row=21, column=1, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        eventNameLabel = Label(self, text="Event Name", foreground='#000000', background='#ffffff')
        eventNameLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        descriptionKeywordLabel = Label(self, text="Description Keyword", foreground='#000000', background='#ffffff')
        descriptionKeywordLabel.grid(row=6, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        siteNameLabel = Label(self, text="Site Name", foreground='#000000', background='#ffffff')
        siteNameLabel.grid(row=7, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=8, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=9, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        TVRLabel = Label(self, text="Total Visits Range", foreground='#000000', background='#ffffff')
        TVRLabel.grid(row=10, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        TPRLabel = Label(self, text="Ticket Price Range", foreground='#000000', background='#ffffff')
        TPRLabel.grid(row=11, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        includeVisitedCheckbutton = Checkbutton(self, variable=self.includeVisited, text="Include Visited", foreground='#000000', background='#ffffff')
        includeVisitedCheckbutton.grid(row=12, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        includeSoldOutCheckbutton = Checkbutton(self, variable=self.includeSoldOut, text="Include Sold Out", foreground='#000000', background='#ffffff')
        includeSoldOutCheckbutton.grid(row=13, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        filterButton = Button(self,command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=14, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        eventDetailButton = Button(self, command=self.onEventDetailClicked, text="Event Detail", background='#4286f4')
        eventDetailButton.grid(row=15, column=1, padx=(2, 2), pady=(2, 2), sticky=W)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=22, column=1, padx=(2, 2), pady=(2, 2), sticky=W)
        eventNameBox = Entry(self, textvariable=self.eventName, width=20)
        eventNameBox.grid(row=5, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        descriptionKeywordBox = Entry(self, textvariable=self.descriptionKeyword, width=20)
        descriptionKeywordBox.grid(row=6, column=3, padx=(0, 2), pady=(0, 4), sticky=E)

        siteNameDropdown = OptionMenu(self, self.siteName, *siteNames + ['Any'])
        siteNameDropdown.grid(row=7, column=3, padx=(2, 5), pady=(0, 4), sticky=W)
        startDateBox = Entry(self, textvariable=self.startDate, width=20)
        startDateBox.grid(row=8, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        endDateBox = Entry(self, textvariable=self.endDate, width=20)
        endDateBox.grid(row=9, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        TVR1Box = Entry(self, textvariable=self.TVR1, width=20)
        TVR1Box.grid(row=10, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        TVR2Box = Entry(self, textvariable=self.TVR2, width=20)
        TVR2Box.grid(row=10, column=4, padx=(0, 2), pady=(0, 4), sticky=E)
        TPR1Box = Entry(self, textvariable=self.TPR1, width=20)
        TPR1Box.grid(row=11, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        TPR2Box = Entry(self, textvariable=self.TPR2, width=20)
        TPR2Box.grid(row=11, column=4, padx=(0, 2), pady=(0, 4), sticky=E)

    def filter(self, sort=None):
        # if sort and self.resultTable.model.getData()[1]['SiteName'] == '':
        #    messagebox.showwarning('Error', 'You must have data in order to sort')
        #    return

        event, site, keyword, startDate, endDate, TVR1, TVR2, TPR1, TPR2, includeVisited, includeSoldOut = self.eventName.get(), self.siteName.get(), self.descriptionKeyword.get(), self.startDate.get(), self.endDate.get(), self.TVR1.get(), self.TVR2.get(), self.TPR1.get(), self.TPR2.get(), self.includeVisited.get(), self.includeSoldOut.get()

        conv = {'': None, 'Any': None}
        event, site, keyword, startDate, endDate, TVR1, TVR2, TPR1, TPR2, includeVisited, includeSoldOut = conv.get(event, event), conv.get(site, site), conv.get(keyword, keyword), conv.get(startDate, startDate), conv.get(endDate, endDate), conv.get(TVR1, TVR1), conv.get(TVR2, TVR2), conv.get(TPR1, TPR1), conv.get(TPR2, TPR2), conv.get(includeVisited, includeVisited), conv.get(includeSoldOut, includeSoldOut)

        if sort is None:
            sort = 'EventName'
        sites = self.SQL.filter(identifier, event, site, keyword, startDate, endDate, TVR1, TVR2, TPR1, TPR2, includeVisited, includeSoldOut, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(sites)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()

    def onEventDetailClicked(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        eventName = row['EventName']
        siteName = row['SiteName']
        startDate = row['StartDate']

        if eventName == '':
            messagebox.showwarning('Error', 'No site selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        visitorEventDetailWindow = visitorEventDetail(self)
        self.withdraw()
        visitorEventDetailWindow.display(eventName, siteName, startDate)


class visitorEventDetail(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Event Detail')
        self.config(background='#ffffff')
        self.SQL = Queries.visitorEventDetail(db)

    def display(self, eventname, sitename, startdate):
        eventName, siteName, startDate, endDate, ticketPrice, ticketsRemaining, description = self.SQL.load(identifier, eventname, sitename, startdate)

        self.eventName = StringVar()
        self.siteName = StringVar()
        self.startDate = StringVar()
        self.endDate = StringVar()
        self.ticketPrice = StringVar()
        self.ticketsRemaining = StringVar()
        self.description = StringVar()
        self.visitDate = StringVar()

        self.eventName.set(eventName)
        self.siteName.set(siteName)
        self.startDate.set(startDate)
        self.endDate.set(endDate)
        self.ticketPrice.set(ticketPrice)
        self.ticketsRemaining.set(ticketsRemaining)
        self.description.set(description)

        eventNameLabel = Label(self, text='Event Name', foreground='#000000', background='#ffffff')
        eventNameLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky=W)
        eventNameDataLabel = Label(self, text=self.eventName.get(), foreground='#000000', background='#ffffff')
        eventNameDataLabel.grid(row=1, column=2, padx=(4,4), pady=(2,2), sticky=W)

        siteNameLabel = Label(self, text='Site Name', foreground='#000000', background='#ffffff')
        siteNameLabel.grid(row=2, column=1, padx=(4,4), pady=(2,2), sticky=W)
        siteNameDataLabel = Label(self, text=self.siteName.get(), foreground='#000000', background='#ffffff')
        siteNameDataLabel.grid(row=2, column=2, padx=(4,4), pady=(2,2), sticky=W)

        startDateLabel = Label(self, text='Start Date', foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=3, column=1, padx=(4,4), pady=(2,2), sticky=W)
        startDateDataLabel = Label(self, text=self.startDate.get(), foreground='#000000', background='#ffffff')
        startDateDataLabel.grid(row=3, column=2, padx=(4,4), pady=(2,2), sticky=W)

        endDateLabel = Label(self, text='End Date', foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=4, column=1, padx=(4,4), pady=(2,2), sticky=W)
        endDateDataLabel = Label(self, text=self.endDate.get(), foreground='#000000', background='#ffffff')
        endDateDataLabel.grid(row=4, column=2, padx=(4,4), pady=(2,2), sticky=W)

        ticketPriceLabel = Label(self, text='Ticket Price($)', foreground='#000000', background='#ffffff')
        ticketPriceLabel.grid(row=5, column=1, padx=(4,4), pady=(2,2), sticky=W)
        ticketPriceDataLabel = Label(self, text=self.ticketPrice.get(), foreground='#000000', background='#ffffff')
        ticketPriceDataLabel.grid(row=5, column=2, padx=(4,4), pady=(2,2), sticky=W)

        ticketsRemainingLabel = Label(self, text='Tickets Remaining', foreground='#000000', background='#ffffff')
        ticketsRemainingLabel.grid(row=6, column=1, padx=(4,4), pady=(2,2), sticky=W)
        ticketsRemainingDataLabel = Label(self, text=self.ticketsRemaining.get(), foreground='#000000', background='#ffffff')
        ticketsRemainingDataLabel.grid(row=6, column=2, padx=(4,4), pady=(2,2), sticky=W)

        descriptionLabel = Label(self, text='Description', foreground='#000000', background='#ffffff')
        descriptionLabel.grid(row=7, column=1, padx=(4,4), pady=(2,2), sticky=W)
        descriptionLabelData = Text(self, height=4, width=15, wrap=WORD)
        descriptionLabelData.insert("1.0", self.description.get())
        descriptionLabelData.grid(row=7, column=2, padx=(4, 4), pady=(2, 2), sticky=W)

        visitDateLabel = Label(self, text='Visit Date', foreground='#000000', background='#ffffff')
        visitDateLabel.grid(row=11, column=1, padx=(4,4), pady=(2,2), sticky=W)
        visitDateDataBox = Entry(self, textvariable=self.visitDate, width=20)
        visitDateDataBox.grid(row=11, column=2, padx=(0, 2), pady=(0, 4), sticky=W)

        logVisitButton = Button(self, command=self.logVisit, text="Log Visit", background='#4286f4')
        logVisitButton.grid(row=12, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=13, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def logVisit(self):
        if((self.visitDate.get() < self.startDate.get()) or (self.visitDate.get() > self.endDate.get())):
            messagebox.showwarning("Invalid Date",
                               "Date must be within the time of the event.")
        elif(self.ticketsRemaining.get() == "0"):
            messagebox.showwarning("No Tickets Remaining",
                               "There are no tickets remaining for this event.")
        else:
            cursor.execute("SELECT EventName FROM visitevent WHERE EventName = \'" +self.eventName.get()+ "\' AND SiteName = \'" +self.siteName.get()+ "\' AND StartDate = \'" +self.startDate.get()+ "\' AND Date = \'" +self.visitDate.get()+ "\' AND visUsername = \'" +identifier+ "\'")
            event = cursor.fetchone()
            if(event is not None):
                messagebox.showwarning("Already Logged",
                               "There is already a visit logged for this event at this time.")
            else:
                cursor.execute("INSERT into visitevent values (%s, %s, %s, %s, %s)",
                          (identifier, self.siteName.get(), self.eventName.get(), self.startDate.get(), self.visitDate.get()))
                messagebox.showinfo("Success",
                               "Your visit has been logged.")


    def back(self):
        self.master.deiconify()
        self.destroy()

class visitorTransitDetail(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Transit Detail')
        self.config(background='#ffffff')
        self.SQL = Queries.visitorTransitDetail(db)

    def display(self, sitename):
        routes, transportTypes = self.SQL.load(sitename)

        self.siteName = StringVar()
        self.siteName.set(sitename)
        self.transportType = StringVar()
        #self.transportTypes = transportTypes
        self.transitDate = StringVar()
        self.routeName = StringVar()

        self.resultTable = TableCanvas(self, editable=True, data=routes,
                                        read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                        rows=len(routes), thefont=('Helvetica', 10), autoresizecols=1,
                                        width=150*len(list(routes.values())[0]), height=25*7)
        self.resultTable.grid(row=1, column=1, rowspan=10, sticky=W + E)
        self.resultTable.show()

        siteNameLabel = Label(self, text="Site Name", foreground='#000000', background='#ffffff')
        siteNameLabel.grid(row=11, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        siteNameDataLabel = Label(self, text=self.siteName.get(), foreground='#000000', background='#ffffff')
        siteNameDataLabel.grid(row=11, column=3, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        transportTypeLabel = Label(self, text="Transport Type", foreground='#000000', background='#ffffff')
        transportTypeLabel.grid(row=12, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        transportTypeDropdown = OptionMenu(self, self.transportType, *transportTypes + ['Any'])
        transportTypeDropdown.grid(row=12, column=3, padx=(2, 5), pady=(0, 4), sticky=W)

        filterButton = Button(self,command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=12, column=4, padx=(2, 2), pady=(2, 2), sticky=W)

        transitDateLabel = Label(self, text="Transit Date", foreground='#000000', background='#ffffff')
        transitDateLabel.grid(row=13, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)
        transitDateBox = Entry(self, textvariable=self.transitDate, width=20)
        transitDateBox.grid(row=13, column=3, padx=(0, 2), pady=(0, 4), sticky=E)

        logVisitButton = Button(self, command=self.logVisit, text="Log Visit", background='#4286f4')
        logVisitButton.grid(row=13, column=4, padx=(2, 2), pady=(2, 2), sticky=W + E)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=14, column=1, padx=(2, 2), pady=(2, 2), sticky=W)

    def logVisit(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        routeName = row['Route']
        cursor.execute("Select Route From take WHERE Username = \'" +identifier+ "\' AND Date = \'" +self.transitDate.get()+ "\' AND Route = \'" +routeName+ "\' AND TransportType = \'" +self.transportType.get()+ "\'")
        route = cursor.fetchone()
        if(route is not None):
            messagebox.showwarning("Already Logged",
                           "There is already a visit logged for you at this site and date.")
        else:
            cursor.execute("INSERT into take values (%s, %s, %s, %s)",
                      (identifier, self.transportType.get(), routeName, self.transitDate.get()))
            messagebox.showinfo("Success",
                           "Your visit has been logged.")

    def filter(self):
        # event, site, keyword, startDate, endDate, TVR1, TVR2, TPR1, TPR2, includeVisited, includeSoldOut = self.eventName.get(), self.siteName.get(), self.descriptionKeyword.get(), self.startDate.get(), self.endDate.get(), self.TVR1.get(), self.TVR2.get(), self.TPR1.get(), self.TPR2.get(), self.includeVisited.get(), self.includeSoldOut.get()

        # conv = {'': None, 'Any': None}
        # event, site, keyword, startDate, endDate, TVR1, TVR2, TPR1, TPR2, includeVisited, includeSoldOut = conv.get(event, event), conv.get(site, site), conv.get(keyword, keyword), conv.get(startDate, startDate), conv.get(endDate, endDate), conv.get(TVR1, TVR1), conv.get(TVR2, TVR2), conv.get(TPR1, TPR1), conv.get(TPR2, TPR2), conv.get(includeVisited, includeVisited), conv.get(includeSoldOut, includeSoldOut)

        # if sort is None:
        #     sort = 'EventName'
        routes = self.SQL.filter(self.siteName.get(), self.transportType.get())

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(routes)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorExploreSite(Toplevel):
    def __init__(self,master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Explore Site')
        self.config(background='#ffffff')
        self.SQL = Queries.VisitorExploreSite(db)

    def display(self):
        sitedict = {1:{"SiteName":"","EventCount":"","TotalVisits":"","MyVisits":""}}
        sites = self.SQL.load(identifier)


        self.includeVisited = StringVar()
        self.includeVisited.set("0")
        self.siteName = StringVar()
        self.siteName.set("Any")
        self.openEveryday = StringVar()
        self.openEveryday.set("Any")
        self.openEverydayList = ["0", "1"]
        self.startDate = StringVar()
        self.endDate = StringVar()
        self.totalVisitsRange1 = StringVar()
        self.totalVisitsRange2 = StringVar()
        self.eventCountRange1 = StringVar()
        self.eventCountRange2 = StringVar()
        self.resultTable = TableCanvas(self, editable=True, data=sitedict,
                                        read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                        rows=len(sitedict), thefont=('Helvetica', 10), autoresizecols=1,
                                        width=150*len(list(sitedict.values())[0]), height=25*7)

        self.resultTable.show()

        siteLabel = Label(self, text="Site", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=2, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        siteNameDropdown = OptionMenu(self, self.siteName, *sites)
        siteNameDropdown.grid(row=2,column=3,padx=(8,5),pady=(0,4),sticky = W)

        openEverydayLabel = Label(self, text="Open Everyday", foreground='#000000', background='#ffffff')
        openEverydayLabel.grid(row=3, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=4, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=5, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        totalVisitsRangeLabel = Label(self, text="Total Visits Range", foreground='#000000', background='#ffffff')
        totalVisitsRangeLabel.grid(row=6, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        eventCountRangeLabel = Label(self, text="Event Count Range", foreground='#000000', background='#ffffff')
        eventCountRangeLabel.grid(row=7, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan = 2)

        includeVisitedCheckbutton = Checkbutton(self, variable=self.includeVisited, text="Include Visited", foreground='#000000', background='#ffffff')
        includeVisitedCheckbutton.grid(row=8, column=1, padx=(4, 4), pady=(2, 2), sticky=W, columnspan=2)

        filterButton = Button(self, command =self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=9, column=1, padx=(2, 2), pady=(2, 2), sticky=W)

        siteDetailButton = Button(self, command = self.onSiteDetailButtonClicked,text="Site Detail", background='#4286f4')
        siteDetailButton.grid(row=9, column=2, padx=(2, 2), pady=(2, 2), sticky=W)

        transitDetailButton = Button(self, command = self.onTransitDetailButtonClicked,text="Transit Detail", background='#4286f4')
        transitDetailButton.grid(row=9, column=3, padx=(2, 2), pady=(2, 2), sticky=W)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=10, column=1, padx=(2, 2), pady=(2, 2), sticky=W)

        sortSite = partial(self.filter,'SiteName')
        sortSiteButton = Button(self,command=sortSite,text='Sort by Site Name', background= '#4286f4')
        sortSiteButton.grid(row=11, column=1,columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        eventCount = partial(self.filter,'EventCount')
        eventCountButton = Button(self,command=eventCount, text = 'Sort by Event Count', background= '#4286f4')
        eventCountButton.grid(row = 12,column=1,columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        totalVisits = partial(self.filter,'TotalVisits')
        totalVisitsButton = Button(self,command=totalVisits, text='Sort by Total Visits', background= '#4286f4')
        totalVisitsButton.grid(row = 13,column=1,columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        myVisits = partial(self.filter, 'MyVisits')
        myVisitsButton = Button(self,command=myVisits, text = 'Sort by My Visits', background= '#4286f4')
        myVisitsButton.grid(row = 14,column=1,columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        openEverydayDropdown = OptionMenu(self, self.openEveryday, *self.openEverydayList + ['Any'])
        openEverydayDropdown.grid(row=3, column=3, padx=(8, 5), pady=(0, 4), sticky=W)
        startDateBox = Entry(self, textvariable=self.startDate, width=20)
        startDateBox.grid(row=4, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        endDateBox = Entry(self, textvariable=self.endDate, width=20)
        endDateBox.grid(row=5, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        totalVisitsRange1Box = Entry(self, textvariable=self.totalVisitsRange1, width=20)
        totalVisitsRange1Box.grid(row=6, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        totalVisitsRange2Box = Entry(self, textvariable=self.totalVisitsRange2, width=20)
        totalVisitsRange2Box.grid(row=6, column=4, padx=(0, 2), pady=(0, 4), sticky=E)
        eventCountRange1Box = Entry(self, textvariable=self.eventCountRange1, width=20)
        eventCountRange1Box.grid(row=7, column=3, padx=(0, 2), pady=(0, 4), sticky=E)
        eventCountRange2Box = Entry(self, textvariable=self.eventCountRange2, width=20)
        eventCountRange2Box.grid(row=7, column=4, padx=(0, 2), pady=(0, 4), sticky=E)


    def onSiteDetailButtonClicked(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        siteName = row['SiteName']

        if siteName == '':
            messagebox.showwarning('Error', 'No site selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        siteDetailWindow = visitorSiteDetail(self)
        siteDetailWindow.display(siteName)
        self.withdraw()

    def onTransitDetailButtonClicked(self):
        row = self.resultTable.model.getRecordAtRow(self.resultTable.getSelectedRow())
        siteName = row['SiteName']

        if siteName == '':
            messagebox.showwarning('Error', 'No site selected. Make sure to click on the non-empty '
                                            'row number to select which transit you are taking.')
            return

        transitDetailWindow = visitorTransitDetail(self)
        transitDetailWindow.display(siteName)
        self.withdraw()

    def filter(self, sort = None):
        if sort and self.resultTable.model.getData()[1]['SiteName'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        includeVisited, siteName, openEveryday, startDate, endDate, totalVisitsRange1, totalVisitsRange2= self.includeVisited.get(), self.siteName.get(), self.openEveryday.get(), self.startDate.get(), self.endDate.get(), self.totalVisitsRange1.get(), self.totalVisitsRange2.get()
        eventCountRange1, eventCountRange2 = self.eventCountRange1.get(), self.eventCountRange2.get()
        converted = []
        conv = {'': None, 'Any': None}
        for i in [includeVisited, siteName, openEveryday, startDate, endDate, totalVisitsRange1, totalVisitsRange2, eventCountRange1, eventCountRange2]:
            converted.append(conv.get(i,i))
        print(converted)
        includeVisited, siteName, openEveryday, startDate, endDate, totalVisitsRange1, totalVisitsRange2, eventCountRange1, eventCountRange2 = converted

        if sort is None:
            sort = 'SiteName'
        sitedetail = self.SQL.filter(identifier, siteName, openEveryday, startDate, endDate, totalVisitsRange1, totalVisitsRange2, eventCountRange1, eventCountRange2, includeVisited, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(sitedetail)
        self.resultTable.redraw()

    def back(self):
        self.master.deiconify()
        self.destroy()


class visitorSiteDetail(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Site Detail')
        self.config(background='#ffffff')
        self.SQL = Queries.visitorSiteDetail(db)

    def display(self, sitename):
        siteName, openEveryday, address = self.SQL.load(sitename)

        self.siteName = StringVar()
        self.openEveryday = StringVar()
        self.address = StringVar()
        self.visitDate = StringVar()

        self.siteName.set(siteName)
        self.openEveryday.set(openEveryday)
        self.address.set(address)

        siteNameLabel = Label(self, text='Site Name', foreground='#000000', background='#ffffff')
        siteNameLabel.grid(row=1, column=1, padx=(4,4), pady=(2,2), sticky=W)
        siteNameDataLabel = Label(self, text=self.siteName.get(), foreground='#000000', background='#ffffff')
        siteNameDataLabel.grid(row=1, column=2, padx=(4,4), pady=(2,2), sticky=W)

        openEverydayLabel = Label(self, text='Open Everyday', foreground='#000000', background='#ffffff')
        openEverydayLabel.grid(row=2, column=1, padx=(4,4), pady=(2,2), sticky=W)
        openEverydayDataLabel = Label(self, text=self.openEveryday.get(), foreground='#000000', background='#ffffff')
        openEverydayDataLabel.grid(row=2, column=2, padx=(4,4), pady=(2,2), sticky=W)

        addressLabel = Label(self, text='Address', foreground='#000000', background='#ffffff')
        addressLabel.grid(row=3, column=1, padx=(4,4), pady=(2,2), sticky=W)
        addressDataLabel = Label(self, text=self.address.get(), foreground='#000000', background='#ffffff')
        addressDataLabel.grid(row=3, column=2, padx=(4,4), pady=(2,2), sticky=W)

        visitDateLabel = Label(self, text='Visit Date', foreground='#000000', background='#ffffff')
        visitDateLabel.grid(row=4, column=1, padx=(4,4), pady=(2,2), sticky=W)
        visitDateDataBox = Entry(self, textvariable=self.visitDate, width=20)
        visitDateDataBox.grid(row=4, column=2, padx=(0, 2), pady=(0, 4), sticky=W)

        logVisitButton = Button(self, command=self.logVisit, text="Log Visit", background='#4286f4')
        logVisitButton.grid(row=5, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=6, column=1, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def logVisit(self):
        cursor.execute("SELECT SiteName FROM visitsite WHERE SiteName = \'" +self.siteName.get()+ "\'" +" AND VisUsername = \'" +identifier+ "\'"+ " AND Date = \'" +self.visitDate.get()+ "\'")
        site = cursor.fetchone()
        if(site is not None):
            messagebox.showwarning("Already Logged",
                           "There is already a visit logged for you at this site and date.")
        else:
            cursor.execute("INSERT into visitsite values (%s, %s, %s)",
                      (identifier, self.siteName.get(), self.visitDate.get()))
            messagebox.showinfo("Success",
                           "Your visit has been logged.")

    def back(self):
        self.master.deiconify()
        self.destroy()


class VisitHistory(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self)
        self.master = master
        self.title('Visit History')
        self.config(background='#ffffff')
        self.SQL = Queries.VisitHistory(db)

    def display(self):
        sites, history = self.SQL.load(identifier)

        self.event, self.site, self.d1, self.d2, = StringVar(), StringVar(), StringVar(), StringVar()

        self.site.set('Any')

        self.resultTable = TableCanvas(self, editable=True, data=history,
                                       read_only=True, rowheaderwidth=15, maxcellwidth=200, cellwidth=150,
                                       rows=len(history), thefont=('Helvetica', 10), autoresizecols=1,
                                       width=150*len(list(history.values())[0]), height=25*7)
        self.resultTable.show()

        backButton = Button(self, command=self.back, text="Back", background='#4286f4')
        backButton.grid(row=20, column=0, padx=(2, 2), pady=(2, 2), sticky=W + E)

        eventLabel = Label(self, text="Event", font="Helvetica", foreground='#000000', background='#ffffff')
        eventLabel.grid(row=2, column=0, padx=(4, 4), pady=(2, 2), sticky=W)
        eventBox = Entry(self, textvariable=self.event, width=10)
        eventBox.grid(row=2, column=1, padx=(2, 5), pady=(0, 4), sticky=W+E)

        siteLabel = Label(self, text="Site", font="Helvetica", foreground='#000000', background='#ffffff')
        siteLabel.grid(row=3, column=0, padx=(4, 4), pady=(2, 2), sticky=W)
        siteDropdown = OptionMenu(self, self.site, *sites + ['Any'])
        siteDropdown.grid(row=3, column=1, padx=(2, 5), pady=(0, 4), sticky=W)

        startDateLabel = Label(self, text="Start Date", foreground='#000000', background='#ffffff')
        startDateLabel.grid(row=4, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        startDateBox = Entry(self, textvariable=self.d1, width=20)
        startDateBox.grid(row=4, column=1, padx=(0, 2), pady=(0, 4), sticky=W)

        endDateLabel = Label(self, text="End Date", foreground='#000000', background='#ffffff')
        endDateLabel.grid(row=5, column=0, padx=(4, 4), pady=(2, 2), sticky=E)
        endDateBox = Entry(self, textvariable=self.d2, width=20)
        endDateBox.grid(row=5, column=1, padx=(0, 2), pady=(0, 4), sticky=W)

        filterButton = Button(self, command=self.filter, text="Filter", background='#4286f4')
        filterButton.grid(row=6, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortDate = partial(self.filter, 'Date')
        sortTypeButton = Button(self, command=sortDate, text="Sort by Date", background='#4286f4')
        sortTypeButton.grid(row=7, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortEvent = partial(self.filter, 'EventName')
        sortEventButton = Button(self, command=sortEvent, text="Sort by Event", background='#4286f4')
        sortEventButton.grid(row=8, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortSite = partial(self.filter, 'SiteName')
        sortSiteButton = Button(self, command=sortSite, text="Sort by Site", background='#4286f4')
        sortSiteButton.grid(row=9, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

        sortPrice = partial(self.filter, 'Price')
        sortPriceButton = Button(self, command=sortPrice, text="Sort by Price", background='#4286f4')
        sortPriceButton.grid(row=10, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky=W + E)

    def filter(self, sort=None):
        if sort and self.resultTable.model.getData()[1]['Date'] == '':
            messagebox.showwarning('Error', 'You must have data in order to sort')
            return

        d1, d2, site, event = self.d1.get(), self.d2.get(), self.site.get(), self.event.get()

        conv = {'': None, 'Any': None}
        d1, d2, event, site = conv.get(d1, d1), conv.get(d2, d2), conv.get(event, event), conv.get(site, site),

        for d in [d1, d2]:
            if d:
                try:
                    datetime.strptime(d, '%Y-%m-%d')
                except Exception as e:
                    print(e)
                    messagebox.showwarning('Error', 'Incorrect date format. Please enter YYYY-MM-DD')

        if sort is None:
            sort = 'Date'

        history = self.SQL.filter(identifier, d1, d2, event, site, sort)

        self.resultTable.model.deleteRows(range(0, self.resultTable.model.getRowCount()))
        self.resultTable.model.importDict(history)
        self.resultTable.redraw()

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
