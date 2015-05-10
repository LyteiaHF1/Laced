"""Model for Laced shopping site."""

import sqlite3

class Shoe(object):
    """An Laced type.

    A wrapper object that corresponds to rows in the Store table.
    """

    def __init__(self,id,shoe_type,common_name,price,imgurl,size,con):
        self.id = id
        self.shoe_type = shoe_type
        self.common_name = common_name
        self.price = price
        self.imgurl = imgurl
        self.size = size
        self.con = con

    def price_str(self):
        """Return price formatted as string $x.xx"""

        return "$%.2f" % self.price

    def __repr__(self):
        """Convenience method to show information about shoe in console."""

        return "<Shoe: %s, %s, %s>" % (
            self.id, self.common_name, self.price_str())

    
    
    @classmethod
    def get_all_home(cls, max=5):
        """Return list of shoes.

        Query the database for the first [max] shoes, returning each as a
        shoe object
        """

        cursor = db_connect()
        QUERY = """
                  SELECT id,
                         shoe_type,
                         common_name,
                         price,
                         imgurl,
                         size,
                         con
                   FROM store
                   WHERE size = '7'
                   LIMIT ?;
               """

        cursor.execute(QUERY, (max,))
        store_rows = cursor.fetchall()
        
        # list comprehension to build a list of Shoe objects by going through
        # the database records and making a shoe for each row. This is done
        # by unpacking in the for-loop.

        shoes = [Shoe(*row) for row in store_rows]

        print shoes
        #print "new shit addded"

        return shoes
    
    
    
    @classmethod
    def get_all(cls, max=55):
        """Return list of shoes.

        Query the database for the first [max] shoes, returning each as a
        shoe object
        """

        cursor = db_connect()
        QUERY = """
                  SELECT id,
                         shoe_type,
                         common_name,
                         price,
                         imgurl,
                         size,
                         con
                   FROM store
                   WHERE imgurl <> ''
                   LIMIT ?;
               """

        cursor.execute(QUERY, (max,))
        store_rows = cursor.fetchall()
        
        # list comprehension to build a list of Shoe objects by going through
        # the database records and making a shoe for each row. This is done
        # by unpacking in the for-loop.

        shoes = [Shoe(*row) for row in store_rows]

        print shoes
        #print "new shit addded"

        return shoes

    @classmethod
    def get_by_id(cls, id):
        """Query for a specific shoe in the database by the primary key"""

        cursor = db_connect()
        QUERY = """
                  SELECT id,
                         shoe_type,
                         common_name,
                         price,
                         imgurl,
                         size,
                         con
                   FROM store
                   WHERE id = ?;
               """

        cursor.execute(QUERY, (id,))

        row = cursor.fetchone()

        if not row:
            return None

        shoe = Shoe(*row)

        return shoe

def db_connect():
    """Return a database cursor."""
    conn = sqlite3.connect("laced.db")
    cursor = conn.cursor()
    return cursor

