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
    if path == "/api/list":
        items = []
        for code, qz in sorted(C.STATE["quizzes"].items(), key=lambda x: -x[1].get("created", 0)):
            res = C.result_of(code, uid)
            if qz.get("open", True) or res:
                items.append(C.info(code, uid))
        return {"ok": True, "items": items}
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
    if path == "/api/result":
        code = (query.get("q") or "").upper()
        return {"ok": True, "result": C.result_of(code, uid), "top": C.top(code)}
    return None


def find_logo():
    for n in sorted(os.listdir(HERE)):
        if os.path.splitext(n)[1].lower() in IMG:
            return os.path.join(HERE, n), IMG[os.path.splitext(n)[1].lower()]
    return None, None


def _resp(status, body, ctype, cache="no-store"):
    if isinstance(body, str):
        body = body.encode("utf-8")
    head = (f"HTTP/1.1 {status} OK\r\nContent-Type: {ctype}\r\nContent-Length: {len(body)}\r\n"
            f"Cache-Control: {cache}\r\nConnection: close\r\n\r\n")
    return head.encode() + body


async def _serve(reader, writer, token):
    try:
        line = await asyncio.wait_for(reader.readline(), 15)
        if not line:
            return
        method, target = line.decode("latin-1").split(" ")[:2]
        headers = {}
        while True:
            h = await asyncio.wait_for(reader.readline(), 15)
            if h in (b"\r\n", b"\n", b""):
                break
            k, _, v = h.decode("latin-1").partition(":")
            headers[k.strip().lower()] = v.strip()
        size = min(int(headers.get("content-length") or 0), 100_000)
        raw = await asyncio.wait_for(reader.readexactly(size), 15) if size else b""
        url = urlsplit(target)
        query = dict(parse_qsl(url.query))
        if url.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "quiz_app.html"), encoding="utf-8") as f:
                resp = _resp(200, f.read(), "text/html; charset=utf-8")
        elif url.path == "/logo":
            p, ct = find_logo()
            if p:
                with open(p, "rb") as f:
                    resp = _resp(200, f.read(), ct, "max-age=86400")
            else:
                resp = _resp(404, "no logo", "text/plain")
        elif url.path.startswith("/api/"):
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                body = {}
            user = check_init_data(headers.get("x-init-data") or body.get("init", ""), token)
            try:
                result = handle(method, url.path, query, body, user)
            except Exception as ex:
                log.exception("Ошибка API")
                result = {"ok": False, "error": f"{type(ex).__name__}: {ex}"[:200]}
            resp = _resp(200 if result else 404, json.dumps(result or {"ok": False}, ensure_ascii=False),
                         "application/json; charset=utf-8")
        else:
            resp = _resp(404, "Not found", "text/plain")
        writer.write(resp)
        await writer.drain()
    except Exception:
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def start_web(token):
    port = int(os.environ.get("PORT", "8080"))
    server = await asyncio.start_server(lambda r, w: _serve(r, w, token), "0.0.0.0", port)
    log.info("Мини-приложение тестов на порту %s", port)
    return server
