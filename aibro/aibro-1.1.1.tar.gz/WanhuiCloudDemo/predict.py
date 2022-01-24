import yaml
from .model.demo_pipeline import Pipeline


def load_model():
    with open('model/demo_pipeline.yaml') as f:
        args = yaml.load(f, Loader=yaml.FullLoader)
        # print(args)
    return Pipeline(**args)


def run(pipeline: Pipeline):
    pipeline.run()
    return pipeline.result


if __name__ == '__main__':
    run()