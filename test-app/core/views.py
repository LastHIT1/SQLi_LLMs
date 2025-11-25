from typing import Final

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from redis import Redis

from core.forms import RegisterForm, VulnerableLoginForm
from core.models import Book

BOOK_COLUMNS: Final[tuple[str, ...]] = (
    "id",
    "title",
    "author",
    "description",
    "cover_image",
    "price",
    "published_year",
)
BOOK_SELECT: Final[str] = f"SELECT {', '.join(BOOK_COLUMNS)} FROM core_book"
GUARDRAIL_STATUS_KEY: Final[str] = "guardrail_status"

redis_client = Redis(host="cache", port=6379, db=0, decode_responses=True)


def get_guardrail_status() -> bool:
    value = redis_client.get("guardrail_status")
    print(value)
    return value != "0" if value is not None else True


def row_to_book(row: tuple | None) -> dict | None:
    return dict(zip(BOOK_COLUMNS, row, strict=False)) if row else None


def execute_query(query: str) -> list[tuple]:
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def home(request: HttpRequest) -> HttpResponse:
    search_query = request.GET.get("q", "")
    books: list[dict] = []
    error_message: str | None = None

    if search_query:
        # VULNERABLE SQL - intentionally for security testing
        query = f"{BOOK_SELECT} WHERE title ILIKE '%{search_query}%' OR author ILIKE '%{search_query}%'"
        try:
            books = [row_to_book(row) for row in execute_query(query)]
        except Exception as e:
            error_message = f"Database error: {e}"
    else:
        books = list(Book.objects.values(*BOOK_COLUMNS))

    return render(
        request,
        "home.html",
        {
            "books": books,
            "guardrail_status": get_guardrail_status(),
            "search_query": search_query,
            "error_message": error_message,
        },
    )


def book_detail(request: HttpRequest, book_id: int) -> HttpResponse:
    book: dict | None = None
    error_message: str | None = None

    # VULNERABLE SQL - intentionally for security testing
    try:
        rows = execute_query(f"{BOOK_SELECT} WHERE id = {book_id}")
        book = row_to_book(rows[0]) if rows else None
    except Exception as e:
        error_message = f"Database error: {e}"

    return render(
        request,
        "book_detail.html",
        {
            "book": book,
            "guardrail_status": get_guardrail_status(),
            "error_message": error_message,
        },
    )


def register(request: HttpRequest) -> HttpResponse:
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("home")
    return render(
        request,
        "register.html",
        {
            "form": form,
            "guardrail_status": get_guardrail_status(),
        },
    )


def vulnerable_login(request: HttpRequest) -> HttpResponse:
    form = VulnerableLoginForm(request.POST or None)
    error_message: str | None = None

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        try:
            # VULNERABLE SQL - intentionally for security testing
            rows = execute_query(
                f"SELECT id, password FROM auth_user WHERE username = '{username}'"
            )
            if rows and check_password(password, rows[0][1]):
                login(request, User.objects.get(id=rows[0][0]))
                return redirect("home")
            error_message = "Invalid credentials"
        except Exception as e:
            error_message = f"SQL Error: {e}"

    return render(
        request,
        "login.html",
        {
            "form": form,
            "error_message": error_message,
            "guardrail_status": get_guardrail_status(),
        },
    )
