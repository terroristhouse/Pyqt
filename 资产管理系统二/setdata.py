import sqlite3
import time
import faker
import random
faker = faker.Faker('zh_CN')
# print(time.strftime('%Y-%m-%d'))
'''填充假数据'''

con = sqlite3.connect('./db/AssetsManagement.db')
cur = con.cursor()
data_list = []
for i in range(50000):
    data_list_child = []
    for j in range(10):
        data = 'rows %s,column %s' % (i, j)
        if j == 0:
            data = faker.building_number()
        if j == 1:
            data = faker.company_suffix()
        if j == 2:
            data = faker.name_male()
        if j == 7:
            data = time.strftime('%Y-%m-%d')

        data_list_child.append(data)
    data_list.append(tuple(data_list_child))
# print(data_list)

insert_sql = 'insert into Assets(room_number,branch,person,asset_name,models,rank,`number`,created_time,status,remark) values(?,?,?,?,?,?,?,?,?,?)'
cur.executemany(insert_sql,data_list)
con.commit()

cur.close()
con.close()





