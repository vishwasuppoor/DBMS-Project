import db
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QHBoxLayout, QMainWindow, QStackedLayout, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QIcon, QFont
from ui import *
import sys
import re

connection = None

email_matcher = re.compile('^[a-zA-Z0-9]+@[a-zA-Z0-9]+[.][a-zA-Z0-9]+$')

def _lstr(generator, seperator = ", "):
    first = True
    s = ""
    for val in generator:

        if not first:
            s += seperator

        first = False

        s += val

    return s

class UserAccess():
    def __init__(self):
        self.__user = None

    def provide(self, user):
        self.__user = user

    def __call__(self):
        return self.__user

class PropertyAccess():
    def __init__(self):
        self.__property = None

    def provide(self, property):
        self.__property = property

    def __call__(self):
        return self.__property

switch = None

switch = None
user = None
property = None

class Login(Dialog):

    def __user(self, email, password):
        users = connection.user(email = email)

        if len(users) == 0:
            self.notify("No user found!")
            return None

        if len(users) != 1:
            raise Exception("Login matched multipler users.")

        if users[0].password != db.hash_pass(password):
            self.notify("Password incorrect!")
            return None

        return users[0]

    def __login(self):
        global user
        login_user = self.__user(self.__email, self.__password)
        if login_user is not None:
            user.provide(login_user)

            switch(user().type + '_main')

    def __email_changed(self, email):
        self.__email = email

    def __password_changed(self, password):
        self.__password = password

    def __init__(self):
        self.__email = ""
        self.__password = ""

        super().__init__(
            'Login',
            {'Login': self.__login,
             'New Visitor': lambda self: switch('visitor_new'),
             'New Owner': lambda self: switch('owner_new')},
            {'Email': self.__email_changed,
             'Password': self.__password_changed}
        )

class AdminMain(Dialog):

    def __init__(self):
        self.__email = ""
        self.__password = ""

        super().__init__(
            'Admin Portal',
            buttons = {'View Visitors': lambda self: switch('admin_visitors'),
                       'View Owners': lambda self: switch('admin_owners'),
                       'View Unconfirmed Properties': lambda self: switch('admin_unconfirmed_properties'),
                       'View Unconfirmed Crops/Animals': lambda self: switch('admin_unconfirmed_items'),
                       'View Confirmed Crops/Animals': lambda self: switch('admin_confirmed_items'),
                       'View Confirmed Properties': lambda self: switch('admin_confirmed_properties'),
                       'Log Out': lambda self: switch.back()}
        )

class AdminConfirmedItems(TableDialog):

    def __generate(self):
        table = ((item.name,
                  item.category)
                 for item
                 in connection.item()
                 if item.approved_by is not None
        )

        return list(table)

    def __unapprove(self):
        global connection
        global property

        if self.row() is None:
            self.notify("No animal/crop selected!")
            return

        name, type = self.row()
        connection.item(name = name, category = type)[0].approved_by = None

        self.update_contents()

    def __delete(self):
        global connection
        global property

        if self.row() is None:
            self.notify("No animal/crop selected!")
            return

        name, type = self.row()
        connection -= connection.item(name = name, category = type)

        self.update_contents()

    def __add_item(self):
        global connection
        connection += connection.item(name = self.__item, category = self.__item_type, approved_by = user().email)
        self.update_contents()

    def __selected_type(self, type):
        self.__item_type = type

    def __animal_updated(self, animal):
        self.__item = animal

    def __init__(self):

        super().__init__(
            title = 'Confirmed Animals/Crops',

            table = [
                ('Name', True),
                ('Type', True)
            ],

            populate = self.__generate,

            combos = {
                'Animal/Crop Type': (lambda:['animal', 'fruit', 'nut', 'flower', 'vegetable'], self.__selected_type),
            },

            fields = {
                'Animal/Crop': self.__animal_updated
            },

            buttons = {
                'Back': lambda self: switch.back(),
                'Unapprove Item': self.__unapprove,
                'Delete Item': self.__delete,
                'Add Crop/Animal': self.__add_item,
            }
        )

