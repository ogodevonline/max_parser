from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Publication(BaseModel):
    """Модель публикации (поста) со всеми метаданными."""
    id: str = Field(..., description="Уникальный идентификатор публикации")
    title: str = Field(..., description="Заголовок публикации")
    content: str = Field(..., description="Текстовое содержимое")
    source_id: str = Field(..., description="ID источника (канала/группы)")
    source_type: str = Field(..., description="Тип источника (например, telegram)")
    published_ts: int = Field(..., description="Unix timestamp времени публикации")
    url: Optional[str] = Field(None, description="Прямая ссылка на пост")
    views: Optional[int] = Field(None, description="Количество просмотров")
    likes: Optional[int] = Field(None, description="Количество лайков")
    reposts: Optional[int] = Field(None, description="Количество репостов")
    comments: Optional[int] = Field(None, description="Количество комментариев")
    media: Optional[List[str]] = Field(None, description="Список ссылок на медиафайлы")
    forward_from: Optional[str] = Field(None, description="Источник пересланного сообщения")
    location: Optional[Dict[str, float]] = Field(None, description="Географические координаты")
    related_resources: Optional[List[str]] = Field(None, description="Связанные ресурсы")
    language: Optional[str] = Field(None, description="Язык публикации")
    sentiment: Optional[str] = Field(None, description="Тональность текста")
    topics: Optional[List[str]] = Field(None, description="Темы публикации")
    entities: Optional[Dict[str, List[Any]]] = Field(None, description="Извлеченные сущности")

class PublicationResponse(BaseModel):
    """Модель ответа со списком публикаций и агрегациями."""
    publications: List[Publication] = Field(..., description="Список публикаций")
    aggregations: Dict[str, Dict[str, int]] = Field(..., description="Агрегированные данные")
