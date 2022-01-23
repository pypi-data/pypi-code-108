def first_option_user(interaction):
    try:
        user_id = interaction["data"]["options"][0]["value"]
    except KeyError:
        return None

    return interaction["data"]["resolved"]["users"][user_id]


def first_option_user_or_author(interaction):
    return (
        first_option_user(interaction)
        or interaction.get("user")
        or interaction["member"]["user"]
    )


def message_command_target(interaction):
    target_id = interaction["data"]["target_id"]
    return interaction["data"]["resolved"]["messages"][target_id]["author"]


def user_command_target(interaction):
    target_id = interaction["data"]["target_id"]
    return interaction["data"]["resolved"]["users"][target_id]
