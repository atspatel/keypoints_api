from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import User, AnnonymousUserTable, UserOTPTable
from .serializers import UserBioSerializer
from utils.image_upload import upload_profile_image


import random
from datetime import datetime
import requests
import constants

MAX_OTP_ATTEMPT = 10

# TEST_USER_BLOCK
TEST_PHONE = "1357908642"
TEST_OTP = "2468"
#######


def validate_otp(phone_number, otp):
    user_otp_info = UserOTPTable.objects.filter(
        phone__iexact=phone_number).first()
    if user_otp_info:
        user_otp = str(user_otp_info.otp)
        if user_otp == str(otp):
            # TEST_USER_BLOCK
            if(phone_number != TEST_PHONE):
                #####
                user_otp_info.delete()
            user, created = User.objects.get_or_create(phone=phone_number)
            return user, created
    return None, None


class OTPRegisterOps(APIView):
    parser_classes = (MultiPartParser, JSONParser,)

    def post(self, request):
        pass

    def get(self, request, phone_number=None):
        if phone_number:
            phone_number = str(phone_number).strip()
            response = self._create_otp(phone_number)
            return Response(response)

        else:
            return Response({
                'status': False,
                'debug': "ERROR",
                'message': 'Phone number not given in request'
            })

    @staticmethod
    def _create_otp(phone_number):
        # TEST_USER_BLOCK
        if(phone_number == TEST_PHONE):
            otp = TEST_OTP
            user_info, _ = UserOTPTable.objects.update_or_create(
                phone=phone_number, defaults={"otp": otp, "count": 0})
            return {
                'status': True,
                'debug': "SUCCESS",
                'message': "OTP sent for Test User",
                'count': user_info.count
            }
        ####
        otp = create_otp()
        user_info, _ = UserOTPTable.objects.get_or_create(phone=phone_number,
                                                          defaults={"otp": otp, "count": 0})
        count = user_info.count
        time_updated = user_info.time_updated

        new_info = create_otp_for_existing(user_info.otp, count, time_updated)

        if new_info['status']:
            sent_response = send_otp_to_user(phone_number, new_info['otp'])
            if sent_response['Status'] == "Success":
                user_info.count = new_info['count']
                user_info.ref_number = sent_response['Details']
                user_info.save()
                return {
                    'status': True,
                    'debug': "SUCCESS",
                    'message': new_info['message'],
                    'count': user_info.count
                }
            else:
                return {
                    'status': False,
                    'debug': "ERROR",
                    'message': "Error in sending message"
                }
        else:
            return {
                'status': False,
                'debug': "ERROR",
                'message': new_info['message']
            }


class UserBioView(APIView):
    parser_classes = (MultiPartParser, JSONParser,)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserBioSerializer(user).data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name', None)
        age = request.data.get('age', None)
        image = request.data.get('image', None)
        if (image):
            image_object = upload_profile_image(image)
        else:
            image_object = None

        user.first_name = first_name
        user.last_name = last_name
        user.profile_pic = image_object

        user.save()

        return Response({'status': True,
                         'message': "information Added",
                         "user_name": user.name})


class LogIn(APIView):
    parser_classes = (JSONParser,)

    def get(self, request):
        ann_obj = get_ann_token(request.user)
        return Response({
            'status': True,
            'ann_token': ann_obj.id
        })

    def post(self, request):
        phone_number = request.data.get('username')
        if phone_number:
            phone_number = str(phone_number)
            password = request.data.get('password')
            user, created = validate_otp(phone_number, password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                ann_token = request.data.get('ann_token', None)
                ann_obj = link_ann_token(user, ann_token)
                if ann_obj == None:
                    ann_obj = get_ann_token(user)
                return Response({
                    'status': True,
                    'token': token.key,
                    'user_id': token.user_id,
                    'ann_token': ann_obj.id,
                    'user_name': user.name,
                    'message': 'Login Successfull'
                })
            else:
                return Response({
                    'status': False,
                    'message': 'Invalid User id OTP'
                })
        else:
            return Response({
                'status': False,
                'message': 'Phone number not given in request'
            })


class LogOut(APIView):
    parser_classes = (JSONParser,)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print("Logged Out :: ", user)
        if user.is_authenticated:
            user.auth_token.delete()
            ann_obj = get_ann_token(None)
            return Response({
                'status': True,
                'ann_token': ann_obj.id,
                'message': 'Logged Out Sucessfully'
            })
        else:
            return Response({
                'status': False,
                'message': 'Not able identify User from request'
            })


def create_otp():
    return random.randint(1000, 9999)


def create_otp_for_existing(otp,
                            count,
                            time_updated):

    if check_time_validation(time_updated):
        if count >= MAX_OTP_ATTEMPT:
            return {
                'status': False,
                'debug': "ERROR",
                'message': 'You have reached 10 attempt of the day, please try again tommorow',
            }
        else:
            return {
                'status': True,
                'debug': "SUCCESS",
                'message': 'Repassing Same OTP',
                'otp': otp,
                'count': count + 1
            }
    else:
        otp = create_otp()
        return {
            'status': True,
            'debug': "SUCCESS",
            'message': 'Repassing Same OTP',
            'otp': otp,
            'count': 1
        }


def check_time_validation(updated_time):
    time_now = datetime.now()
    diff = time_now - updated_time.replace(tzinfo=None)
    if diff.days < 1:
        return True
    else:
        return False


def send_otp_to_user(phone_number, otp):
    url = "https://2factor.in/API/V1/%s/SMS/%s/%s/Keypoints" % (
        constants.two_factor_key, phone_number, otp)
    r = requests.get(url=url)
    return r.json()
    # return {"Status": 'Success', "Details": "1"}


def link_ann_token(user, ann_token):
    ann_obj = None

    ann_obj = AnnonymousUserTable.objects.filter(post_login_id=user).first()
    if ann_obj:
        return ann_obj

    if ann_token:
        ann_obj = AnnonymousUserTable.objects.filter(id=ann_token).first()
        if ann_obj.post_login_id == None:
            ann_obj.post_login_id = user
            ann_obj.save()
        else:
            ann_obj = None
    return ann_obj


def get_ann_token(user):
    ann_obj = None
    if user and user.is_authenticated:
        ann_obj = AnnonymousUserTable.objects.filter(
            post_login_id=user).first()
        if not ann_obj:
            ann_obj = AnnonymousUserTable.objects.create(post_login_id=user)
    if not ann_obj:
        ann_obj = AnnonymousUserTable.objects.create()
    return ann_obj
