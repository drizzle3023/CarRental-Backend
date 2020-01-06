from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import QueryDict
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from datetime import datetime, time
from django.utils.timezone import make_aware
from copy import deepcopy
from django.db.models import Q, Count

from .models import User
from .models import Company
from .models import Coverage
from .models import Payment
from .models import History
from .models import CarType
from .models import Claim
from .models import FileUploadTest

# For parsing request from android app
from .app_serializers import SignUpSerializer
from .app_serializers import SignInSerializer
from .app_serializers import SignVerifySerializer
from .app_serializers import AddCoverageSerializer
from .app_serializers import AddClaimSerializer
from .app_serializers import AddPaymentSerializer

# For managing db
from .serializers import UserEntrySerializer
from .serializers import FileUploadTestSerializer

import json
import requests
import Adyen
import logging
import ast
import geopy.distance

##########################################################################   Login APIs   #######################################################################

# SignUp #
class SignUpView(APIView):

    def post(self, request):
        signup_serializer = SignUpSerializer(data=request.data)
        if (signup_serializer.is_valid()):

            # Receive mobile, name from app
            mobile = signup_serializer.data.get("mobile")
            email = signup_serializer.data.get("email")
            name = signup_serializer.data.get("name")
            car_type_id = signup_serializer.data.get("car_type_id")
            world_zone = signup_serializer.data.get("world_zone")

            if mobile == None:
                message = "required_mobile"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)
            if email == None:
                message = "required_email"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)
            if name == None:
                message = "required_name"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)
            if car_type_id == None:
                message = "required_car_type"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)
            if world_zone == None:
                message = "required_world_zone"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)

            # Send request signin to the SDK server
            request_data = signup_serializer.data
            # Global Constants -> this url. ??
            response = requests.post('https://api.platform.integrations.muzzley.com/v3/applications/6eb9d03d-33da-4bcc-9722-611bb9c9fec2/user-sms-entry', data = request_data)
            jsonResponse = json.loads(response.content)

            # Check if jsonResponse has success value.
            if status.is_success(response.status_code) == False:
                if jsonResponse.get("code") == 21211:
                    message = "invalid_mobile"
                else:
                    message = "Authentication server error"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)

            # Check if there's the mobile number alreday in DB.
            existed_user = User.objects.filter(mobile = mobile).first()

            if existed_user != None:
                # existed_user.user_id = jsonResponse.get("id")
                # existed_user.name = jsonResponse.get("name")
                # existed_user.mobile = jsonResponse.get("mobile")
                # existed_user.namespace = jsonResponse.get("namespace")
                # existed_user.confirmation_hash = jsonResponse.get("confirmation_hash")
                # existed_user.target_id = jsonResponse.get("target_id")
                # existed_user.href = jsonResponse.get("href")
                # existed_user.type = jsonResponse.get("type")
                # existed_user.created_at = jsonResponse.get("created")
                # existed_user.updated_at = jsonResponse.get("updated")
                # existed_user.save()
                response_data = {"success": "false", "data": {"message": "Your phone number is registered already."}}
                return Response(response_data, status = status.HTTP_200_OK)
            else:
                email_object = {'email': email}
                car_type_id_object = {'car_type_id': car_type_id}
                world_zone_object = {'world_zone': world_zone}

                jsonResponse.update(email_object)
                jsonResponse.update(car_type_id_object)
                jsonResponse.update(world_zone_object)

                user_entry_serializer = UserEntrySerializer(data = jsonResponse)

                if user_entry_serializer.is_valid():
                    user_entry_serializer.create(jsonResponse)
                    response_data = {"success": "true", "data": {"message": "Login request succeeded."}}
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {"message": "There's a problem with saving your information."}}
                    return Response(response_data, status=status.HTTP_200_OK)

        response_data = {"success": "false", "data":{"message": "There's a problem with receiving your information."}}
        return Response(response_data, status=status.HTTP_200_OK)

