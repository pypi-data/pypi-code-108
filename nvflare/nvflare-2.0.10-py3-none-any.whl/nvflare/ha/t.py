import random
import time

from nvflare.ha.sd_server import SP, db

db.drop_all()
db.create_all()

# t0 = time.time()
for i in range(2):
    sp = SP(service_point=f"hello.com:{i}", project="example_project", state="starting")
    db.session.add(sp)
    db.session.commit()
time.sleep(1)

for item in SP.query.all():
    item.state = "started"
    time.sleep(1)
    db.session.commit()
for item in SP.query.all():
    print(item.__dict__)

# print(time.time() - t0)

# sp2 = SP.query.filter_by(name_port="hello.com:3828").first()
# if sp2 is None:
#     db.session.add(sp1)
#     db.session.commit()
# for item in SP.query.all():
#     print(item.__dict__)
