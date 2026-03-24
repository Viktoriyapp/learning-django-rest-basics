from django.db.models import Q, Count, Min, Max
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from garage_api.models import Manufacturer, Car
from garage_api.serializers import ManufacturerSerializer, CarSerializer


# Create your views here.

#How to write function based api views
# @api_view(['GET', 'POST'])
# def ...


class ListManufacturerApiView(APIView):
    def get(self, request: Request) -> Response:
        manufacturers = Manufacturer.objects.all() # here we dont need validation bcs this info comes from our db
        serializer = ManufacturerSerializer(manufacturers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK) # here we serialize the data into JSON

    def post(self, request: Request) -> Response:
        serializer = ManufacturerSerializer(data=request.data) # request.data is dict
        serializer.is_valid(raise_exception=True) # if there is exception returns 400 Bad Request
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) # Here we return the now saved data and status


class ListCarApiView(APIView):
    QUERY_LOOKUP_FIELDS = {
        'year': lambda x: Q(year=x),
        'manufacturer_id': lambda x: Q(manufacturer_id=x),
        'model_name': lambda x: Q(model=x),
    }

    QUERY_ORDER_BY_FIELDS = [
        'year',
        '-year',
    ]

    def get(self, request: Request) -> Response:
        cars = Car.objects.all() # here we dont need validation bcs this info comes from our db

        for param in request.query_params: # from url with ?year=2020 we get dict {year: 2020}
            query_lookup = self.QUERY_LOOKUP_FIELDS.get(param)

            if query_lookup:
                cars = cars.filter(query_lookup(request.query_params[param]))

        ordering = request.query_params.get('order_by')

        if ordering and ordering in self.QUERY_ORDER_BY_FIELDS:
            cars = cars.order_by(ordering)

        serializer = CarSerializer(cars, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK) # here we serialize the data into JSON

    def post(self, request: Request) -> Response:
        serializer = CarSerializer(data=request.data) # request.data is dict
        serializer.is_valid(raise_exception=True) # if there is exception returns 400 Bad Request
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) # Here we return the now saved data and status


class CarDetailApiView(APIView):
    def get(self, request: Request, pk: int) -> Response:
        car = get_object_or_404(Car, pk=pk)
        serializer = CarSerializer(car)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, pk: int) -> Response: # Put changes the whole db entry value
        car = get_object_or_404(Car, pk=pk)
        serializer = CarSerializer(car, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pk: int) -> Response:
        car = get_object_or_404(Car, pk=pk)
        serializer = CarSerializer(car, data=request.data, partial=True) # Partial bcs patch changes the db entry value partly
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk: int) -> Response:
        car = get_object_or_404(Car, pk=pk)
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CarStatsView(APIView):
    def get(self, request: Request) -> Response:
        stats = Car.objects.aggregate(
            total_cars=Count('id'),
            oldest_year=Min('year'),
            newest_year=Max('year'),
        )
        return Response(data=stats, status=status.HTTP_200_OK)
    # Here we can go without serializers bcs the data just comes from us