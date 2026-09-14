const track = document.querySelector('.episode-track');
const controls = document.querySelector('.carousel-controls');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (track && controls) {
  const previous = controls.querySelector('[data-carousel-prev]');
  const next = controls.querySelector('[data-carousel-next]');
  controls.hidden = false;
  const update = () => {
    previous.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 2;
  };
  const move = (direction) => {
    const card = track.querySelector('.episode-card');
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    track.scrollBy({left: direction * (card.getBoundingClientRect().width + gap), behavior: reducedMotion.matches ? 'instant' : 'smooth'});
  };
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('scroll', update, {passive: true});
  track.addEventListener('keydown', (event) => {
    if (event.target !== track) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(event.key === 'ArrowLeft' ? -1 : 1);
    } else if (event.key === 'Home' || event.key === 'End') {
      event.preventDefault();
      track.scrollTo({left: event.key === 'Home' ? 0 : track.scrollWidth, behavior: 'instant'});
    }
  });
  new ResizeObserver(update).observe(track);
  update();
}

let activeVideo = null;
for (const shell of document.querySelectorAll('[data-video-id]')) {
  const button = shell.querySelector('.video-play');
  button.hidden = false;
  button.addEventListener('click', () => {
    if (activeVideo) {
      activeVideo.querySelector('iframe')?.remove();
      activeVideo.querySelector('.video-play').hidden = false;
      activeVideo.querySelector('.duration').hidden = false;
    }
    const frame = document.createElement('iframe');
    frame.src = `https://www.youtube-nocookie.com/embed/${shell.dataset.videoId}?autoplay=1&rel=0`;
    frame.title = button.getAttribute('aria-label').replace(/^Play /, '');
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    button.hidden = true;
    shell.querySelector('.duration').hidden = true;
    shell.append(frame);
    activeVideo = shell;
    frame.addEventListener('load', () => frame.focus(), {once: true});
  });
}

// Keep machine-readable ISO dates; format the visible text for the visitor.
for (const time of document.querySelectorAll('time[datetime]')) {
  const date = new Date(`${time.dateTime}T12:00:00Z`);
  time.textContent = new Intl.DateTimeFormat(document.documentElement.lang, {year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC'}).format(date);
}
