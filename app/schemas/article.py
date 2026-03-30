from datetime import datetime

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    titre: str = Field(min_length=3, max_length=200)
    contenu: str = Field(min_length=5)
    image_url: str | None = Field(default=None, max_length=500)
    categorie: str = Field(default="news", max_length=30)
    auteur: str = Field(default="Redaction LINAFP", max_length=120)
    publie: bool = True


class ArticleUpdate(BaseModel):
    titre: str | None = Field(default=None, min_length=3, max_length=200)
    contenu: str | None = Field(default=None, min_length=5)
    image_url: str | None = Field(default=None, max_length=500)
    categorie: str | None = Field(default=None, max_length=30)
    auteur: str | None = Field(default=None, max_length=120)
    publie: bool | None = None


class ArticleRead(BaseModel):
    id: int
    titre: str
    contenu: str
    image_url: str | None
    categorie: str
    auteur: str
    publie: bool
    date_publication: datetime
