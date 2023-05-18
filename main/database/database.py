import os
from collections import namedtuple
from pathlib import Path

import sqlite3

num = "123456789"

class DataBaseData():
    global num
    _instance = {}
    _has_init = {}
    
    DATABASE = Path() / os.path.dirname(os.path.abspath(__file__)) / "database.db"
    DATABASE_TABLE = {
        "waste":["id","len_data","wid_data","shape_data","thinck_data","date","postion","is_delete"]
        }
    
    # WASTE_DATA = namedtuple("waste", ["id","len_data","wid_data",
    #                                   "shape_data","thinck_data","date","is_delete"])
    MAIN_TABLE = "waste"
     
    def __new__(cls, *args, **kwargs):

        if kwargs.get("signal", False):
            cls.MyWindow_sql_signal = kwargs.get("signal")
        if cls._instance.get(num) is None:
            cls._instance[num] = super(DataBaseData, cls).__new__(cls)
        return cls._instance[num] 
     
    def __init__(self, *args, **kwargs):
        
        txt = "数据库已连接！"
        if not self._has_init.get(num):
            self._has_init[num] = True
            self.conn = sqlite3.connect(self.DATABASE, timeout=10, check_same_thread=False)
            
            msg = self._check_table()
            try:
                self.MyWindow_sql_signal.emit(txt + "<br>" + msg)
            except Exception as e:
                pass
            
    def close(self) -> None:
        
        self.conn.close()
        # try:
        #     self.MyWindow_sql_signal.emit("数据库关闭！")
        # except Exception as e:
        #     pass

    def _check_table(self) -> str:
        """检查数据完整性"""
        
        txt = ""
        for table, key in self.DATABASE_TABLE.items():
            if table == "waste":
                cur = self.conn.cursor()
                try:
                    cur.execute(f"select count(*) from {table};")
                except sqlite3.OperationalError:
                    cur.execute(f'''CREATE TABLE {table}
                        ("id" integer primary key autoincrement not null,
                        "len_data" int not null,
                        "wid_data" int not null,
                        "shape_data" char(10),
                        "thinck_data" int,   
                        "date" char(20),
                        "postion" char(20) default null,
                        "is_delete" int default 1
                        );''')
                    self.conn.commit()
                    txt += f"{table}数据表创建成功!"
            else:
                pass
        return txt    

    def add_data(self,len_data: int,wid_data : int ,shape_data: str,thinck_data: int,date: str,postion: str) -> None:
        """在数据库中创建并初始化"""

        sql = f"""insert into {self.MAIN_TABLE} 
        (len_data, wid_data, shape_data, thinck_data, date, postion) 
        values (?,?,?,?,?,?);"""
        cur = self.conn.cursor()
        cur.execute(sql, (len_data, wid_data, shape_data, thinck_data, date, postion))
        self.conn.commit()
        return 
        
    def select_data(self, len_min = None, len_max = None, wid_min = None, wid_max = None, shape_data = None, thinck_data = None) -> tuple:
        sql = f"select * from {self.MAIN_TABLE} where "
        
        if len_min != None and len_max != None:
            sql += f"len_data in ({len_min},{len_max}) and "
        elif len_min == None and len_max != None:
            sql += f"len_data<={len_max} and "
        elif len_min != None and len_max == None:
            sql += f"len_data>={len_min} and "
            
        if wid_min != None and wid_max != None:
            sql += f"wid_data in ({wid_min},{wid_max}) and "
        elif wid_min == None and wid_max != None:
            sql += f"wid_data<={wid_max} and "
        elif wid_min != None and wid_max == None:
            sql += f"wid_data>={wid_min} and "
        
        if shape_data != None:
            sql += f"shape_data={shape_data} and "
        if thinck_data != None:
            sql += f"thinck_data={thinck_data} and "

        if sql[-4:] == "and ":
            sql = sql[:-4]
        # sql += ";"    
        print(sql)
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            return  self.DATABASE_TABLE.get(self.MAIN_TABLE), result
        except Exception as e:
            print(e)
            return False, e

       

