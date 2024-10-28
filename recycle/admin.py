from django.contrib import admin
from .models import DropPoint, RecycledItem
import admin_thumbnails
from .services.classifier import ClothingClassifier
from django.contrib import messages
from django.http import HttpResponse

@admin.register(DropPoint)
class DropPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'description']

@admin.register(RecycledItem)
class RecycledItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'drop_point', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'drop_point']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['name', 'user__username']
    actions = ['analyze_with_ai','generate_analytics_report']

    def analyze_with_ai(self, request, queryset):
        """Analyze selected items with AI"""
        classifier = ClothingClassifier()
        analyzed_count = 0
        
        for item in queryset:
            if not item.image:
                messages.warning(request, f"Item '{item.name}' has no image")
                continue
                
            try:
                result = classifier.analyze_image(item.image.path)
                if result:
                   
                    
                    messages.info(
                        request,
                        f"Item '{item.name}': "
                        f"Condition: {result['condition']}, "
                        f"Confidence: {result['confidence']:.1%} "
                    )
                    analyzed_count += 1
                    
            except Exception as e:
                messages.error(
                    request,
                    f"Error analyzing '{item.name}': {str(e)}"
                )
        
        messages.success(
            request,
            f"Successfully analyzed {analyzed_count} items"
        )
    
    analyze_with_ai.short_description = "Analyze selected items with AI"
    def generate_analytics_report(self, request, queryset):
        try:
            classifier = ClothingClassifier()
            analytics = classifier.generate_admin_analytics(self.model)
            
            if analytics:
                # Convert charts to HTML img tags
                chart_html = f"""
                    <h2>Recycled Items Analytics</h2>
                    
                    <h3>Summary Statistics</h3>
                    <ul>
                        <li>Total Items: {analytics['statistics']['total_items']}</li>
                        <li>Pending Items: {analytics['statistics']['pending_items']}</li>
                        <li>Confirmed Items: {analytics['statistics']['confirmed_items']}</li>
                        <li>Declined Items: {analytics['statistics']['declined_items']}</li>
                        <li>Items in Last 30 Days: {analytics['statistics']['items_last_30_days']}</li>
                        <li>Most Active Drop Point: {analytics['statistics']['top_drop_point']}</li>
                        <li>Top Contributor: {analytics['statistics']['top_contributor']}</li>
                        <li>Most Common Category: {analytics['statistics']['most_common_category']}</li>
                    </ul>
                    
                    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                        <div style="flex: 1; min-width: 300px;">
                            <h3>Status Distribution</h3>
                            <img src="data:image/png;base64,{analytics['charts']['status_distribution']}" 
                                 style="max-width: 100%;">
                        </div>
                        
                        <div style="flex: 1; min-width: 300px;">
                            <h3>Drop Point Distribution</h3>
                            <img src="data:image/png;base64,{analytics['charts']['drop_point_distribution']}"
                                 style="max-width: 100%;">
                        </div>
                        
                        <div style="flex: 1; min-width: 300px;">
                            <h3>Daily Trend</h3>
                            <img src="data:image/png;base64,{analytics['charts']['daily_trend']}"
                                 style="max-width: 100%;">
                        </div>
                        
                        <div style="flex: 1; min-width: 300px;">
                            <h3>Top Contributors</h3>
                            <img src="data:image/png;base64,{analytics['charts']['top_contributors']}"
                                 style="max-width: 100%;">
                        </div>
                        <div style="flex: 1; min-width: 300px;">
                        <h3>Predicted Categories Distribution</h3>
                        <img src="data:image/png;base64,{analytics['charts']['predicted_categories']}"
                             style="max-width: 100%;">
                    </div>
                    </div>
                """
                
                response = HttpResponse(content_type='text/html')
                response.write(f"""
                    <html>
                        <head>
                            <title>Recycled Items Analytics</title>
                            <style>
                                body {{ padding: 20px; font-family: Arial, sans-serif; }}
                                img {{ border: 1px solid #ddd; border-radius: 4px; padding: 5px; }}
                            </style>
                        </head>
                        <body>
                            {chart_html}
                            <br>
                            <a href="../" style="display: inline-block; margin-top: 20px; 
                                padding: 10px 20px; background-color: #447e9b; color: white; 
                                text-decoration: none; border-radius: 4px;">
                                Back to Admin
                            </a>
                        </body>
                    </html>
                """)
                return response
            else:
                self.message_user(request, "Error generating analytics")
                
        except Exception as e:
            self.message_user(request, f"Error generating analytics: {str(e)}")
    
    generate_analytics_report.short_description = "Generate Analytics Report"

