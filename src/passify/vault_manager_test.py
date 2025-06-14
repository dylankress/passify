from vault_manager import VaultManager

vm = VaultManager()

# Add entry (Chrome-style)
vm.add_entry(
    name="99designs.com",
    url="https://99designs.com/launch/logo-design/c483b096ca43096f/details",
    username="dylankress@gmail.com",
    password="Khgdsihdg9jlasd"
)

# Save and reload vault
vm.save_to_file(password="masterpass")
vm.load_from_file(password="masterpass")
# Retrieve entry
entry = vm.get_entry("99designs.com")
print("Entry from vault:", entry)

# Update password
vm.update_entry("99designs.com", password="N3wSecureP@ss")

# Delete entry
vm.delete_entry("99designs.com")

# List
print("Remaining entries:", vm.list_entries())

# Optional: load existing vault first
try:
    vm.load_from_file("vault.svf", "masterpass")
except FileNotFoundError:
    print("No existing vault found. Starting fresh.")

# Import Chrome passwords
count = vm.import_from_chrome_csv("chrome_passwords.csv")
print(f"Imported {count} entries from Chrome.")

# Save updated vault
vm.save_to_file("vault.svf", "masterpass")
