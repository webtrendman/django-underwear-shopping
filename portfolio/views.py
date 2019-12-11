import pandas as pd
import numpy as np
from io import StringIO

from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from accounts.models import Account
from django.conf import settings
# from apps.portfolio.models import Portfolio
# from apps.portfolio.serializers import (CreatePortfolioSerializer,
#                                         PortfolioDetailSerializer,
#                                         PortfolioSerializer)

from accounts.models import Account
from accounts.serializers import AccountSerializer
from portfolio.serializers import PortfolioLikeSerializer
from accounts.models import PortfolioLike
from accounts.models import Gift
from accounts.models import Friend
from accounts.models import ProductRank
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json


class PortfolioListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountSerializer

    def get(self, *args, **kwargs):
        print("user: ", self.request.user)
        account = Account.objects.get(email=self.request.user)

        path = settings.BASE_DIR + '/static/victoria_secret.json'
        json_data = open(path)
        json_portfolios = json.load(json_data)
        topsize = account.topsize
        bottomsize = account.bottomsize
        brasize = account.brasize
        pantysize = account.pantysize
        json_result = []
        for portfolio in json_portfolios:
            
            product_category = portfolio['product_category']
            available_size = portfolio['available_size']
            uniq_id = portfolio['uniq_id']
            
            portfoliolike = PortfolioLike.objects.filter(account=account, uniq_id = uniq_id)
            if portfoliolike:
                portfolio['lol'] = portfoliolike[0].lol
            else:
                portfolio['lol'] = 0
            productrank = ProductRank.objects.filter(uniq_id = uniq_id)

            # gift = Gift.objects.filter(account=account, uniq_id = uniq_id)
            # if len(gift) == 0:
            if product_category == "Panties":
                if pantysize in available_size:
                    json_result.append(portfolio)
            if product_category == "Lingerie":
                if topsize in available_size:
                    json_result.append(portfolio)
            if product_category == "Bras":
                if brasize in available_size:
                    json_result.append(portfolio)
            # if product_category == "Panties":
            #     if pantysize in available_size:
            #         json_result.append(portfolio)

        return Response(
            data=json_result,
            status=status.HTTP_200_OK,
            )



class BrideListAPIView(RetrieveAPIView):

    def post(self, request, *args, **kwargs):

        account = Account.objects.get(email=request.data['email'])
        print(account.id);
        path = settings.BASE_DIR + '/static/victoria_secret.json'
        json_data = open(path)
        json_portfolios = json.load(json_data)
        json_result = []
        for portfolio in json_portfolios:
            uniq_id = portfolio['uniq_id']
            portfoliolike = PortfolioLike.objects.filter(account_id=account.id, uniq_id = uniq_id)

            if portfoliolike:
                if(portfoliolike[0].lol >= 1):
                    portfolio['lol'] = portfoliolike[0].lol
                    json_result.append(portfolio)
        return Response( data=json_result,
                        status=status.HTTP_200_OK)


class EditProfileAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        account = Account.objects.get(email=self.request.user)
        account.firstname = request.data['firstname']
        account.lastname = request.data['lastname']
        account.brasize = request.data['brasize']
        account.pantysize = request.data['pantysize']
        account.bottomsize = request.data['bottomsize']
        account.topsize = request.data['topsize']
        account.save()
        return Response(
            {'status': "OK"},
            status=status.HTTP_200_OK)