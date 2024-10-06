from django.shortcuts import render,redirect, get_object_or_404
from .models import Book, Review, Purchase
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import UserProfile

def home(request):
    # Get all popular books
    popular_books = Book.objects.all()
    
    # Get recommendations if the user is authenticated
    recommendations = get_recommendations(request.user) if request.user.is_authenticated else Book.objects.none()
    
    # Prepare context
    context = {
        'popular_books': popular_books,
        'recommendations': recommendations,
        # other context variables can be added here
    }
    
    # Render the home template with the context
    return render(request, 'book/home.html', context)

def about(request):
    return render(request, "book/about.html", {})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')  # Redirect to the login page after registration
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'book/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            # Ensure the user has a profile (use get_or_create to avoid errors)
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Check if the user's favorite genre and author are set
            if not profile.favorite_genre or not profile.favorite_author:
                # Redirect to the page where the user provides favorite genre and author
                return redirect('ask_favorites')

            # If the user has set both the favorite genre and author, redirect to home
            return redirect('home')
        else:
            # Display an error message if authentication fails
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    # Render the login page for GET request
    return render(request, 'book/login.html')
    


def logout_view(request):
    logout(request)
    messages.success(request, 'Log Out successful! .')
    return redirect('home')



def add_review(request, id):
    book = get_object_or_404(Book, id=id)
    has_reviewed = Review.objects.filter(book=book, user=request.user).exists() if request.user.is_authenticated else False

    if request.method == 'POST':
        if request.user.is_authenticated:
            rating = request.POST.get('rating', '')
            comment = request.POST.get('comment', '')  # Comment can be optional

            # If the user has not reviewed this book yet
            if not has_reviewed:
                # Create the review only if rating is provided
                if rating:
                    # Ensure the rating is a valid number
                    if rating.isdigit():
                        rating = int(rating)
                    else:
                        rating = 0  # Default to 0 if rating is not a valid number
                    # Create the review
                    review = Review(book=book, user=request.user, rating=rating, comment=comment)
                    review.save()
                # Redirect to book details regardless of whether a comment was provided
                return redirect('book_details', id=book.id)
            else:
                # User has already reviewed the book
                return redirect('book_details', id=book.id)
        else:
            return redirect('login')

    return render(request, 'book/add_review.html', {'book': book, 'has_reviewed': has_reviewed})


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Check if the current user is the owner of the review
    if review.user != request.user:
        return redirect('some_error_page')  # Redirect or show an error if necessary
    
    if request.method == 'POST':
        # Update review fields directly from POST data
        rating = request.POST.get('rating', None)  # Use None as default if not provided
        comment = request.POST.get('comment', None)

        # Update only if rating and/or comment are provided
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
            
        review.save()
        return redirect('book_details', id=review.book.id)
    
    else:
        # For GET requests, pass the review data to the template
        context = {
            'review': review,
        }
        return render(request, 'book/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check if the current user is the owner of the review
    if review.user != request.user:
        return redirect('some_error_page')  # Redirect or show an error if necessary
    
    if request.method == 'POST':
        review.delete()
        return redirect('book_details', id=review.book.id)
    
    # Optionally render a confirmation page for GET requests
    return render(request, 'book/delete_review.html', {'review': review})

# views.py
def search_books(request):
    query = request.GET.get('query', '')
    print(f"Search query: {query}")  # Debug line
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        )
    else:
        books = Book.objects.all()
    
    print(f"Number of books found: {books.count()}")  # Debug line

    context = {
        'books': books,
        'search_query': query,
    }
    return render(request, 'book/search_results.html', context)

def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    reviews = Review.objects.filter(book=book)
    has_reviewed = reviews.filter(user=request.user).exists() if request.user.is_authenticated else False
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user)
    else:
        recommendations = None
    return render(request, 'book/book_detail.html', {'book': book, 'reviews': reviews, 'has_reviewed': has_reviewed, 'recommendations': recommendations})

def genre_search(request, genre):
    # Query books based on the genre
    books = Book.objects.filter(genre__icontains=genre)
    
    # Pass the books and search query to the template
    context = {
        'search_query': genre,
        'books': books
    }
    
    return render(request, 'book/genreSearch.html', context)

