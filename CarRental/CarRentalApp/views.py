from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import QueryDict
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from datetime import datetime
from django.utils.timezone import make_aware
from copy import deepcopy

from .models import User
from .models import Company
from .models import Coverage
from .models import Payment
from .models import History

# For parsing request from android app
from .app_serializers import SignUpSerializer
from .app_serializers import SignInSerializer
from .app_serializers import SignVerifySerializer
from .app_serializers import RequestVerifySerializer
from .app_serializers import RequestPaymentSerializer
from .app_serializers import AddCoverageSerializer
from .app_serializers import AddClaimSerializer
from .app_serializers import AddPaymentSerializer

# For managing db
from .serializers import UserEntrySerializer

import json
import requests
import Adyen
import logging
import ast

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

            if mobile == None:
                message = "required_mobile"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_data, status = status.HTTP_204_NO_CONTENT)
            else:
                email_object = {'email': email}
                jsonResponse.update(email_object)
                user_entry_serializer = UserEntrySerializer(data = jsonResponse)

                if user_entry_serializer.is_valid():
                    user_entry_serializer.create(jsonResponse)
                    response_data = {"success": "true", "data": {"message": "Login request succeeded."}}
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {"message": "There's a problem with saving your information."}}
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {"success": "false", "data":{"message": "There's a problem with receiving your information."}}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_data, status=status.HTTP_204_NO_CONTENT)

        response_data = {"success": "false", "data":{"message": "There's a problem with receiving your information."}}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if code == None:
                message = "required_code"
                response_data = {"success": "false", "data": {"message": message}}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                    return Response(response_data, status = status.HTTP_400_BAD_REQUEST)
                else:

                    if response.status_code == status.HTTP_204_NO_CONTENT:
                        response_data = {"success": "false", "data": {"message": "No response from server."}}
                        return Response(response_data, status=status.HTTP_200_OK)

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
                response_data = {"success": "false", "data": {"message": "Your phone number isn't registered."}}
                return Response(response_data, status=status.HTTP_204_NO_CONTENT)

# Get payment methods #
class GetPaymentMethodsView(APIView):

    def post(self, request):

        access_token = request.data.get("access_token")
        amount = request.data.get("amount")
        currency = request.data.get("currency")

        # Check if there's the mobile number alreday in DB.
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            # _mutable = request.data._mutable
            # request_data = request.data
            # request_data._mutable = True
            # request_data['user_id'] = existed_user.id
            # request_data['state'] = 1
            # request_data._mutable = _mutable

            request_data = deepcopy(request.data)
            request_data['user_id'] = existed_user.id
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
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_data = {"success": "false", "data": {"message": "Getting payment methods failed."}}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
                    history_content['amount'] = payment.amount
                    history_content['currency'] = payment.currency
                    history_content['state'] = payment.state

                    history_json_content = json.dumps(history_content)

                    history_data = History(user_id = existed_user.id, type = "Payment", content = history_json_content)
                    history_data.save()

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {
                        "message": "Payment failed."}}
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            else:
                response_data = {"success": "false", "data": {"message": "The payment information doesn't exist."}}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# Add coverage
