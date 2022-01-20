def meeting_effectiveness():
    result = """
    ### complience
    1. The meeting starts on time.
    2. All participants are present or have a good reason for absence (illness, vacation, etc ...).
    3. All participants are on time.
    4. All participants are well prepared.
    5. All relevant information is distributed before the meeting.
    6. Terms of Reference are used to include the participants in the goal of the meeting.
    7. An actions and decisions list is used.
    8. The meeting ends on time.

    ### connection
    1. The chairman is aware of all relevant issues and knows which ones need to be discussed.
    2. There is a good balance between main and side issues.
    3. All items on the agenda are sufficiently covered.
    4. All completed actions are discussed and new actions are assigned.
    5. The chairman pays attention to actions that have not been completed.
    6. All participants have a proactive attitude (solutions instead of problems).
    7. Strikingly good or bad results are discussed in detail.
    8. Discussions focus on the performance issues that have the greatest impact.

    ### completion
    1. The planning and realization are discussed in detail.
    2. The root causes of any gap between planning and realization are determined.
    3. Responsibles (R in RASCI) can explain the differences between planning and realization.
    4. Discussions focus on the performance issues that have the greatest impact.
    5. KPIs are updated when the needs of the business have changed.
    6. The chairman carefully weighs new targets in order to continue to improve.
    7. Undesirable behavior is corrected and managers coach and discuss as part of performance management.
    8. Lessons learned are communicated, best practices are shared between departments and teams.
    """
    return result

def mef():
    mef = {
        'complience': [
            'The meeting starts on time.',
            'All participants are present or have a good reason for absence (illness, vacation, etc ...).',
            'All participants are on time.',
            'All participants are well prepared.',
            'All relevant information is distributed before the meeting.',
            'Terms of Reference are used to include the participants in the goal of the meeting.',
            'An actions and decisions list is used.',
            'The meeting ends on time.',
            ],
        'connection': [
            'The chairman is aware of all relevant issues and knows which ones need to be discussed.',
            'There is a good balance between main and side issues.',
            'All items on the agenda are sufficiently covered.',
            'All completed actions are discussed and new actions are assigned.',
            'The chairman pays attention to actions that have not been completed.',
            'All participants have a proactive attitude (solutions instead of problems).',
            'Strikingly good or bad results are discussed in detail.',
            'Discussions focus on the performance issues that have the greatest impact.',
            ],
        'completion': [
            'The planning and realization are discussed in detail.',
            'The root causes of any gap between planning and realization are determined.',
            'Responsibles (R in RASCI) can explain the differences between planning and realization.',
            'Discussions focus on the performance issues that have the greatest impact.',
            'KPIs are updated when the needs of the business have changed.',
            'The chairman carefully weighs new targets in order to continue to improve.',
            'Undesirable behavior is corrected and managers coach and discuss as part of performance management.',
            'Lessons learned are communicated, best practices are shared between departments and teams.',
        ]
    }