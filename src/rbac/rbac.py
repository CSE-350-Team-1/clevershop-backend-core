RBAC_ROLES = {
    'User': ['Manipulate_self'],
    'Manager': ['Manipulate_self', 'Manipulate_user'],
    'Admin': ['Manipulate_self', 'Manipulate_user', 'Manipulate_manager']
}



REQUIRED_ENDPOINT_PERMS = {
    "/account/change_own_email" : ['Manipulate_self'],
    "/account/delete_own_account" : ['Manipulate_self'],

    "/account/change_user_email" : ['Manipulate_user'],
    "/account/add_user" : ['Manipulate_user'],
    "/account/delete_user" : ['Manipulate_user'],

    "/account/change_manager_email" : ['Manipulate_manager'],
    "/account/add_manager" : ['Manipulate_manager'],
    "/account/delete_manager" : ['Manipulate_manager'],

    "/service/get_items" : [],

    "/service/list_own_lists" : ['Manipulate_self'],
    "/service/get_own_list" : ['Manipulate_self'],
    "/service/add_own_item" : ['Manipulate_self'],
    "/service/remove_own_item" : ['Manipulate_self'],

    "/service/list_user_lists" : ['Manipulate_user'],
    "/service/get_user_list" : ['Manipulate_user'],
    "/service/add_user_item" : ['Manipulate_user'],
    "/service/remove_user_item" : ['Manipulate_user'],

    "/service/list_manager_lists" : ['Manipulate_manager'],
    "/service/get_manager_list" : ['Manipulate_manager'],
    "/service/add_manager_item" : ['Manipulate_manager'],
    "/service/remove_manager_item" : ['Manipulate_manager']
}