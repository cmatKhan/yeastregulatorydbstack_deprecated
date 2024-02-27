from typing import Dict


def load_env_vars_from_file(filepath: str) -> Dict[str, str]:
    """
    Load environment variables from a given file.

    Each line of the file should contain an environment variable in the
    form "-e key"=value.

    :param filepath: The path to the file containing environment variables.
    :type filepath: str

    :return: A dictionary of environment variables read from the file.
    :rtype: Dict[str, str]
    """
    env_vars = {}
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                env_vars[key] = value
    return env_vars


def env_args_str() -> str:
    """
    Create a string of environment variables for use in a command line,
      loaded from predefined files.

      :return: A formatted string of environment variables for command line
        usage.
      :rtype: str
    """
    env_list = []

    # Define the paths to your environment files
    env_files = [".envs/.production/.django", ".envs/.production/.postgres"]

    environmental_variables = {}
    for env_file in env_files:
        environmental_variables.update(load_env_vars_from_file(env_file))

    for k, v in environmental_variables.items():
        env_list.append(f"-e {k}={v} \\")

    return "\n".join(env_list)


def create_django_float_cmd(
    app_name: str,
    security_group_id: str,
    tag_str: str,
    float_alias: str = "float",
) -> str:

    env_args = env_args_str()

    return f"""
{float_alias} submit \\n
  -n {app_name} \\n
  -i django:latest \\n
  -c 2:4 \\n
  -m 1:10 \\n
  {env_args} \\n
  --vmPolicy [onDemand=true,retryLimit=3,retryInterval=600s] \
  --migratePolicy [cpu.upperBoundRatio=80,cpu.lowerBoundRatio=5,\
    cpu.upperBoundDuration=120s,cpu.lowerBoundDuration=300s,\
    cpu.limit=16,cpu.lowerLimit=0,mem.upperBoundRatio=80,\
    mem.lowerBoundRatio=5,mem.upperBoundDuration=120s,\
    mem.lowerBoundDuration=300s,mem.limit=60,mem.lowerLimit=0,\
    stepAuto=true,evadeOOM=true] \\n
  --securityGroup {security_group_id} \\n
  --publish 80 \\n
  --gateway g-f1b2jsvbrctuu5o2ner7l \\n
  --targetPort 80 \\n
  --zone us-east-2a \\n
  --subnet mysubnetid \\n
  --dumpMode full \\n
  --customTag {tag_str}
  """


# create parse_args for create_django_float_cmd
def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Create a django float command.")
    parser.add_argument("app_name", help="The name of the app.")
    parser.add_argument("security_group_id", help="The security group id.")
    parser.add_argument("tag_str", help="The tag string.")
    parser.add_argument("float_alias", help="The float alias.", default="float")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(
        create_django_float_cmd(
            args.app_name, args.security_group_id, args.tag_str, args.float_alias
        )
    )