class AdminVisitors(TableDialog):

    def __generate(self):
        results = []

        for visitor in connection.user(type = 'visitor'):
            results.append((
                visitor.username,
                visitor.email,
                len(connection.visits(user_email = visitor.email))
            ))

        return results

    def __delete_account(self):
        global connection
        if self.row() is None:
            self.notify("No visitor specified!")
            return

        username, email, visits = self.row()

        connection -= connection.user(username = username, email = email)
        self.update_contents()

    def __delete_logs(self):
        global connection
        if self.row() is None:
            self.notify("No visitor specified!")
            return

        username, email, visits = self.row()

        connection -= connection.visits(user_email = email)
        self.update_contents()

    def __init__(self):

        super().__init__(
            title = 'All Visitors in System',

            table = [
                ('Username', True),
                ('Email', True),
                ('Logged Visits', True)
            ],

            populate = self.__generate,

            buttons = {
                'Back': lambda self: switch.back(),
                'Delete Log History': self.__delete_logs,
                'Delete Visitor Account': self.__delete_account,
            }
        )

class AdminOwners(TableDialog):

    def __generate(self):
        results = []

        for owner in connection.user(type = 'owner'):
            print(owner.username, owner.email)
            results.append((
                owner.username,
                owner.email,
                len(connection.property(owned_by = owner.email))
            ))

        return results

    def __delete_account(self):

        global connection

        if self.row() is None:
            self.notify("No owner specified!")
            return

        username, email, visits = self.row()

        connection -= connection.user(username = username, email = email)
        self.update_contents()

    def __init__(self):

        super().__init__(
            title = 'All Owners in System',

            table = [
                ('Username', True),
                ('Email', True),
                ('Number of Properties', True)
            ],

            populate = self.__generate,

            buttons = {
                'Back': lambda self: switch.back(),
                'Delete Owner Account': self.__delete_account,
            }
        )

class AdminUnconfirmedItems(TableDialog):

    def __generate(self):
        table = ((item.name,
                  item.category)
                 for item
                 in connection.item(approved_by = None)
        )

        return list(table)

    def __approve(self):
        global connection
        global property

        if self.row() is None:
            self.notify("No animal/crop specified!")
            return

        name, type = self.row()
        connection.item(name = name, category = type)[0].approved_by = user().email

        self.update_contents()

    def __delete(self):
        global connection
        global property

        if self.row() is None:
            self.notify("No animal/crop specified!")
            return

        name, type = self.row()
        connection -= connection.item(name = name, category = type)

        self.update_contents()

    def __init__(self):

        super().__init__(
            title = 'Unconfirmed Animals/Crops',

            table = [
                ('Name', True),
                ('Type', True)
            ],

            populate = self.__generate,

            buttons = {
                'Back': lambda self: switch.back(),
                'Approve Item': self.__approve,
                'Delete Item': self.__delete
            }
        )

class AdminConfirmedProperties(TableDialog):

    def __generate(self):

        table = []
        
        for property in connection.property():
            if property.approved_by is not None:
                avg = 0.0
                avg_am = 0.0
                for visit in connection.visits(property_id = property.id):
                    avg += visit.rating
                    avg_am += 1.0

                if avg_am != 0:
                    avg = round(avg / avg_am, 2)

                table.append(
                    (property.name,
                    property.address,
                    property.city,
                    property.zip,
                    property.size,
                    property.type,
                    property.is_public,
                    property.is_commercial,
                    property.id,
                    property.owned_by,
                    property.approved_by,
                    avg)
        )

        return table

    def __manage(self):
        global property

        if self.row() is None:
            self.notify("No property specified!")
            return

        property.provide(
            {self.headers()[i]:
             self.row()[i]
             for i in range(0, 10)}
        )

        switch('admin_manage_property')


    def __init__(self):

        super().__init__(
            title = 'Confirmed Properties',

            table = [
                ('Name', True),
                ('Address', False),
                ('City', False),
                ('Zip', False),
                ('Size', True),
                ('Type', False),
                ('Public', False),
                ('Commercial', True),
                ('ID', False),
                ('Owner Email', True),
                ('Confirmed By', False),
                ('Avg. Rating', True)
            ],

            populate = self.__generate,

            buttons = {
                'Back': lambda self: switch.back(),
                'Manage Property': self.__manage
            }
        )

