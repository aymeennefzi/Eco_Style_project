# shop/recommended.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import mean_squared_error
from math import sqrt
from shop.models import ReviewRating

def load_data():
    reviews = ReviewRating.objects.values('user_id', 'product_id', 'rating')
    df = pd.DataFrame(list(reviews))
    return df

def recommend():
    # Charger les données
    tab = load_data()
    
    useri, frequsers = np.unique(tab['user_id'], return_counts=True)
    itemi, freqitems = np.unique(tab['product_id'], return_counts=True)
    n_users = len(useri)
    n_items = len(itemi)

    print("le nombre des utilisateurs est :"+ str(n_users) + " Et le nombre des items est: "+ str(n_items))

    indice_user = pd.DataFrame({'indice': range(1, n_users + 1), 'useri': useri})
    indice_item = pd.DataFrame({'indice': range(1, n_items + 1), 'itemi': itemi})

    x = []
    y = []
    for i in range(len(tab)):
        x.append((indice_user[indice_user.useri == tab['user_id'].iloc[i]]['indice'].values[0]))
        y.append((indice_item[indice_item.itemi == tab['product_id'].iloc[i]]['indice'].values[0]))

    tab['userIdnew'] = x
    tab['movieIdnew'] = y

    train_data, test_data = train_test_split(tab[["userIdnew", "movieIdnew", "rating"]], test_size=0.25, random_state=123)
    sparsity = round(1.0 - len(tab) / float(n_users * n_items), 3)
    print('The sparsity level of our database is ' + str(sparsity * 100) + '%')
    
    train_data_matrix = np.zeros((n_users, n_items))
    for line in train_data.itertuples():
        train_data_matrix[line[1] - 1, line[2] - 1] = line[3]

    test_data_matrix = np.zeros((n_users, n_items))
    for line in test_data.itertuples():
        test_data_matrix[line[1] - 1, line[2] - 1] = line[3]

    user_similarity = pairwise_distances(train_data_matrix, metric='cosine')
    item_similarity = pairwise_distances(train_data_matrix.T, metric='cosine')

    def predict(ratings, similarity, type='user'):
        if type == 'user':
            mean_user_rating = ratings.mean(axis=1)
            ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
            pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
        elif type == 'item':
            pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
        
        x = np.zeros((n_users, n_items))
        for i in range(n_items):
            a, b = pred[:, i].max(), pred[:, i].min()
            for j in range(n_users):
                x[j, i] = (pred[:, i][j] - (a - 0)) * 5 / (b - a + 0)
        
        return x

    item_prediction = predict(test_data_matrix, item_similarity, type='item')
    user_prediction = predict(test_data_matrix, user_similarity, type='user')

    def rmse(prediction, ground_truth):
        prediction = prediction[ground_truth.nonzero()].flatten()
        ground_truth = ground_truth[ground_truth.nonzero()].flatten()
        return sqrt(mean_squared_error(prediction, ground_truth))

    results = {
        'user_based_cf_rmse_cosine': rmse(user_prediction, test_data_matrix),
        'item_based_cf_rmse_cosine': rmse(item_prediction, test_data_matrix),
    }

    return results
