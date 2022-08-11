from collections import namedtuple

# contents of ga.filters.py here

test_tool_users=['carrot@email.org'] # substituted
test_tool_label = "test"

def restrict_alphafold(context, tool):
    """
    Only let GA team, alphafold beta users and UoM vet school alphafold users see alphafold
    """
    if tool.id.startswith('toolshed.g2.bx.psu.edu/repos/galaxy-australia/alphafold2/alphafold'):
        user = context.trans.user
        return user is not None and (
            user.email in test_tool_users or any([
                role for role in user.all_roles() if (
                    role.name in ['Alphafold', 'UoM_Vet_Alphafold'] and not role.deleted
        )]))
    return True


test_tools = [
    {
        'id': 'maxquant_test',
        'role': 'maxquant_test',
    },
]

def hide_test_tools(context, tool):
    """
    hide tools with 'test' tag from all but selected_users
    """
    if hasattr(tool, 'labels') and test_tool_label in tool.labels:
        user = context.trans.user
        for test_tool in test_tools:
            if tool.id == test_tool['id']:
                return user is not None and (
                    user.email in test_tool_users or test_tool['role'] in [
                        r.name for r in user.all_roles() if not r.deleted
                    ]
                )
        return user is not None and user.email in test_tool_users
    return True

def restrict_alphafold(context, tool):
    """
    Only let GA team, alphafold beta users and UoM vet school alphafold users see alphafold
    """
    if tool.id.startswith('toolshed.g2.bx.psu.edu/repos/galaxy-australia/alphafold2/alphafold'):
        user = context.trans.user
        return user is not None and (
            user.email in test_tool_users or any([
                role for role in user.all_roles() if (
                    role.name in ['Alphafold', 'UoM_Vet_Alphafold'] and not role.deleted
        )]))
    return True

# end contents of ga.filters.py here

Tool = namedtuple('Tool', ['id', 'labels'])
context = namedtuple('context', ['trans'])
transaction = namedtuple('transaction', 'user')
User = namedtuple('User', ['all_roles', 'email'])
Role = namedtuple('Role', ['name', 'deleted'])

role1 = Role('Alphafold', False)
role2 = Role('UoM_Vet_Alphafold', False)
role3 = Role('some_role', False)

user1 = User(lambda: [role1, role2], 'amy@email.org')
user2 = User(lambda: [], 'amy@email.org')

trans1 = transaction(user1)
trans2 = transaction(user2)

context1 = context(trans1)
context2 = context(trans2)

tool1 = Tool('toolshed.g2.bx.psu.edu/repos/galaxy-australia/alphafold2/alphafold', [])
tool2 = Tool('anything_but_alphafold', [])

assert restrict_alphafold(context1, tool1) == True  # if tool is alphafold and user is in groups, tool is visible
assert restrict_alphafold(context2, tool1) == False  # if tool is alphafold and user not in groups, tool is not visible
assert restrict_alphafold(context1, tool2) == True  # any tool other than alphafold is visible


roleA = Role('maxquant_test', False)

userA = User(lambda: [roleA], 'amy@email.org')
userB = User(lambda: [], 'amy@email.org')
userC = User(lambda: [], 'carrot@email.org')

transA = transaction(userA)
transB = transaction(userB)
transC = transaction(userC)

contextA = context(transA)
contextB = context(transB)
contextC = context(transC)

toolA = Tool('maxquant_test', ['test'])
toolB = Tool('something_else', ['test'])

assert hide_test_tools(contextA, toolA) == True
assert hide_test_tools(contextB, toolA) == False
assert hide_test_tools(contextC, toolA) == True
assert hide_test_tools(contextA, toolB) == False
assert hide_test_tools(contextB, toolB) == False
assert hide_test_tools(contextC, toolB) == True
