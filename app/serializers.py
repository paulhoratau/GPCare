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
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'required': False},  # Password is only required on create
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
        model = Review
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=False)
    start_time = serializers.TimeField(required=False)
    end_time = serializers.TimeField(required=False)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), required=False)

    class Meta:
        model = Appointment
        fields = ['created', 'date', 'start_time', 'end_time', 'doctor']

    def validate(self, data):
        # Ensure to validate against instance values for partial updates
        date = data.get('date', self.instance.date if self.instance else None)
        start_time = data.get('start_time', self.instance.start_time if self.instance else None)
        end_time = data.get('end_time', self.instance.end_time if self.instance else None)
        validate_time_overlap(date, start_time, end_time, self.instance)
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class PrescriptionSerializer(serializers.ModelSerializer):
    doctor = serializers.ReadOnlyField(source='doctor.username')

    class Meta:
        model = Prescription
        fields = '__all__'