# SignIn #
class SignInView(APIView):

    def post(self, request):
        signin_serializer = SignInSerializer(data=request.data)
        if (signin_serializer.is_valid()):

            # Receive mobile, name from app
            mobile = signin_serializer.data.get("mobile")

            if mobile == None:
                message = "required_mobile"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)

            # Send request signin to the SDK server
            request_data = signin_serializer.data
            # Global Constants -> this url. ??
            response = requests.post('https://api.platform.integrations.muzzley.com/v3/applications/6eb9d03d-33da-4bcc-9722-611bb9c9fec2/user-sms-entry', data = request_data)
            jsonResponse = json.loads(response.content)

            # Check if jsonResponse has success value.
            if status.is_success(response.status_code) == False:
                if jsonResponse.get("code") == 21211:
                    message = "invalid_mobile"
                else:
                    message = "authentication server error"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)

            # Check if there's the mobile number alreday in DB.
            existed_user = User.objects.filter(mobile = mobile).first()

            if existed_user != None:
                existed_user.user_id = jsonResponse.get("id")
                existed_user.name = jsonResponse.get("name")
                existed_user.mobile = jsonResponse.get("mobile")
                existed_user.namespace = jsonResponse.get("namespace")
                existed_user.confirmation_hash = jsonResponse.get("confirmation_hash")
                existed_user.target_id = jsonResponse.get("target_id")
                existed_user.href = jsonResponse.get("href")
                existed_user.type = jsonResponse.get("type")
                existed_user.created_at = jsonResponse.get("created")
                existed_user.updated_at = jsonResponse.get("updated")
                existed_user.save()
                response_data = {"success": "true", "data": {"message": "Login request succeeded."}}
                return Response(response_data, status = status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "Your phone number isn't registered."}}
                return Response(response_data, status=status.HTTP_200_OK)

        response_data = {"success": "false", "data":{"message": "There's a problem with receiving your information."}}
        return Response(response_data, status=status.HTTP_200_OK)

# Sign Verify #
class SignVerifyView(APIView):

    def post(self, request):
        signverify_serializer = SignVerifySerializer(data = request.data)
        if (signverify_serializer.is_valid()):
            mobile = signverify_serializer.data.get("mobile")
            code = signverify_serializer.data.get("code")

            if mobile == None:
                message = "required_mobile"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)

            if code == None:
                message = "required_code"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_200_OK)

            # Check if there's the mobile number alreday in DB.
            existed_user = User.objects.filter(mobile = mobile).first()

            if existed_user != None:
                user_id = existed_user.user_id
                confirmation_hash = existed_user.confirmation_hash
                request_data = {'confirmation_hash': confirmation_hash, 'code': code}
                headers = {'Content-Type': 'application/json'}
                # request_verify_serializer = RequestVerifySerializer()
                # request_verify_serializer.confirmation_hash = confirmation_hash
                # request_verify_serializer.code = code

                url = 'https://api.platform.integrations.muzzley.com/v3/users/' + user_id + '/sms-verify'

                response = requests.post(
                    'https://api.platform.integrations.muzzley.com/v3/users/' + user_id + '/sms-verify',
                    data = json.dumps(request_data), headers = headers)

                if status.is_success(response.status_code) == False:

                    jsonResponse = json.loads(response.content)
                    response_data = {"success": "false", "data": {"message": jsonResponse}}
                    return Response(response_data, status = status.HTTP_200_OK)
                else:

                    if response.status_code == status.HTTP_200_OK:

                        jsonResponse = json.loads(response.content)
                        # Parse endpoints, scope
                        endpoints = jsonResponse.get("endpoints")
                        scope = jsonResponse.get("scope")

                        existed_user.access_token = jsonResponse.get("access_token")
                        existed_user.client_id = jsonResponse.get("client_id")
                        existed_user.code = jsonResponse.get("code")
                        existed_user.expires_at = jsonResponse.get("expires")
                        existed_user.grant_type = jsonResponse.get("grant_type")
                        existed_user.href = jsonResponse.get("href")
                        existed_user.user_id = jsonResponse.get("id")
                        existed_user.owner_id = jsonResponse.get("owner_id")
                        existed_user.refresh_token = jsonResponse.get("refresh_token")
                        existed_user.endpoints_http = endpoints.get("http")
                        existed_user.endpoints_mqtt = endpoints.get("mqtt")
                        existed_user.endpoints_uploader = endpoints.get("uploader")
                        existed_user.scope_1 = scope[0]
                        existed_user.scope_2 = scope[1]
                        existed_user.created_at = jsonResponse.get("created")
                        existed_user.updated_at = jsonResponse.get("updated")

                        existed_user.save()

                        response_data = {"success": "true", "data": {
                            "message": "Sms verification succeeded.",
                            "access_token": jsonResponse.get("access_token")}}
                        return Response(response_data, status = status.HTTP_200_OK)
                    else:
                        response_data = {"success": "false", "data": {
                            "message": "Content error from server."}}
                        return Response(response_data, status = status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "Your phone number isn't registered."}}
                return Response(response_data, status=status.HTTP_200_OK)

