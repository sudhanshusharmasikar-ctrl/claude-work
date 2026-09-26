function cosine(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

function rrf(lists, k = 60) {                 // each list: ids, best first
  const score = new Map();
  for (const list of lists)
    list.forEach((id, i) => score.set(id, (score.get(id) ?? 0) + 1 / (k + i + 1)));
  return [...score]
    .sort((a, b) => b[1] - a[1])                  // highest score first
    .map(([id, s]) => `${id}:${s.toFixed(4)}`);
}

console.log(cosine([1, 2, 3], [2, 4, 6]).toFixed(3),     // same direction
            cosine([1, 0], [0, 1]).toFixed(3));           // at right angles
console.log(rrf([["a", "b", "c"], ["c", "a", "d"]]));
