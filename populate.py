import sys
import db

connection = db.DB(
    host = sys.argv[1],
    user = sys.argv[2],
    password = sys.argv[3],
    database = sys.argv[4],
    debug = {'all'}
)

# Populating table user.

connection += connection.user(username = "admin1",email = "zuckerburg@fb.com", password = "privacyLOL", type="ADMIN")
connection += connection.user(username = "admin2",email = "michael@gmail.com", password = "1234567!", type="ADMIN")
connection += connection.user(username = "ceo",email = "ceo@gatech.edu", password = "choochoo", type="ADMIN")
connection += connection.user(username = "farmowner",email = "farmerJoe@gmail.com", password = "farming123", type="OWNER")
connection += connection.user(username = "gardenowner",email = "gardenerSteve@hotmail.com", password = "ilovegardening", type="OWNER")
connection += connection.user(username = "orchardowner",email = "orchardOwen@myspace.com", password = "wowwowwow", type="OWNER")
connection += connection.user(username = "billybob",email = "bobbilly@harvard.edu", password = "S3cur3P455w0rd!!%$#@", type="VISITOR")
connection += connection.user(username = "iloveflowers",email = "flowerpower@gmail.com", password = "rosesarered", type="VISITOR")
connection += connection.user(username = "greenguy",email = "bill@yahoo.com", password = "broccoli", type="VISITOR")
connection += connection.user(username = "lonelyowner",email = "fake@gmail.com", password = "idontownanything", type="OWNER")
connection += connection.user(username = "riyoy1996",email = "yamada.riyo@navy.mil.gov", password = "Riyo4LIFE", type="VISITOR")
connection += connection.user(username = "kellis",email = "kateellis@gatech.edu", password = "martapassword", type="VISITOR")
connection += connection.user(username = "ashton.woods",email = "awoods30@gatech.edu", password = "2Factor1", type="VISITOR")
connection += connection.user(username = "adinozzo",email = "anthony.dinozzo@ncis.mil.gov", password = "V3rySpecialAgent", type="VISITOR")

# Populating table property.
connection += connection.property(name = "Atwood Street Garden",size = 1,is_commercial = False,is_public = True,address = "Atwood Street SW",city = "Atlanta",zip = "30308",type = "GARDEN",owned_by = "gardenerSteve@hotmail.com",approved_by = 'zuckerburg@fb.com')

connection += connection.property(
    name = "East Lake Urban Farm",
    size = 20,
    is_commercial = True,
    is_public = False,
    address = "2nd Avenue",
    city = "Atlanta",
    zip = "30317",
    type = "FARM",
    owned_by = "farmerJoe@gmail.com"
)

connection += connection.property(name = "Georgia Tech Garden",size = 0.5,is_commercial = False,is_public = True,address = "Spring Street SW",city = "Atlanta",zip = "30308",type = "GARDEN",owned_by = "orchardOwen@myspace.com",approved_by = 'michael@gmail.com')
connection += connection.property(name = "Georgia Tech Orchard",size = 0.5,is_commercial = False,is_public = True,address = "Spring Street SW",city = "Atlanta",zip = "30308",type = "ORCHARD",owned_by = "orchardOwen@myspace.com",approved_by = 'michael@gmail.com')
connection += connection.property(name = "Woodstock Community Garden",size = 5,is_commercial = False,is_public = True,address = "1804 Bouldercrest Road",city = "Woodstock",zip = "30188",type = "GARDEN",owned_by = "gardenerSteve@hotmail.com")
connection += connection.property(name = "Kenari Company Farm",size = 3,is_commercial = True,is_public = True,address = "100 Hightower Road",city = "Roswell",zip = "30076",type = "FARM",owned_by = "farmerJoe@gmail.com",approved_by = 'ceo@gatech.edu')

