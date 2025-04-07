
def print_planner(response):
    node_name = list(response.keys())[0]
    planner_markdown = """# Step-by-Step Plan\r\n\r\n## Plan Steps\r\n\r\n| Agent | Task | Stopping Criteria |\r\n|-------|------|-------------------|\r\n{plan_str}"""
    plan_str = '\r\n'.join([f'|{agent_name}|{task}|{stopping_criteria}|' for agent_name, task, stopping_criteria in response[node_name]['plan_steps']])
    planner_markdown = planner_markdown.format(plan_str=plan_str)
    return planner_markdown


def print_router(response):
    router_markdown = f"""
    # 📋 Task Assignment

    ---

    ### 👤 Next Agent
    **{response['router']['next_agent']}**

    ---

    ### 🎯 Next Task
    **{response['router']['next_task']}**

    ---

    ### ⏹️ Stopping Criteria
    **{response['router']['stopping_criteria']}**
    """
    return router_markdown

def agent_printer(response):
    agent = list(response.keys())[0]
    summary_response = response[agent]['past_steps'][0][1]
    return summary_response

printer_functions_dict = {
    'planner': print_planner,
    'router': print_router,
    'replanner': print_planner,
    'ore_execution_agent': agent_printer,
    'ore_xml_agent': agent_printer,
    'sensitivity_agent': agent_printer,
    'stress_test_agent': agent_printer,
    'portfolio_xml_agent': agent_printer,
    'analysis_agent': agent_printer,
}

