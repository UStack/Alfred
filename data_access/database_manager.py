from tinydb import TinyDB


class DatabaseManager:
    def __init__(self):
        self.db = TinyDB('c:/temp/db.json')

    def insert(self, category, data):
        table = self.db.table(category)

        return table.insert(data)

    def delete(self, category, eid):
        table = self.db.table(category)

        table.remove(eids=[eid])

    def update(self, category, eid, data):
        table = self.db.table(category)

        table.update(data, eids=[eid])

    def get_all(self, category):
        table = self.db.table(category)

        return table.all()

    def get_by_id(self, category, eid):
        table = self.db.table(category)

        return table.get(eid=eid)
