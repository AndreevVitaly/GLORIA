import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower

from apps.core.models import CreatedModel, TimestampedModel

from .managers import UserManager
from .uploads import avatar_path

phone_validator = RegexValidator(r"^\+?[0-9]{7,15}$", "Введите телефон: 7–15 цифр, возможен +.")


class User(AbstractUser):
    uuid = models.UUIDField("UUID", default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=16, blank=True, validators=[phone_validator])
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)
    roles = models.ManyToManyField(
        "Role", verbose_name="Роли", through="UserRole", related_name="users", blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [models.UniqueConstraint(Lower("email"), name="users_email_ci_unique")]

    def clean(self):
        super().clean()
        self.email = type(self).objects.normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.email = type(self).objects.normalize_email(self.email)
        if not self.username:
            self.username = str(self.uuid)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Role(CreatedModel):
    class Code(models.TextChoices):
        CUSTOMER = "customer", "Покупатель"
        OPERATOR = "operator", "Оператор"
        ADMIN = "admin", "Руководитель"

    code = models.SlugField("Код", max_length=32, unique=True, choices=Code.choices)
    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name="Разрешения",
        blank=True,
        related_name="gioia_roles",
        db_table="role_permissions",
    )

    class Meta:
        db_table = "roles"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(code__in=["customer", "operator", "admin"]),
                name="roles_valid_code",
            )
        ]

    def __str__(self):
        return self.name


class UserRole(CreatedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    role = models.ForeignKey(Role, verbose_name="Роль", on_delete=models.PROTECT)

    class Meta:
        db_table = "user_roles"
        verbose_name = "Назначение роли"
        verbose_name_plural = "Назначения ролей"
        constraints = [models.UniqueConstraint(fields=["user", "role"], name="user_role_unique")]

    def __str__(self):
        return f"{self.user} / {self.role}"


class CustomerProfile(TimestampedModel):
    class Gender(models.TextChoices):
        FEMALE = "female", "Женский"
        MALE = "male", "Мужской"
        OTHER = "other", "Другой"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    gender = models.CharField("Пол", max_length=10, choices=Gender.choices, blank=True)
    avatar = models.ImageField("Фотография", upload_to=avatar_path, blank=True)
    marketing_consent = models.BooleanField("Согласие на рассылку", default=False)
    notes = models.TextField("Заметки", blank=True)

    class Meta:
        db_table = "customer_profiles"
        verbose_name = "Профиль покупателя"
        verbose_name_plural = "Профили покупателей"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(gender__in=["", "female", "male", "other"]),
                name="customer_profile_valid_gender",
            )
        ]

    def __str__(self):
        return str(self.user)


class CustomerConnection(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="environment",
    )
    label = models.TextField("Запись")

    class Meta:
        db_table = "customer_connections"
        verbose_name = "Запись окружения"
        verbose_name_plural = "Окружение покупателей"
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(label=""), name="customer_connection_label_not_empty"
            )
        ]

    def __str__(self):
        return self.label[:100]


class CustomerRecipient(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    name = models.CharField("Имя адресата", max_length=200)
    phone = models.CharField("Телефон", max_length=16, blank=True, validators=[phone_validator])
    relationship = models.CharField("Кем вам приходится", max_length=200, blank=True)
    notes = models.TextField("Заметка", blank=True)

    class Meta:
        db_table = "customer_recipients"
        verbose_name = "Адресат"
        verbose_name_plural = "Адресаты"
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(name=""), name="customer_recipient_name_not_empty"
            )
        ]

    def __str__(self):
        return self.name


class RecipientCelebrationDate(TimestampedModel):
    recipient = models.ForeignKey(
        CustomerRecipient,
        verbose_name="Адресат",
        on_delete=models.CASCADE,
        related_name="celebration_dates",
    )
    title = models.CharField("Название события", max_length=200)
    event_date = models.DateField("Дата поздравления")
    repeats_annually = models.BooleanField("Повторяется каждый год", default=True)

    class Meta:
        db_table = "recipient_celebration_dates"
        verbose_name = "Дата поздравления"
        verbose_name_plural = "Даты поздравлений"
        ordering = ["event_date", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(title=""), name="recipient_celebration_title_not_empty"
            )
        ]

    def __str__(self):
        return f"{self.title}: {self.event_date:%d.%m.%Y}"


class CustomerAddress(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    title = models.CharField("Название адреса", max_length=100)
    recipient_name = models.CharField("Имя получателя", max_length=200)
    recipient_phone = models.CharField(
        "Телефон получателя", max_length=16, validators=[phone_validator]
    )
    city = models.CharField("Город", max_length=100)
    street = models.CharField("Улица", max_length=200)
    house = models.CharField("Дом", max_length=30)
    building = models.CharField("Корпус/строение", max_length=30, blank=True)
    apartment = models.CharField("Квартира", max_length=30, blank=True)
    entrance = models.CharField("Подъезд", max_length=30, blank=True)
    floor = models.CharField("Этаж", max_length=10, blank=True)
    intercom = models.CharField("Домофон", max_length=30, blank=True)
    postal_code = models.CharField("Почтовый индекс", max_length=20, blank=True)
    latitude = models.DecimalField(
        "Широта",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        "Долгота",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    delivery_comment = models.TextField("Комментарий для доставки", blank=True)
    is_default = models.BooleanField("Адрес по умолчанию", default=False)

    class Meta:
        db_table = "customer_addresses"
        verbose_name = "Адрес покупателя"
        verbose_name_plural = "Адреса покупателей"
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="one_default_address_per_user",
            ),
            models.CheckConstraint(
                condition=models.Q(latitude__isnull=True)
                | models.Q(latitude__gte=-90, latitude__lte=90),
                name="address_latitude_range",
            ),
            models.CheckConstraint(
                condition=models.Q(longitude__isnull=True)
                | models.Q(longitude__gte=-180, longitude__lte=180),
                name="address_longitude_range",
            ),
        ]

    def __str__(self):
        return f"{self.title}: {self.city}, {self.street}, {self.house}"
