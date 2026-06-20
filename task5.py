# contact_book_cli.py
import json
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

class Contact:
    def __init__(self, contact_id: int, name: str, phone: str, email: str = "", 
                 address: str = "", notes: str = ""):
        self.id = contact_id
        self.name = name
        self.phone = self.format_phone(phone)
        self.email = email
        self.address = address
        self.notes = notes
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number for consistency."""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11:
            return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Contact':
        contact = cls(
            contact_id=data["id"],
            name=data["name"],
            phone=data["phone"],
            email=data.get("email", ""),
            address=data.get("address", ""),
            notes=data.get("notes", "")
        )
        contact.created_at = data.get("created_at", contact.created_at)
        contact.updated_at = data.get("updated_at", contact.updated_at)
        return contact
    
    def __str__(self) -> str:
        return f"{self.name} | {self.phone}"


class ContactBook:
    def __init__(self, storage_file: str = "contacts.json"):
        self.storage_file = storage_file
        self.contacts: List[Contact] = []
        self.next_id = 1
        self.load_contacts()
    
    def add_contact(self, name: str, phone: str, email: str = "", 
                   address: str = "", notes: str = "") -> Contact:
        """Add a new contact."""
        # Check for duplicate phone number
        if self.find_by_phone(phone):
            raise ValueError(f"Phone number {phone} already exists!")
        
        contact = Contact(self.next_id, name, phone, email, address, notes)
        self.contacts.append(contact)
        self.next_id += 1
        self.save_contacts()
        return contact
    
    def get_contact(self, contact_id: int) -> Optional[Contact]:
        """Get a contact by ID."""
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    def update_contact(self, contact_id: int, **kwargs) -> bool:
        """Update contact details."""
        contact = self.get_contact(contact_id)
        if not contact:
            return False
        
        if 'name' in kwargs and kwargs['name']:
            contact.name = kwargs['name']
        if 'phone' in kwargs and kwargs['phone']:
            # Check for duplicate phone number (excluding current contact)
            existing = self.find_by_phone(kwargs['phone'])
            if existing and existing.id != contact_id:
                raise ValueError(f"Phone number {kwargs['phone']} already exists!")
            contact.phone = Contact.format_phone(kwargs['phone'])
        if 'email' in kwargs:
            contact.email = kwargs['email']
        if 'address' in kwargs:
            contact.address = kwargs['address']
        if 'notes' in kwargs:
            contact.notes = kwargs['notes']
        
        contact.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_contacts()
        return True
    
    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact by ID."""
        contact = self.get_contact(contact_id)
        if not contact:
            return False
        self.contacts.remove(contact)
        self.save_contacts()
        return True
    
    def find_by_name(self, name: str) -> List[Contact]:
        """Search contacts by name (case-insensitive partial match)."""
        name_lower = name.lower()
        return [c for c in self.contacts if name_lower in c.name.lower()]
    
    def find_by_phone(self, phone: str) -> Optional[Contact]:
        """Find a contact by phone number (exact match)."""
        formatted_phone = Contact.format_phone(phone)
        for contact in self.contacts:
            if contact.phone == formatted_phone:
                return contact
        return None
    
    def search(self, query: str) -> List[Contact]:
        """Search contacts by name, phone, email, or address."""
        query_lower = query.lower()
        results = []
        for contact in self.contacts:
            if (query_lower in contact.name.lower() or
                query_lower in contact.phone or
                query_lower in contact.email.lower() or
                query_lower in contact.address.lower()):
                results.append(contact)
        return results
    
    def get_all_contacts(self, sort_by: str = "name") -> List[Contact]:
        """Get all contacts sorted by specified field."""
        if sort_by == "name":
            return sorted(self.contacts, key=lambda c: c.name.lower())
        elif sort_by == "created":
            return sorted(self.contacts, key=lambda c: c.created_at, reverse=True)
        elif sort_by == "updated":
            return sorted(self.contacts, key=lambda c: c.updated_at, reverse=True)
        return self.contacts
    
    def get_total_count(self) -> int:
        """Get total number of contacts."""
        return len(self.contacts)
    
    def save_contacts(self):
        """Save contacts to JSON file."""
        data = {
            "next_id": self.next_id,
            "contacts": [contact.to_dict() for contact in self.contacts]
        }
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"❌ Error saving contacts: {e}")
    
    def load_contacts(self):
        """Load contacts from JSON file."""
        if not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.next_id = data.get("next_id", 1)
                self.contacts = [Contact.from_dict(c) for c in data.get("contacts", [])]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Error loading contacts: {e}")
            self.contacts = []
            self.next_id = 1


