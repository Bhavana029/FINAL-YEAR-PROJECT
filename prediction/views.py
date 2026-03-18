from django.shortcuts import render
from .ml.train import train_model
from .forms import PredictionForm
import random
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings

from .ml.preprocess import preprocess_image
from .ml.feature_extraction import extract_fundus_features, extract_sclera_features
from .ml.predict import predict_blood_group

import os
import json
import pandas as pd
import time   # 🔥 IMPORTANT (added)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from datetime import datetime
import cloudinary.uploader
import urllib.request
import tempfile

# ===============================
# TRAINING VIEW
# ===============================
def training_view(request):
    status = None
    accuracy = None
    show_graphs = False

    media_path = os.path.join(settings.BASE_DIR, "media", "training")

    def get_latest(prefix):
        files = [f for f in os.listdir(media_path) if f.startswith(prefix)]
        if not files:
            return ""
        latest = max(files, key=lambda x: os.path.getctime(os.path.join(media_path, x)))
        return "/media/training/" + latest

    if request.method == "POST":
        accuracy = train_model()
        status = "Training completed successfully"
        show_graphs = True

    return render(request, "training.html", {
        "status": status,
        "accuracy": accuracy,
        "show_graphs": show_graphs,
        "accuracy_plot": get_latest("accuracy_curve"),
        "loss_plot": get_latest("loss_curve"),
        "class_plot": get_latest("class_accuracy"),
    })


# ===============================
# PREDICTION PAGE
# ===============================
def prediction_view(request):
    return render(request, "prediction.html")


# ===============================
# FEATURE EXTRACTION
# ===============================
# def extract_features(request):
#     if request.method == "POST":

#         fundus = request.FILES["fundus"]
#         sclera = request.FILES["sclera"]

#         # ✅ Upload to Cloudinary
#         fundus_upload = cloudinary.uploader.upload(fundus)
#         sclera_upload = cloudinary.uploader.upload(sclera)

#         fundus_url = fundus_upload["secure_url"]
#         sclera_url = sclera_upload["secure_url"]

#         # ✅ Download temporarily for OpenCV
#         def download_image(url):
#             temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
#             urllib.request.urlretrieve(url, temp_file.name)
#             return temp_file.name

#         fundus_path = download_image(fundus_url)
#         sclera_path = download_image(sclera_url)

#         # ✅ Preprocess
#         fundus_img = preprocess_image(fundus_path)
#         sclera_img = preprocess_image(sclera_path)

#         # ✅ Extract features
#         fundus_features = extract_fundus_features(fundus_img)
#         sclera_features = extract_sclera_features(sclera_img)

#         # ✅ Save in session
#         request.session["fundus_path"] = fundus_url
#         request.session["sclera_path"] = sclera_url

#         return JsonResponse({
#             "fundus_features": fundus_features,
#             "sclera_features": sclera_features
#         })

# ===============================
# FEATURE EXTRACTION — FIXED
# In your views.py, replace your extract_features function with this:
# ===============================
def extract_features(request):
    if request.method == "POST":

        fundus = request.FILES["fundus"]
        sclera = request.FILES["sclera"]

        # Upload to Cloudinary
        fundus_upload = cloudinary.uploader.upload(fundus)
        sclera_upload = cloudinary.uploader.upload(sclera)

        fundus_url = fundus_upload["secure_url"]
        sclera_url = sclera_upload["secure_url"]

        # Download temporarily for OpenCV processing
        def download_image(url):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            urllib.request.urlretrieve(url, temp_file.name)
            return temp_file.name

        fundus_path = download_image(fundus_url)
        sclera_path = download_image(sclera_url)

        # Preprocess + extract features
        fundus_img = preprocess_image(fundus_path)
        sclera_img = preprocess_image(sclera_path)
        fundus_features = extract_fundus_features(fundus_img)
        sclera_features = extract_sclera_features(sclera_img)

        # ✅ CRITICAL FIX: save Cloudinary URLs in session
        # download_report re-downloads from these URLs — temp paths will be gone by then
        request.session["fundus_url"]  = fundus_url   # ← THIS WAS MISSING
        request.session["sclera_url"]  = sclera_url   # ← THIS WAS MISSING
        # request.session["fundus_path"] = fundus_path
        # request.session["sclera_path"] = sclera_path

        return JsonResponse({
            "fundus_features": fundus_features,
            "sclera_features": sclera_features,
        })
