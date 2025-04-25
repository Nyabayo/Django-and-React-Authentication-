import os
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin  # RBAC: Custom permission for admin-only access

User = get_user_model()


@api_view(['POST'])
def send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

        # Get or create device without setting 'key'
        device, created = EmailDevice.objects.get_or_create(
            user=user,
            name='default',
            defaults={'confirmed': True}
        )

        # Manually set key if missing (required for challenge to work)
        if not hasattr(device, 'key') or not device.bin_key:
            # Accessing private _key field through bin_key (safe workaround)
            device._key = os.urandom(20)  # ⚠️ Accessing protected member
            device.save()

        # Generate and send the OTP
        device.generate_challenge()

        return Response({'detail': 'OTP sent to your email'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'Internal error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'detail': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        device = EmailDevice.objects.get(user=user, name='default', confirmed=True)

        if device.verify_token(otp):
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'detail': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except EmailDevice.DoesNotExist:
        return Response({'detail': 'OTP device not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'Internal error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================
# ✅ RBAC: Admin Role Management
# ==============================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])  # RBAC: Restrict to admin only
def change_user_role(request, user_id):
    """
    Admin-only endpoint to change another user's role.
    This helps enforce RBAC by letting admins manage user access.
    Example PATCH request body:
    {
        "role": "owner"
    }
    """
    try:
        user = User.objects.get(id=user_id)
        new_role = request.data.get('role')

        # Check if role is valid (from User.Role choices)
        if new_role not in dict(User.Role.choices):
            return Response({'detail': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        # Apply the new role and save
        user.role = new_role
        user.save()

        return Response({'detail': f'Role successfully updated to {new_role}'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
