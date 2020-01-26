from nornir.init_nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result

from nornir.core.filter import F
from datetime import datetime
nr = InitNornir("config.yaml")
london = nr.filter(F(groups__contains="London"))
# london_edge = nr.filter(F(groups__contains="London") & F(tags__all=["edge", "isr4300"])


# results = nr.run(task=netmiko_send_command, command_string="show version", use_textfsm=True)
# print_result(results)

def collect_outputs(task, commands):
    dt = datetime.now()
    dt_str = dt.strftime("%Y-%d-%M")
    with open(f"outputs/{task.host.name}_{dt_str}.txt", "w") as f:
        for command in commands:
            result = task.run(netmiko_send_command, command_string=command)
            f.write(f"==={command}====\n{result.result}\n")

london.run(task=collect_outputs, commands=["show ip int brief", "show version", "show ip route"])

