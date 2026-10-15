const n = 4; // number of slides
console.log(1 % n, 3 % n, 4 % n, 5 % n);
console.log(-1 % n);
console.log((-1 + n) % n, (4 + n) % n, (2 + n) % n);

console.log(String(7).padStart(2, '0'));
console.log(String(12).padStart(2, '0'));

const d = new Date(2026, 9, 15, 9, 5, 3); // 15 Oct 2026, 09:05:03
console.log(d.getHours(), d.getMinutes(), d.getSeconds());
console.log(Number('2') + 1, '2' + 1);