class AdminManageProperty(Dialog):

    def __submit_crop_request(self):
        global connection

        if len(connection.item(name = self._crop_animal_request)) != 0:
            self.notify('Crop/Animal already exists with that name!')
            return

        connection += connection.item(name = self._crop_animal_request, category = self._crop_animal_request_type)
        self.notify("Request has been made!")

    def __add_crop(self):
        global connection

        if len(connection.has(item_name = self._item, property_id = property()['ID'])) != 0:
            self.notify('Crop already exists on property!')
            return

        self.__add_crops.add(self._item)
        if self._item in self.__delete_crops:
            self.__delete_crops.remove(self._item)

        self.update_contents()

    def __delete_crop(self):
        global connection

        self.__delete_crops.add(self._ditem)
        if self._ditem in self.__add_crops:
            self.__add_crops.remove(self._ditem)

    def __save(self):
        global connection
        try:
            float(self._size)
        except:
            self.notify("Size must be a number.")
            return

        try:
            float(self._zip)
            if len(self._zip) != 5:
                raise Exception("Wrong length!")
        except:
            self.notify("Zip code must be a five digit number.")
            return

        prop = connection.property(id = int(property()['ID']))[0]
        prop.name = self._name
        prop.address = self._address
        prop.city = self._city
        prop.zip = self._zip
        prop.size = self._size
        prop.is_public = self._public
        prop.is_commercial = self._commercial
        self.update_contents()

        for crop in self.__delete_crops:
            connection -= connection.has(item_name = crop, property_id = prop.id)

        for crop in self.__add_crops:
            connection += connection.has(item_name = crop, property_id = prop.id)
        self.__add_crops = set()
        self.__delete_crops = set()

        prop = connection.property(id = property()['ID'])[0]
        prop.approved_by = user().email
        self.update_contents()

    def __delete_property(self):
        global connection

        connection -= connection.property(id = int(property()['ID']))
        switch.last()

    def __init__(self):

        self.__delete_crops = set()
        self.__add_crops = set()

        def populate_field(field): 
            def s(self):
                try:
                    return property()[field]
                except:
                    return ""

            return s

        def set_attrib(attrib):
            def s(value):
                setattr(self, attrib, value)

            return s

        def set_battrib(attrib):
            def s(value):
                setattr(self, attrib, value == 'Yes')

            return s

        def is_approved():
            if connection.property(id = property()['ID'])[0].approved_by is not None:
                return 'Yes'
            return 'No'

        def types_for(type):
            if type == 'farm':
                return ['animal', 'fruit', 'nut', 'flower', 'vegetable']
            if type == 'garden':
                return ['flower', 'vegetable']
            if type == 'orchard':
                return ['fruit', 'nut']

        super().__init__(
            title = 'Unconfirmed Property',

            fields = {
                'Name': set_attrib('_name'),
                'Address': set_attrib('_address'),
                'City': set_attrib('_city'),
                'Zip': set_attrib('_zip'),
                'Size': set_attrib('_size'),
                'Crop/Animal Request': set_attrib('_crop_animal_request')
            },

            field_providers = {
                'Name': populate_field('Name'),
                'Address': populate_field('Address'),
                'City': populate_field('City'),
                'Zip': populate_field('Zip'),
                'Size': populate_field('Size'),
            },

            labels = {
                "Type": lambda: property()['Type'],
                "ID": lambda: property()['ID'],
                'Property Crops/Animals': lambda: _lstr(i.item_name for i in connection.has(property_id = property()['ID'])),
                'Approved?': is_approved
            },

            combos = {
                "Crop/Animal Request Type": (lambda: types_for(property()['Type']), set_attrib("_crop_animal_request_type")),
                "Add Crop/Animal": (lambda: [
                    i.name
                    for i
                    in connection.item()
                    if i.approved_by is not None and (property()['Type'] in types_for(property()['Type']))
                ],
                         set_attrib('_item')),
                "Delete Crop/Animal": (lambda: [
                    i.item_name
                    for i
                    in connection.has(property_id = property()['ID'])
                ],
                         set_attrib('_ditem')),
                'Public?': (lambda: ['Yes', 'No'], set_battrib('_public')),
                'Commercial?': (lambda: ['Yes', 'No'], set_battrib('_commercial'))
            },

            buttons = {
                'Back': lambda self: switch.back(),
                'Submit Crop Request': self.__submit_crop_request,
                'Add Crop/Animal': self.__add_crop,
                'Delete Crop/Animal': self.__delete_crop,
                'Save Changes': self.__save,
                'Delete Property': self.__delete_property
            }
        )

