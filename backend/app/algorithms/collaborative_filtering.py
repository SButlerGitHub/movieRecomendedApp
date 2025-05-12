import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFiltering:
    def __init__(self, ratings_data):
        self.ratings_df = pd.DataFrame(ratings_data)
        self.user_item_matrix = None
        self.similarity_matrix = None
        
    def build_matrix(self):
        # Create user-item matrix
        self.user_item_matrix = self.ratings_df.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )
        
        # Create similarity matrix
        matrix_sparse = csr_matrix(self.user_item_matrix.values)
        self.similarity_matrix = cosine_similarity(matrix_sparse)
        
    def get_recommendations(self, user_id, n_recommendations=10):
        if user_id not in self.user_item_matrix.index:
            return []
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = self.similarity_matrix[user_idx]
        
        # Get weighted average ratings
        recommendations = {}
        for movie_id in self.user_item_matrix.columns:
            if self.user_item_matrix.loc[user_id, movie_id] == 0:
                weighted_sum = 0
                similarity_sum = 0
                
                for similar_user_idx, similarity in enumerate(similar_users):
                    if similarity > 0:
                        rating = self.user_item_matrix.iloc[similar_user_idx][movie_id]
                        if rating > 0:
                            weighted_sum += similarity * rating
                            similarity_sum += similarity
                
                if similarity_sum > 0:
                    recommendations[movie_id] = weighted_sum / similarity_sum
        
        # Sort and return top N
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [(movie_id, score) for movie_id, score in sorted_recommendations[:n_recommendations]]

