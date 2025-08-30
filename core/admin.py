from django.contrib import admin
from core.models.user_model import User
from core.models.channel_model import Channel, WellbeingIndex, WellbeingAggregate
from core.models.message_model import Message, MessageAnalysis

# Register your models here.

admin.site.register([User, Channel, WellbeingIndex, WellbeingAggregate, Message, MessageAnalysis])