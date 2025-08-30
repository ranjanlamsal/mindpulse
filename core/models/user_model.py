"""
Optimized User model with enhanced indexing and performance improvements.
"""
from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role="employee"):
        if not email:
            raise ValueError("Users must have an email")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password, role="admin")
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    """Optimized User model with enhanced indexing for wellbeing analytics."""
    
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default="employee",
        db_index=True  # Index for role-based queries
    )
    hashed_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    last_login_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Additional optimization fields
    message_count = models.PositiveIntegerField(default=0)  # Denormalized for performance
    last_activity = models.DateTimeField(null=True, blank=True, db_index=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        indexes = [
            # Enhanced indexes for user queries
            models.Index(fields=['email']),
            models.Index(fields=['hashed_id']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['last_activity', 'role']),
            models.Index(fields=['created_at', 'role']),
        ]
        db_table_comment = "Users with optimized indexing for wellbeing analytics"

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @staticmethod
    def get_hashed_id_by_username(username):
        """
        Retrieve the hashed_id for a given username.
        
        Args:
            username (str): The username to look up.
        
        Returns:
            UUID: The hashed_id of the user.
        
        Raises:
            User.DoesNotExist: If no user with the given username exists.
        """
        user = User.objects.get(username=username)
        return user.hashed_id