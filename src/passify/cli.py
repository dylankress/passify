import argparse
import os
import getpass
from pathlib import Path
from vault_manager import VaultManager

DEFAULT_VAULT_PATH = Path.home() / ".passify" / "vault.svf"

def prompt_password(confirm=False) -> str:
    while True:
        pw = getpass.getpass("Enter master password: ")
        if confirm:
            pw2 = getpass.getpass("Confirm master password: ")
            if pw != pw2:
                print("❌ Passwords do not match. Try again.")
                continue
        return pw

def main():
    parser = argparse.ArgumentParser(description="Passify Password Manager CLI")
    subparsers = parser.add_subparsers(dest="command")

    # set-master command
    subparsers.add_parser("set-master", help="Initialize vault with a new master password")

    # import command
    import_parser = subparsers.add_parser("import", help="Import Chrome passwords from CSV")
    import_parser.add_argument("csv_file", help="Path to Chrome-exported CSV file")
    import_parser.add_argument("--vault", default=DEFAULT_VAULT_PATH, help="Vault file path")
    import_parser.add_argument("--password", help="Master password (prompted if omitted)")

    # list command
    list_parser = subparsers.add_parser("list", help="List all saved entry names")
    list_parser.add_argument("--vault", default=DEFAULT_VAULT_PATH, help="Vault file path")
    list_parser.add_argument("--password", help="Master password (prompted if omitted)")

    # get command
    get_parser = subparsers.add_parser("get", help="Retrieve a stored entry by name")
    get_parser.add_argument("--name", required=True, help="Name (label) of the site")
    get_parser.add_argument("--vault", default=DEFAULT_VAULT_PATH, help="Vault file path")
    get_parser.add_argument("--password", help="Master password (prompted if omitted)")

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new entry to the vault")
    add_parser.add_argument("--name", required=True, help="Name (label) for the entry")
    add_parser.add_argument("--url", required=True, help="URL of the site")
    add_parser.add_argument("--username", required=True, help="Username/email for the site")
    add_parser.add_argument("--vault", default=DEFAULT_VAULT_PATH, help="Vault file path")
    add_parser.add_argument("--password", help="Master password (prompted if omitted)")

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a stored entry by name")
    delete_parser.add_argument("--name", required=True, help="Name (label) of the site to delete")
    delete_parser.add_argument("--vault", default=DEFAULT_VAULT_PATH, help="Vault file path")
    delete_parser.add_argument("--password", help="Master password (prompted if omitted)")

    args = parser.parse_args()
    vault_path = Path(args.vault) if hasattr(args, "vault") else DEFAULT_VAULT_PATH

    if args.command == "set-master":
        if vault_path.exists():
            print(f"🔐 Vault already exists at: {vault_path}")
            current_password = prompt_password()

            vm = VaultManager(vault_path)
            try:
                vm.load_from_file(password=current_password)
            except Exception:
                print("❌ Incorrect password. Cannot reset master password.")
                return

            print("✅ Current password verified.")
            print("\n⚠️  WARNING: Resetting your master password will re-encrypt the vault.")
            print("           If you forget the new password, your data will be permanently lost.")
            confirm = input("Type 'YES' to continue: ")
            if confirm.strip() != "YES":
                print("❌ Aborted.")
                return

            new_password = prompt_password(confirm=True)
            vm.save_to_file(password=new_password)
            print(f"✅ Master password has been updated.")

        else:
            print("\n🚨 This will create a brand new encrypted vault.")
            print("   There is no password recovery. If you lose the master password, your data is lost forever.")
            confirm = input("Type 'YES' to proceed: ")
            if confirm.strip() != "YES":
                print("❌ Aborted.")
                return

            vault_path.parent.mkdir(parents=True, exist_ok=True)
            password = prompt_password(confirm=True)

            vm = VaultManager(vault_path)
            vm.save_to_file(password=password)
            print(f"✅ Master password set. Vault created at: {vault_path}")

    elif args.command == "import":
        password = args.password or prompt_password()
        vm = VaultManager(vault_path)

        try:
            vm.load_from_file(password=password)
        except FileNotFoundError:
            print("🔔 No existing vault found. A new one will be created.")

        count = vm.import_from_chrome_csv(args.csv_file)
        vm.save_to_file(password=password)

        if count == 0:
            print("⚠️  No entries were imported. Is the CSV formatted correctly?")
        else:
            print(f"✅ Imported {count} entries into vault at: {vault_path}")

    elif args.command == "list":
        password = args.password or prompt_password()
        vm = VaultManager(vault_path)
        try:
            vm.load_from_file(password=password)
        except Exception as e:
            print(f"❌ Failed to load vault: {e}")
            return

        entries = vm.list_entries()
        if entries:
            print("🔐 Stored entries:")
            for site in entries:
                print(f" - {site}")
        else:
            print("📭 No entries found.")

    elif args.command == "get":
        password = args.password or prompt_password()
        vm = VaultManager(vault_path)
        try:
            vm.load_from_file(password=password)
        except Exception as e:
            print(f"❌ Failed to load vault: {e}")
            return

        entry = vm.get_entry(args.name)
        if entry:
            print(f"\n🔍 Entry for '{args.name}':")
            print(f"   URL     : {entry['url']}")
            print(f"   Username: {entry['username']}")
            print(f"   Password: {entry['password']}")
        else:
            print(f"❌ No entry found for '{args.name}'.")

    elif args.command == "add":
        password = args.password or prompt_password()
        vm = VaultManager(vault_path)
        try:
            vm.load_from_file(password=password)
        except FileNotFoundError:
            print("🔔 No existing vault found. A new one will be created.")

        entry_password = getpass.getpass("Enter password for the site: ")

        vm.add_entry(
            name=args.name,
            url=args.url,
            username=args.username,
            password=entry_password
        )
        vm.save_to_file(password=password)
        print(f"✅ Added entry '{args.name}' to the vault.")

    elif args.command == "delete":
        password = args.password or prompt_password()
        vm = VaultManager(vault_path)
        try:
            vm.load_from_file(password=password)
        except Exception as e:
            print(f"❌ Failed to load vault: {e}")
            return

        if vm.delete_entry(args.name):
            vm.save_to_file(password=password)
            print(f"🗑️  Deleted entry '{args.name}' from the vault.")
        else:
            print(f"❌ No entry named '{args.name}' found.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

