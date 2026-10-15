const emailPattern = /^\S+@\S+\.\S+$/;

console.log(emailPattern.test('ada@example.com'));
console.log(emailPattern.test('not-an-email'));
console.log(emailPattern.test('ada@example'));
console.log(emailPattern.test('ada lovelace@example.com'));
console.log('secret'.length, 'abc'.length < 6);
