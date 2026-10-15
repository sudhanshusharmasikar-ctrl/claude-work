const nums = [10, 9, 100, 1];
console.log([...nums].sort());
console.log([...nums].sort((a, b) => a - b));

console.log('Ada'.localeCompare('Grace'));
console.log('Grace'.localeCompare('Ada'));
console.log('Ada'.localeCompare('Ada'));

const ages = [45, 36, 41, 54, 33, 62];
console.log([...ages].sort((a, b) => a > b)); // the wrong compare function

const people = [
  { name: 'Grace', age: 45 },
  { name: 'Ada', age: 36 },
  { name: 'Alan', age: 41 },
];
console.log(people[1].name, people[1].age);

const copy = people.filter(() => true);
copy.sort((a, b) => a.age - b.age);
console.log(copy.map((p) => p.name));
console.log(people.map((p) => p.name));
