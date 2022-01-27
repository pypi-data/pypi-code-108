from appdynamics.agent.core.pb import CustomMetric as pb_CustomMetric

TIME_AVERAGE = pb_CustomMetric.TIME_AVERAGE
TIME_SUM = pb_CustomMetric.TIME_SUM
CURRENT = pb_CustomMetric.CURRENT
INDIVIDUAL = pb_CustomMetric.INDIVIDUAL
COLLECTIVE = pb_CustomMetric.COLLECTIVE
RATE_COUNTER = pb_CustomMetric.RATE_COUNTER
REGULAR_COUNTER = pb_CustomMetric.REGULAR_COUNTER


class CustomMetric(object):
    def __init__(self, name, time_rollup_type=TIME_AVERAGE, cluster_rollup_type=INDIVIDUAL,
                 hole_handling_type=REGULAR_COUNTER):
        self.name = name
        self.time_rollup_type = time_rollup_type
        self.cluster_rollup_type = cluster_rollup_type
        self.hole_handling_type = hole_handling_type
