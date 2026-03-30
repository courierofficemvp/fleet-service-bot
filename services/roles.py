from sheets.users import get_role

ADMIN_ID = "5643220428"

def check_role(user_id):
    user_id = str(user_id).strip()

    role = get_role(user_id)

    # 🔥 DEBUG (увидишь в логах bothost)
    print(f"DEBUG ROLE CHECK: user_id={user_id}, role_from_sheet={role}")

    # если ты — всегда admin
    if user_id == ADMIN_ID:
        return "admin"

    # если нашли роль в таблице
    if role:
        return str(role).strip()

    return None
