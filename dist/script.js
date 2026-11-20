const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#primary-nav');
const ideasToggle = document.querySelector('.ideas-toggle');
const ideasDropdown = document.querySelector('#ideas-dropdown');
const ideasContainer = document.querySelector('.nav-ideas');
const ideasHover = window.matchMedia('(hover: hover) and (pointer: fine)');
ideasContainer?.addEventListener('pointerenter', () => {
  if (!ideasHover.matches) return;
  ideasToggle.setAttribute('aria-expanded', 'true');
  ideasDropdown.hidden = false;
});
ideasContainer?.addEventListener('pointerleave', () => {
  if (ideasHover.matches && !ideasContainer.contains(document.activeElement)) closeIdeas();
});
const closeIdeas = () => {
  ideasToggle?.setAttribute('aria-expanded', 'false');
  if (ideasDropdown) ideasDropdown.hidden = true;
};
ideasToggle?.addEventListener('click', () => {
  const open = ideasToggle.getAttribute('aria-expanded') !== 'true';
  ideasToggle.setAttribute('aria-expanded', String(open));
  ideasDropdown.hidden = !open;
});
document.addEventListener('click', event => {
  if (!event.target.closest('.nav-ideas')) closeIdeas();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && ideasToggle?.getAttribute('aria-expanded') === 'true') {
    closeIdeas();
    ideasToggle.focus();
  }
});
navigation?.addEventListener('focusout', event => {
  if (!event.relatedTarget?.closest('.nav-ideas')) closeIdeas();
});

menuButton?.addEventListener('click', () => {
  const isOpen = navigation.classList.toggle('is-open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
});

navigation?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    closeIdeas();
    navigation.classList.remove('is-open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

const header = document.querySelector('.expanding-masthead');
const mastheadSpace = document.querySelector('.masthead-space');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let mastheadFrame;
const updateMasthead = () => {
  mastheadFrame = undefined;
  if (!header || !mastheadSpace) return;
  const mobile = window.innerWidth <= 800;
  const largeType = mobile ? Math.min(150, (window.innerWidth - 32) * 0.215) : Math.min(260, window.innerWidth * 0.175);
  const navHeight = mobile ? (navigation?.offsetHeight || 100) : 62;
  const expanded = largeType * 1.08 + (mobile ? navHeight + 28 : 86);
  const compact = mobile ? 58 + navHeight : 80;
  const distance = mobile ? Math.max(140, expanded - compact) : expanded - compact;
  const progress = reducedMotion.matches ? 1 : Math.min(1, Math.max(0, window.scrollY / distance));
  mastheadSpace.style.height = `${reducedMotion.matches ? compact : expanded}px`;
  header.style.height = `${expanded + (compact - expanded) * progress}px`;
  header.style.setProperty('--masthead-font', `${largeType + (30 - largeType) * progress}px`);
  header.style.setProperty('--masthead-nav-top', `${mobile ? expanded - navHeight : expanded - 62 + (16 - (expanded - 62)) * progress}px`);
  header.style.setProperty('--masthead-title-top', `${12 + 8 * progress}px`);
};
const requestMastheadUpdate = () => {
  if (mastheadFrame !== undefined) return;
  mastheadFrame = requestAnimationFrame(updateMasthead);
};
window.addEventListener('scroll', requestMastheadUpdate, { passive: true });
window.addEventListener('resize', requestMastheadUpdate);
reducedMotion.addEventListener('change', requestMastheadUpdate);
updateMasthead();

const newsletter = document.querySelector('#newsletter-form');
const status = document.querySelector('#form-status');

newsletter?.addEventListener('submit', (event) => {
  event.preventDefault();
  status.textContent = 'Thank you — you’re on the list.';
  newsletter.reset();
});
