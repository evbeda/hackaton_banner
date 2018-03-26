from factory import DjangoModelFactory, Sequence, SubFactory, LazyFunction, lazy_attribute
from . import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.defaultfilters import slugify


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    first_name = Sequence(lambda n: "Agent%03d" % n)
    last_name = Sequence(lambda n: "Agent%03d" % n)
    username = lazy_attribute(lambda o: slugify(o.first_name + '.' + o.last_name))

class BannerDesignFactory(DjangoModelFactory):
    class Meta:
        model = models.BannerDesign
        django_get_or_create = ('user',)

    user = SubFactory(UserFactory)
    banner_design_name = Sequence(lambda n: "BannerDesign%03d" % n)
    created_date = LazyFunction(timezone.now)
