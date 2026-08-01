from django.contrib import admin

from .models import Membership, Organization, Subscription, SubscriptionPayment

admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(Subscription)
admin.site.register(SubscriptionPayment)