# Get payment methods #
class GetPaymentMethodsView(APIView):

    def post(self, request):

        access_token = request.data.get("access_token")
        car_type_id = request.data.get("car_type_id")

        # Check if there's the mobile number alreday in DB.
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            car_type = CarType.objects.filter(id = car_type_id).first()
            amount = car_type.price_per_year
            currency = car_type.currency

            # _mutable = request.data._mutable
            # request_data = request.data
            # request_data._mutable = True
            # request_data['user_id'] = existed_user.id
            # request_data['state'] = 1
            # request_data._mutable = _mutable

            request_data = deepcopy(request.data)
            request_data['user_id'] = existed_user.id
            request_data['amount'] = amount
            request_data['currency'] = currency
            request_data['state'] = 1

            adyen = Adyen.Adyen(
                app_name = "CarRental",
                xapikey = "AQEqhmfuXNWTK0Qc+iSYk2Yxs8WYS4RYA4cYCzCc8PvE9PEKkua51zO8HkygEMFdWw2+5HzctViMSCJMYAc=-VnikbEENHj+JVke2cIJHsXNIaUsYWftXVA7MqLsE280=-w69eUf3zT5jJ9zZm",
                platform = "test"
            )

            result = adyen.checkout.payment_methods({
                'merchantAccount': 'HabitAccount235ECOM',
                'channel': 'Android'
            })

            if result.status_code == 200:

                add_payment_serializer = AddPaymentSerializer(data=request_data)
                if (add_payment_serializer.is_valid()):

                    obj = add_payment_serializer.save();

                    response_data = {"success": "true", "data": {
                        "message": "Getting payment methods succeeded.",
                        "paymentMethods": result.message,
                        "payment_id": obj.id}}
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {"message": add_payment_serializer.errors}}
                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "Getting payment methods failed."}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Pay #
