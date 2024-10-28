import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
from PIL import Image
import logging
from django.contrib import messages
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

class ClothingClassifier:
    """Service class for classifying recycled clothing items"""
    
    def __init__(self):
        try:
            self.model = MobileNetV2(weights='imagenet')
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger.error(f"Error initializing classifier: {str(e)}")
            raise
            
        self.clothing_categories = {
            'tops': ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket', 'hoodie'],
            'bottoms': ['pants', 'jeans', 'shorts', 'skirt', 'trousers'],
            'dresses': ['dress', 'gown'],
            'outerwear': ['coat', 'blazer', 'windbreaker'],
            'other': ['clothing', 'apparel', 'textile']
        }

    def analyze_image(self, image_path):
        """Analyze a single image and return classification results"""
        try:
            # Load and preprocess image
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Prepare image for model
            img_array = image.img_to_array(img.resize((224, 224)))
            x = np.expand_dims(img_array, axis=0)
            x = preprocess_input(x)
            
            # Get model predictions
            predictions = self.model.predict(x)
            decoded_predictions = decode_predictions(predictions, top=5)[0]
            
            # Analyze image quality for condition assessment
            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Determine condition based on image quality
            if blur_score > 100:
                condition = 'good'
            elif blur_score > 50:
                condition = 'fair'
            else:
                condition = 'poor'
                
            # Find matching clothing category
            item_type = 'other'
            confidence = 0.0
            
            for _, label, pred_conf in decoded_predictions:
                label = label.lower()
                for category, keywords in self.clothing_categories.items():
                    if any(keyword in label for keyword in keywords):
                        item_type = category
                        confidence = float(pred_conf)
                        break
                if item_type != 'other':
                    break
                    
            return {
                'item_type': item_type,
                'confidence': confidence,
                'condition': condition,
                'top_predictions': [
                    {'label': label, 'confidence': float(conf)}
                    for _, label, conf in decoded_predictions
                ]
            }
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            return None

    def generate_admin_analytics(self, recycled_items_model):
        """
        Generate analytics charts for recycled clothing items
        
        Args:
            recycled_items_model: Django model class for recycled items
            
        Returns:
            dict: Dictionary containing base64 encoded chart images and statistics
        """
        try:
            # Get current date for time-based filtering
            today = timezone.now()
            thirty_days_ago = today - timedelta(days=30)
            
            # Get status distribution
            status_counts = (recycled_items_model.objects
                .values('status')
                .annotate(count=Count('id'))
                .order_by('-count'))

            # Get drop point distribution
            drop_point_counts = (recycled_items_model.objects
                .values('drop_point__name')
                .annotate(count=Count('id'))
                .order_by('-count'))

            # Get user contribution distribution (top 10)
            user_counts = (recycled_items_model.objects
                .values('user__email')
                .annotate(count=Count('id'))
                .order_by('-count')[:10])
            
            # Get daily items received (last 30 days)
            daily_items = (recycled_items_model.objects
                .filter(created_at__gte=thirty_days_ago)
                .extra({'date': "date(created_at)"})
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date'))

            predicted_categories = []
            for item in recycled_items_model.objects.all():
                if item.image:
                    try:
                        prediction = self.analyze_image(item.image.path)
                        if prediction:
                            predicted_categories.append(prediction['item_type'])
                    except Exception as e:
                        self.logger.error(f"Error analyzing image for item {item.id}: {str(e)}")

            category_counts = {}
            for category in predicted_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            # Generate charts
            charts = {}

            plt.figure(figsize=(10, 6))
            categories = list(category_counts.keys())
            counts = list(category_counts.values())

            sorted_indices = np.argsort(counts)[::-1]
            categories = [categories[i] for i in sorted_indices]
            counts = [counts[i] for i in sorted_indices]

            colors = plt.cm.Pastel1(np.linspace(0, 1, len(categories)))
            plt.bar(categories, counts, color=colors)
            plt.title('Distribution of Predicted Item Categories')
            plt.xlabel('Category')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            charts['predicted_categories'] = base64.b64encode(buffer.getvalue()).decode()

            # Status Distribution Pie Chart
            plt.figure(figsize=(10, 6))
            plt.pie([c['count'] for c in status_counts],
                   labels=[c['status'] for c in status_counts],
                   autopct='%1.1f%%')
            plt.title('Distribution of Items by Status')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            charts['status_distribution'] = base64.b64encode(buffer.getvalue()).decode()
            
            # Drop Point Distribution Bar Chart
            plt.figure(figsize=(12, 6))
            drop_points = [c['drop_point__name'] for c in drop_point_counts]
            counts = [c['count'] for c in drop_point_counts]
            plt.bar(drop_points, counts)
            plt.title('Items Received by Drop Point')
            plt.xlabel('Drop Point')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            charts['drop_point_distribution'] = base64.b64encode(buffer.getvalue()).decode()
            
            # Daily Items Line Chart
            plt.figure(figsize=(12, 6))
            dates = [item['date'] for item in daily_items]
            counts = [item['count'] for item in daily_items]
            plt.plot(dates, counts)
            plt.title('Daily Recycled Items (Last 30 Days)')
            plt.xlabel('Date')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            charts['daily_trend'] = base64.b64encode(buffer.getvalue()).decode()

            # Top Contributors Bar Chart
            plt.figure(figsize=(12, 6))
            users = [c['user__email'] for c in user_counts]
            counts = [c['count'] for c in user_counts]
            plt.bar(users, counts)
            plt.title('Top 10 Contributors')
            plt.xlabel('User Email')
            plt.ylabel('Number of Items')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            charts['top_contributors'] = base64.b64encode(buffer.getvalue()).decode()
            
            # Add category statistics
            total_items = sum(c['count'] for c in status_counts)
            pending_items = next((c['count'] for c in status_counts if c['status'] == 'pending'), 0)
            confirmed_items = next((c['count'] for c in status_counts if c['status'] == 'confirmed'), 0)
            declined_items = next((c['count'] for c in status_counts if c['status'] == 'declined'), 0)
            items_last_30_days = sum(c['count'] for c in daily_items)
            top_drop_point = drop_point_counts[0]['drop_point__name'] if drop_point_counts else 'N/A'
            top_contributor = user_counts[0]['user__email'] if user_counts else 'N/A'

            most_common_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'N/A'
            
            # Calculate summary statistics
            total_items = sum(c['count'] for c in status_counts)
            pending_items = next((c['count'] for c in status_counts if c['status'] == 'pending'), 0)
            confirmed_items = next((c['count'] for c in status_counts if c['status'] == 'confirmed'), 0)
            declined_items = next((c['count'] for c in status_counts if c['status'] == 'declined'), 0)
            items_last_30_days = sum(c['count'] for c in daily_items)
            top_drop_point = drop_point_counts[0]['drop_point__name'] if drop_point_counts else 'N/A'
            top_contributor = user_counts[0]['user__email'] if user_counts else 'N/A'
            
            
            return {
                'charts': charts,
                'statistics': {
                    'total_items': total_items,
                    'pending_items': pending_items,
                    'confirmed_items': confirmed_items,
                    'declined_items': declined_items,
                    'items_last_30_days': items_last_30_days,
                    'top_drop_point': top_drop_point,
                    'top_contributor': top_contributor,
                    'most_common_category': most_common_category,
                    'category_distribution': [
                        {'category': cat, 'count': count}
                        for cat, count in category_counts.items()
                    ],
                    'status_distribution': list(status_counts),
                    'drop_point_distribution': list(drop_point_counts),
                    'top_contributors': list(user_counts)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating admin analytics: {str(e)}")
            return None