import json
import os
import sys
import requests


class Verify:
    login_url = None
    global version
    version = "v1.7.2"

    def __init__(self, course_url):

        self.course_url = course_url
        self.login_url = None

        self.config_file = "config"
        self.home_folder = os.path.join(os.path.expanduser('~'), ".gb_dl")
        self.config_file_ = os.path.join(self.home_folder, self.config_file)

        if not os.path.exists(self.home_folder):
            os.mkdir(self.home_folder)

        def is_valid(data):
            from uuid import getnode as get_cid
            import hashlib
            cid = str(get_cid())

            try:
                cid = cid.encode("utf-8")

            except Exception as e:
                print("An error occurred . Please report this issue")
                sys.exit(1)

            cid = hashlib.sha256(cid).hexdigest()

            _data = data

            data = {"from": "gb-dl",
                    "key": _data,
                    "machine_id": cid,
                     "version": version}
            data_json = json.dumps(data)
            headers = {'Content-type': 'application/json'}
            url = "https://gb-dl.cf/webhook1"
            response = requests.post(url, data=data_json, headers=headers)
            response_json = json.loads(response.content)

            if response_json['response'] == "200":
                token = response_json['token']

                try:
                    with open(self.config_file_, 'w') as file:
                        file.write(_data)

                except Exception as e:
                    pass

                finally:

                    data = {"from": "gb-dl",
                            "key": _data,
                            "machine_id": cid,
                            "token": token}

                    data_json = json.dumps(data)
                    _schools_url = 'https://www.gb-dl.cf/l/hello.do'
                    _schools_ = requests.post(_schools_url, data=data_json).content
                    schools = json.loads(_schools_)

                    school_id = [schools[school] for school in schools.keys() if school in self.course_url]

                    if school_id:
                        school_id = school_id[0]

                        login_url = "https://sso.teachable.com/secure/" + str(school_id) + \
                                    "/users/sign_in?flow_school_id=" + str(school_id)

                        self.login_url = login_url
                        return
                    return None
            else:

                print(response_json['message'])
                print("Kindly contribute a one time donation and get a key to use this tool. Thanks\n"
                      "Get your key here https://www.buymeacoffee.com/l/gbdl")

                with open(self.config_file_, 'w') as file:
                    file.write("")
                    self.__init__(self.course_url)

        try:

            with open(self.config_file_, 'r') as _file:
                license_key = _file.readline().strip()

                if license_key == "":
                    try:
                        license_key = raw_input("Enter your gb-dl license key > ").strip()
                    except Exception as e:

                        license_key = input("Enter your gb-dl license key > ").strip()
                    is_valid(license_key)
                else:
                    is_valid(license_key)

        except Exception as e:
            with open(self.config_file_, 'w') as _file:
                _file.write("")
                self.__init__(self.course_url)

    def get_login_url(self):
        return self.login_url