class PaymentView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        payment_id = request.data.get("payment_id")
        payment_component_data = request.data.get("paymentComponentData")

        payment_method = payment_component_data.get("paymentMethod")

        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            payment = Payment.objects.filter(id = payment_id).first()

            if payment != None:

                adyen = Adyen.Adyen(
                    app_name="CarRental",
                    xapikey="AQEqhmfuXNWTK0Qc+iSYk2Yxs8WYS4RYA4cYCzCc8PvE9PEKkua51zO8HkygEMFdWw2+5HzctViMSCJMYAc=-VnikbEENHj+JVke2cIJHsXNIaUsYWftXVA7MqLsE280=-w69eUf3zT5jJ9zZm",
                    platform="test"
                )

                reference = "car_rental_payment" + str(payment_id)

                result = adyen.checkout.payments({
                    'amount':{
                        'value': payment.amount,
                        'currency': payment.currency
                    },
                    'reference': reference,
                    'paymentMethod': payment_method,
                    'merchantAccount': 'HabitAccount235ECOM',
                    'channel': 'Android',
                    'returnUrl': 'https://your-company.com/checkout?shopperOrder=12xy'
                })

                if result.status_code == 200:

                    if 'action' in result.message:

                        payment = Payment.objects.filter(id = payment_id).first()
                        payment.state = 2
                        payment.save()

                        response_data = {"success": "true", "data": {
                            "action": result.message['action'],
                            "message": "More action needed."}}
                    elif result.message['resultCode'] == 'Authorised' :

                        payment = Payment.objects.filter(id = payment_id).first()
                        payment.state = 7
                        payment.save()

                        response_data = {"success": "true", "data": {
                            "message": "Payment succeeded.",
                            "resultCode": result.message['resultCode']}}

                    elif result.message['resultCode'] == 'Pending':

                        payment = Payment.objects.filter(id=payment_id).first()
                        payment.state = 6
                        payment.save()

                        response_data = {"success": "true", "data": {
                            "message": "Payment is pending.",
                            "resultCode": result.message['resultCode']}}

                    elif result.message['resultCode'] == 'Received' :

                        payment = Payment.objects.filter(id = payment_id).first()
                        payment.state = 5
                        payment.save()

                        response_data = {"success": "true", "data": {
                            "message": "Received the payment. Please wait.",
                            "resultCode": result.message['resultCode']}}
                    else :
                        if result.message['resultCode'] == 'Refused':
                            payment = Payment.objects.filter(id = payment_id).first()
                            payment.state = 4
                            payment.save()
                        else:
                            payment = Payment.objects.filter(id = payment_id).first()
                            payment.state = 3
                            payment.save()

                        response_data = {"success": "false", "data": {
                            "message": result.message['refusalReason'],
                            "resultCode": result.message['resultCode']}}

                    logger = logging.getLogger(__name__)
                    logger.error(result.message['resultCode'])

                    history_content = {}

                    history_content['id'] = payment.id
                    history_content['user_id'] = payment.user_id
                    history_content['car_type_id'] = payment.car_type_id
                    history_content['amount'] = payment.amount
                    history_content['currency'] = payment.currency
                    history_content['state'] = payment.state

                    payment_date = payment.date

                    if payment_date is None:
                        payment_date_timestamp = payment_date
                    else:
                        payment_date_timestamp = payment_date.timestamp()

                    history_content['date'] = int(payment_date_timestamp)

                    history_json_content = json.dumps(history_content)

                    history_data = History(user_id = existed_user.id, type = "Payment", content = history_json_content)
                    history_data.save()

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {
                        "message": "Payment failed."}}
                    return Response(response_data, status=status.HTTP_200_OK)

            else:
                response_data = {"success": "false", "data": {"message": "The payment information doesn't exist."}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Get user profile
class GetUserProfileView(APIView):

    def post(self, request):

        access_token = request.data.get("access_token")

        # Check if there's the mobile number alreday in DB.
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            response_data = {"success": "true", "data": {
                "message": "Succeeded.",
                "profile": {
                    "id": existed_user.id,
                    "email": existed_user.email,
                    "name": existed_user.name,
                    "mobile": existed_user.mobile
                }}}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Add coverage
class AddCoverageView(APIView):

    # parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        start_at = request.data.get("start_at")
        end_at = request.data.get("end_at")

        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            # Add user_id to the request data to save as a model field

            if start_at == None:
                start_at_datetime = start_at
            else:
                start_at_datetime = datetime.fromtimestamp(int(start_at))
                start_at_datetime = start_at_datetime.strftime("%Y-%m-%d %H:%M:%S")

            if end_at == None:
                end_at_datetime = end_at
            else:
                end_at_datetime = datetime.fromtimestamp(int(end_at))
                end_at_datetime = end_at_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # request_data = deepcopy(request.data)
            # request_data['user_id'] = existed_user.id
            # request_data['start_at'] = start_at_datetime
            # request_data['end_at'] = end_at_datetime

            add_coverage_serializer = AddCoverageSerializer(data = request.data)
            if (add_coverage_serializer.is_valid()):

                active_coverage = Coverage.objects.filter(user_id = existed_user.id).exclude(state = 3).first()

                if active_coverage != None:

                    active_coverage.latitude = add_coverage_serializer.data.get("latitude")
                    active_coverage.longitude = add_coverage_serializer.data.get("longitude")
                    active_coverage.address = add_coverage_serializer.data.get("address")
                    active_coverage.company_id = add_coverage_serializer.data.get("company_id")
                    active_coverage.starting_at = start_at_datetime
                    active_coverage.ending_at = end_at_datetime
                    active_coverage.video_mile = add_coverage_serializer.data.get("video_mile")
                    active_coverage.video_vehicle = add_coverage_serializer.data.get("video_vehicle")
                    active_coverage.state = add_coverage_serializer.data.get("state")

                    active_coverage.save()
                else :
                    obj = add_coverage_serializer.save()

                    active_coverage = Coverage.objects.filter(id = obj.id).first()

                    active_coverage.user_id = existed_user.id
                    active_coverage.starting_at = start_at_datetime
                    active_coverage.ending_at = end_at_datetime

                    active_coverage.save()

                history_content = {}

                history_content['id'] = active_coverage.id
                history_content['name'] = active_coverage.name
                history_content['user_id'] = active_coverage.user_id
                history_content['latitude'] = active_coverage.latitude
                history_content['longitude'] = active_coverage.longitude
                history_content['address'] = active_coverage.address
                history_content['company_id'] = active_coverage.company_id
                history_content['start_at'] = int(start_at)
                history_content['end_at'] = int(end_at)
                history_content['video_mile'] = str(active_coverage.video_mile)
                history_content['video_vehicle'] = str(active_coverage.video_vehicle)
                history_content['state'] = active_coverage.state
                history_content['claim_count'] = 0;

                json_content = json.dumps(history_content)


                history_data = History(user_id = existed_user.id, type = "Coverage", content = str(json_content))
                history_data.save()

                response_data = {"success": "true", "data": {"message": "Adding coverage succeeded.", "coverage_id": active_coverage.id}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": add_coverage_serializer.errors}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Get company list
class GetCarTypeListView(APIView):

    def post(self, request):

        car_type_list = CarType.objects.all()

        response_car_type_list = []

        for car_type in car_type_list:

            car_type_id = car_type.id
            car_type_name = car_type.name
            car_type_icon_url = car_type.icon_url
            car_type_price_per_year = car_type.price_per_year
            car_type_currency = car_type.currency

            record = {"id": car_type_id, "name": car_type_name, "icon_url": str(car_type_icon_url), "price_per_year": car_type_price_per_year, "currency": car_type_currency}
            response_car_type_list.append(record)

        response_data = {"success": "true", "data": {
            "message": "Getting car type list succeeded.",
            "carTypeList": response_car_type_list}}

        return Response(response_data, status=status.HTTP_200_OK)

# Get active coverage list
class GetActiveCoverageView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            coverage = Coverage.objects.filter(user_id = existed_user.id).exclude(state=3).first()

            if coverage != None:

                coverage_id = coverage.id
                coverage_name = coverage.name
                coverage_latitude = coverage.latitude
                coverage_longitude = coverage.longitude
                coverage_address = coverage.address
                coverage_company_id = coverage.company_id
                coverage_start_at = coverage.starting_at
                coverage_end_at = coverage.ending_at
                coverage_video_mile = coverage.video_mile
                coverage_video_vehicle = coverage.video_vehicle
                coverage_state = coverage.state

                # Get count of claim for this coverage
                claim_count = Claim.objects.filter(coverage_id = coverage_id).count()

                company = Company.objects.filter(id = coverage_company_id).first()

                if company != None:

                    company_id = company.id
                    company_name = company.name
                    company_latitude = company.latitude
                    company_longitude = company.longitude
                    company_address = company.address
                    company_type = company.type

                    response_company = {
                        "id": company_id,
                        "name": company_name,
                        "latitude": company_latitude,
                        "longitude": company_longitude,
                        "address": company_address,
                        "type": company_type
                    }

                    # Change the datetime field to timestamp
                    start_at = coverage_start_at
                    if start_at is None:
                        start_at_timestamp = start_at
                    else :
                        start_at_timestamp = start_at.timestamp()
                    end_at = coverage_end_at
                    if end_at is None:
                        end_at_timestamp = end_at
                    else:
                        end_at_timestamp = end_at.timestamp()

                    response_coverage = {
                        "id": coverage_id,
                        "name": coverage_name,
                        "latitude": coverage_latitude,
                        "longitude": coverage_longitude,
                        "address": coverage_address,
                        "company": response_company,
                        "start_at": int(start_at_timestamp),
                        "end_at": int(end_at_timestamp),
                        "video_mile": str(coverage_video_mile),
                        "video_vehicle": str(coverage_video_vehicle),
                        "state": coverage_state,
                        "claim_count": claim_count}

                    response_data = {"success": "true", "data": {
                        "message": "Getting active coverage succeeded.",
                        "coverage": response_coverage}}

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {"message": "The company information of the active coverage doesn't exist."}}
                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "The active coverage doesn't exist."}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Cancel coverage
