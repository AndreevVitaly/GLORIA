from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.utils import timezone

from .models import (
    CustomerConnection,
    CustomerProfile,
    CustomerRecipient,
    RecipientCelebrationDate,
    User,
)
from .uploads import prepare_avatar


class GioiaUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username", "phone")


class GioiaUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class EmailFormMixin:
    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        existing = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError("Аккаунт с таким email уже существует.")
        return email


class SignupForm(EmailFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "email", "phone")
        labels = {"first_name": "Имя", "email": "Email", "phone": "Телефон"}
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "+79991234567"}),
        }


class CustomerLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )


class AccountForm(EmailFormMixin, forms.ModelForm):
    current_password = forms.CharField(
        label="Текущий пароль",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        help_text="Нужен только при изменении email для входа.",
    )

    class Meta:
        model = User
        fields = ("phone", "first_name", "email")
        labels = {"phone": "Телефон", "first_name": "Имя", "email": "Email"}
        widgets = {
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "+79991234567"}),
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = self.instance.email

    def clean(self):
        data = super().clean()
        email = data.get("email")
        if email and email != self.original_email:
            if not self.instance.check_password(data.get("current_password", "")):
                self.add_error("current_password", "Для изменения email введите текущий пароль.")
        return data


class ProfileForm(forms.ModelForm):
    photo = forms.FileField(
        label="Ваше фото",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
    )
    remove_photo = forms.BooleanField(label="Удалить текущее фото", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"].choices = [("", "Не выбрано"), *CustomerProfile.Gender.choices]

    class Meta:
        model = CustomerProfile
        fields = ("birth_date", "gender")
        labels = {"birth_date": "Дата рождения", "gender": "Пол"}
        widgets = {"birth_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}

    def clean_birth_date(self):
        date = self.cleaned_data["birth_date"]
        if date and date > timezone.localdate():
            raise forms.ValidationError("Дата рождения не может быть в будущем.")
        return date

    def clean_photo(self):
        upload = self.cleaned_data.get("photo")
        return prepare_avatar(upload) if upload else None

    def clean(self):
        data = super().clean()
        if data.get("photo") and data.get("remove_photo"):
            self.add_error(
                "remove_photo", "Выберите одно действие: загрузить фото или удалить его."
            )
        return data


class ConnectionForm(forms.ModelForm):
    class Meta:
        model = CustomerConnection
        fields = ("label",)
        labels = {"label": "Кто в вашем окружении?"}
        widgets = {
            "label": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Например: супруга, тёща или подруга Анна",
                }
            )
        }

    def clean_label(self):
        label = self.cleaned_data["label"].strip()
        if not label:
            raise forms.ValidationError("Напишите, кого хотите добавить.")
        return label


class RecipientForm(forms.ModelForm):
    class Meta:
        model = CustomerRecipient
        fields = ("name", "phone", "relationship", "notes")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например: Анна"}),
            "phone": forms.TextInput(attrs={"placeholder": "+79991234567", "autocomplete": "tel"}),
            "relationship": forms.TextInput(attrs={"placeholder": "Например: супруга"}),
            "notes": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Любимые цветы, предпочтения или подсказка"}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Укажите имя адресата.")
        return name


class CelebrationDateForm(forms.ModelForm):
    class Meta:
        model = RecipientCelebrationDate
        fields = ("title", "event_date", "repeats_annually")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "День рождения"}),
            "event_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title and self.cleaned_data.get("event_date"):
            raise forms.ValidationError("Укажите название события.")
        return title


CelebrationDateFormSet = forms.inlineformset_factory(
    CustomerRecipient,
    RecipientCelebrationDate,
    form=CelebrationDateForm,
    extra=1,
    can_delete=True,
)
