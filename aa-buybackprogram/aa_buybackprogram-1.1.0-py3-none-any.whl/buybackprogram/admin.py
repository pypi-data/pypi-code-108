from django.contrib import admin

from .models import Location, Owner, Program

# Register your models here.


class ProgramAdmin(admin.ModelAdmin):
    model = Program

    list_display = (
        "owner",
        "location",
        "is_corporation",
        "hauling_fuel_cost",
        "tax",
        "refining_rate",
        "price_dencity_modifier",
        "allow_all_items",
        "use_refined_value",
        "use_compressed_value",
        "use_raw_ore_value",
        "allow_unpacked_items",
    )


admin.site.register(Program, ProgramAdmin)


admin.site.register(Owner)

admin.site.register(Location)