class CancelCoverage(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        coverage_id = request.data.get("coverage_id")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            coverage = Coverage.objects.filter(id = coverage_id).first()

            if coverage != None:
                coverage.state = 3
                coverage.save()

                claim_count = Claim.objects.filter(coverage_id = coverage_id).count()

                history_content = {}

                history_content['id'] = coverage.id
                history_content['name'] = coverage.name
                history_content['user_id'] = coverage.user_id
                history_content['latitude'] = coverage.latitude
                history_content['longitude'] = coverage.longitude
                history_content['address'] = coverage.address
                history_content['company_id'] = coverage.company_id

                # Change the datetime field to timestamp
                start_at = coverage.starting_at
                if start_at != None:
                    history_content['start_at'] = int(start_at.timestamp())
                else:
                    history_content['start_at'] = None
                end_at = coverage.ending_at
                if end_at != None:
                    history_content['end_at'] = int(end_at.timestamp())
                else:
                    history_content['end_at'] = None
                history_content['video_mile'] = str(coverage.video_mile)
                history_content['video_vehicle'] = str(coverage.video_vehicle)
                history_content['state'] = coverage.state
                history_content['claim_count'] = claim_count;

                history_json_content = json.dumps(history_content)

                history_data = History(user_id = existed_user.id, type = "Coverage", content = history_json_content)
                history_data.save()

                response_data = {"success": "true", "data": {
                    "message": "The coverage was cancelled successfully."}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "The coverage information doesn't exist."}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Add claim
class AddClaimView(APIView):

    #parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")

        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            # Add user_id to the request data to save as a model field
            # _mutable = request.data._mutable
            # request_data = request.data
            # request_data._mutable = True
            # request_data['user_id'] = existed_user.id
            # request_data._mutable = _mutable

            add_claim_serializer = AddClaimSerializer(data = request.data)
            if (add_claim_serializer.is_valid()):

                obj = add_claim_serializer.save();

                claim = Claim.objects.filter(id = obj.id).first()

                # For saving content to history table (not date_time_happenend)
                if request.data.get("time_happened") != None:
                    time_happenend = int(request.data.get("time_happened"))
                    datetime_happened = make_aware(datetime.fromtimestamp(time_happenend))
                else:
                    datetime_happened = None

                claim.user_id = existed_user.id
                claim.date_time_happened = datetime_happened

                claim.save();

                history_content = {}

                history_content['id'] = claim.id
                history_content['name'] = claim.name
                history_content['user_id'] = claim.user_id
                history_content['latitude'] = claim.latitude
                history_content['longitude'] = claim.longitude
                history_content['address'] = claim.address
                history_content['coverage_id'] = claim.coverage_id
                if claim.time_happened != None:
                    history_content['time_happened'] = int(claim.time_happened)
                else:
                    history_content['time_happened'] = None
                history_content['damaged_part'] = claim.damaged_part
                history_content['video'] = str(claim.video)
                history_content['note'] = claim.note
                history_content['state'] = claim.state

                json_content = json.dumps(history_content)

                history_data = History(user_id = existed_user.id, type = "Claim", content = str(json_content))
                history_data.save()

                response_data = {"success": "true", "data": {"message": "Adding claim succeeded."}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": add_claim_serializer.errors}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Get claim list
class GetClaimListView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        coverage_id = request.data.get("coverage_id")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            if coverage_id != None:
                claim_list = Claim.objects.filter(user_id = existed_user.id).filter(coverage_id = coverage_id).all()

                response_claim_list = []

                for claim in claim_list:

                    record = {
                        "id" : claim.id,
                        "name" : claim.name,
                        "user_id" : claim.user_id,
                        "what_happenend" : claim.what_happened,
                        "time_happened" : claim.time_happened,
                        "latitude" : claim.latitude,
                        "longitude" : claim.longitude,
                        "address" : claim.address,
                        "damaged_part" : claim.damaged_part,
                        "video" : str(claim.video),
                        "note" : claim.note,
                        "state" : claim.state
                    }

                    response_claim_list.append(record)

                response_data = {"success": "true", "data": {
                    "message": "Getting claim list succeeded.",
                    "claimList": response_claim_list}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "The coverage id is invalid."}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)


# Remove claim
class RemoveClaimView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        claim_id = request.data.get("claim_id")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            claim = Claim.objects.filter(id = claim_id).first()

            if claim != None:
                if claim.state != 1:
                    response_data = {"success": "false", "data": {"message": "The claim can't be removed because it's state isn't incomplete."}}
                    return Response(response_data, status=status.HTTP_200_OK)

                history_content = {}

                history_content['id'] = claim.id
                history_content['name'] = claim.name
                history_content['user_id'] = claim.user_id
                history_content['latitude'] = claim.latitude
                history_content['longitude'] = claim.longitude
                history_content['address'] = claim.address
                history_content['coverage_id'] = claim.coverage_id
                if claim.time_happened != None:
                    history_content['time_happened'] = int(claim.time_happened)
                else:
                    history_content['time_happened'] = None
                history_content['damaged_part'] = claim.damaged_part
                history_content['video'] = str(claim.video)
                history_content['note'] = claim.note
                history_content['state'] = claim.state

                history_json_content = json.dumps(history_content)

                history_data = History(user_id = existed_user.id, type = "Claim", content = history_json_content)
                history_data.save()

                claim.delete()

                response_data = {"success": "true", "data": {
                    "message": "The claim was removed successfully."}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "The claim data doesn't exist."}}
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)


