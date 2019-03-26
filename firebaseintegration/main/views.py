from django.shortcuts import render
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from pyrebase import pyrebase

from main.firebaseconfig import __config
from main.forms import fileForm


def index(request):
    upload2(request)
    return render(request, 'index.html')


def upload(request):
    if request.method == 'POST':
        form = fileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["File"]
            print(file.size)
            firebase = pyrebase.initialize_app(__config)
            storage = firebase.storage()
            storage.child("capsula1/" + file.name).put(file)
            print("VALID")
        print("POST")
    else:
        form = fileForm()
        print("GET")
    return render(request,'upload.html', {'form': form})


def upload2(request):
    credentials_dict = {
    }

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict
    )
    client = storage.Client(credentials=credentials, project='djangostorage')
    bucket = client.get_bucket('djangostorage-97bad.appspot.com')
    blob = bucket.blob('pruebanueva.png')
    blob.upload_from_filename('s.png')





