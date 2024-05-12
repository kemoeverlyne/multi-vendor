from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.db.models.functions import ExtractMonth 
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import stripe.error


from vendor.models import Vendor
from userauths.models import User

from decimal import Decimal
from datetime import datetime, timedelta

import stripe
import requests

from backend.settings import stripe_secret_key, stripe_public_key, FROM_EMAIL, PAYPAL_CLIENT_ID, PAYPAL_SECRET_KEY

from userauths.models import Profile
from store.models import CartOrder, CartOrderItem, Product, Category, Cart, Tax, Coupon, Notification, Review, Wishlist
from store.serializer import EarningSerializer, ProductReadSerializer, VendorSerializer
from store.serializer import ProductWriteSerializer
from store.serializer import CategorySerializer
from store.serializer import CartSerializer
from store.serializer import CartOrderSerializer
from store.serializer import CartOrderItemSerializer
from store.serializer import CouponSerializer
from store.serializer import NotificationSerializer
from store.serializer import ReviewSerializer
from store.serializer import WishlistSerializer
from store.serializer import SummarySerializer
from store.serializer import CouponSummarySerializer
from store.serializer import NotificationSummarySerializer
from store.serializer import ProfileSerializer


class DashboardStatsAPIView(generics.ListAPIView):
    serializer_class = SummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        # Calculate summary values
        product_count = Product.objects.filter(vendor=vendor).count()
        order_count = CartOrder.objects.filter(vendor=vendor, payment_status='paid').count()
        revenue = CartOrderItem.objects.filter(vendor=vendor, order__payment_status='paid').aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0

        return [
            {
                'products': product_count,
                'orders': order_count,
                'revenue': revenue
            }
        ]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

