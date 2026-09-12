import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.models import CustomerRecipient, RecipientCelebrationDate, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def customer_client(client, user):
    client.force_login(user)
    return client


def recipient_data(**values):
    data = {
        "name": "Анна",
        "phone": "+79991234567",
        "relationship": "супруга",
        "notes": "Любит пионы",
        "dates-TOTAL_FORMS": "2",
        "dates-INITIAL_FORMS": "0",
        "dates-MIN_NUM_FORMS": "0",
        "dates-MAX_NUM_FORMS": "1000",
        "dates-0-title": "День рождения",
        "dates-0-event_date": "1992-04-15",
        "dates-0-repeats_annually": "on",
        "dates-1-title": "Годовщина",
        "dates-1-event_date": "2020-08-20",
        "dates-1-repeats_annually": "on",
    }
    data.update(values)
    return data


@pytest.mark.parametrize(
    "url",
    ["/account/recipients/", "/account/recipients/add/", "/account/recipients/1/edit/"],
)
def test_recipient_pages_require_login(client, url):
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith("/account/login/?next=")


def test_create_recipient_with_multiple_dates(customer_client, user):
    response = customer_client.post("/account/recipients/add/", recipient_data())
    assert response.status_code == 302
    recipient = user.recipients.get()
    assert recipient.name == "Анна"
    assert recipient.relationship == "супруга"
    assert recipient.celebration_dates.count() == 2
    birthday = recipient.celebration_dates.get(title="День рождения")
    assert str(birthday.event_date) == "1992-04-15"
    assert birthday.repeats_annually
    page = customer_client.get("/account/recipients/").content.decode()
    for text in ["Анна", "супруга", "День рождения", "15.04.1992", "Годовщина"]:
        assert text in page


def test_recipient_edit_add_and_delete_date(customer_client, user):
    recipient = CustomerRecipient.objects.create(user=user, name="Мама")
    first = RecipientCelebrationDate.objects.create(
        recipient=recipient, title="День рождения", event_date="1965-03-02"
    )
    data = recipient_data(
        name="Мама — Елена",
        relationship="мама",
        **{
            "dates-INITIAL_FORMS": "1",
            "dates-0-id": str(first.pk),
            "dates-0-title": "День рождения",
            "dates-0-event_date": "1965-03-02",
            "dates-0-DELETE": "on",
            "dates-1-title": "Именины",
            "dates-1-event_date": "2026-06-03",
        },
    )
    response = customer_client.post(reverse("accounts:recipient_edit", args=[recipient.pk]), data)
    assert response.status_code == 302
    recipient.refresh_from_db()
    assert recipient.name == "Мама — Елена"
    assert list(recipient.celebration_dates.values_list("title", flat=True)) == ["Именины"]


def test_recipient_delete_is_post_only_and_cascades_dates(customer_client, user):
    recipient = CustomerRecipient.objects.create(user=user, name="Тёща")
    RecipientCelebrationDate.objects.create(
        recipient=recipient, title="День рождения", event_date="1970-01-01"
    )
    url = reverse("accounts:recipient_delete", args=[recipient.pk])
    assert customer_client.get(url).status_code == 405
    assert customer_client.post(url).status_code == 302
    assert not CustomerRecipient.objects.exists()
    assert not RecipientCelebrationDate.objects.exists()


def test_recipient_ownership(customer_client, user):
    other = User.objects.create_user(email="other-recipient@example.com")
    recipient = CustomerRecipient.objects.create(user=other, name="Чужой адресат")
    RecipientCelebrationDate.objects.create(
        recipient=recipient, title="Чужая дата", event_date="2000-01-01"
    )
    for action in ["recipient_edit", "recipient_delete"]:
        url = reverse(f"accounts:{action}", args=[recipient.pk])
        assert customer_client.post(url, recipient_data()).status_code == 404
    page = customer_client.get("/account/recipients/").content.decode()
    assert "Чужой адресат" not in page
    assert "Чужая дата" not in page
    recipient.refresh_from_db()
    assert recipient.name == "Чужой адресат"


def test_recipient_pagination_has_no_total_cap(customer_client, user):
    CustomerRecipient.objects.bulk_create(
        [CustomerRecipient(user=user, name=f"Адресат {number}") for number in range(101)]
    )
    response = customer_client.get("/account/recipients/?page=6")
    assert response.status_code == 200
    assert response.context["recipients"].paginator.count == 101
    assert len(response.context["recipients"]) == 1
    assert (
        customer_client.post(
            "/account/recipients/add/",
            recipient_data(name="Адресат 102", **{"dates-TOTAL_FORMS": "0"}),
        ).status_code
        == 302
    )
    assert user.recipients.count() == 102


@pytest.mark.parametrize(
    "changes,error_target",
    [
        ({"name": "   "}, "form"),
        ({"phone": "incorrect"}, "form"),
        ({"dates-0-event_date": "incorrect"}, "formset"),
        ({"dates-0-title": ""}, "formset"),
    ],
)
def test_invalid_recipient_is_not_partially_saved(customer_client, user, changes, error_target):
    response = customer_client.post("/account/recipients/add/", recipient_data(**changes))
    assert response.status_code == 200
    if error_target == "form":
        assert response.context["form"].errors
    else:
        assert response.context["date_formset"].errors
    assert not user.recipients.exists()
    assert not RecipientCelebrationDate.objects.exists()


def test_recipient_text_is_escaped(customer_client):
    customer_client.post(
        "/account/recipients/add/",
        recipient_data(
            name='<script>alert("name")</script>',
            notes='<img src=x onerror=alert("note")>',
            **{"dates-0-title": '<script>alert("date")</script>'},
        ),
    )
    page = customer_client.get("/account/recipients/").content.decode()
    assert '<script>alert("name")</script>' not in page
    assert '<img src=x onerror=alert("note")>' not in page
    assert "&lt;script&gt;" in page


def test_recipient_posts_require_csrf(user):
    recipient = CustomerRecipient.objects.create(user=user, name="Мама")
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    for url in [
        "/account/recipients/add/",
        reverse("accounts:recipient_edit", args=[recipient.pk]),
        reverse("accounts:recipient_delete", args=[recipient.pk]),
    ]:
        assert client.post(url, recipient_data()).status_code == 403
