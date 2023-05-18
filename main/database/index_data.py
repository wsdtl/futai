import random
import datetime

from database import DataBaseData

sql = DataBaseData()


def wid_data():

    return random.randint(1,500)

def len_data():

    return random.randint(501,1000)

def shape_data():

    return str(random.choice(["三角形","长方形","正方形","圆形","异形"]))

def thinck_data():

    return random.randint(1,10)

def date():

    return str(datetime.date.today()) 

def postion():

    return str(random.choice(["1号柜","2号柜","3号柜","4号柜","5号柜","6号柜","7号柜","8号柜","9号柜","0号柜"]))


sql = DataBaseData()

for i in range(1,10):

    len_data_ = len_data()
    wid_data_ = wid_data()
    shape_data_ = shape_data()
    thinck_data_ = thinck_data()
    date_ = date()
    postion_ = postion()

    print(len_data_,wid_data_,shape_data_,thinck_data_,date_,postion_)
    sql.add_data(len_data=len_data_ , wid_data=wid_data_ , shape_data= shape_data_,
                 thinck_data= thinck_data_, date= date_, postion= postion_)
 


sql.close()