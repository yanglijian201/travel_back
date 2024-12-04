import sys
import code
from test4 import test4


global_capture_testcase_frame = {
    "frame_count": 0,
    "frame_stack": {},
    "CURRENT_SCOPE_ID": 0
}

def hey(a, b):
    a += 3
    b += 2
    test4(a, b)

def test(a=4, b=3, f=5):
    def test2(c, d):
        c += 1
        d += 2
        hey(c, d)
    a = 1
    b = 2
    a += 2
    test2(a, b)

def tracefunc(frame, event, arg):
    if event == 'call':
        code_object = frame.f_code
        func_name = code_object.co_name
        func_obj = frame.f_globals.get(func_name, None)
        file_name = code_object.co_filename
        function_name = "{}:{}".format(file_name, func_name)
        parameter_names = list(frame.f_locals.keys())
        capture_testcase_frame = {
            'frame': frame,
            "parameters": {},
            "func_name": function_name
        }
        for name in parameter_names:
            capture_testcase_frame['parameters'][name] = frame.f_locals[name]
        frame_count = global_capture_testcase_frame['frame_count']
        global_capture_testcase_frame['frame_stack'][frame_count] = capture_testcase_frame
        global_capture_testcase_frame['frame_count'] += 1


sys.settrace(tracefunc)
test()
sys.settrace(None)

def jump_stack(global_capture_testcase_frame, target_stack_id, initial=False):
    if target_stack_id < 0 or target_stack_id >= global_capture_testcase_frame['frame_count']:
        raise Exception("Unknow error")
    target_stack = global_capture_testcase_frame['frame_stack'][target_stack_id]

    target_frame = target_stack['frame']
    parameters = target_stack['parameters']
    func_name = target_stack['func_name']
    locals_scope = dict(target_frame.f_locals)
    globals_scope = dict(target_frame.f_globals)
    debug_scope = dict()
    debug_scope.update(globals_scope)
    debug_scope.update(locals_scope)
    scope_dict = {
        "debug_scope": debug_scope,
        "parameters": parameters,
        "func_name": func_name
    }
    return [True, scope_dict]


def vf():
    if global_capture_testcase_frame["CURRENT_SCOPE_ID"] >= global_capture_testcase_frame['frame_count']:
        print("You are on the end of stack, not able to jump")
        return
    target_stack_id = global_capture_testcase_frame["CURRENT_SCOPE_ID"] + 1
    if target_stack_id >= global_capture_testcase_frame['frame_count']:
        print("You are on the end of stack, not able to jump")
        return
    state, scope_dict = jump_stack(global_capture_testcase_frame, target_stack_id)
    global_capture_testcase_frame["CURRENT_SCOPE_ID"] = target_stack_id
    if state:
        # if target_stack_id > 1:
        #     # I want to exit code.interact, not the whole program, but only the current stack
        #     exit()

        debug_scope = scope_dict['debug_scope']
        func_name = scope_dict['func_name']
        parameters = scope_dict['parameters']
        debug_scope['vf'] = vf
        debug_scope['vb'] = vb
        debug_scope['v'] = v
        debug_scope['global_capture_testcase_frame'] = global_capture_testcase_frame
        print("Travel back to: {}".format(func_name))
        for key, value in parameters.items():
            print("  Parameter: {} = {}".format(key, value))
        code.interact(local=debug_scope)
    else:
        print("Unknow error")


def vb():
    if not global_capture_testcase_frame["CURRENT_SCOPE_ID"]:
        print("You are on the initial stack, not able to jump")
        return
    target_stack_id = global_capture_testcase_frame["CURRENT_SCOPE_ID"] - 1
    if target_stack_id >= global_capture_testcase_frame['frame_count']:
        print("You are on the end of stack, not able to jump")
        return
    state, scope_dict = jump_stack(global_capture_testcase_frame, target_stack_id)
    global_capture_testcase_frame["CURRENT_SCOPE_ID"] = target_stack_id
    if state:
        # if target_stack_id > 1:
        #     exit()
        debug_scope = scope_dict['debug_scope']
        func_name = scope_dict['func_name']
        parameters = scope_dict['parameters']
        debug_scope['vf'] = vf
        debug_scope['vb'] = vb
        debug_scope['v'] = v
        debug_scope['global_capture_testcase_frame'] = global_capture_testcase_frame
        print("Travel back to: {}".format(func_name))
        for key, value in parameters.items():
            print("  Parameter: {} = {}".format(key, value))
        code.interact(local=debug_scope)
    else:
        print("Unknow error")


class vTest(object):
    @property
    def f(self):
        return vf()

    @property
    def b(self):
        return vb()

v = vTest()

def initial():
    state, scope_dict = jump_stack(global_capture_testcase_frame, 0, initial=True)
    if not state:
        print("Unknow error")
        return
    debug_scope = scope_dict['debug_scope']
    debug_scope['vf'] = vf
    debug_scope['vb'] = vb
    debug_scope['v'] = v
    debug_scope['global_capture_testcase_frame'] = global_capture_testcase_frame
    debug_scope['jump_stack'] = jump_stack
    func_name = scope_dict['func_name']
    parameters = scope_dict['parameters']
    print("Travel back to: {}".format(func_name))
    for key, value in parameters.items():
        print("  Parameter: {} = {}".format(key, value))
    code.interact(local=debug_scope)

initial()