@api_view(['GET'])
def MonthlyOrderChartAPIView(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    orders = CartOrder.objects.filter(vendor=vendor, payment_status='paid')
    order_by_month = orders.annotate(month=ExtractMonth('date')).values('month').annotate(orders=models.Count('id')).order_by('month')

    return Response(order_by_month)


@api_view(['GET'])
def MonthlyProductChartAPIView(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    products = Product.objects.filter(vendor=vendor)
    products_by_month = products.annotate(month=ExtractMonth('date')).values('month').annotate(products=models.Count('id')).order_by('month')

    return Response(products_by_month)


class ProductAPIView(generics.ListAPIView):
    serializer_class = ProductReadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return Product.objects.filter(vendor=vendor).order_by('-id')
    

class OrderAPIView(generics.ListAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return CartOrder.objects.filter(vendor=vendor).order_by('-id')
    

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        order_oid = self.kwargs['order_oid']

        vendor = Vendor.objects.get(id=vendor_id)
        order = CartOrder.objects.get(
            vendor=vendor, payment_status="paid", oid=order_oid)

        return order
    

class RevenueAPIView(generics.ListAPIView):
    serializer_class = CartOrderItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return CartOrderItem.objects.filter(vendor=vendor, order__payment_status='paid').aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0
    
class FilterOrderAPIView(generics.ListAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        filter = self.request.GET.get('filter')
        orders = CartOrder.objects.filter(vendor=vendor)

        if filter == 'paid':
            orders = orders.filter(payment_status='paid')
        elif filter == 'cancelled':
            orders = orders.filter(payment_status='cancelled')
        elif filter == 'pending':
            orders = orders.filter(payment_status='pending')
        elif filter == 'processing':
            orders = orders.filter(payment_status='processing')
        elif filter == 'latest':
            orders = orders.order_by('-date')
        elif filter == 'oldest':
            orders = orders.order_by('date')
        elif filter == 'Pending':
            orders = orders.filter(order_status='Pending')
        elif filter == 'Fullfilled':
            orders = orders.filter(order_status='Fullfilled')
        elif filter == 'Cancelled':
            orders = orders.filter(order_status='Cancelled')

        # Default ordering by '-id' for other cases
        return orders
    

class FilterProductAPIView(generics.ListAPIView):
    serializer_class = ProductReadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        filter = self.request.GET.get('filter')

        if filter == 'published':
            products = Product.objects.filter(vendor=vendor, status='published')
        elif filter == 'in_review':
            products = Product.objects.filter(vendor=vendor, status='in_review')
        elif filter == 'draft':
            products = Product.objects.filter(vendor=vendor, status='draft')
        else:
            products = Product.objects.filter(vendor=vendor, status='disabled')

        return products.order_by('-id')
    

class EarningAPIView(generics.ListAPIView):
    serializer_class = EarningSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        one_month_ago = datetime.today() - timedelta(days=28)
        monthly_revenue = CartOrderItem.objects.filter(vendor=vendor, order__payment_status='paid', date__gte=one_month_ago).aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0
        total_revenue = CartOrderItem.objects.filter(vendor=vendor, order__payment_status='paid').aggregate(total_revenue=models.Sum(models.F('sub_total') + models.F('shipping_amount')))['total_revenue'] or 0

        return [{
            'monthly_revenue': monthly_revenue,
            'total_revenue': total_revenue
        }]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def MonthlyEarningTracker(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    monthly_earning_tracker = (
        CartOrderItem.objects
        .filter(vendor=vendor, order__payment_status='paid')
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(
            sales_count=models.Sum('qty'),
            total_earnings=models.Sum(models.F('sub_total') + models.F('shipping_amount'))
        )
        .order_by('-month')
    )
    return Response(monthly_earning_tracker)


class ReviewListAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return Review.objects.filter(product__vendor=vendor).order_by('-id')
    

class ReviewDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        review_id = self.kwargs['review_id']
        vendor = Vendor.objects.get(id=vendor_id)
        review = Review.objects.get(id=review_id, product__vendor=vendor)

        return review
    

class CouponListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return Coupon.objects.filter(vendor=vendor).order_by('-id')
    
    def create(self, request, *args, **kwargs):
        payload = request.data

        vendor_id = payload['vendor_id']
        code = payload['code']
        discount = payload['discount']
        active = payload['active']

        vendor = Vendor.objects.get(id=vendor_id)

        Coupon.objects.create(
            vendor=vendor,
            code=code,
            discount=discount,
            active=(active.lower() == 'true')
        )

        return Response({'message': 'Coupon created successfully'}, status=status.HTTP_201_CREATED)


        
class CouponDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_id = self.kwargs['vendor_id']
        coupon_id = self.kwargs['coupon_id']
        
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            return Coupon.objects.get(id=coupon_id, vendor=vendor)
        except Vendor.DoesNotExist:
            raise Http404("Vendor not found")
        except Coupon.DoesNotExist:
            raise Http404("Coupon not found")
    

class CouponStatsAPIView(generics.ListAPIView):
    serializer_class = CouponSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        total_coupons = Coupon.objects.filter(vendor=vendor).count()
        active_coupons = Coupon.objects.filter(
            vendor=vendor, active=True).count()

        return [{
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
        }]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    


class NotificationUnseenAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return Notification.objects.filter(vendor=vendor, seen=False).order_by('-id')
    

class NotificationSeenAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        return Notification.objects.filter(vendor=vendor, seen=True).order_by('-id')
    

class NotificationSummaryAPIView(generics.ListAPIView):
    serializer_class = NotificationSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        vendor_id = self.kwargs['vendor_id']
        vendor = Vendor.objects.get(id=vendor_id)

        unread_notification = Notification.objects.filter(vendor=vendor, seen=False).count()
        read_notification = Notification.objects.filter(vendor=vendor, seen=True).count()
        all_notification = Notification.objects.filter(vendor=vendor).count()

        return [{
            'read_notification': read_notification,
            'unread_notification': unread_notification,
            'all_notification': all_notification
        }]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class NotificationVendorMarkAsSeen(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_id =self.kwargs['vendor_id']
        noti_id = self.kwargs['noti_id']

        vendor = Vendor.objects.get(id=vendor_id)
        noti = Notification.objects.get(id=noti_id, vendor=vendor)

        noti.seen = True
        noti.save()

        return noti
    


class VendorProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]



class ShopUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [AllowAny]



class ShopAPIView(generics.RetrieveAPIView):
    serializer_class = VendorSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        vendor_slug = self.kwargs['vendor_slug']
        return Vendor.objects.get(slug=vendor_slug)



class ShopProductsAPIView(generics.ListAPIView):
    serializer_class = ProductReadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vendor_slug = self.kwargs['vendor_slug']
        vendor = Vendor.objects.get(slug=vendor_slug)
        return Product.objects.filter(vendor=vendor).order_by('-id')




    





