
"""Мини-приложение тестов: веб-сервер (страница, логотип, API) внутри бота."""

import os
import re
import hmac
import json
import asyncio
import hashlib
import logging
import time

from urllib.parse import parse_qsl, urlsplit

import quiz_core as C


log = logging.getLogger("quiz-web")

HERE = os.path.dirname(os.path.abspath(__file__))

LANGS = ["ru", "uz", "en", "zh"]

IMG = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

NAME_RE = re.compile(
    r"[^\W\d_ʻʼ'’-]+(['ʻʼ’-][^\W\d_]+)*",
    re.UNICODE
)

MAX_BODY_SIZE = 100_000
REQUEST_TIMEOUT = 15
AUTH_MAX_AGE = 86400


def check_init_data(init_data, token):
    """Проверяет подпись и актуальность Telegram WebApp initData."""
    try:
        if not init_data or not token:
            return None

        pairs_list = parse_qsl(
            init_data,
            keep_blank_values=True
        )

        pairs = {}

        for key, value in pairs_list:
            if key in pairs:
                return None
            pairs[key] = value

        got = pairs.pop("hash", "")

        if not got or not re.fullmatch(r"[a-fA-F0-9]{64}", got):
            return None

        check = "\n".join(
            f"{key}={value}"
            for key, value in sorted(pairs.items())
        )

        secret = hmac.new(
            b"WebAppData",
            token.encode("utf-8"),
            hashlib.sha256
        ).digest()

        expected = hmac.new(
            secret,
            check.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, got):
            return None

        auth_date = int(pairs.get("auth_date", "0"))
        now = int(time.time())

        if auth_date <= 0 or auth_date > now + 60:
            return None

        if now - auth_date > AUTH_MAX_AGE:
            return None

        user = json.loads(pairs.get("user", "{}"))

        if not isinstance(user, dict) or not user.get("id"):
            return None

        return user

    except (ValueError, TypeError, json.JSONDecodeError):
        return None
    except Exception:
        log.exception("Ошибка проверки Telegram initData")
        return None


def good_name(text):
    if not isinstance(text, str):
        return False

    words = text.split()

    return (
        2 <= len(words) <= 4
        and len(text) <= 60
        and all(NAME_RE.fullmatch(word) for word in words)
    )


def handle(method, path, query, body, user):
    if not user:
        return {"ok": False, "error": "auth"}

    uid = str(user["id"])
    u = C.user(uid)

    if path == "/api/me" and method == "GET":
        lang = u.get("lang")

        if lang not in LANGS:
            code = (user.get("language_code") or "")[:2]
            lang = code if code in LANGS else "ru"

        st = C.state(uid)
        quiz_code = (query.get("q") or "").upper()

        return {
            "ok": True,
            "lang": lang,
            "name": u.get("name"),
            "state": st,
            "quiz": C.info(quiz_code, uid) if quiz_code else None
        }

    if path == "/api/name" and method == "POST":
        raw_name = body.get("name", "")

        if not isinstance(raw_name, str):
            return {"ok": False, "error": "bad_name"}

        name = " ".join(
            word.capitalize()
            for word in raw_name.split()
        )

        if not good_name(name):
            return {"ok": False, "error": "bad_name"}

        u["name"] = name
        C.save()

        return {"ok": True, "name": name}

    if path == "/api/lang" and method == "POST":
        lang = body.get("lang")

        if lang in LANGS:
            u["lang"] = lang
            C.save()
        else:
            return {"ok": False, "error": "bad_lang"}

        return {"ok": True}

    if path == "/api/list" and method == "GET":
        items = []

        for code, qz in sorted(
            C.STATE["quizzes"].items(),
            key=lambda item: -item[1].get("created", 0)
        ):
            result = C.result_of(code, uid)

            if qz.get("open", True) or result:
                items.append(C.info(code, uid))

        return {"ok": True, "items": items}

    if path == "/api/quiz" and method == "GET":
        code = (query.get("q") or "").upper()
        quiz = C.info(code, uid)

        return {
            "ok": bool(quiz),
            "quiz": quiz,
            "error": None if quiz else "no_quiz"
        }

    if path == "/api/start" and method == "POST":
        code = body.get("code")

        if not isinstance(code, str):
            return {"ok": False, "error": "bad_request"}

        err = C.start(uid, code.upper())

        if err:
            return {"ok": False, "error": err}

        return {"ok": True, "state": C.state(uid)}

    if path == "/api/state" and method == "GET":
        session = C.STATE["sessions"].get(uid) or {}

        return {
            "ok": True,
            "state": C.after(uid, session.get("code"))
        }

    if path == "/api/answer" and method == "POST":
        try:
            i = int(body.get("i"))
            k = int(body.get("k"))

            if i < 0 or k < 0:
                return {"ok": False, "error": "bad_request"}

            state = C.answer(uid, i, k)

            return {"ok": True, "state": state}

        except (TypeError, ValueError):
            return {"ok": False, "error": "bad_request"}

    if path == "/api/leave" and method == "POST":
        return {
            "ok": True,
            "state": C.leave(uid)
        }

    if path == "/api/result" and method == "GET":
        code = (query.get("q") or "").upper()

        return {
            "ok": True,
            "result": C.result_of(code, uid),
            "top": C.top(code)
        }

    return None


def find_logo():
    try:
        for name in sorted(os.listdir(HERE)):
            ext = os.path.splitext(name)[1].lower()

            if ext in IMG:
                return os.path.join(HERE, name), IMG[ext]

    except OSError:
        log.exception("Не удалось найти логотип")

    return None, None


