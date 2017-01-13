from django.db import models
from bksys.managers import *
from datetime import datetime, timedelta

class recurringEventsManager(models.Manager):
    def newBooking(self,rm_id,start,end,recur_type):
        return self.create(room_id=rm_id,start_date=start,end_date=end,recurrence=recur_type)

class BookingsQueryset(models.query.QuerySet):
    def get_booking(self,id):
        return self.get(booking_ref=id)
    
    def get_description(self,id):
        return self.get_booking(id).description

    def get_contact(self,id):
        return self.get_booking(id).contact    

    def formatDate(self,id):
        booking = self.get_booking(id)
        return str(booking.date.strftime("%d-%m-%Y")) + " " + str(booking.start_time) + " - " + str(booking.end_time)

    def delete(self,id):
        self.get_booking(id).delete()

    def ongoingevents(self,date,start,end):
        bookings_for_day = self.filter(date=date)
        ongoingevents = bookings_for_day.filter(end_time__gte = start,start_time__lte = end)
        return ongoingevents

class BookingsManager(models.Manager):
    def newBooking(self,room_id,date,start,end,contact,description):
        booking = self.create(room_id=room_id,date=date,start_time=start,end_time=end,contact=contact,description=description)
        return booking

    def getInterval(self,value):
        if value == "1":
            return 1
        elif value == "2":
            return 7
        elif value == "3":
            return 14

    def newRecurringBooking(self,room_id,date,start,end,contact,description,type,recur_end):
        recur_end = datetime.strptime(recur_end,"%d-%m-%Y")
        start_date = datetime.strptime(date,"%Y-%m-%d")
        dates = []
        weekend = set([5, 6])
        while True:
            start_date = start_date + timedelta(days=self.getInterval(type))
            if start_date > recur_end:
                break;
            elif start_date.weekday() in weekend:
                print start_date
            else:
                dates.append(start_date)
        recur_end = recur_end.strftime("%Y-%m-%d")
        r_booking = recurringEvents.objects.newBooking(room_id,date,recur_end,type)
        booking = self.create(room_id=room_id,date=date,start_time=start,end_time=end,contact=contact,description=description,recurrence_id=r_booking.id)
        for date in dates:
            self.create(room_id=room_id,date=date,start_time=start,end_time=end,contact=contact,description=description,recurrence_id=r_booking.id)
        return booking

    def getOngoingEvents(self,date,start,end):
        return self.get_queryset().ongoingevents(date,start,end)

    def get_queryset(self):
        return BookingsQueryset(self.model, using=self._db)

    def delete(self,id):
        self.get_queryset().delete(id)

    def description(self,id):
        return self.get_queryset().get_description(id)

    def contact(self,id):
        return self.get_queryset().get_contact(id)

    def formatDate(self,id):
        return self.get_queryset().formatDate(id)

class RoomsQueryset(models.query.QuerySet):
    def get_name(self,id):
        query = self.get(room_id=id)
        return query.room_name

class RoomsManager(models.Manager):
    def get_queryset(self):
        return RoomsQueryset(self.model, using=self._db)

    def get_name(self,id):
        return self.get_queryset().get_name(id)

class rooms(models.Model):
    room_id         = models.AutoField(primary_key=True)
    room_name       = models.CharField(max_length=60, null = False)
    room_size       = models.IntegerField(null = False)
    room_location   = models.TextField(null = False)
    room_features   = models.TextField(null = False)
    in_use          = models.BooleanField(default=True)

    objects = RoomsManager()
    def getJSON(self):
        return dict(
            room_id = self.room_id,
            room_name = self.room_name,
            room_size = self.room_size,
            room_location = self.room_location,
            room_features = self.room_features,
        )

class reservations(models.Model):
    id = models.AutoField(primary_key = True, null = False)
    room               = models.ForeignKey(rooms,  on_delete=models.CASCADE, null = False)
    start_time             = models.DateTimeField(auto_now_add=True)

class recurringEvents(models.Model):
    id = models.AutoField(primary_key = True, null = False)
    room = models.ForeignKey(rooms,  on_delete=models.CASCADE, null=False)
    start_date = models.DateField(null = False)
    end_date = models.DateField(null = False)
    recurrence_options = (
        ('1','Daily'),
        ('2','Weekly'),
        ('3',"Biweekly"),
    )
    recurrence = models.CharField(max_length=10,choices=recurrence_options)
    objects = recurringEventsManager()

class bookings(models.Model):
    booking_ref = models.AutoField(primary_key=True)
    room        = models.ForeignKey(rooms,  on_delete=models.CASCADE, null = False)
    date        = models.DateField(null = False)
    start_time  = models.TimeField(null = False)
    end_time    = models.TimeField(null = False)
    contact     = models.CharField(max_length=60, null = False)
    description = models.CharField(max_length=60, null = False)
    recurrence  = models.ForeignKey(recurringEvents,  on_delete=models.CASCADE, null = True)
    objects = BookingsManager()

    def getJSON(self):
        return dict(
            booking_ref = self.booking_ref,
            room_id = self.room_id,
            date = str(self.date),
            start_time = str(self.start_time),
            end_time = str(self.end_time),
            contact = self.contact,
            description = self.description
        )
