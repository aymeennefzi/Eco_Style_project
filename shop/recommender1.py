import numpy as np
import pandas as pd
import sqlite3  # ou import mysql.connector si vous utilisez MySQL
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import mean_squared_error
from math import sqrt

# Connexion à la base de données
conn = sqlite3.connect('C:\\Users\\OMGBoomRito1\\Desktop\\E-Commerce\\db.sqlite3')

# Extraction des données de la table shop_reviewrating
query = "SELECT user_id, product_id, rating FROM shop_reviewrating"
data = pd.read_sql(query, conn)

# Fermez la connexion à la base de données
conn.close()

# Diviser les données en train et test (par exemple, 80% pour train et 20% pour test)
train_data = data.sample(frac=0.8, random_state=42)  # 80% pour l'entraînement
test_data = data.drop(train_data.index)  # 20% pour le test

# Mapping des user_id et product_id à des indices continus
user_ids = data['user_id'].unique()
product_ids = data['product_id'].unique()

# Création de dictionnaires pour mapper les IDs aux indices
user_id_to_index = {user_id: index for index, user_id in enumerate(user_ids)}
product_id_to_index = {product_id: index for index, product_id in enumerate(product_ids)}

# Création de la matrice d'entraînement
train_data_matrix = np.zeros((len(user_ids), len(product_ids)))
for line in train_data.itertuples(index=False):
    train_index = user_id_to_index[line.user_id]
    product_index = product_id_to_index[line.product_id]
    train_data_matrix[train_index, product_index] = line.rating

# Création de la matrice de test
test_data_matrix = np.zeros((len(user_ids), len(product_ids)))
for line in test_data.itertuples(index=False):
    test_index = user_id_to_index[line.user_id]
    product_index = product_id_to_index[line.product_id]
    test_data_matrix[test_index, product_index] = line.rating

# Calcul de la similarité cosinus
user_similarity_cosine = pairwise_distances(train_data_matrix, metric='cosine')
item_similarity_cosine = pairwise_distances(train_data_matrix.T, metric='cosine')

# Calcul de la similarité de Manhattan (cityblock)
user_similarity_cityblock = pairwise_distances(train_data_matrix, metric='cityblock')
item_similarity_cityblock = pairwise_distances(train_data_matrix.T, metric='cityblock')

def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])

    # Normalisation des prédictions
    x = np.zeros((len(user_ids), len(product_ids)))
    for i in range(len(product_ids)):
        a = max(pred[:, i])
        b = min(pred[:, i])
        c = 0
        d = 5
        for j in range(len(user_ids)):
            x[j, i] = (pred[j, i] - (a - c)) * d / (b - a + c)

    return x

# Prédictions avec différents modèles
item_prediction_cosine = predict(test_data_matrix, item_similarity_cosine, type='item')
user_prediction_cosine = predict(test_data_matrix, user_similarity_cosine, type='user')
item_prediction_cityblock = predict(test_data_matrix, item_similarity_cityblock, type='item')
user_prediction_cityblock = predict(test_data_matrix, user_similarity_cityblock, type='user')

# Fonction pour calculer le RMSE
def rmse(prediction, ground_truth):
    prediction = prediction[ground_truth.nonzero()].flatten()
    ground_truth = ground_truth[ground_truth.nonzero()].flatten()
    return sqrt(mean_squared_error(prediction, ground_truth))

# Affichage des RMSE
print(f'User-based CF: The RMSE for the cosine similarity metric is: {rmse(user_prediction_cosine, test_data_matrix)}')
print(f'Item-based CF: The RMSE for the cosine similarity metric is: {rmse(item_prediction_cosine, test_data_matrix)}')
print(f'User-based CF: The RMSE for the cityblock similarity metric is: {rmse(user_prediction_cityblock, test_data_matrix)}')
print(f'Item-based CF: The RMSE for the cityblock similarity metric is: {rmse(item_prediction_cityblock, test_data_matrix)}')
