from rules import add_perm

from aleksis.apps.evalu.util.predicates import (
    has_any_evaluation_group,
    is_evaluated_person,
    is_evaluated_person_for_group,
    is_evaluation_status,
    is_evaluation_status_for_group,
    is_finished,
    is_finishing_possible,
    is_member_of_any_evaluation_group,
    is_member_of_evaluated_group,
    is_participant_for_group,
    is_registration_running,
    is_unlocked,
)
from aleksis.core.util.predicates import has_global_perm, has_object_perm, has_person

view_evaluationparts_predicate = has_person & has_global_perm("evalu.view_evaluationpart")
add_perm("evalu.view_evaluationparts_rule", view_evaluationparts_predicate)

add_evaluationpart_predicate = view_evaluationparts_predicate & has_global_perm(
    "evalu.add_evaluationpart"
)
add_perm("evalu.add_evaluationpart_rule", add_evaluationpart_predicate)

edit_evaluationpart_predicate = view_evaluationparts_predicate & has_global_perm(
    "evalu.change_evaluationpart"
)
add_perm("evalu.edit_evaluationpart_rule", edit_evaluationpart_predicate)

delete_evaluationpart_predicate = view_evaluationparts_predicate & has_global_perm(
    "evalu.delete_evaluationpart"
)
add_perm("evalu.delete_evaluationpart_rule", delete_evaluationpart_predicate)

view_evaluationphases_predicate = has_person & has_global_perm("evalu.view_evaluationphase")
add_perm("evalu.view_evaluationphases_rule", view_evaluationphases_predicate)

view_evaluationphase_predicate = has_person & (
    has_global_perm("evalu.view_evaluationphase") | has_object_perm("evalu.view_evaluationphase")
)
add_perm("evalu.view_evaluationphase_rule", view_evaluationphase_predicate)

create_evaluationphase_predicate = view_evaluationphases_predicate & has_global_perm(
    "evalu.create_evaluationphase"
)
add_perm("evalu.create_evaluationphase_rule", create_evaluationphase_predicate)

edit_evaluationphase_predicate = view_evaluationphases_predicate & (
    has_global_perm("evalu.change_evaluationphase")
    | has_object_perm("evalu.change_evaluationphase")
)
add_perm("evalu.edit_evaluationphase_rule", edit_evaluationphase_predicate)

delete_evaluationphase_predicate = view_evaluationphases_predicate & (
    has_global_perm("evalu.delete_evaluationphase")
    | has_object_perm("evalu.delete_evaluationphase")
)
add_perm("evalu.delete_evaluationphase_rule", delete_evaluationphase_predicate)

view_evaluationphases_overview_predicate = has_person & (is_member_of_any_evaluation_group)
add_perm("evalu.view_evaluationphases_overview_rule", view_evaluationphases_overview_predicate)

register_for_evaluation_predicate = (
    has_person & is_member_of_evaluated_group & is_registration_running
)
add_perm("evalu.register_for_evaluation_rule", register_for_evaluation_predicate)

view_evaluationregistration_predicate = has_person & (
    is_evaluated_person | has_global_perm("evalu.view_evaluationregistration")
)
add_perm("evalu.view_evaluationregistration_rule", view_evaluationregistration_predicate)

manage_evaluation_process_predicate = (
    view_evaluationregistration_predicate & is_evaluation_status("evaluation") & ~is_finished
)
add_perm("evalu.manage_evaluation_process_rule", manage_evaluation_process_predicate)

view_evaluations_results_predicate = view_evaluationregistration_predicate & (
    is_evaluation_status("results") | is_finished
)
add_perm("evalu.view_evaluation_results_rule", view_evaluations_results_predicate)

finish_evaluation_predicate = view_evaluationregistration_predicate & is_finishing_possible
add_perm("evalu.finish_evaluation_rule", finish_evaluation_predicate)

start_evaluation_for_group_predicate = (
    has_person
    & is_evaluation_status_for_group("evaluation")
    & ~is_finished
    & ~is_unlocked
    & (is_evaluated_person_for_group | has_global_perm("evalu.edit_evaluationgroup"))
)
add_perm("evalu.start_evaluation_for_group_rule", start_evaluation_for_group_predicate)

stop_evaluation_for_group_predicate = (
    has_person
    & is_evaluation_status_for_group("evaluation")
    & ~is_finished
    & is_unlocked
    & (is_evaluated_person_for_group | has_global_perm("evalu.edit_evaluationgroup"))
)
add_perm("evalu.stop_evaluation_for_group_rule", stop_evaluation_for_group_predicate)

view_evaluations_as_participant_predicate = has_person & has_any_evaluation_group
add_perm("evalu.view_evaluations_as_participant_rule", view_evaluations_as_participant_predicate)

evaluate_person_predicate = (
    has_person
    & is_participant_for_group
    & is_evaluation_status_for_group("evaluation")
    & is_unlocked
)
add_perm("evalu.evaluate_person_rule", evaluate_person_predicate)

view_evaluation_menu_predicate = has_person & (
    view_evaluationparts_predicate
    | view_evaluationphases_predicate
    | view_evaluationphases_overview_predicate
    | view_evaluations_as_participant_predicate
)
add_perm("evalu.view_menu_rule", view_evaluation_menu_predicate)
