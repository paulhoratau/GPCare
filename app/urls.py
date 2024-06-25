from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('auth/register/', views.CreateUserView.as_view(), name='register'),
    path('auth/register/doctor/', views.DoctorRegisterView.as_view(), name='doctor-register'),
    path('auth/login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),


    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/password/', views.PasswordChangeView.as_view()),



    path('doctors/', views.DoctorListView.as_view(), name='doctor-list'),
    path('doctor/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor-detail'),


    path('post/review/', views.ReviewList.as_view(), name='review-list-create'),  # URL for listing and creating comments.
    path('review/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),  # URL for retrieving, updating, and deleting a comment by its primary key (pk).
    path('doctor/<int:pk>/reviews/', views.DoctorReviews.as_view()),

    path('appointment/', views.AppointmentView.as_view()),
    path('appointment/<int:pk>', views.AppointmentDetailView.as_view()),
    path('doctor/<int:pk>/appointment/', views.DoctorAppointments.as_view()),

    path('prescription/', views.PrescriptionList.as_view()),


]
