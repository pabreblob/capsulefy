from django.shortcuts import render_to_response

def handler404(request, exception):
    response = render_to_response("errors/404.html")
    response.status_code = 404
    return response