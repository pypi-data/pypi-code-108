from module_placeholder.config import read_config

config = read_config("config.yml")
target = config['target']
target_accuracy = config['target_accuracy']
target_accuracy_tolerance = 0.03        # 3%
minimum_savings = 10_000
minimum_business_case_improvement = 100  # 1%


def calculate(calibration_results, print_results=False):
    automation_rate = calibration_results[target]['automation_overall']['automation']
    accuracy_rate = calibration_results[target]['automation_overall']['accuracy']

    cost_of_error = 5.5
    # £15 per hour, 20 mins for a pet inspection
    exam_time_in_hours = 1 / 60 * 20
    cost_of_review = 15 * exam_time_in_hours
    human_accuracy_rate = 0.74
    count_of_cases_per_year = 2_234_000
    # Kortical costs 1 model, 1 worker for one year (11_256), Data scientist salary assumed at 60k and 2% time for monitoring
    total_cost_of_ownership_of_automation = 11_256 + 60_000 * 0.02

    cost_for_fully_human_process = count_of_cases_per_year * cost_of_review + count_of_cases_per_year * (1 - human_accuracy_rate) * cost_of_error
    fully_human_process_man_hours = count_of_cases_per_year * exam_time_in_hours
    automation_error_cost = count_of_cases_per_year * automation_rate * (1 - accuracy_rate) * cost_of_error
    human_in_the_loop_cost = count_of_cases_per_year * cost_of_review * (1 - automation_rate)
    human_in_the_loop_error_cost = count_of_cases_per_year * (1 - automation_rate) * (1 - human_accuracy_rate) * cost_of_error
    superhuman_process_man_hours_saved = count_of_cases_per_year * automation_rate * exam_time_in_hours
    cost_for_superhuman_process = total_cost_of_ownership_of_automation + automation_error_cost + human_in_the_loop_cost + human_in_the_loop_error_cost

    savings = cost_for_fully_human_process - cost_for_superhuman_process

    if print_results:
        print(f"Automation Rate {automation_rate*100:.2f}%")
        print(f"Fully Human Process Cost £{cost_for_fully_human_process:.0f}")
        print(f"Superhuman Process Cost £{cost_for_superhuman_process:.0f}")
        print(f"Savings £{savings:.0f}, Percentage Savings {(1 - cost_for_superhuman_process / cost_for_fully_human_process) * 100:.0f}%")
        print(f"Man Hours Saved {superhuman_process_man_hours_saved:.0f}, As a percentage {(superhuman_process_man_hours_saved / fully_human_process_man_hours) * 100:.0f}%")

    return savings


def should_publish(challenger_calibration_results, champion_calibration_results):

    target = list(challenger_calibration_results.keys())[0]

    challenger_accuracy = challenger_calibration_results[target]['automation_overall']['accuracy']
    target_accuracy_delta = abs(challenger_accuracy - target_accuracy)

    # determine if the calibration_results accuracy is close enough to the target accuracy
    if challenger_accuracy < target_accuracy and \
        target_accuracy_delta > target_accuracy_tolerance:
        return False, f"The accuracy for the challenger model accuracy [{challenger_accuracy:.3f}] was not within the tolerance [{target_accuracy_tolerance}] of the target accuracy [{target_accuracy}]."

    challenger_savings = calculate(challenger_calibration_results)

    # Check that the challenger meets minimum savings criteria
    if challenger_savings < minimum_savings:
        return False, f"Savings of [£{challenger_savings:.2f}] did not meet the minimum requirement [£{minimum_savings:.2f}]"

    # If there is no champion and the target accuracy is met publish the challenger
    if champion_calibration_results is None:
        return True, f"There is no current champion. Publishing the model is recommended. The challenger accuracy [{challenger_accuracy:.3f}], the difference to the target is [{target_accuracy_delta:.3f}]. The savings are [{challenger_savings:.2f}]."

    champion_savings = calculate(champion_calibration_results)

    savings_change = challenger_savings - champion_savings

    # determine if the business case is a meaningful amount better if not return False
    if challenger_savings < champion_savings + minimum_business_case_improvement:
        return False, f"The challenger model does not meaningfully improve the business case [£{savings_change:.3f}]."

    return True, f"The challenger savings are [£{challenger_savings:.2f}], the target accuracy difference [{target_accuracy_delta:.3f}] is acceptable and the business case is improved by [£{savings_change:.2f}]."