class OwnerManageProperty(Dialog):

    def __submit_crop_request(self):
        global connection

        if len(connection.item(name = self._crop_animal_request)) != 0:
            self.notify('Crop/Animal already exists with that name!')
            return

        connection += connection.item(name = self._crop_animal_request, category = self._crop_animal_request_type)
        self.notify("Request has been made!")

    def __add_crop(self):
        global connection

        if len(connection.has(item_name = self._item, property_id = property()['ID'])) != 0:
            self.notify('Crop already exists on property!')
            return

        self.__add_crops.add(self._item)
        if self._item in self.__delete_crops:
            self.__delete_crops.remove(self._item)

        self.update_contents()

    def __delete_crop(self):
        global connection

        self.__delete_crops.add(self._ditem)
        if self._ditem in self.__add_crops:
            self.__add_crops.remove(self._ditem)

    def __save(self):
        global connection
        try:
            float(self._size)
        except:
            self.notify("Size must be a number.")
            return

        try:
            float(self._zip)
            if len(self._zip) != 5:
                raise Exception("Wrong length!")
        except:
            self.notify("Zip code must be a five digit number.")
            return

        prop = connection.property(id = int(property()['ID']))[0]
        prop.name = self._name
        prop.address = self._address
        prop.city = self._city
        prop.zip = self._zip
        prop.size = self._size
        prop.is_public = self._public
        prop.is_commercial = self._commercial
        self.update_contents()

        for crop in self.__delete_crops:
            connection -= connection.has(item_name = crop, property_id = prop.id)

        for crop in self.__add_crops:
            connection += connection.has(item_name = crop, property_id = prop.id)
        self.__add_crops = set()
        self.__delete_crops = set()

        prop = connection.property(id = property()['ID'])[0]
        prop.approved_by = user().email
        self.update_contents()

    def __delete_property(self):
        global connection

        connection -= connection.property(id = int(property()['ID']))
        switch('owner_main')

    def __init__(self):

        self.__add_crops = set()
        self.__delete_crops = set()

        def populate_field(field):

            def s(self):
                try:
                    return property()[field]
                except:
                    return ""

            return s

        def set_attrib(attrib):
            def s(value):
                setattr(self, attrib, value)

            return s

        def set_battrib(attrib):
            def s(value):
                setattr(self, attrib, value == 'Yes')

            return s

        def types_for(type):
            if type == 'farm':
                return ['animal', 'fruit', 'nut', 'flower', 'vegetable']
            if type == 'garden':
                return ['flower', 'vegetable']
            if type == 'orchard':
                return ['fruit', 'nut']

        super().__init__(
            title = 'Unconfirmed Property',

            fields = {
                'Name': set_attrib('_name'),
                'Address': set_attrib('_address'),
                'City': set_attrib('_city'),
                'Zip': set_attrib('_zip'),
                'Size': set_attrib('_size'),
                'Crop/Animal Request': set_attrib('_crop_animal_request')
            },

            field_providers = {
                'Name': populate_field('Name'),
                'Address': populate_field('Address'),
                'City': populate_field('City'),
                'Zip': populate_field('Zip'),
                'Size': populate_field('Size'),
            },

            labels = {
                "Type": lambda: property()['Type'],
                "ID": lambda: property()['ID'],
                'Property Crops/Animals': lambda: _lstr(i.item_name for i in connection.has(property_id = property()['ID']))
            },

            combos = {
                "Crop/Animal Request Type": (lambda: types_for(property()['Type']), set_attrib("_crop_animal_request_type")),
                "Add Crop/Animal": (lambda: [
                    i.name
                    for i
                    in connection.item()
                    if i.approved_by is not None and (property()['Type'] in types_for(property()['Type']))
                ],
                         set_attrib('_item')),
                "Delete Crop/Animal": (lambda: [
                    i.item_name
                    for i
                    in connection.has(property_id = property()['ID'])
                ],
                         set_attrib('_ditem')),
                'Public?': (lambda: ['Yes', 'No'], set_battrib('_public')),
                'Commercial?': (lambda: ['Yes', 'No'], set_battrib('_commercial'))
            },

            buttons = {
                'Back': lambda self: switch.back(),
                'Submit Crop Request': self.__submit_crop_request,
                'Add Crop/Animal': self.__add_crop,
                'Delete Crop/Animal': self.__delete_crop,
                'Save Changes': self.__save,
                'Delete Property': self.__delete_property
            }
        )

