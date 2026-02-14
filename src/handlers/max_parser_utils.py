import time
from typing import List
from src.models.publication import Publication, PublicationResponse
from src.handlers.svelte_selectors import (
    query_selector_svelte,
    query_selector_all_svelte
)

async def parse_max_publication(post_el, source_id: str) -> Publication:
    """Парсинг одного сообщения MAX со всеми метаданными."""
    # Текст сообщения (используем устойчивый селектор)
    content_el = await query_selector_svelte(post_el, 'text')
    content = await content_el.inner_text() if content_el else ""
    
    # Мета-информация (время)
    # time_el = await query_selector_svelte(post_el, 'meta')
    # time_text = await time_el.inner_text() if time_el else ""
    
    # Реакции и лайки
    likes = 0
    reaction_els = await query_selector_all_svelte(post_el, 'reaction')
    for rel in reaction_els:
        counter_el = await query_selector_svelte(rel, 'counter')
        if counter_el:
            c_text = await counter_el.inner_text()
            likes += int(c_text) if c_text.isdigit() else 0

    # Медиафайлы
    media = []
    img_els = await query_selector_all_svelte(post_el, 'img', ['image'])
    for img in img_els:
        src = await img.get_attribute('src')
        if src:
            media.append(src)

    # Формируем объект публикации
    return Publication(
        id=f"{source_id}_{int(time.time())}_{hash(content[:20])}",
        title=content[:50].replace('\n', ' '),
        content=content,
        source_id=source_id,
        source_type="max",
        published_ts=int(time.time()), # В идеале парсить из time_text
        likes=likes,
        media=media,
        views=0,
        reposts=0,
        comments=0
    )

async def create_publication_response(publications: List[Publication]) -> PublicationResponse:
    """Создание ответа с агрегированной статистикой."""
    total_likes = sum(p.likes or 0 for p in publications)
    total_media = sum(len(p.media or []) for p in publications)
    
    aggregations = {
        "stats": {
            "total_count": len(publications),
            "total_likes": total_likes,
            "total_media": total_media
        }
    }
    
    return PublicationResponse(
        publications=publications,
        aggregations=aggregations
    )
