from django.shortcuts import render

def front_page(request):
    # Logic to fetch data for the front page
    return render(request, 'front_page.html')

def login(request):
    # Logic for handling login functionality
    return render(request, 'login.html')

