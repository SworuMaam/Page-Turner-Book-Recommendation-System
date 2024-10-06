# import pandas as pd
# import numpy as np
# from book.models import Review, Book, User
# from django.db.models import Avg

# def get_user_book_matrix():
#     reviews = Review.objects.all().values('user_id', 'book_id', 'rating')
#     df = pd.DataFrame(list(reviews))
#     user_book_matrix = df.pivot(index='user_id', columns='book_id', values='rating')
#     return user_book_matrix

# def calculate_similarity(user_book_matrix):
#     similarity_matrix = user_book_matrix.corr(method='pearson').fillna(0)
#     return similarity_matrix

# def get_recommendations(user_id, num_recommendations=5):
#     user_book_matrix = get_user_book_matrix()
#     similarity_matrix = calculate_similarity(user_book_matrix)
    
#     user_ratings = user_book_matrix.loc[user_id].dropna()
#     similar_users = similarity_matrix[user_id].drop(user_id).dropna()
#     weighted_ratings = user_ratings.dot(similar_users) / similar_users.sum()
    
#     unrated_books = user_book_matrix.loc[user_id][user_book_matrix.loc[user_id].isna()].index
#     recommendations = weighted_ratings[unrated_books].sort_values(ascending=False).head(num_recommendations)
    
#     recommended_books = [Book.objects.get(id=book_id) for book_id in recommendations.index]
#     return recommended_books

# if __name__ == "__main__":
#     user_id = 1  # Example user ID
#     recommendations = get_recommendations(user_id)
#     for book in recommendations:
#         print(book.title)