def _resp(status, body, ctype, cache="no-store"):
    if isinstance(body, str):
        body = body.encode("utf-8")

    reasons = {
        200: "OK",
        400: "Bad Request",
        401: "Unauthorized",
        404: "Not Found",
        405: "Method Not Allowed",
        413: "Payload Too Large",
        500: "Internal Server Error",
    }

    reason = reasons.get(status, "Unknown")

    head = (
        f"HTTP/1.1 {status} {reason}\r\n"
        f"Content-Type: {ctype}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Cache-Control: {cache}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    return head.encode("latin-1") + body


async def _serve(reader, writer, token):
    try:
        line = await asyncio.wait_for(
            reader.readline(),
            REQUEST_TIMEOUT
        )

        if not line:
            return

        parts = line.decode("latin-1").strip().split()

        if len(parts) != 3:
            writer.write(
                _resp(400, "Bad Request", "text/plain")
            )
            await writer.drain()
            return

        method, target, version = parts

        if version not in ("HTTP/1.0", "HTTP/1.1"):
            writer.write(
                _resp(400, "Bad Request", "text/plain")
            )
            await writer.drain()
            return

        headers = {}

        while True:
            h = await asyncio.wait_for(
                reader.readline(),
                REQUEST_TIMEOUT
            )

            if h in (b"\r\n", b"\n", b""):
                break

            k, sep, v = h.decode("latin-1").partition(":")

            if sep:
                headers[k.strip().lower()] = v.strip()

        content_length = headers.get("content-length", "0")

        try:
            size = int(content_length)
        except ValueError:
            writer.write(
                _resp(400, "Bad Request", "text/plain")
            )
            await writer.drain()
            return

        if size < 0:
            writer.write(
                _resp(400, "Bad Request", "text/plain")
            )
            await writer.drain()
            return

        if size > MAX_BODY_SIZE:
            writer.write(
                _resp(413, "Payload Too Large", "text/plain")
            )
            await writer.drain()
            return

        raw = (
            await asyncio.wait_for(
                reader.readexactly(size),
                REQUEST_TIMEOUT
            )
            if size else b""
        )

        url = urlsplit(target)

        query = dict(
            parse_qsl(url.query, keep_blank_values=True)
        )

        if url.path in ("/", "/index.html") and method == "GET":

            page = os.path.join(HERE, "quiz_app.html")

            try:
                with open(page, encoding="utf-8") as f:
                    content = f.read()

                resp = _resp(
                    200,
                    content,
                    "text/html; charset=utf-8"
                )

            except OSError:
                log.exception("Не удалось открыть quiz_app.html")
                resp = _resp(
                    500,
                    "Internal Server Error",
                    "text/plain"
                )

        elif url.path == "/logo" and method == "GET":

            path, content_type = find_logo()

            if path:
                try:
                    with open(path, "rb") as f:
                        content = f.read()

                    resp = _resp(
                        200,
                        content,
                        content_type,
                        "max-age=86400"
                    )

                except OSError:
                    log.exception("Ошибка загрузки логотипа")
                    resp = _resp(
                        500,
                        "Internal Server Error",
                        "text/plain"
                    )

            else:
                resp = _resp(
                    404,
                    "No logo",
                    "text/plain"
                )

        elif url.path.startswith("/api/"):

            allowed_methods = {
                "/api/me": {"GET"},
                "/api/name": {"POST"},
                "/api/lang": {"POST"},
                "/api/list": {"GET"},
                "/api/quiz": {"GET"},
                "/api/start": {"POST"},
                "/api/state": {"GET"},
                "/api/answer": {"POST"},
                "/api/leave": {"POST"},
                "/api/result": {"GET"},
            }

            if url.path not in allowed_methods:
                resp = _resp(
                    404,
                    json.dumps({"ok": False, "error": "not_found"}),
                    "application/json; charset=utf-8"
                )

            elif method not in allowed_methods[url.path]:
                resp = _resp(
                    405,
                    json.dumps({"ok": False, "error": "method_not_allowed"}),
                    "application/json; charset=utf-8"
                )

            else:
                try:
                    body = (
                        json.loads(raw.decode("utf-8"))
                        if raw else {}
                    )

                    if not isinstance(body, dict):
                        raise ValueError("Invalid JSON body")

                except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                    resp = _resp(
                        400,
                        json.dumps({"ok": False, "error": "bad_json"}),
                        "application/json; charset=utf-8"
                    )

                else:
                    init_data = (
                        headers.get("x-init-data")
                        or body.get("init", "")
                    )

                    user = check_init_data(
                        init_data,
                        token
                    )

                    try:
                        result = handle(
                            method,
                            url.path,
                            query,
                            body,
                            user
                        )

                        if result is None:
                            result = {
                                "ok": False,
                                "error": "not_found"
                            }

                        status = 401 if result.get("error") == "auth" else 200

                    except Exception:
                        log.exception("Ошибка API")

                        result = {
                            "ok": False,
                            "error": "internal_error"
                        }

                        status = 500

                    resp = _resp(
                        status,
                        json.dumps(result, ensure_ascii=False),
                        "application/json; charset=utf-8"
                    )

        else:
            resp = _resp(
                404,
                "Not Found",
                "text/plain"
            )

        writer.write(resp)
        await writer.drain()

    except asyncio.TimeoutError:
        log.warning("Таймаут HTTP-запроса")

    except asyncio.IncompleteReadError:
        log.warning("Неполный HTTP-запрос")

    except Exception:
        log.exception("Ошибка веб-сервера")

    finally:
        writer.close()

        try:
            await writer.wait_closed()
        except Exception:
            pass


async def start_web(token):
    port = int(os.environ.get("PORT", "8080"))

    server = await asyncio.start_server(
        lambda reader, writer: _serve(
            reader,
            writer,
            token
        ),
        "0.0.0.0",
        port
    )

    log.info(
        "Мини-приложение тестов запущено на порту %s",
        port
    )

    return server
