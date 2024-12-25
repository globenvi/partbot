
  // Добавляем обработчик для всех кнопок submit на странице
  document.querySelectorAll('button[type="submit"]').forEach(button => {
    button.addEventListener("click", function (e) {
      const spinner = document.createElement('span');  // Создаем спиннер
      spinner.classList.add("spinner-border", "spinner-border-sm", "ms-2");  // Классы для спиннера Bootstrap

      const buttonText = button.querySelector('span');  // Ищем текст внутри кнопки, если есть

      // Добавляем спиннер рядом с кнопкой
      button.appendChild(spinner);

      // Если есть текст в кнопке, меняем его
      if (buttonText) {
        buttonText.textContent = "Загрузка...";
      } else {
        button.setAttribute("aria-label", "Загрузка...");  // Если нет текста, меняем aria-label
      }

      // Блокируем кнопку
      button.disabled = true;

      // Имитация задержки перед отправкой формы (например, 2 секунды)
      setTimeout(() => {
        button.closest('form').submit(); // Отправляем форму после задержки
      }, 2000);

      // Предотвращаем немедленную отправку формы
      e.preventDefault();
    })
  });