
  // Добавляем обработчик для всех кнопок submit на странице
  document.querySelectorAll('button[type="submit"]').forEach(button => {
    button.addEventListener("click", function (e) {
      const spinner = button.querySelector('.spinner-border'); // Находим спиннер в кнопке
      const buttonText = button.querySelector('#buttonText'); // Ищем текст кнопки

      // Показываем спиннер и скрываем текст
      spinner.style.display = "inline-block";
      if (buttonText) {
        buttonText.textContent = "Загрузка...";
      }

      // Блокируем кнопку
      button.disabled = true;

      // Имитация задержки перед отправкой формы (например, 2 секунды)
      setTimeout(() => {
        button.closest('form').submit(); // Отправляем форму после задержки
      }, 2000);

      // Предотвращаем немедленную отправку формы
      e.preventDefault();
    });
  });
