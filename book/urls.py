from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from . import views
from django.urls import path, include

urlpatterns = [
    # Home and About
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    

    # Search
    path('search/', views.search_books, name='search_books'),

    # Authentication
    path('SignIn/register/', views.register, name='register'),
    path('SignIn/login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Book Details and Reviews
    
    path('book/<int:id>/book_detail', views.book_detail, name='book_details'),
    path('book/<int:id>/add_review/', views.add_review, name='add_review'),
    # path('review/<int:review_id>/edit_review/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/edit_review/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('book/buy/<int:id>/', views.buy_book, name='buy_book'),

    # Genre Search
    path('genre/<str:genre>/', views.genre_search, name='genre_search'),
    
    path('book/<int:id>/', views.book_detail, name='book_detail'), 
    path('favorites/', views.favorite_books, name='favorite_books'),
    path('book/<int:id>/add_favorite/', views.add_favorite, name='add_favorite'),
    path('book/<int:id>/remove_favorite/', views.remove_favorite, name='remove_favorite'),
    path('ask_favorites/', views.ask_favorites, name='ask_favorites'),
    
    path('profile/', views.user_profile, name='user_profile'),
    
#     path('book/', include('book.urls')),
 ]

    
    # path('recommendations/', views.recommendations, name='recommendations'),

    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)