class AddCoverageView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")

        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:

            # Add user_id to the request data to save as a model field

            request_data = deepcopy(request.data)
            request_data['user_id'] = existed_user.id
            request_data['state'] = 1

            add_coverage_serializer = AddCoverageSerializer(data = request_data)
            if (add_coverage_serializer.is_valid()):

                obj = add_coverage_serializer.save();

                history_content = deepcopy(request_data)
                history_content['id'] = obj.id
                json_content = json.dumps(history_content)

                history_data = History(user_id = existed_user.id, type = "Coverage", content = str(json_content))
                history_data.save()

                response_data = {"success": "true", "data": {"message": "Adding coverage succeeded."}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": add_coverage_serializer.errors}}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# Get company list
class GetCompanyListView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            company_list = Company.objects.all()

            response_company_list = []

            for company in company_list:
                company_id = company.id
                company_name = company.name
                company_icon_url = company.icon_url
                company_price_per_year = company.price_per_year

                record = {"id": company_id, "name": company_name, "icon_url": company_icon_url, "price_per_year": company_price_per_year}
                response_company_list.append(record)

            response_data = {"success": "true", "data": {
                "message": "Getting company list succeeded.",
                "companyList": response_company_list}}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# Get active coverage list
class GetActiveCoverageView(APIView):

    def post(self, request):

        # Get user_id from access_token
        access_token = request.data.get("access_token")
        existed_user = User.objects.filter(access_token = access_token).first()

        if existed_user != None:
            coverage = Coverage.objects.filter(user_id = existed_user.id).first()

            if coverage != None:

                coverage_id = coverage.id
                coverage_name = coverage.name
                coverage_latitude = coverage.latitude
                coverage_longitude = coverage.longitude
                coverage_address = coverage.address
                coverage_company_id = coverage.company_id
                coverage_start_at = coverage.start_at
                coverage_end_at = coverage.end_at
                coverage_video_mile = coverage.video_mile
                coverage_video_vehicle = coverage.video_vehicle
                coverage_state = coverage.state

                company = Company.objects.filter(id = coverage_company_id).first()

                if company != None:

                    company_id = company.id
                    company_name = company.name
                    company_latitude = company.latitude
                    company_longitude = company.longitude
                    company_address = company.address
                    company_icon_url = company.icon_url
                    company_price_per_year = company.price_per_year

                    response_company = {
                        "id": company_id,
                        "name": company_name,
                        "latitude": company_latitude,
                        "longitude": company_longitude,
                        "address": company_address,
                        "icon_url": company_icon_url,
                        "price_per_year": company_price_per_year
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
                        "start_at": start_at_timestamp,
                        "end_at": end_at_timestamp,
                        "video_mile": coverage_video_mile,
                        "video_vehicle": coverage_video_vehicle,
                        "state": coverage_state}

                    response_data = {"success": "true", "data": {
                        "message": "Getting active coverage succeeded.",
                        "coverage": response_coverage}}

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"success": "false", "data": {"message": "The company information of the active coverage doesn't exist."}}
                    return Response(response_data, status=status.HTTP_204_NO_CONTENT)
            else:
                response_data = {"success": "false", "data": {"message": "The active coverage doesn't exist."}}
                return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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

                history_content = {}

                history_content['id'] = coverage.id
                history_content['name'] = coverage.name
                history_content['user_id'] = coverage.user_id
                history_content['latitude'] = coverage.latitude
                history_content['longitude'] = coverage.longitude
                history_content['address'] = coverage.address
                history_content['company_id'] = coverage.company_id

                # Change the datetime field to timestamp
                start_at = coverage.start_at
                if start_at != None:
                    history_content['start_at'] = start_at.timestamp()
                else:
                    history_content['start_at'] = None
                end_at = coverage.end_at
                if end_at != None:
                    history_content['end_at'] = end_at.timestamp()
                else:
                    history_content['end_at'] = None
                history_content['video_mile'] = coverage.video_mile
                history_content['video_vehicle'] = coverage.video_vehicle
                history_content['state'] = coverage.state

                history_json_content = json.dumps(history_content)

                history_data = History(user_id = existed_user.id, type = "Coverage", content = history_json_content)
                history_data.save()

                response_data = {"success": "true", "data": {
                    "message": "The coverage was cancelled successfully."}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": "The coverage information doesn't exist."}}
                return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# Add claim
class AddClaimView(APIView):

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

            request_data = deepcopy(request.data)
            request_data['user_id'] = existed_user.id
            request_data['state'] = 1

            # For saving content to history table (not date_time_happenend)
            history_content = deepcopy(request_data)

            time_happenend = int(request_data.get("time_happened"))
            datetime_happened = make_aware(datetime.fromtimestamp(time_happenend))
            request_data['date_time_happened'] = datetime_happened

            add_claim_serializer = AddClaimSerializer(data = request_data)
            if (add_claim_serializer.is_valid()):

                obj = add_claim_serializer.save();

                history_content['id'] = obj.id
                json_content = json.dumps(history_content)

                history_data = History(user_id = existed_user.id, type = "Claim", content = str(json_content))
                history_data.save()

                response_data = {"success": "true", "data": {"message": "Adding coverage succeeded."}}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"success": "false", "data": {"message": add_claim_serializer.errors}}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = {"success": "false", "data": {"message": "The access token is invalid."}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
