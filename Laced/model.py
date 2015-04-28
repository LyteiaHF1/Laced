import mysql.connector

class Shoe(object):
     """A wrapper object that corresponds to rows in the store table."""
    def __init__(self, productId, productName, Img, price, size, descript, con):
        self.productId, = productId,
        self.productName = productName
        self.Img = Img
        self.price = price
        self.size = size
        self.descript = descript
        self.con = con
        
    def price_str(self):
        return "$%.2f"%self.price

    def __repr__(self):
        return "<Shoe: %s, %s, %s>"%(self.productId, self.productName, self.price_str())