const products = ['Apple iPhone', 'Samsung Galaxy', 'Apple Watch'];

products.forEach((product) => {
  console.log('->', product);
});

const query = 'APPLE'.toLowerCase();
const matches = products.filter((product) => {
  return product.toLowerCase().includes(query);
});
console.log(query);
console.log(matches);
console.log(matches.length);

console.log('Apple Watch'.includes(''));
console.log(products.filter((p) => p.toLowerCase().includes('')).length);
