from django.conf.urls import  url
from . import views

urlpatterns = [ url(r'^$',views.index, name = 'index'),
                url(r'^find_rooms/$',views.find_rooms, name = 'find_rooms'),
                url(r'^view_room/([0-9]+)/$',views.view_room, name = 'view_room'),
                url(r'^book_room/$',views.book_room, name = 'book_room'),
                url(r'^viewBooking/$',views.viewBooking, name = 'viewBooking'),
                url(r'^findBooking/$',views.findBooking, name = 'findBooking'),
                url(r'^updateBooking/$',views.updateBooking, name = 'updateBooking'),
                url(r'^cancelBooking/$',views.cancelBooking, name = 'cancelBooking'),
                url(r'^getBookings/$',views.getBookings, name = 'getBookings'),
                url(r'^getRoomsBookings/$',views.getRoomsBookings, name = 'getRoomsBookings'),
              ]