import os
import entity

class Model:
    def __init__(self):
        """ This class expects a `ids.csv` file in the data folder which will
        store the participants' data. Each line of this file is expected to
        follow this pattern:

            telegram id; person name; e-mail; origin

        Based off that, we can store the user's data and make sense of it later.
        The data will be stored on a list called `users`, relating this
        data on a map. It also needs some admins, whose ids are expected to
        appear on a `admins.csv` file. The model is also responsible for dealing
        with the attendance list, and will store the ids of those who
        participate on that dojo."""
        # TODO Load data
        self.users = [ ]
        self.loadData()
        self.admins = set()
        self.loadAdmins()
        self.attendance = entity.Attendance()
        # Lock attendance
        self.locked_attendance = True

    def setController(self, c):
        """Sets the controller for this model on a MVC fashion."""
        self.controller = c

    def loadData(self):
        """Loads all registered users."""
        file_name = 'data/ids.csv'
        if os.path.isfile(file_name):
            with open(file_name, 'r') as fp:
                for line in fp:
                    user = { }
                    rows = list(map(lambda s: s.strip(), line.split(';')))
                    user['id'] = int(rows[0])
                    user['name'] = rows[1]
                    user['email'] = rows[2]
                    user['origin'] = rows[3]
                    self.users.append(user)

    def loadAdmins(self):
        """Loads all registered admins."""
        file_name = 'data/admins.csv'
        if os.path.isfile(file_name):
            with open(file_name, 'r') as fp:
                for line in fp:
                    self.admins.add(int(line))

    def isAdmin(self, userId):
        """Checks if a user id is on the VIP list."""
        return userId in self.admins

    def reactToAdmin(self, update):
        """Answer to admin messages."""
        message = update['message']['text']
        reaction = None
        if message == '/unlock':
            self.locked_attendance = False
            reaction = 'Unlocked! :D'
        elif message == '/lock':
            self.locked_attendance = True
            reaction = 'Locked! :x'
        else:
            self.controller.sendHelp()
        return reaction

    def saveData(self):
        """Updates the list with all registered users."""
        with open('data/ids.csv', 'w') as fp:
            for user in self.users:
                if 'origin' in user:
                    fp.write('{0}; {1}; {2}; {3}\n'.format(user['id'], user['name'], user['email'], user['origin']))

    def getIds(self):
        return list(map(lambda u: u['id'], self.users))

    def addUser(self, user):
        if user not in self.users:
            self.users.append(user)
        else:
            for i, u in enumerate(self.users):
                if u['id'] == user['id']:
                    self.users[i] = user
        if 'origin' in user:
            self.saveData()

    def getUser(self, chat_id):
        """Gets the user identified by the given id. If no such user exists,
        this methods returns None. A user is a map relating a Telegram id with
        a name, an e-mail and their origin."""
        outlet = None
        for user in self.users:
            if chat_id == user['id']:
                outlet = user
        return outlet

    def signAttendance(self, userId):
        """Adds an id to the attendance list if it is not so already."""
        self.attendance.sign(userId)