class AdminUnconfirmedProperties(TableDialog):

    def __generate(self):
        table = ((property.name,
                  property.address,
                  property.city,
                  property.zip,
                  property.size,
                  property.type,
                  property.is_public,
                  property.is_commercial,
                  property.id,
                  property.owned_by)
                 for property in connection.property(approved_by = None))

        return list(table)

    def __manage(self):
        global property

        if self.row() is None:
            self.notify("No property specified!")
            return

        property.provide(
            {self.headers()[i]:
             self.row()[i]
             for i in range(0, 10)}
        )

        switch('admin_manage_property')


    def __init__(self):

        super().__init__(
            title = 'Unconfirmed Property',

            table = [
                ('Name', True),
                ('Address', False),
                ('City', False),
                ('Zip', False),
                ('Size', True),
                ('Type', False),
                ('Public', False),
                ('Commercial', True),
                ('ID', False),
                ('Owner Email', True)
            ],

            populate = self.__generate,

            buttons = {
                'Back': lambda self: switch.back(),
                'Manage Property': self.__manage
            }
        )

class OwnerViewProperty(Dialog):

    def __init__(self):

        def prop(name):
            if name == "Avg. Rating":
                props = connection.visits(property_id = property()["ID"], user_email = user().email)
                val = 0.0
                for prop in props:
                    val += prop.rating

                if len(props) != 0:
                    val /= len(props)

                return str(val)

            if name == 'Crops':

                crops = set()
                for has in connection.has(property_id = property()["ID"]):
                    for item in connection.item(name = has.item_name):
                        crops.add(item.name)

                return _lstr(crops)

            return property()[name]

        def prop_func(n):
            return lambda: prop(n)

        super().__init__(
            'Property',
            buttons = {"Back": lambda self: switch.back()},

            labels = {n: prop_func(n)
                      for n in ["Name",
                                "Address",
                                "City",
                                "Zip",
                                "Size",
                                "Type",
                                "Public",
                                "Commercial",
                                "ID",
                                "Visits",
                                "Avg. Rating",
                                "Crops"]
                      }
        )

class VisitorProperty(Dialog):

    def __log_visit(self):
        global connection
        props = connection.visits(property_id = property()["ID"], user_email = user().email)

        if len(props) > 1:
            raise Exception("Too many properties for visit")

        if len(props) == 0:
            connection += connection.visits(
                rating = self.__rating,
                user_email = user().email,
                property_id = property()["ID"]
            )

            self.update_contents()
            return

        connection -= connection.visits(user_email = user().email, property_id = property()["ID"])
        self.update_contents()

    def __select_rating(self, text):
        if text == '':
            return
        self.__rating = float(int(text))

    def __init__(self):
        self.__email = ""
        self.__password = ""

        def prop(name):
            if name == "Avg. Rating":
                props = connection.visits(property_id = property()["ID"], user_email = user().email)
                val = 0.0
                for prop in props:
                    val += prop.rating

                if len(props) != 0:
                    val /= len(props)

                return str(val)

            if name == "Visited":
                if len(connection.visits(property_id = property()["ID"], user_email = user().email)) == 0:
                    return "False"

                return "True"

            if name == 'Crops':

                crops = set()
                for has in connection.has(property_id = property()["ID"]):
                    for item in connection.item(name = has.item_name):
                        crops.add(item.name)

                return _lstr(crops)

            return property()[name]

        def prop_func(n):
            return lambda: prop(n)

        super().__init__(
            'Property',
            buttons = {"Toggle Visit": self.__log_visit,
                       "Back": lambda self: switch.back()},

            labels = {n: prop_func(n)
                      for n in ["Name",
                                "Address",
                                "City",
                                "Zip",
                                "Size",
                                "Type",
                                "Public",
                                "Commercial",
                                "ID",
                                "Visits",
                                "Visited",
                                "Avg. Rating",
                                "Crops"]
                      },

            combos = {'Rating': (lambda: [str(n) for n in range(1,6)],
                                 self.__select_rating)}
        )

class VisitorHistory(TableDialog):

    def __generate(self):
        if user() is None:
            return []

        table = []
        for visit in connection.visits(user_email = user().email):
            print(len(connection.property(id = visit.property_id)))
            table.append(
                (connection.property(id = visit.property_id)[0].name,
                 str(visit.rating),
                 visit.date)
            )

        print("Table", table)

        return table

    def __view_property(self):
        global property

        if self.row() is None:
            self.notify("No property specified!")
            return

        property_name = self.row()[0]

        avg = 0.0
        avg_am = 0.0
        for visit in connection.visits(property_id = connection.property(name = property_name)[0].id, user_email = user().email):
            avg += visit.rating
            avg_am += 1.0

        if avg_am != 0:
            avg = round(avg / avg_am, 2)

        prop = connection.property(name = property_name)[0]

        property.provide({
            "Name": prop.name,
            "Address": prop.address,
            "City": prop.city,
            "Zip": prop.zip,
            "Size": prop.size,
            "Type": prop.type,
            "Public": prop.is_public,
            "Commercial": prop.is_commercial,
            "ID": prop.id,
            "Visits": len(connection.visits(property_id = prop.id)),
            "Avg. Rating": avg
        })

        switch('visitor_property')

    def __init__(self):
        super().__init__(
            title = "Property List",

            table = [
                ("Name", True),
                ("Rating", False),
                ("Date", True)
            ],

            populate = self.__generate,

            buttons = {
                "View Property": self.__view_property,
                "Back": lambda self: switch.back()
            }
        )

