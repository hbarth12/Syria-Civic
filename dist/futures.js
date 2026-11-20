const interestForm = document.querySelector('#interest-form');
document.querySelectorAll('[data-interest]').forEach(link => {
  link.addEventListener('click', () => {
    for (const box of interestForm.querySelectorAll('[name="interest"]')) {
      if (box.value === link.dataset.interest) box.checked = true;
    }
  });
});
interestForm.addEventListener('submit', event => {
  event.preventDefault();
  const data = new FormData(interestForm);
  const body = [
    'Hello Syria Civic,', '', 'I would like to register my interest in Civic Futures.', '',
    `Name: ${data.get('name')}`, `Email: ${data.get('email')}`,
    `Interests: ${data.getAll('interest').join(', ') || 'Still exploring'}`,
    `University or organization: ${data.get('organization') || 'Not provided'}`, '',
    data.get('message') || '', '',
    `Email updates: ${data.has('updates') ? 'Yes, I would like Civic Futures opportunity and activity emails.' : 'No recurring emails requested; please reply only about this enquiry.'}`
  ].join('\n');
  window.location.href = `mailto:info@syriacivic.com?subject=${encodeURIComponent('Civic Futures — expression of interest')}&body=${encodeURIComponent(body)}`;
  document.querySelector('#interest-status').textContent = document.documentElement.lang === 'ar' ? 'ستفتح مسودة في تطبيق البريد. راجعها واضغط إرسال. لم تُرسل أي بيانات عبر هذه الصفحة. إذا لم يفتح التطبيق، راسل info@syriacivic.com مباشرة.' : 'Your email app should open with a draft. Review it and press Send to register your interest. If it does not open, email info@syriacivic.com directly. Nothing has been submitted through this page.';
});
