import sqlite3


DB_NAME = 'db/func_db.sqlite'


class FunctionNotFound(Exception):
    pass


class SavedFunctionsDB:

    def __init__(self):
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()

    def add_func_to_db(self, graph_func: str):
        self.con.execute(f"""INSERT INTO Functions(function) VALUES("{graph_func}")""")
        self.con.commit()

    def get_all_func_from_db(self):
        res = self.con.execute("""SELECT function FROM Functions""")
        return [i for i, in res]

    def get_func_from_db(self, search_string):
        res = self.con.execute(
            f"""SELECT function FROM Functions WHERE function LIKE "%{search_string}%" """)
        return [i for i, in res]

    def get_id_by_func(self, graph_func: str):
        res = self.con.execute(
            f"""SELECT id FROM Functions WHERE function = "{graph_func}" """).fetchone()
        if res is None:
            raise FunctionNotFound
        else:
            return res[0]

    def get_func_by_id(self, identification):
        res = self.con.execute(
            f"""SELECT function FROM Functions WHERE id = {identification} """).fetchone()
        return res[0]

    def update_func_by_id(self, identification, new_graph_func: str):
        self.con.execute(
            f"""UPDATE Functions SET function = "{new_graph_func}" WHERE id = {identification}""")
        self.con.commit()

    def delete_func_by_id(self, identification):
        self.con.execute(
            f"""DELETE FROM Functions WHERE id = {identification}""")
        self.con.commit()