class OwnerOtherProperties(TableDialog):

    def __generate(self):

        table = []
        
        for property in connection.property():
            if property.owned_by != user().email and property.approved_by is not None and property.is_public:
                avg = 0.0
                avg_am = 0.0
                for visit in connection.visits(property_id = property.id):
                    avg += visit.rating
                    avg_am += 1.0

                if avg_am != 0:
                    avg = round(avg / avg_am, 2)

                table.append(
                    (property.name,
                    property.address,
                    property.city,
                    property.zip,
                    property.size,
                    property.type,
                    property.is_public,
                    property.is_commercial,
                    property.id,
                    avg_am,
                    avg)
            )

        return table

    def __manage_property(self):
        global property

        if self.row() is None:
            self.notify("No property specified!")
            return

        property.provide(
            {self.headers()[i]:
             self.row()[i]
             for i in range(0, 11)}
        )
        switch('owner_view_property')

    def __init__(self):
        super().__init__(
            title = "Other Properties",

            table = [
                ("Name", True),
                ("Address", False),
                ("City", True),
                ("Zip", False),
                ("Size", True),
                ("Type", True),
                ("Public", True),
                ("Commercial", False),
                ("ID", False),
                ("Visits", True),
                ("Avg. Rating", True)
            ],

            populate = self.__generate,

            buttons = {
                "View Property": self.__manage_property,
                "Back": lambda self: switch.back()
            }
        )

class OwnerMain(TableDialog):

    def __generate(self):

        table = []
        
        for property in connection.property():
            if property.owned_by == user().email and property.approved_by is not None and property.is_public:
                avg = 0.0
                avg_am = 0.0
                for visit in connection.visits(property_id = property.id):
                    avg += visit.rating
                    avg_am += 1.0

                if avg_am != 0:
                    avg = round(avg / avg_am, 2)

                table.append(
                    (property.name,
                    property.address,
                    property.city,
                    property.zip,
                    property.size,
                    property.type,
                    property.is_public,
                    property.is_commercial,
                    property.id,
                    property.approved_by,
                    avg_am,
                    avg)
            )

        return table

    def __manage_property(self):
        global property

        if self.row() is None:
            self.notify("No property specified!")
            return

        property.provide(
            {self.headers()[i]:
             self.row()[i]
             for i in range(0, 11)}
        )
        switch('owner_manage_property')

    def __init__(self):
        super().__init__(
            title = "Property List",

            table = [
                ('Name', True),
                ('Address', False),
                ('City', True),
                ('Zip', False),
                ('Size', True),
                ('Type', True),
                ('Public', True),
                ('Commercial', False),
                ('ID', False),
                ('Approved By', False),
                ('Visits', True),
                ('Avg. Rating', True)
            ],

            populate = self.__generate,

            buttons = {
                'Manage Property': self.__manage_property,
                'Add Property': lambda self: switch('owner_add_property'),
                'View Other Properties': lambda self: switch('owner_other_properties'),
                'Log Out': lambda self: switch.back()
            }
        )

