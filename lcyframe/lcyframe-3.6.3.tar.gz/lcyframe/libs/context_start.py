#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import logging
import time
import platform


class AutoStartContext(object):
    @classmethod
    def sleep(cls, s=1):
        time.sleep(s)

    @classmethod
    def is_repliset(cls, c):
        return c["model"] == "repliset"

    @classmethod
    def command(cls, c, is_return=True):
        if is_return:
            return os.popen(c).read().replace("\n", "")
        else:
            os.system(c)

    @classmethod
    def md2mo(cls, md):
        dir = os.path.dirname(md)
        return os.path.join(dir, "mongo")

    @classmethod
    def get_pid(cls, name, is_return=True):
        return cls.command("ps -ef| grep %s| grep -v grep| awk '{print($2}'" % name, is_return)

    @classmethod
    def is_local(cls, platform_name_list=list()):
        return not platform_name_list or platform.node() in platform_name_list

    @classmethod
    def replset_initiate(cls, c):
        """replSetInitiate"""
        if not cls.is_repliset(c):
            return

        master_item = """{"_id": "%s", "members": [{"_id": 1, "host": "%s:%s"}]}""" % (c["replsetName"], c["host"], c["port"])
        run_command = """db.runCommand({"replSetInitiate": %s})""" % master_item
        initiate_command = """%s --host=%s --port=%s admin --eval """ % (cls.md2mo(c["exepath"]), c["host"], c["port"])
        eval_command = u"'" + run_command + u"'"
        s = initiate_command + eval_command
        cls.command(s)

    @classmethod
    def add_replset_item(cls, i, c):
        slave_command = """{"_id": %s, "host": "%s:%s", "arbiterOnly": %s}""" % (i + 2, c["host"], c["port"], "true" if c.get("arbiterOnly") else "false")
        run_command = "rs.add(%s)" % slave_command
        add_command = """%s --host=%s --port=%s admin --eval '%s'""" % (cls.md2mo(c["exepath"]), c["master_host"], c["master_port"], run_command)
        cls.command(add_command.replace("\\", ""))

    @classmethod
    def get_master_command(cls, c):
        s = cls.get_mongo_command(c)
        confpath = c.get("confpath")
        if confpath:
            return s
        else:
            model = c["model"]
            if model == "master-slave":
                s += " --master"
            else:
                if model == "repliset":
                    s += " --replSet=%s" % c.get("replsetName", "rs0")
                    s += " --oplogSize=%s" % c.get("oplogSize", 2048)

            return s

    @classmethod
    def get_slave_command(cls, c):
        # slave
        s = cls.get_mongo_command(c)
        confpath = c.get("confpath")
        if confpath:
            return s
        else:
            model = c["model"]
            if model == "master-slave":
                s += " --slave --source=%s:%s" % (c["master_host"], c["master_port"])
            elif model == "repliset":
                # if c["host"] == "127.0.0.1":
                #     raise Exception("bind_ip cannot is 127.0.0.1")
                s += " --replSet=%s" % (c.get("replsetName", "rs0"))
                s += " --oplogSize=%s" % c.get("oplogSize", 2048)
            return s

    @classmethod
    def get_mongo_command(self, c):
        confpath = c.get("confpath")
        if confpath:
            s = "%s --config %s &" % (c["exepath"], c["confpath"])
        else:
            s = "%s " \
                " --bind_ip=%s" \
                " --port=%s" \
                " --dbpath=%s" \
                " --logpath=%s" \
                "" % (c["exepath"], c.get("bind_ip", "127.0.0.1"), c["port"], c["dbpath"], c["logpath"])

            if c.get("logappend", True):
                s += " --logappend"
            if c.get("fork", True):
                s += " --fork"
            if c.get("auth"):
                s += " --auth"

        return s

    @classmethod
    def kill_pid(cls, pid):
        return cls.command("kill -15 %s" % str(pid))

    @classmethod
    def mkdir(self, p):
        if not os.path.exists(p):
            os.makedirs(p)

    @classmethod
    def rm_lock(cls, path):
        cls.command("rm -f %s/mongod.lock" % path)

    @classmethod
    def start_command(cls, c):
        cls.sleep()
        logging.warning("start mongo please wait...")
        # cls.kill_pid(pid)
        cls.rm_lock(c["dbpath"])
        cls.mkdir(c["dbpath"])
        cls.mkdir(os.path.dirname(c["logpath"]))
        cls.command(c["command"])
        logging.warning("MongoDB model %s start port: %s success!" % (c.get("model", "slave"), c["port"]))

    @classmethod
    def start_mongodb(cls, c):
        if not c or not c.get("auto", False):
            return

        if cls.is_local(c.get("platform", [])):
            pid = cls.get_pid(c["dbpath"])
            p = cls.command("lsof -i:%s" % c["port"])
            if not pid and not p:
                c["command"] = cls.get_master_command(c)
                cls.start_command(c)
                cls.replset_initiate(c)
            else:
                logging.warning("MongoDB port %s has starting!" % c["port"])

        if c["model"] != "single":
            for i, slave in enumerate(c.get("slaves", [])):
                slave["model"] = c["model"]
                slave["exepath"] = slave.get("exepath") or c["exepath"]
                slave["master_host"] = c["host"]
                slave["master_port"] = c["port"]
                slave["command"] = cls.get_slave_command(slave)

                if not cls.is_local(slave.get("platform", [])):
                    logging.warning("Please run the command in hostname %s: '%s'" % (slave["host"], slave["command"]))
                    continue
                else:
                    slave_pid = cls.get_pid(slave["dbpath"])
                    # 集群时，其他机器会监听，导致误报
                    # p = cls.command("lsof -i:%s" % slave["port"])
                    if slave_pid:
                        logging.warning("port has runing:%s:%s" % (slave.get("host", c["host"]), slave["port"]))
                        continue

                    cls.start_command(slave)

                    if c["model"] != "master-slave":
                        cls.add_replset_item(i, slave)

    @classmethod
    def stop_mongodb(cls, c):
        run_pid = cls.get_pid(c["dbpath"])
        if run_pid:
            cls.command("kill -15 %s" % run_pid)

    @classmethod
    def start_redis(cls, c):
        if not c or not c.get("auto", False):
            return

        pid = cls.get_pid(c["confpath"])
        p = cls.command("lsof -i:%s" % c["port"])
        if not pid and not p:
            if not os.path.exists(c["confpath"]):
                logging.warning("%s not exists!" % c["confpath"])
                raise Exception("%s not exists!" % c["confpath"])

            cls.command("%s %s &" % (c["exepath"], c["confpath"]), False)
            logging.debug("Redis port %s starte success!" % c["port"])

        else:
            logging.debug("Redis port %s has starting!" % c["port"])

    @classmethod
    def start_ssdb(cls, c):
        if not c or not c.get("auto", False):
            return

        pid = cls.get_pid(c["confpath"])
        p = cls.command("lsof -i:%s" % c["port"])
        if not pid and not p:
            if not os.path.exists(c["confpath"]):
                logging.warning("%s not exists!" % c["confpath"])
                raise Exception("%s not exists!" % c["confpath"])

            cls.command("%s %s &" % (c["exepath"], c["confpath"]), False)
            logging.debug("ssdb port %s starte success!" % c["port"])

        else:
            logging.debug("ssdb port %s has starting!" % c["port"])

    @classmethod
    def start_supervisor(cls, c):
        if not c or not c.get("auto", False):
            return

        pid = cls.get_pid(c["confpath"])
        if not pid:
            cls.kill_pid(cls.get_pid(c["confpath"]))
            cls.command("rm -f %s" % c["pidpath"])
            cls.command("rm -f %s" % c["lockpath"])
            cls.command("%s -c %s" % (c["exepath"], c["confpath"]))
            print("Supervisor start success!")
        else:
            logging.warning("Supervisor has starting!")

    @classmethod
    def start_nginx(cls, c):
        if not c or not c.get("auto", False):
            return

        pid = cls.get_pid(c["confpath"])
        p = cls.command("lsof -i:%s" % c.get("port", "80"))
        if not pid and not p:
            # cls.kill_pid(cls.command("ps -ef| grep %s| grep -v grep| awk '{print($2}'" % c["confpath"])))
            cls.command("rm -f %s" % c["pidpath"])
            cls.command("sudo %s -c %s" % (c["exepath"], c["confpath"]))  # TODO sudo
            print("Nginx start success!")
        else:
            logging.warning("Nginx has starting!")


if __name__ == "__main__":
    pass
    # config = get_context()
    # AutoStartContext.start_mongodb(config["mongo_config"])
    # AutoStartContext.start_redis(config["redis_config"])
    # AutoStartContext.start_ssdb(config["ssdb_config"])
    # AutoStartContext.start_supervisor(config.get("supervisor"))
    # AutoStartContext.start_nginx(config.get("nginx"))