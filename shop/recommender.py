import numpy as np
from shop.models import ReviewRating
from scipy.sparse.linalg import svds
from sklearn.metrics import mean_squared_error
import math

# Extraire les Données de ShopReviewRating
def get_user_item_matrix():
    ratings = ReviewRating.objects.all()
    users = ratings.values_list('user_id', flat=True).distinct()
    items = ratings.values_list('product_id', flat=True).distinct()

    user_index = {user_id: idx for idx, user_id in enumerate(users)}
    item_index = {product_id: idx for idx, product_id in enumerate(items)}

    n_users = len(users)
    n_items = len(items)
    user_item_matrix = np.zeros((n_users, n_items))

    # Remplir la matrice utilisateur-article avec les notes
    for rating in ratings:
        u = user_index[rating.user_id]
        i = item_index[rating.product_id]
        user_item_matrix[u][i] = rating.rating

    return user_item_matrix, user_index, item_index

# Appliquer le Filtrage Collaboratif
def collaborative_filtering(user_item_matrix, k=20):
    print("Shape of user_item_matrix:", user_item_matrix.shape)

    if user_item_matrix.size == 0:
        raise ValueError("La matrice utilisateur-article est vide. Impossible de calculer SVD.")

    # Calculer la décomposition SVD
    u, s, vt = svds(user_item_matrix, k=k)
    s_diag_matrix = np.diag(s)
    x_pred = np.dot(np.dot(u, s_diag_matrix), vt)

    # Normalisation
    normalized_x_pred = normalize_predictions(x_pred)

    return normalized_x_pred

def normalize_predictions(x_pred, min_val=0, max_val=5):
    # Normaliser les prédictions pour qu'elles soient dans la plage spécifiée
    return np.clip((x_pred - x_pred.min()) * (max_val - min_val) / (x_pred.max() - x_pred.min()), min_val, max_val)

# Définir la Fonction d’Évaluation RMSE
def rmse(predictions, actuals):
    # Vérifier si il y a des valeurs valides
    if np.count_nonzero(actuals) == 0:
        return float('inf')  # Ou une autre valeur appropriée pour indiquer l'erreur

    # Calculer RMSE
    return np.sqrt(mean_squared_error(actuals[actuals > 0], predictions[actuals > 0]))

def calculate_occurrence_percentage(user_item_matrix):
    total_ratings = np.count_nonzero(user_item_matrix)
    total_possible_ratings = user_item_matrix.size
    return (total_ratings / total_possible_ratings) * 100

def train_and_evaluate():
    user_item_matrix, user_index, item_index = get_user_item_matrix()

    # Diviser en train et test (par exemple, 80% train, 20% test)
    mask = np.random.rand(*user_item_matrix.shape) < 0.8
    train_data = user_item_matrix * mask
    test_data = user_item_matrix * (~mask)

    print("Train Data Shape:", train_data.shape)  # Debugging

    # Vérifier la forme de train_data pour ajuster k
    min_dimension = min(train_data.shape)

    # Ajuster k
    k = min(20, min_dimension - 1)  # k doit être strictement inférieur à la dimension minimale
    if k <= 0:
        raise ValueError("La valeur de k doit être positive et inférieure à la dimension de la matrice utilisateur-article.")

    # Calculer le pourcentage d'occurrence
    occurrence_percentage = calculate_occurrence_percentage(train_data)
    print(f"Pourcentage d'occurrence des évaluations : {occurrence_percentage:.2f}%")

    # Exécuter le filtrage collaboratif
    predictions = collaborative_filtering(train_data, k=k)

    # Calculer RMSE pour les données d'entraînement et de test
    train_rmse = rmse(predictions, train_data)
    test_rmse = rmse(predictions, test_data)

    print("Train RMSE:", train_rmse)
    print("Test RMSE:", test_rmse)

    return predictions, train_rmse, test_rmse

# Lancer le modèle
if __name__ == "__main__":
    train_and_evaluate()