def display_contact(contact: Contact, show_full: bool = False):
    """Display a single contact."""
    print("\n" + "="*50)
    print(f"📇 {contact.name}")
    print("="*50)
    print(f"📞 Phone:  {contact.phone}")
    if contact.email:
        print(f"✉️ Email:  {contact.email}")
    if contact.address:
        print(f"📍 Address: {contact.address}")
    if contact.notes:
        print(f"📝 Notes:  {contact.notes}")
    if show_full:
        print(f"🆔 ID: {contact.id}")
        print(f"📅 Created: {contact.created_at}")
        print(f"🔄 Updated: {contact.updated_at}")
    print("="*50)


def display_contact_list(contacts: List[Contact], title: str = "Contacts"):
    """Display a list of contacts."""
    if not contacts:
        print(f"\n📋 {title}: No contacts found.")
        return
    
    print(f"\n📋 {title}:")
    print("-"*60)
    print(f"{'ID':<4} {'Name':<25} {'Phone':<20} {'Email':<20}")
    print("-"*60)
    for contact in contacts:
        print(f"{contact.id:<4} {contact.name[:24]:<25} {contact.phone:<20} {contact.email[:19]:<20}")
    print("-"*60)
    print(f"Total: {len(contacts)} contacts\n")


def get_valid_phone() -> str:
    """Get and validate phone number."""
    while True:
        phone = input("📞 Phone number: ").strip()
        if not phone:
            print("❌ Phone number cannot be empty!")
            continue
        
        # Basic phone number validation (at least 10 digits)
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            print("❌ Phone number must have at least 10 digits!")
            continue
        
        return phone


def get_valid_email() -> str:
    """Get and validate email address."""
    while True:
        email = input("✉️ Email (optional): ").strip()
        if not email:
            return ""
        
        # Simple email validation
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return email
        else:
            print("❌ Invalid email format! Example: name@domain.com")
            continue


