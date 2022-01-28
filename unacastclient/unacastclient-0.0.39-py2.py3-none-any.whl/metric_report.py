from unacastclient.unacast.metric.v1 import Metric as v1_Metric

class MetricReport(object):

    def __init__(self, catalog, metric: v1_Metric):
        self._catalog = catalog
        self._metric = metric

    def to_dict(self):
        return self._metric.to_dict()
        
    def report(self):
        return self._catalog._client.metric_report(self._catalog.id, self._metric.id)

    def print(self):
        report = self.report()
        obs_date = report.observation_period
        period_filters = self._metric.your_lens.lens_filters.period_filters
        print(f"""
            metric_id: {self._metric.id}
            description: {self.to_dict()['dimensions'][0]['description']}
            total entries (for your restricted search): {report.total_size}
            cardinality (for your restricted search): {self.print_address_component_cardinality(report.address_components)}
            your filter restrictions: {self.print_address_component_filters_restrictions(self._metric.your_lens.lens_filters.address_component_filters)}
            your observation period restrictions: {self.period_restrictions(period_filters)}
            """)
    
    @staticmethod
    def print_address_component_cardinality(address_components_reports):
        cardinality = []
        for a in address_components_reports:
            cardinality.append(f"""{a.display_name}: {a.cardinality}""")

        return cardinality

    @staticmethod
    def print_address_component_filters_restrictions(address_components_restrictions):
        if len(address_components_restrictions) == 0:
            return 'no restrictions'

        restrictions = []
        for a in address_components_restrictions:
            restrictions.append(f"""{a.component}: {a.values}""")

        return restrictions

    @staticmethod
    def period_restrictions(period_filters):
        if len(period_filters) == 0:
            return 'no restrictions'

        restricted_date = period_filters[0]

        return f"start: '{restricted_date.start.year}-{restricted_date.start.month}-{restricted_date.start.day}'" + f", end: '{restricted_date.end.year}-{restricted_date.end.month}-{restricted_date.end.day}' "
