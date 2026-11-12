"""Разбор тестов из текста или Word (.docx): варианты A) B) C) D) или а) б) в) г)."""
import io
import re

LAT = "ABCDEFGH"
CYR = "АБВГДЕЖЗ"          # а) б) в) г) — 1-й, 2-й, 3-й, 4-й вариант
MARK = "*+#✓✔"            # знак правильного ответа
OPT_RE = re.compile(r"^\s*([*+#✓✔]?)\s*([A-Ha-hА-За-з])\s*[).\]:]\s*(.+?)\s*$")
PM_RE = re.compile(r"^\s*([+\-−–])\s*(.+?)\s*$")                       # формат «+ верно / - неверно»
ANS_RE = re.compile(r"^\s*(правильный\s+ответ|ответ|to[ʻ'‘’`]?g[ʻ'‘’`]?ri\s+javob|javob|answer|答案)\s*[:：\-]\s*(.+)$", re.I)
HEAD_RE = {
    "title": re.compile(r"^\s*(название|nomi|title|тема|mavzu)\s*[:：]\s*(.+)$", re.I),
    "subject": re.compile(r"^\s*(предмет|дисциплина|fan|subject|科目)\s*[:：]\s*(.+)$", re.I),
    "time": re.compile(r"^\s*(время|vaqt|time)\s*[:：]\s*(\d+)", re.I),
    "count": re.compile(r"^\s*(вопросов|savollar|questions)\s*[:：]\s*(\d+)", re.I),
}
NUM_RE = re.compile(r"^\s*(?:(?:вопрос|savol|question)\s*)?\d+\s*[.)]\s*", re.I)


def letter_index(ch):
    ch = ch.upper()
    if ch in LAT:
        return LAT.index(ch)
    if ch in CYR:
        return CYR.index(ch)
    return None


def _ptext(p):
    out = []
    for el in p.iter():
        tag = el.tag.split("}")[-1]
        if tag == "t":
            out.append(el.text or "")
        elif tag in ("br", "cr"):
            out.append("\n")
        elif tag == "tab":
            out.append(" ")
    return "".join(out)


def docx_text(data):
    """Текст из Word: абзацы и ячейки таблиц по порядку (переносы Shift+Enter тоже)."""
    import docx
    d = docx.Document(io.BytesIO(data))
    lines = []
    for block in d.element.body.iterchildren():
        tag = block.tag.split("}")[-1]
        if tag == "p":
            lines.append(_ptext(block))
        elif tag == "tbl":
            for p in block.iter():
                if p.tag.endswith("}p"):
                    lines.append(_ptext(p))
    return "\n".join(lines)


def parse(text, title="Тест", per_q=30):
    count, questions, cur, subject = None, [], None, ""

    def close():
        if cur and cur["opts"]:
            questions.append(cur)

    for raw in text.replace("\r", "").split("\n"):
        line = raw.strip().replace("\u00a0", " ")
        if not line:
            continue
        m = HEAD_RE["title"].match(line)
        if m:
            title = m.group(2).strip()
            continue
        m = HEAD_RE["subject"].match(line)
        if m:
            subject = m.group(2).strip()
            continue
        m = HEAD_RE["time"].match(line)
        if m:
            per_q = max(5, min(600, int(m.group(2))))
            continue
        m = HEAD_RE["count"].match(line)
        if m:
            count = int(m.group(2))
            continue
        m = ANS_RE.match(line)
        if m and cur and cur["opts"]:
            k = letter_index(m.group(2).strip()[:1])
            if k is not None and k < len(cur["opts"]):
                cur["right"] = k
            continue
        m = OPT_RE.match(line)
        if m and cur is not None and letter_index(m.group(2)) == len(cur["opts"]):
            text_opt = m.group(3)
            star = bool(m.group(1)) or text_opt.endswith(("*", "(+)", "✓", "✔"))
            text_opt = re.sub(r"\s*(\*|\(\+\)|✓|✔)$", "", text_opt)
            cur["opts"].append(text_opt)
            if star:
                cur["right"] = len(cur["opts"]) - 1
            continue
        m = PM_RE.match(line)
        if m and cur is not None and not NUM_RE.match(line):
            cur["opts"].append(m.group(2))
            if m.group(1) == "+":
                cur["right"] = len(cur["opts"]) - 1
            continue
        if cur is not None and not cur["opts"] and not NUM_RE.match(line):
            cur["q"] += " " + line          # продолжение текста вопроса
            continue
        close()
        cur = {"q": NUM_RE.sub("", line), "opts": [], "right": None}
    close()
    good = [q for q in questions if len(q["opts"]) >= 2 and q["right"] is not None]
    bad = [q["q"][:60] for q in questions if q not in good]
    return {"title": title[:120], "subject": subject[:60], "time": per_q, "count": min(count or len(good), len(good)),
            "questions": good}, bad
