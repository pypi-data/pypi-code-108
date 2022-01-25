def validate_passport(env_dict):
    ...

def provide_visa(env_dict):
    ...

def declare_goods(env_dict):
    ...

us_citizen_workflow = [ validate_passport, declare_goods ]
mex_citizen_workflow = [ provide_visa, validate_passport, declare_goods ]

workflows_by_country = { "US":us_citizen_workflow,  
                         "MEX":mex_citizen_workflow }

def process_entry(person):
    env_dict = person.copy()
    for work_step in workflows_by_country[person["country"]]:
        work_step(env_dict)
    return env_dict["entry_status"]