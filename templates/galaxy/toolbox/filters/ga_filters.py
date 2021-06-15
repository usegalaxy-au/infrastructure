test_tool_users = {{}}
test_tool_label = '{{}}'

def hide_test_tools(context, tool):
    """
    hide tools with 'test' tag from all but selected_users
    """
    if hasattr(tool, 'labels') and test_tool_label in tool.labels.split(','):  # is this a list or a string?
        return False
    return True