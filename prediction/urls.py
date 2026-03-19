
from django.urls import path
from .download_report import download_report   # ✅ CORRECT
from .views import  extract_features, final_result, prediction_view, accuracy_view, analysis_view
app_name = "prediction"

urlpatterns = [
   path("predict/", prediction_view, name="predict"),
     path("extract-features/", extract_features, name="extract_features"),
    path("final-result/", final_result, name="final_result"), 
    path("analysis/", analysis_view, name="analysis"),
    # path("training/", training_view, name="training"),
    path("accuracy/", accuracy_view, name="accuracy"),
    # path("download-report/",download_report, name="download_report"),
     path("download-report/", download_report, name="download_report"), 
]

