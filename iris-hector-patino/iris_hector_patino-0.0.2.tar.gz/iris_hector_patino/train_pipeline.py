from iris_hector_patino.config.core import config
from iris_hector_patino.pipeline import iris_pipeline
from iris_hector_patino.processing.data_manager import load_dataset, save_pipeline
from sklearn.model_selection import train_test_split


def run_training():
    """train the model"""

    data = load_dataset(file_name=config.app_config.training_data_file)

    # split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop(config.model_config.target, axis=1),
        data[config.model_config.target],
        test_size=config.model_config.test_size,
        random_state=config.model_config.random_state,
        shuffle=config.app_config.shuffle,
        stratify=data[config.model_config.target],
    )

    iris_pipeline.fit(X_train, y_train)

    save_pipeline(pipeline_to_persist=iris_pipeline)


if __name__ == "__main__":
    run_training()
