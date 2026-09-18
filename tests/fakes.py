"""Firestore 없이 API를 검증하기 위한 가짜 클라이언트.

실제 google-cloud-firestore에서 라우터가 사용하는 부분만 흉내낸다.

- client.collection(name)          -> FakeCollection
- collection.document()            -> 새 문서 ID를 자동 생성
- collection.document(document_id) -> 기존 문서 참조
- collection.stream()              -> 저장된 문서 목록
- document.set / update / delete / get

문서는 set 또는 update로 값이 들어올 때만 실제로 만들어진다.
조회만 했는데 빈 문서가 생기면 목록 개수가 틀어지기 때문이다.
"""


class FakeSnapshot:
    """document.get()과 collection.stream()이 돌려주는 읽기 전용 결과."""

    def __init__(self, document_id: str, payload: dict | None):
        self.id = document_id
        self._payload = payload

    @property
    def exists(self) -> bool:
        return self._payload is not None

    def to_dict(self) -> dict:
        return dict(self._payload) if self._payload is not None else {}


class FakeDocumentReference:
    """실제 문서 데이터는 컬렉션이 들고 있고, 참조만 담당한다."""

    def __init__(self, collection: "FakeCollection", document_id: str):
        self._collection = collection
        self.id = document_id

    def set(self, payload: dict) -> None:
        self._collection.documents[self.id] = dict(payload)

    def update(self, payload: dict) -> None:
        if self.id not in self._collection.documents:
            raise KeyError(self.id)
        self._collection.documents[self.id].update(payload)

    def delete(self) -> None:
        self._collection.documents.pop(self.id, None)

    def get(self) -> FakeSnapshot:
        return FakeSnapshot(self.id, self._collection.documents.get(self.id))


class FakeCollection:
    def __init__(self, name: str):
        self.name = name
        self.documents: dict[str, dict] = {}
        self._next_id = 1

    def document(self, document_id: str | None = None) -> FakeDocumentReference:
        if document_id is None:
            document_id = f"{self.name}-{self._next_id}"
            self._next_id += 1
        return FakeDocumentReference(self, document_id)

    def stream(self) -> list[FakeSnapshot]:
        return [
            FakeSnapshot(document_id, payload)
            for document_id, payload in self.documents.items()
        ]


class FakeFirestoreClient:
    def __init__(self):
        self.collections: dict[str, FakeCollection] = {}

    def collection(self, name: str) -> FakeCollection:
        if name not in self.collections:
            self.collections[name] = FakeCollection(name)
        return self.collections[name]