# Get history list (Coverage, Claim, Payment)
class GetHistoryListView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            history_list = History.objects.filter(user_id = existed_user.id).all()

            response_history_list = []

            for history in history_list:
                history_id = history.id
                history_type = history.type
                history_content = history.content

                json_content = json.loads(history_content)

                record = {"id": history_id, "type": history_type, "content": json_content}
                response_history_list.append(record)

            response_data = {"success": "true", "data": {
                "message": "Getting history list succeeded.",
                "historyList": response_history_list}}
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

# Get company list near user
class GetNearCompanyListView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            # User's position
            pos_one = (latitude, longitude)

            company_list = Company.objects.all()

            response_company_list = []

            for company in company_list:
                company_latitude = company.latitude
                company_longitude = company.longitude

                # Company's position
                pos_two = (company_latitude, company_longitude)

                # Unit: Km
                company_distance_from_user = geopy.distance.vincenty(pos_one, pos_two).kilometers
                company_id = company.id
                company_name = company.name
                company_type = company.type

                record = {"id": company_id, "name": company_name, "type": company_type, "distance": company_distance_from_user}
                response_company_list.append(record)

            response_data = {"success": "true", "data": {
                "message": "Getting company list succeeded.",
                "companyList": response_company_list}}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_200_OK)

class FileUploadTestView(APIView):

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):

        file_serializer = FileUploadTestSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_200_OK)