# Populate items.
connection += connection.item(name = "Apple",approved_by = "ceo@gatech.edu",category = "FRUIT")
connection += connection.item(name = "Banana",approved_by = "ceo@gatech.edu",category = "FRUIT")
connection += connection.item(name = "Orange",approved_by = "ceo@gatech.edu",category = "FRUIT")
connection += connection.item(name = "Peach",approved_by = "ceo@gatech.edu",category = "FRUIT")
connection += connection.item(name = "Peruvian Lily",approved_by = "ceo@gatech.edu",category = "FLOWER")
connection += connection.item(name = "Sunflower",approved_by = "ceo@gatech.edu",category = "FLOWER")
connection += connection.item(name = "Pineapple Sage",approved_by = None,category = "FLOWER")
connection += connection.item(name = "Daffodil",approved_by = None,category = "FLOWER")
connection += connection.item(name = "Onion",approved_by = "ceo@gatech.edu",category = "VEGETABLE")
connection += connection.item(name = "Garlic",approved_by = "ceo@gatech.edu",category = "VEGETABLE")
connection += connection.item(name = "Broccoli",approved_by = "ceo@gatech.edu",category = "VEGETABLE")
connection += connection.item(name = "Carrot",approved_by = "ceo@gatech.edu",category = "VEGETABLE")
connection += connection.item(name = "Corn",approved_by = "ceo@gatech.edu",category = "VEGETABLE")
connection += connection.item(name = "Salami",approved_by = None,category = "VEGETABLE")
connection += connection.item(name = "Peas",approved_by = "ceo@gatech.edu",category = "VEGETABLE")
connection += connection.item(name = "Rose",approved_by = "ceo@gatech.edu",category = "FLOWER")
connection += connection.item(name = "Daisy",approved_by = "ceo@gatech.edu",category = "FLOWER")
connection += connection.item(name = "Peanut",approved_by = "ceo@gatech.edu",category = "NUT")
connection += connection.item(name = "Cashew ",approved_by = "ceo@gatech.edu",category = "NUT")
connection += connection.item(name = "Almond",approved_by = None,category = "NUT")
connection += connection.item(name = "Fig",approved_by = None,category = "NUT")
connection += connection.item(name = "Pig",approved_by = "ceo@gatech.edu",category = "ANIMAL")
connection += connection.item(name = "Chicken",approved_by = "ceo@gatech.edu",category = "ANIMAL")
connection += connection.item(name = "Cow",approved_by = "ceo@gatech.edu",category = "ANIMAL")
connection += connection.item(name = "Mongoose",approved_by = None,category = "ANIMAL")
connection += connection.item(name = "Monkey",approved_by = "ceo@gatech.edu",category = "ANIMAL")
connection += connection.item(name = "Cheetah",approved_by = None,category = "ANIMAL")
connection += connection.item(name = "Pete",approved_by = None,category = "ANIMAL")
connection += connection.item(name = "Pineapple",approved_by = None,category = "FRUIT")
connection += connection.item(name = "Kiwi",approved_by = "ceo@gatech.edu",category = "FRUIT")
connection += connection.item(name = "Tomato",approved_by = None,category = "FRUIT")
connection += connection.item(name = "Goat",approved_by = "ceo@gatech.edu",category = "ANIMAL")

# Populate visits.
connection += connection.visits(user_email = "bobbilly@harvard.edu",property_id = "00001",date = "11-12-2018 12:00:01 AM",rating = 5)
connection += connection.visits(user_email = "bobbilly@harvard.edu",property_id = "00004",date = "10-23-2017 04:21:49 PM",rating = 3)
connection += connection.visits(user_email = "bobbilly@harvard.edu",property_id = "00003",date = "10-24-2017 07:31:12 AM",rating = 1)
connection += connection.visits(user_email = "bill@yahoo.com",property_id = "00003",date = "1/23/2018 05:12:34 PM",rating = 4)
connection += connection.visits(user_email = "flowerpower@gmail.com",property_id = "00001",date = "2/14/2018 12:21:12 PM",rating = 5)
connection += connection.visits(user_email = "bill@yahoo.com",property_id = "00001",date = "3/3/2018 11:12:10 AM",rating = 2)
connection += connection.visits(user_email = "bill@yahoo.com",property_id = "00006",date = "1/2/2018 07:21:10 PM",rating = 2)
connection += connection.visits(user_email = "yamada.riyo@navy.mil.gov",property_id = "00006",date = "10-28-2017 10:11:13 PM",rating = 4)
connection += connection.visits(user_email = "kateellis@gatech.edu",property_id = "00006",date = "10-27-2017 09:40:11 AM",rating = 2)
connection += connection.visits(user_email = "awoods30@gatech.edu",property_id = "00003",date = "10-27-2017 04:31:30 AM",rating = 5)
connection += connection.visits(user_email = "anthony.dinozzo@ncis.mil.gov",property_id = "00004",date = "10-10-2017 12:00:00 AM",rating = 1)

connection += connection.has(property_id = "00001", item_name = "Broccoli")
connection += connection.has(property_id = "00002", item_name = "Corn")
connection += connection.has(property_id = "00003", item_name = "Rose")
connection += connection.has(property_id = "00004", item_name = "Apple")
connection += connection.has(property_id = "00005", item_name = "Carrot")
connection += connection.has(property_id = "00006", item_name = "Chicken")
connection += connection.has(property_id = "00002", item_name = "Pig")
connection += connection.has(property_id = "00006", item_name = "Corn")
connection += connection.has(property_id = "00004", item_name = "Peanut")
connection += connection.has(property_id = "00003", item_name = "Peas")
connection += connection.has(property_id = "00003", item_name = "Peruvian Lily")
connection += connection.has(property_id = "00001", item_name = "Corn")
connection += connection.has(property_id = "00002", item_name = "Cow")
connection += connection.has(property_id = "00003", item_name = "Chicken")
connection += connection.has(property_id = "00001", item_name = "Onion")
connection += connection.has(property_id = "00001", item_name = "Daisy")
connection += connection.has(property_id = "00004", item_name = "Peach")
connection += connection.has(property_id = "00006", item_name = "Orange")
connection += connection.has(property_id = "00006", item_name = "Cashew ")
connection += connection.has(property_id = "00006", item_name = "Cow")
connection += connection.has(property_id = "00006", item_name = "Sunflower")
