from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('caterer', 'Caterer'),
        ('admin', 'Admin'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Consider using Django's authentication system
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, null=True, blank=True)
    
    USERNAME_FIELD = 'email'  # Specify the field to be used for login (email in this case)
    REQUIRED_FIELDS = ['password']
    def __str__(self):
        return f"{self.name} ({self.role})"

class Block(models.Model):
    block_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.block_name
    
class Canteen(models.Model):
    canteen_name = models.CharField(max_length=255)
    block = models.ForeignKey(Block,related_name='canteens', on_delete=models.CASCADE)  # Foreign key to Block
    caterer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'caterer'})  # Foreign key to User with 'caterer' role
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Add this

    def __str__(self):
        return self.canteen_name

class Contact(models.Model):
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.fname} {self.lname} ({self.email})"