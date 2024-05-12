from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from userauths import views as userauths_views
from store import views as store_views
from customer import views as customer_views
from vendor import views as vendor_views

urlpatterns = [
    path('user/token/', userauths_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/register/', userauths_views.RegisterView.as_view(), name='auth_register'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/password-reset/<str:email>/', userauths_views.PasswordResetEmailVerificationView.as_view(), name='password-reset'),
    path('user/password-change/', userauths_views.PasswordChangeView.as_view(), name='password-change'),
    path('user/profile/<user_id>/', userauths_views.ProfileAPIView.as_view(), name='profile'),

    # Store Endpoints
    path('category/', store_views.CategoryListAPIView.as_view(), name='category-list'),
    path('products/', store_views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<str:slug>/', store_views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('cart-view/', store_views.CartAPIView.as_view(), name='cart-view'),
    path('cart-list/<str:cart_id>/<int:user_id>/', store_views.CartListAPIView.as_view(), name='cart-list'),
    path('cart-list/<str:cart_id>/', store_views.CartListAPIView.as_view(), name='cart-list'),
    path('cart-detail/<str:cart_id>/<int:user_id>/', store_views.CartDetailAPIView.as_view(), name='cart-detail'),
    path('cart-detail/<str:cart_id>/', store_views.CartDetailAPIView.as_view(), name='cart-detail'),
    path('cart-delete/<str:cart_id>/<int:item_id>/<int:user_id>/', store_views.CartItemDeleteAPIView.as_view(), name='cart-delete'),
    path('cart-delete/<str:cart_id>/<int:item_id>/', store_views.CartItemDeleteAPIView.as_view(), name='cart-delete'),
    path('create-order/', store_views.CreateOrderAPIView.as_view(), name='cart-delete'),
    path('checkout/<str:order_id>/', store_views.CheckoutAPIView.as_view(), name='checkout'),
    path('coupon/', store_views.CouponAPIView.as_view(), name='coupon'),
    path('reviews/<str:product_id>/', store_views.ReviewListAPIView.as_view(), name='reviews'),
    path('search/', store_views.SearchProductAPIView.as_view(), name='search'),

    # Payment Endpoints
    path('stripe-checkout/<str:order_oid>/', store_views.StripeCheckoutAPIView.as_view(), name='stripe-checkout'),
    path('payment-success/<str:order_oid>/', store_views.PaymentSuccessAPIView.as_view(), name='payment-success'),

    # Customer Endpoints
    path('customer/orders/<int:user_id>/', customer_views.OrdersAPIView.as_view(), name='orders'),
    path('customer/order/<int:user_id>/<str:order_oid>/', customer_views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('customer/wishlist/<int:user_id>/', customer_views.WishlistAPIView.as_view(), name='wishlist'),
    path('customer/notification/<int:user_id>/', customer_views.CustomerNotification.as_view(), name='notification'),
    path('customer/notification/<int:user_id>/<int:noti_id>/', customer_views.MarkCustomerNotificationAsSeen.as_view(), name='notification'),

    # Vendor Endpoints
    path('vendor/stats/<vendor_id>/', vendor_views.DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('vendor-orders-chart/<vendor_id>/', vendor_views.MonthlyOrderChartAPIView, name='vendor-orders-chart'),
    path('vendor-products-chart/<vendor_id>/', vendor_views.MonthlyProductChartAPIView, name='vendor-products-chart'),
    path('vendor/products-list/<vendor_id>/', vendor_views.ProductAPIView.as_view(), name='vendor-products-list'),
    path('vendor/orders-list/<vendor_id>/', vendor_views.OrderAPIView.as_view(), name='vendor-orders-list'),
    path('vendor/orders-list-filter/<vendor_id>/', vendor_views.FilterOrderAPIView.as_view(), name='vendor-orders-list-filter'),
    path('vendor/orders-detail/<vendor_id>/<order_oid>/', vendor_views.OrderDetailAPIView.as_view(), name='vendor-orders-detail'),
    path('vendor/revenue/<vendor_id>/', vendor_views.RevenueAPIView.as_view(), name='vendor-revenue'),
    path('vendor/filter-products/<vendor_id>/', vendor_views.FilterProductAPIView.as_view(), name='vendor-filter-products'),
    path('vendor/earning/<vendor_id>/', vendor_views.EarningAPIView.as_view(), name='vendor-earning'),
    path('vendor/monthly-earning/<vendor_id>/', vendor_views.MonthlyEarningTracker, name='vendor-monthly-earning'),
    path('vendor/reviews-list/<vendor_id>/', vendor_views.ReviewListAPIView.as_view(), name='vendor-reviews'),
    path('vendor/reviews-detail/<vendor_id>/<review_id>/', vendor_views.ReviewDetailAPIView.as_view(), name='vendor-reviews-detail'),
    path('vendor/coupons-list/<vendor_id>/', vendor_views.CouponListCreateAPIView.as_view(), name='vendor-coupons-list'),
    path('vendor/coupons-detail/<vendor_id>/<coupon_id>/', vendor_views.CouponDetailAPIView.as_view(), name='vendor-coupons-detail'),
    path('vendor/coupons-stats/<vendor_id>/', vendor_views.CouponStatsAPIView.as_view(), name='vendor-coupons-stats'),
    path('vendor/notification-unseen/<vendor_id>/', vendor_views.NotificationUnseenAPIView.as_view(), name='vendor-notification-unseen'),
    path('vendor/notification-seen/<vendor_id>/', vendor_views.NotificationSeenAPIView.as_view(), name='vendor-notification-seen'),
    path('vendor/notification-summary/<vendor_id>/', vendor_views.NotificationSummaryAPIView.as_view(), name='vendor-notification-summary'),
    path('vendor/notification-marked-seen/<vendor_id>/<noti_id>/', vendor_views.NotificationVendorMarkAsSeen.as_view(), name='vendor-notification-marked-seen'),
    path('vendor/profile-update/<int:pk>/', vendor_views.VendorProfileUpdateView.as_view(), name='vendor-profile-update'),
    path('shop/<vendor_slug>/', vendor_views.ShopAPIView.as_view(), name='vendor-shop'),
    path('vendor/shop-settings/<int:pk>/', vendor_views.ShopUpdateView.as_view(), name='vendor-shop-settings'),
    path('vendor/shop-products/<vendor_slug>/', vendor_views.ShopProductsAPIView.as_view(), name='vendor-shop-products'),
]