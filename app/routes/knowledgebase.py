"""
Knowledge base endpoints.

CSS-35  POST  /articles          — create an article
CSS-36  PUT   /articles/<id>     — update article fields
CSS-37  GET   /articles          — list all articles
CSS-37  GET   /articles/<id>     — single article view
CSS-38  GET   /articles?q=       — search articles (integrated into list)
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from .. import db
from ..models.user import Role
from ..models.article import Article, ArticleType

knowledgebase_bp = Blueprint("knowledgebase", __name__)


def _get_article_or_404(article_id: int):
    """Return (article, None) or (None, error_response)."""
    article = Article.query.get(article_id)
    if article is None:
        return None, (jsonify({"error": "Article not found."}), 404)
    return article, None


# CSS-35  Create article

@knowledgebase_bp.post("/articles")
@login_required
def create_article():
    data = request.get_json(silent=True) or {}

    title       = (data.get("title") or "").strip()
    content     = (data.get("content") or "").strip()
    article_type = (data.get("type") or "").strip()
    attachments_raw = data.get("attachments")

    if not title:
        return jsonify({"error": "Title is required."}), 400
    if len(title) > 200:
        return jsonify({"error": "Title must be 200 characters or fewer."}), 400
    if not content:
        return jsonify({"error": "Content is required."}), 400
    if not article_type:
        return jsonify({"error": "Type is required."}), 400
    if not ArticleType.is_valid(article_type):
        return jsonify({"error": f"Type must be one of: {', '.join(ArticleType.ALL)}."}), 400

    if attachments_raw is not None:
        if isinstance(attachments_raw, list):
            attachments = ",".join(f.strip() for f in attachments_raw if f.strip()) or None
        else:
            attachments = str(attachments_raw).strip() or None
    else:
        attachments = None

    article = Article(
        title=title,
        content=content,
        type=article_type,
        attachments=attachments,
        author_id=current_user.id,
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"message": "Article created successfully.", "article": article.to_dict()}), 201


# CSS-36  Update article

@knowledgebase_bp.put("/articles/<int:article_id>")
@login_required
def update_article(article_id: int):
    article, err = _get_article_or_404(article_id)
    if err:
        return err

    is_author = article.author_id == current_user.id
    is_manager_or_above = Role.has_permission(current_user.role, Role.MANAGER)
    if not is_author and not is_manager_or_above:
        return jsonify({"error": "You do not have permission to edit this article."}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No fields provided to update."}), 400

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return jsonify({"error": "Title cannot be empty."}), 400
        if len(title) > 200:
            return jsonify({"error": "Title must be 200 characters or fewer."}), 400
        article.title = title

    if "content" in data:
        content = (data["content"] or "").strip()
        if not content:
            return jsonify({"error": "Content cannot be empty."}), 400
        article.content = content

    if "type" in data:
        new_type = (data["type"] or "").strip()
        if not ArticleType.is_valid(new_type):
            return jsonify({"error": f"Type must be one of: {', '.join(ArticleType.ALL)}."}), 400
        article.type = new_type

    if "attachments" in data:
        raw = data["attachments"]
        if isinstance(raw, list):
            article.attachments = ",".join(f.strip() for f in raw if f.strip()) or None
        else:
            article.attachments = str(raw).strip() or None

    db.session.commit()
    return jsonify({"message": "Article updated successfully.", "article": article.to_dict()}), 200


# CSS-37 + CSS-38  List / search articles

@knowledgebase_bp.get("/articles")
@login_required
def list_articles():
    q = request.args.get("q", "").strip()
    query = Article.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Article.title.ilike(like), Article.content.ilike(like))
        )
    articles = query.order_by(Article.created_at.desc()).all()
    return jsonify({"articles": [a.to_dict() for a in articles]}), 200


# CSS-37  Single article view

@knowledgebase_bp.get("/articles/<int:article_id>")
@login_required
def get_article(article_id: int):
    article, err = _get_article_or_404(article_id)
    if err:
        return err
    return jsonify({"article": article.to_dict()}), 200