def buy_book(request, id):
    book = get_object_or_404(Book, id=id)
    
    if request.method == 'POST':
        # Example purchase logic: Create a Purchase record
        purchase = Purchase(user=request.user, book=book)
        purchase.save()
        
        # Redirect to a success page or the book details page
        # return redirect('purchase_success', id=book.id)
        messages.success(request, 'Purchase sucessfull! .')
        return redirect('home')
    elif request.method == 'GET':
        return render(request, 'book/buy.html', {'book': book})


@login_required
def favorite_books(request):
    # Get the books that the user has added to their favorites
    favorite_books = Book.objects.filter(favorites=request.user)
    
    context = {
        'favorite_books': favorite_books,
    }
    
    return render(request, 'book/favorite_books.html', context)

def add_favorite(request, id):
    book = get_object_or_404(Book, id=id)
    book.favorites.add(request.user)
    messages.success(request, 'Book added to favorites!')
    return redirect('home')  # Redirect to the book detail page

def remove_favorite(request, id):
    book = get_object_or_404(Book, id=id)
    book.favorites.remove(request.user)
    messages.success(request, 'Book removed from favorites!')
    return redirect('home' )
    
@login_required
def ask_favorites(request):
    if request.method == 'POST':
        favorite_genre = request.POST.get('favorite_genre')
        favorite_author = request.POST.get('favorite_author')

        # Ensure the user has a UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.favorite_genre = favorite_genre
        profile.favorite_author = favorite_author
        profile.save()

        return redirect('home')

    # Get all unique genres and authors from books for the dropdown
    genres = Book.objects.values_list('genre', flat=True).distinct()
    authors = Book.objects.values_list('author', flat=True).distinct()

    return render(request, 'book/ask_favorites.html', {'genres': genres, 'authors': authors})

def get_recommendations(user):
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Book.objects.none()  # Return empty if no profile exists

    user_reviews = Review.objects.filter(user=user)
    reviewed_books_ids = set(user_reviews.values_list('book_id', flat=True))

    favorite_books = Book.objects.filter(favorites=user)
    favorite_books_ids = set(favorite_books.values_list('id', flat=True))

    favorite_genres = favorite_books.values_list('genre', flat=True)
    favorite_authors = favorite_books.values_list('author', flat=True)

    # Collaborative filtering: Find books based on similar users
    similar_user_reviews = Review.objects.filter(
        Q(book_id__in=reviewed_books_ids) | Q(book_id__in=favorite_books_ids)
    ).exclude(user=user)

    recommended_books_ids = set()
    for review in similar_user_reviews:
        other_user_reviews = Review.objects.filter(
            user=review.user
        ).exclude(Q(book_id__in=reviewed_books_ids) | Q(book_id__in=favorite_books_ids))
        
        for other_review in other_user_reviews:
            recommended_books_ids.add(other_review.book_id)

    # Content-based filtering: Recommend books of the same genre and author as favorites
    same_genre_author_books = Book.objects.filter(
        Q(genre__in=favorite_genres) | Q(author__in=favorite_authors)
    ).exclude(Q(id__in=reviewed_books_ids) | Q(id__in=favorite_books_ids))

    # Add the profile's favorite genre and author
    recommended_books = Book.objects.filter(
        Q(id__in=recommended_books_ids) |  # Based on similar users
        Q(genre=profile.favorite_genre) |  # Favorite genre from profile
        Q(author=profile.favorite_author)  # Favorite author from profile
    ).exclude(Q(id__in=reviewed_books_ids) | Q(id__in=favorite_books_ids))

    # Combine the two querysets (collaborative + content-based)
    recommended_books = recommended_books | same_genre_author_books

    return recommended_books

def create_new_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Creating a new user
        new_user = User.objects.create_user(username=username, password=password)

        # Check if the profile is created
        new_profile = UserProfile.objects.get(user=new_user)
        print(new_profile)  # Should print the username of the new user

        return redirect('home')  # Redirect after creation

    return render(request, 'create_user.html')

@login_required
def user_profile(request):
    # Get the logged-in user's profile
    profile = UserProfile.objects.get(user=request.user)
    
    # Get the list of books reviewed by the user
    reviews = Review.objects.filter(user=request.user)

    context = {
        'profile': profile,
        'reviews': reviews
    }

    return render(request, 'book/user_profile.html', context)

def some_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    # Your logic here...
