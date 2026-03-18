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
        request.session["fundus_path"] = fundus_path
        request.session["sclera_path"] = sclera_path

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

    dataset_path = os.path.join(
        settings.BASE_DIR,
        "dataset",
        "BloodEye_Balanced_2400_Rows.csv"
    )

    df = pd.read_csv(dataset_path)

    numeric_cols = ["vessel_red", "AVR", "tortuosity"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols)

    order = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
    df["blood_group"] = pd.Categorical(
        df["blood_group"],
        categories=order,
        ordered=True
    )

    grouped = df.groupby("blood_group", observed=True)

    labels = grouped.mean(numeric_only=True).index.tolist()
    vessel_redness = grouped["vessel_red"].mean().round(2).tolist()
    avr = grouped["AVR"].mean().round(3).tolist()
    tortuosity = grouped["tortuosity"].mean().round(3).tolist()

    distribution = df["blood_group"].value_counts().sort_index()

    context = {
        "labels": json.dumps(labels),
        "vessel_redness": json.dumps(vessel_redness),
        "avr": json.dumps(avr),
        "tortuosity": json.dumps(tortuosity),
        "distribution_labels": json.dumps(distribution.index.tolist()),
        "distribution_values": json.dumps(distribution.tolist()),
    }

    return render(request, "analysis.html", context)


# def download_report(request):
#     try:
#         fundus_path = request.session.get("fundus_path")
#         sclera_path = request.session.get("sclera_path")

#         if not fundus_path or not sclera_path:
#             return HttpResponse("No data available")

#         result = predict_blood_group(fundus_path, sclera_path)

#         # 🔥 GET FEATURES AGAIN
#         fundus_img = preprocess_image(fundus_path)
#         sclera_img = preprocess_image(sclera_path)

#         fundus_features = extract_fundus_features(fundus_img)
#         sclera_features = extract_sclera_features(sclera_img)

#         # 🔥 USER DETAILS
#         user = request.user.username
#         email = request.user.email
#         now = datetime.now().strftime("%d-%m-%Y %H:%M")

#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="blood_report.pdf"'

#         doc = SimpleDocTemplate(response)
#         styles = getSampleStyleSheet()
#         elements = []

#         # ===============================
#         # HEADER
#         # ===============================
#         elements.append(Paragraph("🩸 BloodEye - Blood Group Prediction Report", styles['Title']))
#         elements.append(Spacer(1, 15))

#         # USER INFO
#         elements.append(Paragraph(f"<b>User:</b> {user}", styles['Normal']))
#         elements.append(Paragraph(f"<b>Email:</b> {email}", styles['Normal']))
#         elements.append(Paragraph(f"<b>Generated At:</b> {now}", styles['Normal']))
#         elements.append(Spacer(1, 20))

#         # ===============================
#         # RESULT
#         # ===============================
#         elements.append(Paragraph("Prediction Result", styles['Heading2']))
#         elements.append(Paragraph(f"Blood Group: {result['predicted_group']}", styles['Normal']))
#         elements.append(Paragraph(f"Confidence: {round(result['confidence'],2)}%", styles['Normal']))
#         elements.append(Spacer(1, 20))

#         # ===============================
#         # FUNDUS FEATURES
#         # ===============================
#         elements.append(Paragraph("Fundus Features", styles['Heading2']))

#         for k, v in fundus_features.items():
#             elements.append(Paragraph(f"{k} : {round(v,4)}", styles['Normal']))

#         elements.append(Spacer(1, 20))

#         # ===============================
#         # SCLERA FEATURES
#         # ===============================
#         elements.append(Paragraph("Sclera Features", styles['Heading2']))

#         for k, v in sclera_features.items():
#             elements.append(Paragraph(f"{k} : {round(v,4)}", styles['Normal']))

#         elements.append(Spacer(1, 20))

#         # ===============================
#         # IMAGES
#         # ===============================
#         if os.path.exists(fundus_path):
#             elements.append(Paragraph("Fundus Image", styles['Heading3']))
#             elements.append(Image(fundus_path, width=250, height=180))

#         if os.path.exists(sclera_path):
#             elements.append(Paragraph("Sclera Image", styles['Heading3']))
#             elements.append(Image(sclera_path, width=250, height=180))

#         elements.append(Spacer(1, 20))

#         # ===============================
#         # PROBABILITIES
#         # ===============================
#         elements.append(Paragraph("All Probabilities", styles['Heading2']))

#         for k, v in result["all_probabilities"].items():
#             elements.append(Paragraph(f"{k} : {round(v,2)}", styles['Normal']))

#         elements.append(Spacer(1, 30))

#         # ===============================
#         # FOOTER
#         # ===============================
#         elements.append(Paragraph("-----", styles['Normal']))
#         elements.append(Paragraph("Generated by BloodEye AI System", styles['Italic']))

#         doc.build(elements)

#         return response

#     except Exception as e:
#         print("ERROR:", e)
#         return HttpResponse(f"Error generating PDF: {str(e)}")