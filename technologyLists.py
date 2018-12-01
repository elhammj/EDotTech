# Elham Jaffar
# Nov 2018
# This file has data for the online technologies shop

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Items, User

engine = create_engine('sqlite:///edottechshop.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# create the session
session = DBSession()

# Add dummy User
User1 = User(name="Elham Jaffar", email="elham@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Adding Catrgories and items
category1 = Category(user_id=1, id=1, name="Mobile Phone")
session.add(category1)
session.commit()

item1 = Items(user_id=1, id=001,name='iPhone 6', description='It is an iOS mobile phone version 6', price='480$', category=category1)
session.add(item1)
session.commit()

item2 = Items(user_id=1, id=002,name='iPhone 7', description='It is an iOS mobile phone version 7', price='580$', category=category1)
session.add(item2)
session.commit()

item3 = Items(user_id=1, id=003,name='iPhone 8', description='It is an iOS mobile phone version 8', price='680$', category=category1)
session.add(item3)
session.commit()

item4 = Items(user_id=1, id=004,name='iPhone X', description='It is an iOS mobile phone version 10', price='780$', category=category1)
session.add(item4)
session.commit()

item5 = Items(user_id=1, id=005,name='iPhone XS Max', description='It is an iOS mobile phone version 11', price='1080$', category=category1)
session.add(item5)
session.commit()

category2 = Category(user_id=1, id=2, name="Home Devices")
session.add(category2)
session.commit()

item6 = Items(user_id=1, id=006,name='Google Home Mini', description='It is a mini home device that can assist you by Google', price='180$', category=category2)
session.add(item6)
session.commit()

item7 = Items(user_id=1, id=007,name='Google Home', description='It is a home device that can assist you by Google', price='280$', category=category2)
session.add(item7)
session.commit()

item8 = Items(user_id=1, id=8 ,name='Amazon Alexa', description='It is a home device that can assist you', price='380$', category=category2)
session.add(item8)
session.commit()


category3 = Category(user_id=1, id=3, name="Laptops")
session.add(category3)
session.commit()

item9 = Items(user_id=1, id=015,name='Macbook Pro', description='It is one of the best laptops', price='1080$', category=category3)
session.add(item9)
session.commit()

item10 = Items(user_id=1, id=016,name='Macbook Air', description='It is a new slim laptop', price='1270$', category=category3)
session.add(item10)
session.commit()


category4 = Category(user_id=1, id=4, name="Desktops")
session.add(category4)
session.commit()

item11 = Items(user_id=1, id=011,name='HP Desktop', description='It is a CPU and Screen', price='1380$', category=category4)
session.add(item11)
session.commit()


category5 = Category(user_id=1, id=5, name="TV")
session.add(category5)
session.commit()

item12 = Items(user_id=1, id=012,name='Samsung 64', description='It is aa high resolution TV', price='380$', category=category5)
session.add(item12)
session.commit()

item13 = Items(user_id=1, id=013,name='Sony 120', description='It is a big fancy TV', price='1880$', category=category5)
session.add(item13)
session.commit()

category6 = Category(user_id=1, id=6, name="Accessories")
session.add(category6)
session.commit()

item14 = Items(user_id=1, id=014,name='Airpods', description='Headphones for Apple Devices, works with phones and laptops', price='200$', category=category6)
session.add(item14)
session.commit()

print "added items!"