def main():
    contact_book = ContactBook()
    
    while True:
        print("\n" + "="*50)
        print("📇 CONTACT BOOK APPLICATION")
        print("="*50)
        print(f"Total Contacts: {contact_book.get_total_count()}")
        print("-"*50)
        print("1. ➕ Add Contact")
        print("2. 📋 View All Contacts")
        print("3. 🔍 Search Contact")
        print("4. ✏️ Update Contact")
        print("5. 🗑️ Delete Contact")
        print("6. 📊 View Contact Details")
        print("7. 🗂️ Sort Contacts")
        print("8. 💾 Export Contacts")
        print("0. 🚪 Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye! Your contacts have been saved.")
            break
        
        elif choice == "1":  # Add Contact
            print("\n➕ ADD NEW CONTACT")
            print("-"*30)
            
            name = input("👤 Full name: ").strip()
            if not name:
                print("❌ Name cannot be empty!")
                continue
            
            phone = get_valid_phone()
            email = get_valid_email()
            address = input("📍 Address (optional): ").strip()
            notes = input("📝 Notes (optional): ").strip()
            
            try:
                contact = contact_book.add_contact(name, phone, email, address, notes)
                print(f"\n✅ Contact added successfully! (ID: {contact.id})")
                display_contact(contact)
            except ValueError as e:
                print(f"❌ Error: {e}")
        
        elif choice == "2":  # View All Contacts
            contacts = contact_book.get_all_contacts()
            display_contact_list(contacts, "All Contacts")
        
        elif choice == "3":  # Search Contact
            print("\n🔍 SEARCH CONTACTS")
            print("-"*30)
            print("Search by:")
            print("1. Name")
            print("2. Phone Number")
            print("3. Any field (name, phone, email, address)")
            
            search_choice = input("Enter choice (1-3): ").strip()
            
            if search_choice == "1":
                name = input("Enter name to search: ").strip()
                if not name:
                    print("❌ Name cannot be empty!")
                    continue
                results = contact_book.find_by_name(name)
                display_contact_list(results, f"Search Results: '{name}'")
            
            elif search_choice == "2":
                phone = get_valid_phone()
                contact = contact_book.find_by_phone(phone)
                if contact:
                    display_contact(contact, show_full=True)
                else:
                    print(f"❌ No contact found with phone number: {phone}")
            
            elif search_choice == "3":
                query = input("Enter search term: ").strip()
                if not query:
                    print("❌ Search term cannot be empty!")
                    continue
                results = contact_book.search(query)
                display_contact_list(results, f"Search Results: '{query}'")
            
            else:
                print("❌ Invalid choice!")
        
        elif choice == "4":  # Update Contact
            print("\n✏️ UPDATE CONTACT")
            print("-"*30)
            
            try:
                contact_id = int(input("Enter contact ID to update: "))
                contact = contact_book.get_contact(contact_id)
                if not contact:
                    print("❌ Contact not found!")
                    continue
                
                print(f"\nCurrent details:")
                display_contact(contact, show_full=True)
                
                print("\nEnter new details (press Enter to keep current value):")
                name = input(f"👤 Name ({contact.name}): ").strip()
                phone = input(f"📞 Phone ({contact.phone}): ").strip()
                email = input(f"✉️ Email ({contact.email}): ").strip()
                address = input(f"📍 Address ({contact.address}): ").strip()
                notes = input(f"📝 Notes ({contact.notes}): ").strip()
                
                # Prepare update data
                update_data = {}
                if name:
                    update_data['name'] = name
                if phone:
                    update_data['phone'] = phone
                if email:
                    update_data['email'] = email
                if address:
                    update_data['address'] = address
                if notes:
                    update_data['notes'] = notes
                
                if not update_data:
                    print("ℹ️ No changes made.")
                    continue
                
                try:
                    if contact_book.update_contact(contact_id, **update_data):
                        print("✅ Contact updated successfully!")
                        display_contact(contact_book.get_contact(contact_id), show_full=True)
                except ValueError as e:
                    print(f"❌ Error: {e}")
            
            except ValueError:
                print("❌ Invalid ID format!")
        
        elif choice == "5":  # Delete Contact
            print("\n🗑️ DELETE CONTACT")
            print("-"*30)
            
            try:
                contact_id = int(input("Enter contact ID to delete: "))
                contact = contact_book.get_contact(contact_id)
                if not contact:
                    print("❌ Contact not found!")
                    continue
                
                print(f"\nContact to delete:")
                display_contact(contact)
                
                confirm = input("\nAre you sure you want to delete this contact? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    if contact_book.delete_contact(contact_id):
                        print("✅ Contact deleted successfully!")
                else:
                    print("❌ Deletion cancelled.")
            
            except ValueError:
                print("❌ Invalid ID format!")
        
        elif choice == "6":  # View Contact Details
            print("\n📊 VIEW CONTACT DETAILS")
            print("-"*30)
            
            try:
                contact_id = int(input("Enter contact ID: "))
                contact = contact_book.get_contact(contact_id)
                if contact:
                    display_contact(contact, show_full=True)
                else:
                    print("❌ Contact not found!")
            except ValueError:
                print("❌ Invalid ID format!")
        
        elif choice == "7":  # Sort Contacts
            print("\n🗂️ SORT CONTACTS")
            print("-"*30)
            print("Sort by:")
            print("1. Name (A-Z)")
            print("2. Recently Added")
            print("3. Recently Updated")
            
            sort_choice = input("Enter choice (1-3): ").strip()
            
            if sort_choice == "1":
                contacts = contact_book.get_all_contacts("name")
                display_contact_list(contacts, "Contacts (Sorted by Name)")
            elif sort_choice == "2":
                contacts = contact_book.get_all_contacts("created")
                display_contact_list(contacts, "Contacts (Recently Added)")
            elif sort_choice == "3":
                contacts = contact_book.get_all_contacts("updated")
                display_contact_list(contacts, "Contacts (Recently Updated)")
            else:
                print("❌ Invalid choice!")
        
        elif choice == "8":  # Export Contacts
            print("\n💾 EXPORT CONTACTS")
            print("-"*30)
            print("Export format:")
            print("1. JSON (current format)")
            print("2. CSV (spreadsheet format)")
            
            export_choice = input("Enter choice (1-2): ").strip()
            
            if export_choice == "1":
                # Just show the file location
                print(f"📁 Contacts are already saved in: {contact_book.storage_file}")
                print(f"📊 Total: {contact_book.get_total_count()} contacts")
            
            elif export_choice == "2":
                # Export to CSV
                import csv
                filename = f"contacts_export_{datetime.now().strftime('%Y%m%d')}.csv"
                try:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Name', 'Phone', 'Email', 'Address', 'Notes', 'Created', 'Updated'])
                        for contact in contact_book.get_all_contacts():
                            writer.writerow([
                                contact.name,
                                contact.phone,
                                contact.email,
                                contact.address,
                                contact.notes,
                                contact.created_at,
                                contact.updated_at
                            ])
                    print(f"✅ Contacts exported to: {filename}")
                except Exception as e:
                    print(f"❌ Error exporting contacts: {e}")
            
            else:
                print("❌ Invalid choice!")
        
        else:
            print("❌ Invalid choice! Please enter a number between 0 and 8.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Your contacts have been saved.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")