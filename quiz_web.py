"""Мини-приложение тестов: веб-сервер (страница, логотип, API) внутри бота."""
import os
import re
import hmac
import json
import asyncio
import hashlib
import logging
from urllib.parse import parse_qsl, urlsplit

import quiz_core as C

log = logging.getLogger("quiz-web")
HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["ru", "uz", "en", "zh"]
IMG = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
NAME_RE = re.compile(r"[^\W\d_ʻʼ'’-]+(['ʻʼ’-][^\W\d_]+)*")


def check_init_data(init_data, token):
    try:
        pairs = dict(parse_qsl(init_data or "", keep_blank_values=True))
        got = pairs.pop("hash", "")
        if not got:
            return None
        check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
        secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(hmac.new(secret, check.encode(), hashlib.sha256).hexdigest(), got):
            return None
        return json.loads(pairs.get("user", "{}")) or None
    except Exception:
        return None


def good_name(text):
    words = text.split()
    return 2 <= len(words) <= 4 and len(text) <= 60 and all(NAME_RE.fullmatch(w) for w in words)


def handle(method, path, query, body, user):
    if not user:
        return {"ok": False, "error": "auth"}
    uid = str(user["id"])
    u = C.user(uid)
    if path == "/api/me":
        lang = u.get("lang")
        if lang not in LANGS:
            code = (user.get("language_code") or "")[:2]
            lang = code if code in LANGS else "ru"
        st = C.state(uid)
        code = (query.get("q") or "").upper()
        return {"ok": True, "lang": lang, "name": u.get("name"), "state": st,
                "quiz": C.info(code, uid) if code else None}
    if path == "/api/name" and method == "POST":
        name = " ".join(w.capitalize() for w in str(body.get("name", "")).split())
        if not good_name(name):
            return {"ok": False, "error": "bad_name"}
        u["name"] = name
        C.save()
        return {"ok": True, "name": name}
    if path == "/api/lang" and method == "POST":
        if body.get("lang") in LANGS:
            u["lang"] = body["lang"]
            C.save()
        return {"ok": True}
    if path == "/api/quiz":
        q = C.info(query.get("q", ""), uid)
        return {"ok": bool(q), "quiz": q, "error": None if q else "no_quiz"}
    if path == "/api/start" and method == "POST":
        err = C.start(uid, body.get("code"))
        if err:
            return {"ok": False, "error": err}
        return {"ok": True, "state": C.state(uid)}
    if path == "/api/state":
        return {"ok": True, "state": C.after(uid, (C.STATE["sessions"].get(uid) or {}).get("code"))}
    if path == "/api/answer" and method == "POST":
        try:
            return {"ok": True, "state": C.answer(uid, int(body.get("i")), int(body.get("k")))}
        except (TypeError, ValueError):
            return {"ok": False, "error": "bad_request"}
    if path == "/api/leave" and method == "POST":
        return {"ok": True, "state": C.leave(uid)}
    if path ==
