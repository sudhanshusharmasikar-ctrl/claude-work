const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');

let index = 0;

function show(i) {
  // wrap around: -1 becomes the last slide, 4 becomes 0
  index = (i + slides.length) % slides.length;

  slides.forEach((slide) => slide.classList.remove('active'));
  dots.forEach((dot) => dot.classList.remove('active'));

  slides[index].classList.add('active');
  dots[index].classList.add('active');
}

nextBtn.addEventListener('click', () => show(index + 1));
prevBtn.addEventListener('click', () => show(index - 1));

dots.forEach((dot) => {
  dot.addEventListener('click', () => show(Number(dot.dataset.index)));
});

show(0);
