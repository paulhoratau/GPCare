from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth import get_user_model

from rest_framework import serializers, generics, permissions, status, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, Review, Appointment, Prescription
from .serializers import PasswordChangeSerializer, UserSerializer, DoctorSerializer, ReviewSerializer, AppointmentSerializer, PrescriptionSerializer

UserModel = get_user_model()



class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class ProfileView(RetrieveUpdateAPIView):
   model = UserModel
   queryset = UserModel.objects.all()
   serializer_class = UserSerializer
   permission_classes = [IsAuthenticated]

   def get_object(self):
        return self.request.user

class PasswordChangeView(UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=400)


        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password has been changed."})


class DoctorCreateAccount(generics.CreateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = DoctorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DoctorRegisterView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'pk'


class ReviewList(generics.ListCreateAPIView):  # View for listing and creating comments.
    queryset = Review.objects.all()  # Define the queryset to be all comments.
    serializer_class = ReviewSerializer  # Define the serializer class to be used.

    def perform_create(self, serializer):  # Override the default create behavior.
        serializer.save(owner=self.request.user)  # Set the owner of the comment to the current logged-in user.


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):  # View for retrieving, updating, and deleting a specific comment.
    queryset = Review.objects.all()  # Define the queryset to be all comments.
    serializer_class = ReviewSerializer  # Define the serializer class to be used.


class DoctorReviews(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = 'pk'


class AppointmentView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'


class DoctorAppointments(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'



class PrescriptionList(generics.ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def perform_create(self, serializer):
        user = self.request.user
        try:
            doctor = Doctor.objects.get(user=user)
            serializer.save(doctor=doctor)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("The logged-in user is not associated with any doctor.")

from .permissions import IsOwnerOrReadOnly

class PatientPrescription(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Prescription.objects.filter(patient=self.request.user)
