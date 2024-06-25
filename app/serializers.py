from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Doctor, Review, Appointment, Prescription
from .validators import validate_time_overlap

UserModel = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = UserModel
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)




class DoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'specialization', 'hospital', 'phone_number']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['password'] = validated_data.pop('password')
        user = UserModel.objects.create_user(**user_data)
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor



class ReviewSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')  # The username of the owner, read-only.

    class Meta:
        model = Review  # The model to serialize.
        fields = '__all__'  # Serialize all fields of the Comment model.


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment  # The model to serialize.
        fields = ['created', 'date','start_time','end_time', 'doctor']

    def validate(self, data):
        validate_time_overlap(data['date'], data['start_time'], data['end_time'], self.instance)
        return data



class PrescriptionSerializer(serializers.ModelSerializer):
    doctor = serializers.ReadOnlyField(source='doctor.username')  # The username of the owner, read-only.

    class Meta:
        model = Prescription  # The model to serialize.
        fields = '__all__'  # Serialize all fields of the Comment model.

