from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.timezone import now 
from django.utils import timezone
from main.models import User, Block, Canteen,Contact  # Importing from main:models.py
# from django.contrib.auth.models import User

class Item(models.Model):
    LABELS = (
        ('BestSeller', 'BestSeller'),
        ('New', 'New'),
        ('Spicy🔥', 'Spicy🔥'),
    )

    CATEGORY = (
        ('Special', 'Special'),
        ('Juice', 'Juice'),
        ('Shake', 'Shake'),
        ('Snack', 'Snack'),
    )
    STATUS = (
        ('Available','Available'),
        ('Not available','Not available')
    )

    title = models.CharField(max_length=150)
    description = models.CharField(max_length=250, blank=True)
    price = models.FloatField()
    pieces = models.IntegerField(default=6)
    category = models.CharField(max_length=25, choices=CATEGORY, blank=True)
    instructions = models.CharField(max_length=250, choices=STATUS, blank=True)
    image = models.ImageField(default='default.png', upload_to='images/')
    labels = models.CharField(max_length=25, choices=LABELS, blank=True)
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
         
         return f"{self.title} (Canteen: {self.canteen})"

class Reviews(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # Rating choices from 1 to 5
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=100, blank=True)  # Optional review title
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=1)
    review = models.TextField()
    posted_on = models.DateField(default=timezone.now)
    # updated_on = models.DateField(auto_now=True)  # Auto-update on review edits

    def __str__(self):
        return f"Review by {self.user.name} for {self.item.title} ({self.rating} stars)"



class CartItem(models.Model):
    ORDER_STATUS = (
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Delivered', 'Delivered'),
    )
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="cart_items")
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    ordered_date = models.DateTimeField(default=timezone.now)  # Set only when ordered
    delivery_date = models.DateTimeField(null=True, blank=True)  # Tracks delivery time
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Preparing')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    payment = models.ForeignKey('Payment', null=True, blank=True, on_delete=models.SET_NULL)  # New field
    def subtotal(self):
        return self.quantity * self.item.price
    def save(self, *args, **kwargs):
        """Automatically set ordered_date when the order is placed."""
        if self.ordered and not self.ordered_date:
            self.ordered_date = now()  # Fetch current system time
        
        if self.status == 'Delivered' and not self.delivery_date:
            self.delivery_date = now()  # Set delivery time when delivered

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.item.title} for {self.user.name} ({self.status})"

    # @property
    # def subtotal(self):
    #     return self.quantity * self.item.price

    # def __str__(self):
    #     return f"{self.quantity} x {self.item.title} for {self.user.name} ({self.status})"

    # def get_remove_from_cart_url(self):
    #     return reverse("remove-from-cart", kwargs={'pk': self.pk})

    # def get_update_status_url(self):
    #     return reverse("update_status", kwargs={'pk': self.pk})
import time
import uuid

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Cash', 'Cash on Delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure precision
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)  
    receipt_number = models.CharField(max_length=20, unique=True, blank=True, null=True)  # For manual reference
    cart_items = models.ManyToManyField('CartItem', related_name="paid_payments")  # Only stores paid items

    def __str__(self):
        return f"Payment {self.id} - ₹{self.amount} by {self.user.name} ({self.payment_status})"

    def save(self, *args, **kwargs):
        """Generate unique receipt number and transaction ID if not set"""
        if not self.receipt_number:
            self.receipt_number = f"PAY-{self.user.id}-{int(time.time())}"
        
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)

