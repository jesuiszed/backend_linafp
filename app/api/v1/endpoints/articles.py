from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.article import Article
from app.models.user import UserRole
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate

router = APIRouter()


def _to_read(item: Article) -> ArticleRead:
    return ArticleRead(
        id=item.id,
        titre=item.title,
        contenu=item.content,
        image_url=item.image_url,
        categorie=item.category,
        auteur=item.author,
        publie=item.is_published,
        date_publication=item.published_at,
    )


@router.get("")
def list_articles(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    categorie: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> dict:
    query = db.query(Article)
    if categorie:
        query = query.filter(Article.category == categorie)
    if q:
        query = query.filter((Article.title.ilike(f"%{q}%")) | (Article.content.ilike(f"%{q}%")))

    total = query.count()
    items = (
        query.order_by(Article.published_at.desc(), Article.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "data": [_to_read(item).model_dump() for item in items],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "categorie": categorie,
            "q": q,
        },
    }


@router.get("/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, db: Session = Depends(get_db)) -> ArticleRead:
    item = db.query(Article).filter(Article.id == article_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return _to_read(item)


@router.post("", response_model=ArticleRead)
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> ArticleRead:
    now = datetime.utcnow()
    item = Article(
        title=payload.titre,
        content=payload.contenu,
        image_url=payload.image_url,
        category=payload.categorie,
        author=payload.auteur,
        is_published=payload.publie,
        published_at=now,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_read(item)


@router.put("/{article_id}", response_model=ArticleRead)
def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> ArticleRead:
    item = db.query(Article).filter(Article.id == article_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    updates = payload.model_dump(exclude_unset=True)
    if "titre" in updates:
        item.title = updates["titre"]
    if "contenu" in updates:
        item.content = updates["contenu"]
    if "image_url" in updates:
        item.image_url = updates["image_url"]
    if "categorie" in updates:
        item.category = updates["categorie"]
    if "auteur" in updates:
        item.author = updates["auteur"]
    if "publie" in updates:
        item.is_published = updates["publie"]

    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_read(item)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> None:
    item = db.query(Article).filter(Article.id == article_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    db.delete(item)
    db.commit()
