# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem

engine = create_engine('postgresql:///catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



#Prepolulate categories
category1 = Category(name = "Soccer")

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(title = "Shinguards",
                             description = "Shin guards are as much a part of the player's uniform as cleats or a jersey.\
                               A required piece of equipment, it can be hard to decide which shinguard is right for you.\
                               For example, a midfielder may not require the same type of guard as a forward.\
                               A youth player will not wear the same type guard as an older player.".rstrip('\n'),
                             category = category1)

session.add(categoryItem1)
session.commit()


category2 = Category(name = "Basketball")

session.add(category2)
session.commit()

category3 = Category(name = "Baseball")

session.add(category3)
session.commit()

category4 = Category(name = "Frisbee")

session.add(category4)
session.commit()

category5 = Category(name = "Snowboarding")

session.add(category5)
session.commit()

categoryItem1 = CategoryItem(title = "Snowboard",
                             description = """Best for any terrain and conditions.  All-mountain snowboards perform anywhere
                              on a mountain - groomed runs, backcountry, even park and pipe.  They may be directional
                              (meaning downhill only) or twin-tip (for ride switching, meaning either direction).
                              Most boarders ride all-mountain boards.""",
                             category = category5)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(title = "Goggles",
                             description = """forms of protective eyewear that usually enclose or protect the area surrounding
                              the eye in order to prevent particulates, water or chemicals from striking the eyes.""",
                             category = category5)

session.add(categoryItem2)
session.commit()

category6 = Category(name = "Rock Climbing")

session.add(category6)
session.commit()

category7 = Category(name = "Foosball")

session.add(category7)
session.commit()

category8 = Category(name = "Skating")

session.add(category8)
session.commit()

category9 = Category(name = "Hockey")

session.add(category9)
session.commit()


print "added categories and items!"

