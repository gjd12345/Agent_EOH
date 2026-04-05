class GetPrompts:
    def __init__(self):
        self.prompt_task = (
            "You are a Go engineer. Your task is to implement a routing operator for a VRPTW solver.\n"
            "Implement the following Go method exactly with this receiver and name:\n"
            "func (assign *Assign) GenRoute()\n"
            "It should rebuild the current route and update the fields used by the simulator.\n"
        )
        self.prompt_func_name = "GenRoute"
        self.prompt_func_inputs = ["assign"]
        self.prompt_func_outputs = ["void"]
        self.prompt_inout_inf = (
            "- Receiver: *Assign\n"
            "- Available methods/fields on Assign include: GenSeq(), RoutingTask, RoutingResult, "
            "StationsLen, TimeCurrent, NextSta, NextTime, RouteLen, Route[0].CurSta, Route[0].CurTime, Cost.\n"
            "- You can call: RoutingTS(&assign.RoutingTask) to compute assign.RoutingResult.\n"
            "- SAFETY: Never set NextSta to a negative value unless StationsLen == 0.\n"
            "- SAFETY: If routing is infeasible (Cost < 0), keep NextSta/NextTime unchanged or set them to a safe station index (e.g., 0).\n"
        )
        self.prompt_other_inf = (
            "CRITICAL: Return ONLY Go code. Do not wrap in markdown. Do not include any explanations.\n"
            "Return ONLY the method definition `func (assign *Assign) GenRoute() { ... }`.\n"
            "Do not write `package main` and do not add any imports.\n"
        )

    def get_task(self):
        return self.prompt_task

    def get_func_name(self):
        return self.prompt_func_name

    def get_func_inputs(self):
        return self.prompt_func_inputs

    def get_func_outputs(self):
        return self.prompt_func_outputs

    def get_inout_inf(self):
        return self.prompt_inout_inf

    def get_other_inf(self):
        return self.prompt_other_inf
