
import click

# TODO(gaocegege): Factory pattern to create different renderers.
renders = {}


class TerminalTableRender():
    # TODO(gaocegege): Make a base class here.
    def render(self, resource, artifacts):
        # TODO(gaocegege): Use reflection to render project and run.
        from terminaltables import AsciiTable

        if resource == "project":
            table_data = [
                ["project_name", "runs"],
            ]
            for project in artifacts:
                table_data = table_data + [[project.name, project.runs]]
        else:
            table_data = [
                ["run_name", "project_name", "metrics"],
            ]
            for run in artifacts:
                table_data = table_data + \
                    [[run.name, run.project, run.metrics]]
        table = AsciiTable(table_data)
        click.echo(table.table)


class TerminalChartRender():
    def render(self, resource, metric):
        if resource != "metric":
            raise ValueError("Invalid resource type: {}".format(resource))
        import plotext as plt
        plt.plot(metric.datapoints)
        plt.title("{}/{} {}".format(metric.project, metric.run, metric.name))
        plt.show()

def register(name, render):
    renders[name] = render


def register_all_renders():
    register("normal", TerminalTableRender())
    register("chart", TerminalChartRender())


def render(resource, artifacts, output):
    register_all_renders()
    if output not in renders:
        raise ValueError("Invalid output type: {}".format(output))
    renders[output].render(resource, artifacts)
