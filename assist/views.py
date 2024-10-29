import subprocess
from django.http import JsonResponse

# Global variable to track process state
process_running = False

def voice_bot_view(request):
    global process_running

    if request.method == "GET":
        if not process_running:
            try:
                process_running = True
                # Start the subprocess
                subprocess.Popen(['python', 'assist/assistant.py'])
                return JsonResponse({'status': 'success', 'message': 'Voice bot started'})
            except Exception as e:
                process_running = False
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Voice bot is already running'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})