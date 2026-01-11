from user_repo import create_item, delete_user, get_all_users

create_item("Example title", "https://example.com")

items = get_all_users()
for item in items:
    print(dict(item))

delete_user(1)
