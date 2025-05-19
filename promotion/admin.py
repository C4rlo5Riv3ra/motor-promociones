from django.contrib import admin
from .models import Promotion, PromotionRule, PromotionReward, PromotionRuleTier

# Register your models here.

admin.site.register(Promotion)
admin.site.register(PromotionRule)
admin.site.register(PromotionReward)
admin.site.register(PromotionRuleTier)