from DobotRPC import loggers

loggers.set_use_file(False)

loggers.get('test').info('222')

