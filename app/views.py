from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth import get_user_model

from rest_framework import serializers, generics, permissions, status, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import AdminOnlyPermission, IsOwnerOrReadOnly, IsAdminOrReadOnly
from .models import Doctor, Review, Appointment, Prescription
from .serializers import (
    PasswordChangeSerializer,
    UserSerializer,
    DoctorSerializer,
    ReviewSerializer,
    AppointmentSerializer,
    PrescriptionSerializer
)

UserModel = get_user_model()

# If there are any views or additional logic to be added, it can go below this line



class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class ProfileView(RetrieveUpdateAPIView):
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




class DoctorRegisterView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, AdminOnlyPermission]

    def create(self, request, *args, **kwargs):
        # Check if the username already exists
        username = request.data.get('username')
        if UserModel.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



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
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):  # Override the default create behavior.
        serializer.save(owner=self.request.user)  # Set the owner of the comment to the current logged-in user.


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):  # View for retrieving, updating, and deleting a specific comment.
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()  # Define the queryset to be all comments.
    serializer_class = ReviewSerializer  # Define the serializer class to be used.


class DoctorReviews(generics.ListAPIView):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        doctor_pk = self.kwargs['pk']
        queryset = Review.objects.filter(doctor_id=doctor_pk)
        return queryset


class AppointmentView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)



class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Save appointment details before deletion for notification
        deleted_date = instance.date
        deleted_start_time = instance.start_time
        deleted_doctor = instance.doctor

        # Perform the delete operation
        self.perform_destroy(instance)

        # Return a custom response indicating successful deletion and message
        return Response(
            {'message': f'Your appointment on {deleted_date} at {deleted_start_time} with {deleted_doctor} has been deleted.'},
            status=status.HTTP_200_OK
        )



class DoctorAppointments(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        doctor_pk = self.kwargs['pk']
        queryset = Appointment.objects.filter(doctor_id=doctor_pk)
        return queryset



class PrescriptionList(generics.ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        user = self.request.user
        try:
            doctor = Doctor.objects.get(user=user)
            serializer.save(doctor=doctor)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("The logged-in user is not associated with any doctor.")


class PatientPrescription(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Prescription.objects.filter(patient=self.request.user)
