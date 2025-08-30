#!/usr/bin/env python
"""
Debug script for authentication issues.
Run: python debug_auth.py
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindpulse.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models.user_model import User

def debug_user_auth(username, password):
    print(f"\n=== Debugging Authentication for '{username}' ===")
    
    try:
        # Check if user exists
        user = User.objects.get(username=username)
        print(f"✅ User found: {user}")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Role: {user.role}")
        print(f"   - Is Active: {user.is_active}")
        print(f"   - Is Staff: {user.is_staff}")
        print(f"   - Has Usable Password: {user.has_usable_password()}")
        
        # Test password directly
        password_valid = user.check_password(password)
        print(f"   - Password Check: {password_valid}")
        
        # Test Django authenticate
        auth_user = authenticate(username=username, password=password)
        print(f"   - Django Authenticate: {'SUCCESS' if auth_user else 'FAILED'}")
        
        if not auth_user:
            print("\n❌ Authentication Failed - Possible Issues:")
            if not user.is_active:
                print("   - User account is not active")
            if not user.has_usable_password():
                print("   - User does not have a usable password")
            if not password_valid:
                print("   - Password is incorrect")
        else:
            print("\n✅ Authentication SUCCESS")
            
    except User.DoesNotExist:
        print(f"❌ User '{username}' does not exist")
        
        # Show available users
        print("\nAvailable users:")
        for u in User.objects.all():
            print(f"   - {u.username} ({u.role}) - Active: {u.is_active}")

def list_all_users():
    print("\n=== All Users in Database ===")
    users = User.objects.all()
    if not users:
        print("No users found in database")
        return
    
    for user in users:
        print(f"Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Has password: {user.has_usable_password()}")
        print("---")

def create_test_manager():
    """Create a test manager user"""
    print("\n=== Creating Test Manager ===")
    try:
        user = User.objects.create_user(
            username='testmanager',
            email='manager@test.com',
            password='TestPass123!',
            role='manager'
        )
        user.is_active = True
        user.save()
        print(f"✅ Created manager: {user.username}")
        return user
    except Exception as e:
        print(f"❌ Failed to create manager: {e}")
        return None

if __name__ == "__main__":
    print("Django Auth Debug Tool")
    print("=" * 50)
    
    # List all users first
    list_all_users()
    
    # Test authentication
    username = input("\nEnter username to test (or press Enter for 'testmanager'): ").strip()
    if not username:
        username = 'testmanager'
        
    password = input("Enter password (or press Enter for 'TestPass123!'): ").strip()
    if not password:
        password = 'TestPass123!'
    
    # If testmanager doesn't exist, create it
    if username == 'testmanager':
        try:
            User.objects.get(username='testmanager')
        except User.DoesNotExist:
            create_test_manager()
    
    debug_user_auth(username, password)