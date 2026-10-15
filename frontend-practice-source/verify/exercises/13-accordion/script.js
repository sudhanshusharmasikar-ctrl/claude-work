const items = document.querySelectorAll('.accordion-item');

items.forEach((item) => {
  const header = item.querySelector('.accordion-header');

  header.addEventListener('click', () => {
    const wasOpen = item.classList.contains('open');

    // 1. Close every item
    items.forEach((other) => {
      const otherHeader = other.querySelector('.accordion-header');
      other.classList.remove('open');
      otherHeader.setAttribute('aria-expanded', 'false');
      other.querySelector('.icon').textContent = '+';
    });

    // 2. Open the clicked one, unless it was already open
    if (!wasOpen) {
      item.classList.add('open');
      header.setAttribute('aria-expanded', 'true');
      item.querySelector('.icon').textContent = '-';
    }
  });
});
