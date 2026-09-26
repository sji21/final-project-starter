import re

from app.models import Document


def chunk_documents(documents: list[Document]):
    chunks = []
    for doc in documents:
        # Blank lines define stable paragraphs; long paragraphs retain exact substrings.
        paragraph_no = 0
        for paragraph in re.split(r"\n\s*\n", doc.content):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            for start in range(0, len(paragraph), 1200):
                paragraph_no += 1
                chunks.append(
                    {
                        "id": f"{doc.id}:p{paragraph_no}",
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "document_version": doc.version,
                        "role": doc.role,
                        "text": paragraph[start : start + 1200],
                        "paragraph": paragraph_no,
                    }
                )
    return chunks


def features(text):
    normalized = re.sub(r"\s+", "", text.lower())
    words = set(re.findall(r"[a-z0-9]+|[가-힣]{2,}", text.lower()))
    return words | {normalized[i : i + 2] for i in range(len(normalized) - 1)}


def retrieve(criteria, chunks, top_k=8, full_scan_limit=30):
    targets = [chunk for chunk in chunks if chunk["role"] == "target"]
    results = {}
    for criterion in criteria:
        query = features(criterion.title + " " + criterion.description)
        scored = []
        for chunk in targets:
            terms = features(chunk["text"])
            score = len(query & terms) / max(1, len(query | terms))
            scored.append((score, chunk))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        selected = scored if len(targets) <= full_scan_limit else scored[:top_k]
        results[criterion.id] = {
            "chunk_ids": [chunk["id"] for _, chunk in selected],
            "scores": [round(score, 4) for score, _ in selected],
            "all_target_chunks_presented": len(selected) == len(targets),
            "strategy": "full_scope_with_lexical_ranking"
            if len(selected) == len(targets)
            else "lexical_top_k",
        }
    return results
