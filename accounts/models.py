from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator, URLValidator

import uuid

phone_regex = RegexValidator(regex=r'^[\d]{10}$',
                             message="Phone number invalid")

url_validator = URLValidator(
    schemes=('http', 'https', 'ftp', 'ftps', 'rtsp', 'rtmp'))


class UserManager(BaseUserManager):
    def create_user(self,
                    phone,
                    password=None,
                    first_name=None,
                    last_name=None,
                    profile_pic=None,
                    is_active=True,
                    is_admin=False):
        if not phone:
            raise ValueError('Please Enter Phone number')

        user_obj = self.model(phone=phone,
                              first_name=first_name,
                              last_name=last_name,
                              profile_pic=profile_pic,
                              is_active=is_active,
                              is_admin=is_admin)

        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_admin=True
        )
        return user


class AbstractTimeClass(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserImagesUrl(AbstractTimeClass):
    image_url = models.URLField(max_length=500, validators=[
                                url_validator], unique=True)
    image_hash = models.CharField(max_length=200, unique=True)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(
        validators=[phone_regex], max_length=15, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(
        max_length=100, blank=True, null=True, default='')
    profile_pic = models.ForeignKey(
        UserImagesUrl, on_delete=models.SET_NULL, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if self.first_name:
            return "%s %s" % (self.first_name, self.last_name)
        else:
            return self.phone

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        else:
            return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def name(self):
        if self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        else:
            return self.first_name


class UserOTPTable(models.Model):
    phone = models.CharField(validators=[phone_regex], max_length=15)
    otp = models.IntegerField()
    ref_number = models.CharField(max_length=100, default='1')
    count = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['phone', 'otp', 'count']


class AnnonymousUserTable(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_login_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.post_login_id:
            return "%s--%s" % (self.id, self.post_login_id.name)
        return "%s" % self.id
