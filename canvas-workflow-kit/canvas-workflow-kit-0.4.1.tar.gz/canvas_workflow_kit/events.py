"""

Events are specified to allow the system to know when to compute the protocol.

They are declared in the `responds_to_event_types` class attribute in `ClinicalQualityMeasure`
classes.


```python
from canvas_workflow_kit import events

class Hcc002v2(ClinicalQualityMeasure):
    title = 'CKD suspect'

    ...

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    ...
```


## Event triggers

### HEALTH_MAINTENANCE
**canvas\_workflow\_kit.events.HEALTH\_MAINTENANCE**

Run protocol when patient data has changed.

### CHART_OPEN
**canvas\_workflow\_kit.events.CHART\_OPEN**

Run protocol when patient the patient chart has been opened.

"""

# Run protocol when patient data has changed.
HEALTH_MAINTENANCE = 'HEALTH_MAINTENANCE'

# Run protocol when patient the patient chart has been opened.
CHART_OPEN = 'CHART_OPEN'
