import logging
from sklearn.metrics import f1_score
from kortical import api
from kortical.storage.exception import ItemNotFoundException
from module_placeholder.config import read_config
from module_placeholder.workflows import common, business_case

logger = logging.getLogger(__name__)
config = read_config("config.yml")
target = config['target']
target_accuracy = config['target_accuracy']
instance_name = config['instance_name']


def superhuman_calibration(df_calibrate, df_test, deployment_name='Integration'):
    api.init(config['system_url'])

    # Do custom processing
    datasets = [df_calibrate, df_test]
    for df in datasets:
        common.preprocessing(df)

    # Get instance and deployment
    instance = api.instance.Instance.create_or_select(instance_name)
    deployment = instance.get_deployment(deployment_name)

    df_test_raw = df_test.copy()
    df_calibrate = deployment.predict(df_calibrate)
    df_test = deployment.predict(df_test)

    # score test set
    test_f1 = f1_score(df_test[target], df_test[f'predicted_{target}'], average='weighted')
    print(f"Raw Model F1 Score: {test_f1:.3f}")

    # do Superhuman Calibration
    calibration_data = api.superhuman_calibration.calibrate(
        df_calibrate,
        target, target_accuracy,
        non_automated_class=common.not_automated_class
    )

    df_test = api.superhuman_calibration.apply(
        df_test,
        calibration_data
    )

    # call Superhuman Calibration score
    calibration_results = api.superhuman_calibration.score(df_test, calibration_data)

    uat_deployment = instance.get_deployment('UAT')

    uat_model = uat_deployment.get_live_model()

    if uat_model is not None:
        try:
            uat_calibration_data = common.storage.get(common.get_calibration_data_storage_name(uat_model.id))
        except ItemNotFoundException:
            uat_calibration_data = None

        if uat_calibration_data is not None:
            df_test_uat = deployment.predict(df_test_raw)
            df_test_uat = api.superhuman_calibration.apply(
                df_test_uat,
                uat_calibration_data
            )

            uat_calibration_results = api.superhuman_calibration.score(df_test_uat, uat_calibration_data)
        else:
            logger.warning("Current UAT model doesn't have calibration data, so may be replaced. If this is not desired republish the UAT model in the platform.")
    else:
        uat_calibration_results = None

    should_publish, reason = business_case.should_publish(calibration_results, uat_calibration_results)

    # send report for new model
    print(f"Business Case:\n\nShould Publish: {should_publish},\nReason: {reason}")

    # Optional
    if should_publish:
        model = deployment.get_live_model()

        calibration_data[target]['automation_accuracy'] = calibration_results[target]['automation_overall']['accuracy']
        common.storage.store(common.get_calibration_data_storage_name(model.id), calibration_data)

        # Optional could just be a report
        uat_deployment.publish_model(model)