# ===============================
# PREDICT
# ===============================
def predict_view(request):
    fundus_url = request.session.get("fundus_path")
    sclera_url = request.session.get("sclera_path")

    result = predict_blood_group(fundus_url, sclera_url)
    return JsonResponse(result)


# ===============================
# FINAL RESULT
# ===============================
def final_result(request):
    fundus_url = request.session.get("fundus_path")
    sclera_url = request.session.get("sclera_path")

    if not fundus_url or not sclera_url:
        return JsonResponse({"error": "Please extract features first"}, status=400)

    result = predict_blood_group(fundus_url, sclera_url)

    return JsonResponse({
        "predicted_group": result["predicted_group"],
        "confidence": result["confidence"],
        "all_probabilities": result["all_probabilities"]
    })


# ===============================
# ACCURACY VIEW (🔥 FIXED)
# ===============================
# def accuracy_view(request):

#     media_path = os.path.join(settings.BASE_DIR, "media", "training")

#     # 🔥 function to get latest file
#     def get_latest(prefix):
#         files = [f for f in os.listdir(media_path) if f.startswith(prefix)]
#         if not files:
#             return ""
#         latest = max(files, key=lambda x: os.path.getctime(os.path.join(media_path, x)))
#         return settings.MEDIA_URL + "training/" + latest

#     # Load metrics
#     metrics_path = os.path.join(media_path, "metrics.json")

#     overall_accuracy = 0
#     final_loss = 0

#     if os.path.exists(metrics_path):
#         with open(metrics_path, "r") as f:
#             metrics = json.load(f)
#             overall_accuracy = metrics.get("overall_accuracy", 0)
#             final_loss = metrics.get("final_loss", 0)

#     context = {
#         "overall_accuracy": overall_accuracy,
#         "final_loss": final_loss,

#         # 🔥 DYNAMIC IMAGES
#         "accuracy_curve": get_latest("accuracy_curve"),
#         "loss_curve": get_latest("loss_curve"),
#         "class_accuracy": get_latest("class_accuracy"),
#     }

#     return render(request, "accuracy.html", context)
# ================================================================
# In views.py — replace accuracy_view with this
# ================================================================
def accuracy_view(request):
    import json, os
    from django.conf import settings

    media_path   = os.path.join(settings.BASE_DIR, "media", "training")
    metrics_path = os.path.join(media_path, "metrics.json")

    overall_accuracy = 0
    final_loss       = 0
    accuracy_curve   = ""
    loss_curve       = ""
    class_accuracy   = ""

    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            metrics = json.load(f)

        overall_accuracy = metrics.get("overall_accuracy", 0)
        final_loss       = metrics.get("final_loss", 0)

        # ✅ FIX: read Cloudinary URLs directly from metrics.json
        # train.py saves secure_url here — no need to scan local files
        accuracy_curve = metrics.get("accuracy_curve", "")
        loss_curve     = metrics.get("loss_curve", "")
        class_accuracy = metrics.get("class_accuracy", "")

    context = {
        "overall_accuracy": overall_accuracy,
        "final_loss":       final_loss,
        "accuracy_curve":   accuracy_curve,   # https://res.cloudinary.com/...
        "loss_curve":       loss_curve,        # https://res.cloudinary.com/...
        "class_accuracy":   class_accuracy,    # https://res.cloudinary.com/...
    }

    return render(request, "accuracy.html", context)
# ===============================
# ANALYSIS VIEW
# ===============================
def analysis_view(request):
    import os, json
    from django.conf import settings

    # Path to analysis.json (saved during training)
    data_path = os.path.join(settings.BASE_DIR, "prediction", "ml", "analysis.json")

    # If file missing
    if not os.path.exists(data_path):
        return JsonResponse({
            "error": "Analysis data not available. Please train the model first."
        }, status=500)

    # Load JSON
    with open(data_path, "r") as f:
        data = json.load(f)

    # Send to template
    context = {
        "labels": json.dumps(data["labels"]),
        "vessel_redness": json.dumps(data["vessel_redness"]),
        "avr": json.dumps(data["avr"]),
        "tortuosity": json.dumps(data["tortuosity"]),
        "distribution_labels": json.dumps(data["distribution_labels"]),
        "distribution_values": json.dumps(data["distribution_values"]),
    }

    return render(request, "analysis.html", context)