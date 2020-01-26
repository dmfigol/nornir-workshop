from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from datetime import datetime
from pathlib import Path

nr = InitNornir(config_file="config.yaml")

# results = nr.run(netmiko_send_command, command_string="show ip int brief")
# print_result(results)

# results = nr.run(netmiko_send_command, command_string="show version", use_textfsm=True)
# print_result(results)

london = nr.filter(F(groups__contains="London"))
london_edge = nr.filter(F(groups__contains="London") & F(tags__all=["isr4400", "edge"]))



def save_commands_output(task, commands):
    dt = datetime.now()
    dt_str = dt.strftime('%Y-%m-%d_%H:%M:%S')
    file_path = Path("outputs") / f"{task.host.name}__{dt_str}.txt"
    with open(file_path, "w") as f:
        for command in commands:
            f.write(f"===== {command} =====")
            output = task.run(netmiko_send_command, command_string=command)
            f.write(output.result)


london_edge.run(save_commands_output, commands=["show ip arp", "show ip int br"])