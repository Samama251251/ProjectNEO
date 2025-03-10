from modules.code.coder import coder
from modules.code.tester import tester
from modules.shell.shell_actions import shell_actions

async def code_controller(instructions):
    improvement_required = True
    tester_output = ""
    while (improvement_required):
        print("code invoked")
        code = await coder(instructions, ' '.join(tester_output))
        print("\033[1;32m" + code['code'] + "\033[1;0m")
        tester_output = await tester(code['code'], "Assume the output using dry run")
        print("\033[1;33m" + str(tester_output) + "\033[1;0m")
        if tester_output['improve'] == False or tester_output['improve'] == 'false':
            improvement_required = False

    return "The final code is:" + str(code) + "\n Ask the user what to do with it."