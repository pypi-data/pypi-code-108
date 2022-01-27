def filter_for_files(output_activity):
    dep_name = output_activity["name"]
    return {
        "name": f"Only files from {dep_name}",
        "type": "Filter",
        "dependsOn": [
            {
                "activity": dep_name,
                "dependencyConditions": [
                    "Succeeded"
                ]
            }
        ],
        "userProperties": [],
        "typeProperties": {
            "items": {
                "value": f"@activity('{dep_name}').output.childItems",
                "type": "Expression"
            },
            "condition": {
                "value": "@equals(item().type, 'File')",
                "type": "Expression"
            }
        }
    }