class VisitorMain(TableDialog):

    def __generate(self):
        table = []
        
        for property in connection.property():
            if property.approved_by is not None and property.is_public:
                avg = 0.0
                avg_am = 0.0
                for visit in connection.visits(property_id = property.id):
                    avg += visit.rating
                    avg_am += 1.0

                if avg_am != 0:
                    avg = round(avg / avg_am, 2)

                table.append(
                    (property.name,
                    property.address,
                    property.city,
                    property.zip,
                    property.size,
                    property.type,
                    property.is_public,
                    property.is_commercial,
                    property.id,
                    avg_am,
                    avg)
                )

        return table

    def __view_property(self):
        if self.row() is None:
            self.notify("No property specified!")
            return

        property.provide(
            {self.headers()[i]:
             self.row()[i]
             for i in range(0, 11)}
        )
        switch('visitor_property')

    def __init__(self):
        super().__init__(
            title = "Properties",

            table = [
                ("Name", True),
                ("Address", False),
                ("City", True),
                ("Zip", False),
                ("Size", True),
                ("Type", True),
                ("Public", True),
                ("Commercial", False),
                ("ID", False),
                ("Visits", True),
                ("Avg. Rating", True)
            ],

            populate = self.__generate,

            buttons = {
                "View Property": self.__view_property,
                "View Visit History": lambda self: switch('visitor_history'),
                "Log Out": lambda self: switch.back()
            }
        )

class OwnerAddProperty(Dialog):

    def __register(self):
        global connection

        connection += connection.property(
            address = self._address,
            name = self._name,
            city = self._city,
            zip = self._zip,
            size = self._acres,
            is_commercial = self._commercial,
            is_public = self._public,
            type = self._property_type.lower(),
            owned_by = user().email
        )

        if self._property_type.lower() != 'farm':
            connection += connection.has(property_id = connection.property(name = self._name)[0].id, item_name = self._crop)
        else:
            connection += connection.has(property_id = connection.property(name = self._name)[0].id, item_name = self._animal)

        switch('owner_main')

    def __populate_animals(self):
        results = []
        for animal in connection.item(category = 'animal'):
            if animal.approved_by is not None:
                results.append(animal.name)

        return results

    def __populate_crops(self):
        results = []
        for item in connection.item():
            if item.approved_by is not None and item.category != 'animal':
                results.append(item.name)

        return results

    def __init__(self):

        def set_attrib(attrib):
            def s(value):
                setattr(self, attrib, value)

            return s

        def set_battrib(attrib):
            def s(value):
                setattr(self, attrib, value == 'Yes')

            return s

        super().__init__(
            'Add Property',
            buttons = {'Cancel': lambda self: switch('owner_main'),
                       'Add': self.__register},
            fields = {'Property Name': set_attrib('_name'),
                      'Street Address': set_attrib('_address'),
                      'City': set_attrib('_city'),
                      'Zip': set_attrib('_zip'),
                      'Acres': set_attrib('_acres')},

            combos = {'Property Type': (lambda: ['Farm', 'Orchard', 'Garden'], set_attrib('_property_type')),
                      'Animal': (self.__populate_animals, set_attrib('_animal')),
                      'Crop': (self.__populate_crops, set_attrib('_crop')),
                      'Public?': (lambda: ['Yes', 'No'], set_battrib('_public')),
                      'Commercial?': (lambda: ['Yes', 'No'], set_battrib('_commercial'))}
        )

class OwnerNew(Dialog):

    def __user(self, email, password):
        users = connection.user(email = email, password = password)
        if len(users) == 0:
            return None
        elif len(users) != 1:
            raise Exception("Retrieving user returned multiple")

        return user[0]

    def __register(self):
        global connection

        if not email_matcher.match(self._email):
            self.notify("Invalid email specified.")
            return

        if len(self._password) < 8:
            self.notify("Password must have at least 8 characters!")
            return

        if self._password != self._confirm:
            self.notify("Passwords do not match!")
            return

        existing = connection.user(
            username = self._username,
        )

        if len(existing) != 0:
            self.notify("Username already taken!")
            return

        existing = connection.user(
            email = self._email
        )

        if len(existing) != 0:
            self.notify("Email already registered!")
            return

        try:
            float(self._acres)
        except:
            self.notify("Size must be a number.")
            return

        try:
            float(self._zip)
            if len(self._zip) != 5:
                raise Exception("Wrong length!")
        except:
            self.notify("Zip code must be a five digit number.")
            return

        connection += connection.user(
            username = self._username,
            password = self._password,
            email = self._email,
            type = 'owner'
        )

        connection += connection.property(
            address = self._address,
            name = self._property_name,
            city = self._city,
            zip = self._zip,
            size = self._acres,
            is_commercial = self._commercial,
            is_public = self._public,
            type = self._property_type.lower(),
            owned_by = self._email
        )

        switch('login')

    def __populate_animals(self):
        print("Populating animals...")
        results = []
        for animal in connection.item(category = 'animal'):
            if animal.approved_by is not None:
                results.append(animal,name)

        return results

    def __populate_crops(self):
        results = []
        for item in connection.item():
            if item.approved_by is not None and item.category != 'animal':
                results.append(item.name)

        return results

    def __init__(self):

        def set_attrib(attrib):
            def s(value):
                setattr(self, attrib, value)

            return s

        def set_battrib(attrib):
            def s(value):
                setattr(self, attrib, value == 'Yes')

            return s

        super().__init__(
            'New Owner Registration',
            buttons = {'Cancel': lambda self: switch('login'),
                       'Register': self.__register},
            fields = {'Email': set_attrib('_email'),
                      'Username': set_attrib('_username'),
                      'Password': set_attrib('_password'),
                      'Confirm Password': set_attrib('_confirm'),
                      'Property Name': set_attrib('_property_name'),
                      'Street Address': set_attrib('_address'),
                      'City': set_attrib('_city'),
                      'Zip': set_attrib('_zip'),
                      'Acres': set_attrib('_acres')},
            combos = {'Property Type': (lambda: ['Farm', 'Orchard', 'Garden'], set_attrib('_property_type')),
                      'Animal': (self.__populate_animals, set_attrib('_animal')),
                      'Crop': (self.__populate_crops, set_attrib('_crop')),
                      'Public?': (lambda: ['Yes', 'No'], set_battrib('_public')),
                      'Commercial?': (lambda: ['Yes', 'No'], set_battrib('_commercial'))}
        )

