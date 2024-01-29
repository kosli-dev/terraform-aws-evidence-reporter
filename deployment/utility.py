def prepare_kosli_trail_name(principal_id):
    principal_id_split = principal_id.split(":")
    prefix = principal_id_split[0]
    username = principal_id_split[1].split("@")[0]
    username = username.replace("@", "_")
    kosli_trail_name = f"{prefix}_{username}"

    return kosli_trail_name