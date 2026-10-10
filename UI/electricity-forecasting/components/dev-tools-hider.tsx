"use client"

import { useEffect } from "react"

export function DevToolsHider() {
  useEffect(() => {
    // Функция для скрытия панели инструментов разработчика
    const hideDevTools = () => {
      // Находим все элементы, связанные с панелью инструментов разработчика
      const devToolsElements = document.querySelectorAll(
        '[id^="__next-build-watcher"], [data-nextjs-dialog-overlay], [data-nextjs-dialog], [data-nextjs-toast], [data-nextjs-toast-errors]',
      )

      // Скрываем каждый элемент
      devToolsElements.forEach((element) => {
        if (element instanceof HTMLElement) {
          element.style.display = "none"
          element.style.visibility = "hidden"
          element.style.opacity = "0"
          element.style.pointerEvents = "none"
        }
      })
    }

    // Скрываем панель при загрузке страницы
    hideDevTools()

    // Наблюдаем за изменениями в DOM, чтобы скрыть панель, если она появится снова
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.addedNodes.length) {
          hideDevTools()
        }
      }
    })

    // Начинаем наблюдение за изменениями в body
    observer.observe(document.body, { childList: true, subtree: true })

    // Очищаем наблюдатель при размонтировании компонента
    return () => {
      observer.disconnect()
    }
  }, [])

  return null
}
