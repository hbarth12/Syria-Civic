const search = document.querySelector('#search');
const kind = document.querySelector('#kind');
function filterArchive() {
  let count = 0;
  document.querySelectorAll('.archive-card').forEach(card => {
    const match = (card.dataset.search + ' ' + card.textContent.toLowerCase()).includes(search.value.trim().toLowerCase()) && (!kind.value || card.dataset.kind === kind.value);
    card.hidden = !match;
    if (match) count++;
  });
  document.querySelector('#results').textContent = document.documentElement.lang === 'ar' ? `${count} منشور` : `${count} publication${count === 1 ? '' : 's'}`;
  document.querySelector('#empty').hidden = count !== 0;
}
search.addEventListener('input', filterArchive);
kind.addEventListener('change', filterArchive);
