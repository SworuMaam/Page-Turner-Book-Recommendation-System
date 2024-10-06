from django.test import TestCase
from django.contrib.auth.models import User
from book.models import UserProfile

class UserProfileTest(TestCase):
    def test_user_profile_creation(self):
        # Create a new user
        new_user = User.objects.create_user(username='testuser', password='password123')

        # Check if the profile is created
        new_profile = UserProfile.objects.get(user=new_user)
        self.assertEqual(new_profile.user.username, 'testuser')

