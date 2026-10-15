const raw = '   Ada Lovelace  ';
console.log('[' + raw + ']');
console.log('[' + raw.trim() + ']');

const name = raw.trim();
console.log(`Thanks, ${name}! Your account was created.`);

console.log(5 == '5', 5 === '5');
console.log('password' === 'password', 'password' === 'text');

const isMasked = true;
console.log(isMasked ? 'Hide' : 'Show');