class VisitorNew(Dialog):

    def __user(self, email, password):
        users = connection.user(email = email, password = password)
        if len(users) == 0:
            return None
        elif len(users) != 1:
            raise Exception("Retrieving user returned multiple")

        return user[0]

    def __register(self):
        global connection

        if not email_matcher.match(self.__email):
            self.notify("Invalid email specified.")
            return

        if len(self.__password) < 8:
            self.notify("Password must have at least 8 characters!")
            return

        if self.__password != self.__confirm:
            self.notify("Passwords do not match!")
            return

        existing = connection.user(
            username = self.__username,
        )

        if len(existing) != 0:
            self.notify("Username already taken!")
            return

        existing = connection.user(
            email = self.__email
        )

        if len(existing) != 0:
            self.notify("Email already registered!")
            return

        connection += connection.user(
            username = self.__username,
            password = self.__password,
            email = self.__email,
            type = 'visitor'
        )

        switch('login')

    def __email_changed(self, email):
        self.__email = email

    def __password_changed(self, password):
        self.__password = password

    def __username_changed(self, username):
        self.__username = username

    def __confirm_changed(self, confirm):
        self.__confirm = confirm

    def __init__(self):
        super().__init__(
            'New Visitor Registration',
            {'Cancel': lambda self: switch('login'),
             'Register': self.__register},
            {'Email': self.__email_changed,
             'Username': self.__username_changed,
             'Password': self.__password_changed,
             'Confirm Password': self.__confirm_changed}
        )

if __name__ == '__main__':

    # Setup the QT application.
    app = QApplication(sys.argv)

    if len(sys.argv) < 5:
        print("Usage: <host> <user> <password> <database>")
    else:

        connection = db.DB(
            host = sys.argv[1],
            user = sys.argv[2],
            password = sys.argv[3],
            database = sys.argv[4],
            debug = {'all'}
        )

        # Setup the user provider.
        user = UserAccess()

        # Setup property provider.
        property = PropertyAccess()

        # Setup window switcher.
        switch = WindowSwitcher({
            "login":       Login(),
            "owner_new": OwnerNew(),
            "owner_main": OwnerMain(),
            "owner_add_property": OwnerAddProperty(),
            "owner_other_properties": OwnerOtherProperties(),
            "owner_view_property": OwnerViewProperty(),
            "visitor_new": VisitorNew(),
            "visitor_main": VisitorMain(),
            'visitor_property': VisitorProperty(),
            'visitor_history': VisitorHistory(),
            'admin_main': AdminMain(),
            'admin_unconfirmed_properties': AdminUnconfirmedProperties(),
            'admin_confirmed_properties': AdminConfirmedProperties(),
            'admin_confirmed_items': AdminConfirmedItems(),
            'admin_unconfirmed_items': AdminUnconfirmedItems(),
            'admin_owners': AdminOwners(),
            'admin_visitors': AdminVisitors(),
            'admin_manage_property': AdminManageProperty(),
            'owner_manage_property': OwnerManageProperty()
        })

        # Switch to login window.
        switch('login')

        # run application.
        sys.exit(app.exec_())
