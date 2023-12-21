class Images(db.Model):
    ID = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    count = db.Column('count', db.Integer)
    name = db.Column('name', db.TEXT)