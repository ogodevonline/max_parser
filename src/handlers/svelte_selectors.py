"""
Утилиты для работы с динамическими Svelte-селекторами.

Svelte генерирует хэши вида svelte-{HASH}, которые могут меняться.
Этот модуль предоставляет устойчивые методы поиска элементов.
"""
from typing import Optional, List


def build_svelte_selector(base_class: str) -> str:
    """
    Создает CSS-селектор для поиска элементов с динамическим Svelte-хэшем.
    
    Args:
        base_class: Базовый класс (например, 'bubble', 'text', 'meta')
    
    Returns:
        CSS-селектор с паттерном для поиска элемента с любым Svelte-хэшем
    
    Example:
        >>> build_svelte_selector('bubble')
        '[class*="bubble"][class*="svelte-"]'
    """
    return f'[class*="{base_class}"][class*="svelte-"]'


def build_combined_selector(classes: List[str]) -> str:
    """
    Создает селектор для элемента с несколькими классами и Svelte-хэшем.
    
    Args:
        classes: Список базовых классов (например, ['img', 'image'])
    
    Returns:
        CSS-селектор для поиска элемента со всеми указанными классами
    
    Example:
        >>> build_combined_selector(['img', 'image'])
        '[class*="img"][class*="image"][class*="svelte-"]'
    """
    selectors = [f'[class*="{cls}"]' for cls in classes]
    selectors.append('[class*="svelte-"]')
    return ''.join(selectors)


async def query_selector_svelte(
    element, 
    base_class: str, 
    additional_classes: Optional[List[str]] = None
):
    """
    Поиск одного элемента с динамическим Svelte-хэшем.
    
    Args:
        element: Playwright element или page для поиска
        base_class: Основной класс элемента
        additional_classes: Дополнительные классы (опционально)
    
    Returns:
        Найденный элемент или None
    """
    if additional_classes:
        selector = build_combined_selector([base_class] + additional_classes)
    else:
        selector = build_svelte_selector(base_class)
    
    return await element.query_selector(selector)


async def query_selector_all_svelte(
    element,
    base_class: str,
    additional_classes: Optional[List[str]] = None
):
    """
    Поиск всех элементов с динамическим Svelte-хэшем.
    
    Args:
        element: Playwright element или page для поиска
        base_class: Основной класс элемента
        additional_classes: Дополнительные классы (опционально)
    
    Returns:
        Список найденных элементов
    """
    if additional_classes:
        selector = build_combined_selector([base_class] + additional_classes)
    else:
        selector = build_svelte_selector(base_class)
    
    return await element.query_selector_all(selector)
